from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from apps.ministerios.models import Miembro
from apps.ministerios.permissions import IsSecretariaOrAdmin, IsAdminOrReadOnly
from apps.secretaria.models import (
    ActaReunion, SolicitudTramite, VisitaIglesia,
    ComunicadoInterno, HistorialEstadoMiembro,
    ConfiguracionWhatsApp, MensajeWhatsApp, EnvioWhatsAppLog,
)
from apps.secretaria.serializers import (
    ActaReunionSerializer, SolicitudTramiteSerializer, VisitaIglesiaSerializer,
    ComunicadoInternoSerializer, LecturaComunicadoSerializer,
    HistorialEstadoMiembroSerializer,
    ConfiguracionWhatsAppSerializer, MensajeWhatsAppSerializer,
    EnvioWhatsAppLogSerializer,
)
from apps.secretaria import services, selectors
from apps.secretaria.services import actas as actas_svc
from apps.secretaria.services import solicitudes as solicitudes_svc
from apps.secretaria.services import visitas as visitas_svc
from apps.secretaria.services import comunicados as comunicados_svc
from apps.secretaria.services import documentos as documentos_svc
from apps.secretaria.services import whatsapp as wa_svc
from apps.secretaria.selectors import (
    actas as actas_sel,
    solicitudes as solicitudes_sel,
    visitas as visitas_sel,
    comunicados as comunicados_sel,
    estadisticas as estadisticas_sel,
)


class ActaReunionViewSet(viewsets.ModelViewSet):
    serializer_class = ActaReunionSerializer
    permission_classes = [IsSecretariaOrAdmin]

    def get_queryset(self):
        return actas_sel.listar_actas(
            estado=self.request.query_params.get('estado'),
            tipo=self.request.query_params.get('tipo'),
            search=self.request.query_params.get('search'),
            fecha_desde=self.request.query_params.get('fecha_desde'),
            fecha_hasta=self.request.query_params.get('fecha_hasta'),
        )

    def perform_create(self, serializer):
        acta = actas_svc.crear_acta(self.request.user, **serializer.validated_data)
        serializer.instance = acta

    def perform_update(self, serializer):
        actas_svc.actualizar_acta(serializer.instance, **serializer.validated_data)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        acta = self.get_object()
        if acta.estado != 'borrador':
            return Response(
                {'error': 'Solo se pueden aprobar actas en estado borrador.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        acta = actas_svc.aprobar_acta(acta, request.user)
        return Response(ActaReunionSerializer(acta, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def archivar(self, request, pk=None):
        acta = self.get_object()
        acta = actas_svc.archivar_acta(acta)
        return Response(ActaReunionSerializer(acta, context={'request': request}).data)

    @action(detail=True, methods=['get'])
    def generar_pdf(self, request, pk=None):
        acta = self.get_object()
        pdf_bytes = documentos_svc.generar_acta_pdf(acta)
        filename = f"acta_{acta.id}_{acta.fecha_reunion}.pdf"
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp


class SolicitudTramiteViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudTramiteSerializer
    permission_classes = [IsSecretariaOrAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return solicitudes_sel.listar_solicitudes(
            estado=self.request.query_params.get('estado'),
            tipo=self.request.query_params.get('tipo'),
            search=self.request.query_params.get('search'),
            fecha_desde=self.request.query_params.get('fecha_desde'),
            fecha_hasta=self.request.query_params.get('fecha_hasta'),
        )

    def perform_create(self, serializer):
        solicitud = solicitudes_svc.crear_solicitud(
            self.request.user, **serializer.validated_data
        )
        serializer.instance = solicitud

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        solicitud = self.get_object()
        nuevo_estado = request.data.get('estado')
        notas = request.data.get('notas', '')
        estados_validos = [e[0] for e in SolicitudTramite.ESTADO_CHOICES]
        if nuevo_estado not in estados_validos:
            return Response(
                {'error': f'Estado inválido. Opciones: {estados_validos}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        solicitud = solicitudes_svc.actualizar_estado_solicitud(
            solicitud, nuevo_estado, request.user, notas
        )
        return Response(SolicitudTramiteSerializer(solicitud, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def generar_documento(self, request, pk=None):
        solicitud = self.get_object()
        if not solicitud.solicitante_miembro:
            return Response(
                {'error': 'Solicitud no tiene miembro vinculado para generar documento.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        solicitud = solicitudes_svc.generar_documento_solicitud(solicitud)
        return Response(SolicitudTramiteSerializer(solicitud, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def exportar_pdf(self, request):
        qs = self.get_queryset()
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        pdf_bytes = documentos_svc.reporte_solicitudes_pdf(qs, fecha_desde, fecha_hasta)
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="reporte_solicitudes.pdf"'
        return resp


class VisitaIglesiaViewSet(viewsets.ModelViewSet):
    serializer_class = VisitaIglesiaSerializer
    permission_classes = [IsSecretariaOrAdmin]

    def get_queryset(self):
        activo_param = self.request.query_params.get('activo')
        activo = activo_param.lower() == 'true' if activo_param else None
        return visitas_sel.listar_visitas(
            activo=activo if activo_param else True,
            seguimiento=self.request.query_params.get('seguimiento'),
            search=self.request.query_params.get('search'),
            fecha_desde=self.request.query_params.get('fecha_desde'),
            fecha_hasta=self.request.query_params.get('fecha_hasta'),
        )

    def perform_create(self, serializer):
        visita = visitas_svc.registrar_visita(
            self.request.user, **serializer.validated_data
        )
        serializer.instance = visita

    @action(detail=True, methods=['post'])
    def actualizar_seguimiento(self, request, pk=None):
        visita = self.get_object()
        seguimiento = request.data.get('seguimiento')
        responsable_id = request.data.get('responsable_id')
        opciones = [s[0] for s in VisitaIglesia.SEGUIMIENTO_CHOICES]
        if seguimiento not in opciones:
            return Response(
                {'error': f'Seguimiento inválido. Opciones: {opciones}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        responsable = None
        if responsable_id:
            from apps.ministerios.models import User
            try:
                responsable = User.objects.get(pk=responsable_id)
            except User.DoesNotExist:
                pass
        visita = visitas_svc.actualizar_seguimiento(visita, seguimiento, responsable)
        return Response(VisitaIglesiaSerializer(visita, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def vincular_miembro(self, request, pk=None):
        visita = self.get_object()
        miembro_id = request.data.get('miembro_id')
        if not miembro_id:
            return Response(
                {'error': 'miembro_id requerido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            miembro = Miembro.objects.get(pk=miembro_id)
        except Miembro.DoesNotExist:
            return Response({'error': 'Miembro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        visita = visitas_svc.vincular_a_miembro(visita, miembro)
        return Response(VisitaIglesiaSerializer(visita, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def exportar_pdf(self, request):
        qs = self.get_queryset()
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        pdf_bytes = documentos_svc.reporte_visitas_pdf(qs, fecha_desde, fecha_hasta)
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="reporte_visitas.pdf"'
        return resp


class ComunicadoInternoViewSet(viewsets.ModelViewSet):
    serializer_class = ComunicadoInternoSerializer
    permission_classes = [IsSecretariaOrAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        publicado_param = self.request.query_params.get('publicado')
        return comunicados_sel.listar_comunicados(
            publicado=publicado_param.lower() == 'true' if publicado_param else None,
            search=self.request.query_params.get('search'),
            fecha_desde=self.request.query_params.get('fecha_desde'),
            fecha_hasta=self.request.query_params.get('fecha_hasta'),
        )

    def perform_create(self, serializer):
        ministerios_ids = self.request.data.getlist('ministerios_destino', [])
        comunicado = comunicados_svc.crear_comunicado(
            self.request.user,
            ministerios_ids=ministerios_ids or None,
            **serializer.validated_data,
        )
        serializer.instance = comunicado

    @action(detail=True, methods=['post'])
    def publicar(self, request, pk=None):
        comunicado = self.get_object()
        comunicado = comunicados_svc.publicar_comunicado(comunicado)
        return Response(ComunicadoInternoSerializer(comunicado, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def marcar_leido(self, request, pk=None):
        comunicado = self.get_object()
        lectura = comunicados_svc.marcar_leido(comunicado, request.user)
        return Response(LecturaComunicadoSerializer(lectura).data)

    @action(detail=True, methods=['get'])
    def lecturas(self, request, pk=None):
        comunicado = self.get_object()
        lecturas = comunicados_sel.lecturas_de_comunicado(comunicado.id)
        return Response(LecturaComunicadoSerializer(lecturas, many=True).data)


class HistorialEstadoMiembroViewSet(viewsets.ModelViewSet):
    serializer_class = HistorialEstadoMiembroSerializer
    permission_classes = [IsSecretariaOrAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = HistorialEstadoMiembro.objects.select_related(
            'miembro', 'documentado_por'
        ).order_by('-fecha_evento')
        if miembro_id := self.request.query_params.get('miembro'):
            qs = qs.filter(miembro_id=miembro_id)
        if tipo_evento := self.request.query_params.get('tipo_evento'):
            qs = qs.filter(tipo_evento=tipo_evento)
        return qs

    def perform_create(self, serializer):
        serializer.save(documentado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def exportar_pdf(self, request):
        from apps.secretaria.services import documentos as documentos_svc
        from django.http import HttpResponse
        qs = self.get_queryset()
        pdf = documentos_svc.reporte_historial_pdf(qs)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="historial_estado_miembros.pdf"'
        return response


class DirectorioViewSet(viewsets.GenericViewSet):
    permission_classes = [IsSecretariaOrAdmin]

    def _get_miembros(self):
        from apps.ministerios.models import Miembro
        qs = Miembro.objects.select_related('ministry').order_by(
            'primer_apellido', 'primer_nombre'
        )
        ministerio = self.request.query_params.get('ministerio')
        activo = self.request.query_params.get('activo')
        clase = self.request.query_params.get('clase')
        if ministerio:
            qs = qs.filter(ministry__slug=ministerio)
        if activo is not None:
            qs = qs.filter(activo=activo.lower() == 'true')
        else:
            qs = qs.filter(activo=True)
        if clase:
            qs = qs.filter(clase=clase)
        return qs

    @action(detail=False, methods=['get'])
    def exportar_excel(self, request):
        miembros = self._get_miembros()
        excel_bytes = documentos_svc.exportar_directorio_excel(miembros)
        resp = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        resp['Content-Disposition'] = 'attachment; filename="directorio_miembros.xlsx"'
        return resp

    @action(detail=False, methods=['get'])
    def exportar_pdf(self, request):
        miembros = self._get_miembros()
        pdf_bytes = documentos_svc.exportar_directorio_pdf(miembros)
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="directorio_miembros.pdf"'
        return resp


class EstadisticasViewSet(viewsets.GenericViewSet):
    permission_classes = [IsSecretariaOrAdmin]

    @action(detail=False, methods=['get'])
    def resumen(self, request):
        membresia = estadisticas_sel.resumen_membresia()
        secretaria = estadisticas_sel.resumen_secretaria()
        return Response({**membresia, **secretaria})


class WhatsAppViewSet(viewsets.GenericViewSet):
    permission_classes = [IsSecretariaOrAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(detail=False, methods=['get'])
    def status(self, request):
        try:
            data = wa_svc.get_status()
        except ConnectionError as e:
            data = {'status': 'unavailable', 'error': str(e)}
        return Response(data)

    @action(detail=False, methods=['get'])
    def qr(self, request):
        try:
            data = wa_svc.get_qr()
        except ConnectionError as e:
            data = {'qr': None, 'status': 'unavailable', 'error': str(e)}
        return Response(data)

    @action(detail=False, methods=['delete'])
    def logout(self, request):
        try:
            data = wa_svc.logout()
        except ConnectionError as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(data)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def config(self, request):
        cfg = ConfiguracionWhatsApp.obtener()
        if request.method == 'GET':
            return Response(ConfiguracionWhatsAppSerializer(cfg).data)
        serializer = ConfiguracionWhatsAppSerializer(
            cfg, data=request.data, partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Reschedule if hora_envio changed
        if 'hora_envio' in serializer.validated_data:
            try:
                from apps.secretaria.scheduler import _scheduler
                hora = cfg.hora_envio
                from apscheduler.triggers.cron import CronTrigger
                _scheduler.reschedule_job(
                    'envio_dominical_whatsapp',
                    trigger=CronTrigger(
                        day_of_week='sun', hour=hora.hour, minute=hora.minute
                    ),
                )
            except Exception:
                pass

        return Response(ConfiguracionWhatsAppSerializer(cfg).data)

    @action(detail=False, methods=['get', 'post'])
    def mensajes(self, request):
        if request.method == 'GET':
            msgs = MensajeWhatsApp.objects.all()
            return Response(MensajeWhatsAppSerializer(msgs, many=True, context={'request': request}).data)
        serializer = MensajeWhatsAppSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path='mensajes/(?P<msg_id>[0-9]+)')
    def mensaje_detail(self, request, msg_id=None):
        try:
            msg = MensajeWhatsApp.objects.get(pk=msg_id)
        except MensajeWhatsApp.DoesNotExist:
            return Response({'error': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MensajeWhatsAppSerializer(
            msg, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='mensajes/(?P<msg_id>[0-9]+)/limpiar_imagen')
    def limpiar_imagen_mensaje(self, request, msg_id=None):
        try:
            msg = MensajeWhatsApp.objects.get(pk=msg_id)
        except MensajeWhatsApp.DoesNotExist:
            return Response({'error': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if msg.imagen:
            msg.imagen.delete(save=False)
            msg.imagen = None
            msg.save(update_fields=['imagen'])
        return Response(MensajeWhatsAppSerializer(msg, context={'request': request}).data)

    @action(detail=False, methods=['post'])
    def test_send(self, request):
        _ERRORES = {
            'sin_grupo': 'No hay grupo de WhatsApp configurado. Ingresa el Group JID en la configuración.',
            'inactivo': 'El envío automático está desactivado, pero igual se intentará el envío de prueba.',
            'sin_mensajes': 'No hay mensajes guardados. Agrega al menos un mensaje en las tarjetas.',
        }
        try:
            log, motivo = wa_svc.ejecutar_envio_dominical(force=True)
        except ConnectionError as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if log is None:
            return Response(
                {'error': _ERRORES.get(motivo, 'No se pudo enviar.')},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(EnvioWhatsAppLogSerializer(log).data)

    @action(detail=False, methods=['get'])
    def historial(self, request):
        logs = EnvioWhatsAppLog.objects.select_related('mensaje').all()[:50]
        return Response(EnvioWhatsAppLogSerializer(logs, many=True).data)
