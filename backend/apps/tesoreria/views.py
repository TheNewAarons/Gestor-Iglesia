from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils.timezone import now
import json

from .models import ConfiguracionFinanzas, InformeMensual
from .serializers import ConfiguracionFinanzasSerializer, InformeMensualSerializer
from .permissions import IsTesoreraOrAdmin, IsAdmin
from .selectors import flujo as flujo_selectors
from .services import informe as informe_services
from apps.ministerios.serializers import MovimientoCajaSerializer


class TesoreriaViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsTesoreraOrAdmin]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        saldos = flujo_selectors.saldos_ministerios()
        config = flujo_selectors.configuracion_actual()
        return Response({
            'saldos': saldos,
            'configuracion': ConfiguracionFinanzasSerializer(config).data,
        })

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

    @action(detail=False, methods=['get'])
    def traspasos(self, request):
        qs = flujo_selectors.listar_traspasos()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = MovimientoCajaSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MovimientoCajaSerializer(qs, many=True)
        return Response(serializer.data)

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

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated, IsTesoreraOrAdmin])
    def configuracion(self, request):
        if request.method == 'GET':
            config = flujo_selectors.configuracion_actual()
            return Response(ConfiguracionFinanzasSerializer(config).data)

        if request.method == 'PUT':
            if request.user.rol != 'admin':
                return Response(
                    {'error': 'Solo el admin puede modificar la configuración.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = ConfiguracionFinanzasSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            config = informe_services.actualizar_configuracion(
                pres_distrital_pct=serializer.validated_data['pres_distrital_pct'],
                pres_educacional_pct=serializer.validated_data['pres_educacional_pct'],
                pres_evangelismo_pct=serializer.validated_data['pres_evangelismo_pct'],
                jubilacion_monto=serializer.validated_data['jubilacion_monto'],
                usuario=request.user,
            )
            return Response(ConfiguracionFinanzasSerializer(config).data)

    @action(detail=False, methods=['get'])
    def informes(self, request):
        informes = flujo_selectors.informes_mensuales()
        serializer = InformeMensualSerializer(informes, many=True)
        return Response(serializer.data)
