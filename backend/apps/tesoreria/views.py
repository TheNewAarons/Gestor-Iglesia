from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils.timezone import now
import json

from .models import ConfiguracionFinanzas, InformeMensual, MovimientoTesoreria, CuotaFija
from .serializers import (
    ConfiguracionFinanzasSerializer, InformeMensualSerializer,
    MovimientoTesoreriaSerializer, CuotaFijaSerializer,
)
from .permissions import IsTesoreraOrAdmin
from .selectors import flujo as flujo_selectors
from .services import informe as informe_services
from .services import traspasos as traspasos_services
from .services import exportar_excel as exportar_excel_services
from apps.ministerios.serializers import MovimientoCajaSerializer


class TesoreriaViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsTesoreraOrAdmin]

    # ---- Dashboard ----
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        saldos = flujo_selectors.saldos_ministerios()
        config = flujo_selectors.configuracion_actual()
        return Response({
            'saldos': saldos,
            'configuracion': ConfiguracionFinanzasSerializer(config).data,
        })

    # ---- Flujo de caja ----
    @action(detail=False, methods=['get'], url_path='flujo-caja')
    def flujo_caja(self, request):
        mes = int(request.query_params.get('mes', now().month))
        anio = int(request.query_params.get('anio', now().year))
        consolidado = flujo_selectors.consolidar_flujo_caja(mes, anio)
        saldos = flujo_selectors.saldos_ministerios()
        return Response({
            **consolidado,
            'saldos_ministerios': saldos,
        })

    # ---- Boletas ----
    @action(detail=False, methods=['get'])
    def boletas(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        from datetime import datetime

        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

        qs = flujo_selectors.listar_boletas_egresos(fecha_inicio, fecha_fin)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = MovimientoCajaSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MovimientoCajaSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='boleta-detalle')
    def boleta_detalle(self, request):
        boleta_id = request.query_params.get('id')
        if not boleta_id:
            return Response({'error': 'Se requiere parametro id'}, status=400)
        from apps.ministerios.models import MovimientoCaja
        try:
            boleta = MovimientoCaja.objects.select_related(
                'caja__ministry', 'registrado_por'
            ).get(pk=boleta_id, tipo='egreso')
        except MovimientoCaja.DoesNotExist:
            return Response({'error': 'Boleta no encontrada'}, status=404)
        return Response({
            'id': boleta.id,
            'monto': float(boleta.monto),
            'descripcion': boleta.descripcion,
            'fecha': boleta.fecha.isoformat(),
            'imagen': boleta.imagen.url if boleta.imagen else None,
            'ministry_nombre': boleta.caja.ministry.nombre,
            'ministry_color': boleta.caja.ministry.color,
            'registrado_por_nombre': boleta.registrado_por.get_full_name() if boleta.registrado_por else None,
        })

    # ---- Traspasos ----
    @action(detail=False, methods=['get'])
    def traspasos(self, request):
        qs = flujo_selectors.listar_traspasos()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = MovimientoCajaSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MovimientoCajaSerializer(qs, many=True)
        return Response(serializer.data)

    @traspasos.mapping.post
    def crear_traspaso(self, request):
        ministry_slug = request.data.get('ministry_slug')
        monto_str = request.data.get('monto')
        descripcion = request.data.get('descripcion', '')

        if not ministry_slug or not monto_str:
            return Response(
                {'error': 'ministry_slug y monto son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            monto = Decimal(str(monto_str))
            if monto <= 0:
                raise ValueError
        except (ValueError, Exception):
            return Response(
                {'error': 'Monto debe ser un numero positivo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            movimiento = traspasos_services.registrar_traspaso(
                ministry_slug=ministry_slug,
                monto=monto,
                descripcion=descripcion,
                usuario=request.user,
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MovimientoCajaSerializer(movimiento)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---- Informe ----
    @action(detail=False, methods=['get'])
    def informe(self, request):
        mes = int(request.query_params.get('mes', now().month))
        anio = int(request.query_params.get('anio', now().year))
        force = request.query_params.get('force', 'false').lower() == 'true'

        informe_existente = flujo_selectors.obtener_informe(anio, mes)
        if informe_existente and not force:
            return Response(InformeMensualSerializer(informe_existente).data)

        informe = informe_services.generar_informe(anio, mes, request.user)
        return Response(InformeMensualSerializer(informe).data)

    @action(detail=False, methods=['get'], url_path='exportar-informe')
    def exportar_informe(self, request):
        mes = int(request.query_params.get('mes', now().month))
        anio = int(request.query_params.get('anio', now().year))
        informe = flujo_selectors.obtener_informe(anio, mes)
        if not informe:
            informe = informe_services.generar_informe(anio, mes, request.user)

        content = json.dumps(informe.datos, indent=2, ensure_ascii=False)
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="informe_{anio}_{mes:02d}.json"'
        return response

    @action(detail=False, methods=['get'], url_path='exportar-pdf')
    def exportar_pdf(self, request):
        mes = int(request.query_params.get('mes', now().month))
        anio = int(request.query_params.get('anio', now().year))
        informe = flujo_selectors.obtener_informe(anio, mes)
        if not informe:
            informe = informe_services.generar_informe(anio, mes, request.user)

        d = informe.datos
        months = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_RIGHT, TA_CENTER
        import io

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=15*mm, bottomMargin=15*mm,
                               leftMargin=20*mm, rightMargin=20*mm)
        styles = getSampleStyleSheet()
        style_right = ParagraphStyle('Right', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=9)
        style_center = ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)
        style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9, spaceBefore=4, spaceAfter=2)
        style_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceBefore=10, spaceAfter=4)
        style_title = ParagraphStyle('Title', parent=styles['Title'], fontSize=16, spaceAfter=12)

        fmt = lambda v: f'{v:,.0f} Gs'
        ing = d['ingresos']
        egr = d['egresos']
        tot = d['totales']
        conf = d['configuracion']

        def row(label, value, bold=False):
            s = style_bold if bold else styles['Normal']
            sr = ParagraphStyle('R', parent=s, alignment=TA_RIGHT, fontSize=9) if isinstance(value, str) and value else style_right
            if isinstance(value, str):
                return [Paragraph(label, s), Paragraph(value, sr)]
            return [Paragraph(label, s), Paragraph(fmt(value), style_right)]

        def section(title, items):
            result = [Paragraph(title, style_h2)]
            data = [row(k, v) for k, v in items]
            t = Table(data, colWidths=[120*mm, 60*mm])
            t.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LINEBELOW', (0, 0), (-1, -1), 0.3, colors.HexColor('#eeeeee')),
                ('LINEBELOW', (0, len(data)-1), (-1, len(data)-1), 1, colors.HexColor('#cccccc')),
            ]))
            result.append(t)
            result.append(Spacer(1, 6*mm))
            return result

        months_es = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        story = []
        story.append(Paragraph(f'INFORME MENSUAL - {months_es[mes]} {anio}', style_title))

        # INGRESOS
        story.append(Paragraph('INGRESOS', style_h2))

        story += section('1. Saldo del Mes Pasado', [
            ('Otros Ministerios', ing['saldo_mes_pasado']['otros_ministerios']),
            ('Iglesia', ing['saldo_mes_pasado']['iglesia']),
            ('DNI', ing['saldo_mes_pasado']['dni']),
            ('JNI', ing['saldo_mes_pasado']['jni']),
            ('MNI', ing['saldo_mes_pasado']['mni']),
        ])

        story += section('2. Iglesia Local', [
            ('Ofrendas', ing['iglesia_local']['ofrendas']),
            ('Diezmos', ing['iglesia_local']['diezmos']),
            ('Especiales', ing['iglesia_local']['especiales']),
        ])

        story += section('3. Otros Ministerios', [
            (m['nombre'], m['ingresos']) for m in ing['otros_ministerios']
        ] + [
            ('Ahorro', ing['fondos_especiales']['ahorro']),
            ('Proyectos', ing['fondos_especiales']['proyectos']),
        ])

        story += section('4. DNI', [('Ofrendas DNI', ing['dni']['total_ofrendas'])])
        story += section('5. JNI', [('Ofrendas JNI', ing['jni']['total_ofrendas'])])

        mni_items = [(k.replace('_', ' ').title(), v) for k, v in ing['mni'].items() if k != 'total']
        story += section('6. MNI', mni_items)

        # EGRESOS
        story.append(Spacer(1, 8*mm))
        story.append(Paragraph('EGRESOS', style_h2))

        story += section('1. Iglesia Local', [
            (k.replace('_', ' ').title(), v) for k, v in egr['iglesia_local'].items()
        ])

        story += section('2. Otros Ministerios', [
            (m['nombre'], m['egresos']) for m in egr['otros_ministerios']
        ])

        for idx, (key, name) in enumerate([('dni', 'DNI'), ('jni', 'JNI'), ('mni', 'MNI')], 3):
            story += section(f'{idx}. {name}', [
                (k.replace('_', ' ').title(), v) for k, v in egr[key].items()
            ])

        # SALDO FIN DE MES
        story.append(Spacer(1, 8*mm))
        story.append(Paragraph('SALDO FIN DE MES', style_h2))
        data = [
            row('Saldo Mes Pasado', tot['saldo_mes_pasado']),
            row('Total Ingresos', tot['total_ingresos']),
            row('Total Gastos', tot['total_gastos']),
            row('Saldo Final', tot['saldo_final'], bold=True),
        ]
        t = Table(data, colWidths=[120*mm, 60*mm])
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor('#eeeeee')),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.HexColor('#333333')),
        ]))
        story.append(t)

        # Footer
        story.append(Spacer(1, 10*mm))
        story.append(Paragraph(
            f'Configuracion: PRES.DISTRITAL {conf["pres_distrital_pct"]}% | '
            f'PRES EDUCACIONAL {conf["pres_educacional_pct"]}% | '
            f'PRES.EVANGELISMO {conf["pres_evangelismo_pct"]}% | '
            f'Jubilacion {fmt(conf["jubilacion_monto"])}',
            style_center
        ))

        doc.build(story)
        pdf = buf.getvalue()
        buf.close()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="informe_{anio}_{mes:02d}.pdf"'
        return response

    @action(detail=False, methods=['get'], url_path='exportar-excel')
    def exportar_excel(self, request):
        mes = int(request.query_params.get('mes', now().month))
        anio = int(request.query_params.get('anio', now().year))
        buf = exportar_excel_services.exportar_informe_excel(anio, mes, request.user)
        response = HttpResponse(
            buf.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="informe_{anio}_{mes:02d}.xlsx"'
        return response

    # ---- Configuracion ----
    @action(detail=False, methods=['get', 'put'])
    def configuracion(self, request):
        if request.method == 'GET':
            config = flujo_selectors.configuracion_actual()
            return Response(ConfiguracionFinanzasSerializer(config).data)

        if request.method == 'PUT':
            if request.user.rol != 'admin':
                return Response(
                    {'error': 'Solo el admin puede modificar la configuracion.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = ConfiguracionFinanzasSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            config = informe_services.actualizar_configuracion(
                pres_distrital_pct=serializer.validated_data.get('pres_distrital_pct'),
                pres_educacional_pct=serializer.validated_data.get('pres_educacional_pct'),
                pres_evangelismo_pct=serializer.validated_data.get('pres_evangelismo_pct'),
                jubilacion_monto=serializer.validated_data.get('jubilacion_monto'),
                usuario=request.user,
            )
            return Response(ConfiguracionFinanzasSerializer(config).data)

    # ---- Informes historicos ----
    @action(detail=False, methods=['get'])
    def informes(self, request):
        informes = flujo_selectors.informes_mensuales()
        serializer = InformeMensualSerializer(informes, many=True)
        return Response(serializer.data)

    # ---- Movimientos de tesoreria ----
    @action(detail=False, methods=['get', 'post'])
    def movimientos(self, request):
        if request.method == 'GET':
            tipo = request.query_params.get('tipo')
            qs = flujo_selectors.listar_movimientos_tesoreria(tipo)
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = MovimientoTesoreriaSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = MovimientoTesoreriaSerializer(qs, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            serializer = MovimientoTesoreriaSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(registrado_por=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---- Cuotas fijas ----
    @action(detail=False, methods=['get', 'put'])
    def cuotas(self, request):
        if request.method == 'GET':
            qs = flujo_selectors.listar_cuotas_fijas()
            serializer = CuotaFijaSerializer(qs, many=True)
            return Response(serializer.data)

        if request.method == 'PUT':
            items = request.data if isinstance(request.data, list) else [request.data]
            results = []
            for item in items:
                ministry_id = item.get('ministry')
                tipo = item.get('tipo')
                monto = item.get('monto')
                if not ministry_id or not tipo or monto is None:
                    continue
                cuota, _ = CuotaFija.objects.update_or_create(
                    ministry_id=ministry_id, tipo=tipo,
                    defaults={'monto': Decimal(str(monto))}
                )
                results.append(CuotaFijaSerializer(cuota).data)
            return Response(results if len(results) > 1 else (results[0] if results else {}),
                          status=status.HTTP_200_OK)
