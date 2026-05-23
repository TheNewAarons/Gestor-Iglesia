from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError

from .services.eventos import ConflictoHorarioException
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date

from .models import (
    Ministerio, Miembro, CajaMinisterio, MovimientoCaja,
    Cancion, ProgramaAlabanza, LeccionEXPLO, Permiso,
    Evento, RecursoComunicacion, IdeaComunicacion
)
from .serializers import (
    MinisterioSerializer, MiembroSerializer, CajaMinisterioSerializer,
    MovimientoCajaSerializer, InventarioSerializer, OfrendaSerializer,
    AsistenciaSerializer, EventoSerializer, CancionSerializer,
    ProgramaAlabanzaSerializer, LeccionEXPLOSerializer,
    RecursoComunicacionSerializer, IdeaComunicacionSerializer,
    PlanificacionActividadSerializer,
    UserSerializer, LoginSerializer, UsuarioCompletoSerializer,
    UsuarioCreateSerializer, UsuarioUpdateSerializer, PermisoSerializer
)
from .permissions import IsAdminOrReadOnly, CanEditEvento

from .selectors import (
    ministerio as ministerio_selectors,
    miembro as miembro_selectors,
    finanzas as finanzas_selectors,
    asistencia as asistencia_selectors,
    inventario as inventario_selectors,
    eventos as eventos_selectors,
    alabanza as alabanza_selectors,
    usuarios as usuarios_selectors,
    comunicacion as comunicacion_selectors,
)
from .services import (
    ministerio as ministerio_services,
    miembro as miembro_services,
    finanzas as finanzas_services,
    asistencia as asistencia_services,
    inventario as inventario_services,
    eventos as eventos_services,
    alabanza as alabanza_services,
    usuarios as usuarios_services,
    comunicacion as comunicacion_services,
)

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if not user:
            return Response(
                {'success': False, 'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            'success': True,
            'user': UserSerializer(user).data
        })

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=900,
            path='/',
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=604800,
            path='/',
        )
        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response({'success': True, 'message': 'Sesión cerrada'})

        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        return response


class TokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {'error': 'No hay token de refresco'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({'success': True})
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=900,
                path='/',
            )
            return response
        except Exception:
            return Response(
                {'error': 'Token de refresco inválido o expirado'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class MeView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'rol': request.user.rol,
            'ministerios_lidera': [
                {'id': m.id, 'nombre': m.nombre, 'slug': m.slug}
                for m in request.user.ministerios_lidera.all()
            ]
        })


class MinisterioViewSet(viewsets.ModelViewSet):
    queryset = Ministerio.objects.all()
    serializer_class = MinisterioSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminOrReadOnly()]

    def get_queryset(self):
        return ministerio_selectors.listar_ministerios()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['get'])
    def dashboard(self, request, slug=None):
        ministry = self.get_object()
        data = ministerio_selectors.obtener_dashboard(ministry)
        return Response({
            'ministerio': MinisterioSerializer(ministry).data,
            'miembros_count': data['miembros_count'],
            'saldo_caja': data['saldo_caja'],
            'ofertas_mes': data['ofertas_mes'],
            'eventos_proximos': EventoSerializer(data['eventos_proximos'], many=True).data,
            'miembros': MiembroSerializer(data['miembros_recientes'], many=True).data,
        })

    @action(detail=True, methods=['get', 'post'])
    def miembros(self, request, slug=None):
        ministry = self.get_object()
        if request.method == 'GET':
            clase = request.query_params.get('clase')
            miembros = miembro_selectors.listar_miembros_por_ministerio(ministry, clase)
            return Response(MiembroSerializer(miembros, many=True).data)

        serializer = MiembroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ministry=ministry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def caja(self, request, slug=None):
        ministry = self.get_object()
        caja = finanzas_services.obtener_o_crear_caja(ministry)

        if request.method == 'GET':
            caja = finanzas_selectors.obtener_caja(ministry) or caja
            return Response(CajaMinisterioSerializer(caja).data)

        serializer = MovimientoCajaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(caja=caja, registrado_por=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def inventario(self, request, slug=None):
        ministry = self.get_object()
        if request.method == 'GET':
            items = inventario_selectors.listar_inventario(ministry)
            return Response(InventarioSerializer(items, many=True).data)

        serializer = InventarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ministry=ministry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def ofrendas(self, request, slug=None):
        ministry = self.get_object()
        if request.method == 'GET':
            ofrendas = finanzas_selectors.listar_ofrendas(ministry, {
                'fecha_inicio': request.query_params.get('fecha_inicio'),
                'fecha_fin': request.query_params.get('fecha_fin'),
            })
            return Response(OfrendaSerializer(ofrendas, many=True).data)

        serializer = OfrendaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ministry=ministry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def asistencia(self, request, slug=None):
        ministry = self.get_object()
        if request.method == 'GET':
            filters = {}
            if fecha := request.query_params.get('fecha'):
                filters['fecha'] = fecha
            else:
                filters['semana_actual'] = True
            if clase := request.query_params.get('clase'):
                filters['clase'] = clase
            asistencias = asistencia_selectors.listar_asistencias(ministry, filters)
            return Response(AsistenciaSerializer(asistencias, many=True).data)

        serializer = AsistenciaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ministry=ministry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='asistencia/resumen')
    def asistencia_resumen(self, request, slug=None):
        ministry = self.get_object()
        mes = request.query_params.get('mes')
        anio = request.query_params.get('anio')
        resultado = asistencia_selectors.resumen_asistencia(
            ministry, int(mes) if mes else None, int(anio) if anio else None
        )
        return Response(resultado)

    @action(detail=True, methods=['get'], url_path='asistencia/acumulativa')
    def asistencia_acumulativa(self, request, slug=None):
        ministry = self.get_object()
        mes = request.query_params.get('mes')
        anio = request.query_params.get('anio')
        clase = request.query_params.get('clase')
        resultado = asistencia_selectors.asistencia_acumulativa(
            ministry, int(mes) if mes else None, int(anio) if anio else None, clase
        )
        return Response(resultado)

    @action(detail=True, methods=['get'], url_path='asistencia/estadisticas')
    def asistencia_estadisticas(self, request, slug=None):
        ministry = self.get_object()
        mes = request.query_params.get('mes')
        anio = request.query_params.get('anio')
        resultado = asistencia_selectors.estadisticas_asistencia(
            ministry, int(mes) if mes else None, int(anio) if anio else None
        )
        return Response(resultado)

    @action(detail=True, methods=['get', 'post'])
    def eventos(self, request, slug=None):
        ministry = self.get_object()
        if request.method == 'GET':
            eventos = eventos_selectors.listar_eventos_por_ministerio(ministry)
            return Response(EventoSerializer(eventos, many=True).data)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        data['ministry'] = ministry.id
        serializer = EventoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        forzar = request.data.get('forzar', False)
        try:
            data = dict(serializer.validated_data)
            ministerios_relacionados = data.pop('ministerios_relacionados', None)
            data.pop('ministry', None)
            data.pop('creado_por', None)
            evento = eventos_services.crear_evento(
                ministry=ministry,
                creado_por=request.user,
                ministerios_relacionados=ministerios_relacionados,
                forzar=forzar,
                **data
            )
            return Response(EventoSerializer(evento).data, status=status.HTTP_201_CREATED)
        except ConflictoHorarioException as e:
            return Response({'error': e.data}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            error_data = e.message_dict if hasattr(e, 'message_dict') else str(e)
            return Response({'error': error_data}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def planificaciones(self, request, slug=None):
        ministry = self.get_object()
        if request.method == 'GET':
            estado = request.query_params.get('estado')
            planes = eventos_selectors.listar_planificaciones(
                ministry, {'estado': estado} if estado else None
            )
            return Response(PlanificacionActividadSerializer(planes, many=True).data)

        serializer = PlanificacionActividadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ministry=ministry, responsable=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CancionViewSet(viewsets.ModelViewSet):
    queryset = Cancion.objects.all()
    serializer_class = CancionSerializer

    def get_queryset(self):
        categoria = self.request.query_params.get('categoria')
        return alabanza_selectors.listar_canciones(categoria)

    @action(detail=False, methods=['post'])
    def generar_programa(self, request):
        fecha_str = request.data.get('fecha')
        ministry_slug = request.data.get('ministerio')
        try:
            fecha = date.fromisoformat(fecha_str)
            ministry = Ministerio.objects.get(slug=ministry_slug)
        except (ValueError, Ministerio.DoesNotExist):
            return Response(
                {'error': 'Fecha o ministry inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        programa = alabanza_services.generar_programa_automatico(ministry, fecha, request.user)
        return Response(ProgramaAlabanzaSerializer(programa).data)


class ProgramaAlabanzaViewSet(viewsets.ModelViewSet):
    queryset = ProgramaAlabanza.objects.all()
    serializer_class = ProgramaAlabanzaSerializer

    def get_queryset(self):
        ministry_slug = self.request.query_params.get('ministerio')
        return alabanza_selectors.listar_programas(ministry_slug)


class LeccionEXPLOViewSet(viewsets.ModelViewSet):
    queryset = LeccionEXPLO.objects.all()
    serializer_class = LeccionEXPLOSerializer


class RecursoComunicacionViewSet(viewsets.ModelViewSet):
    queryset = RecursoComunicacion.objects.all()
    serializer_class = RecursoComunicacionSerializer

    def get_queryset(self):
        return comunicacion_selectors.listar_recursos({
            'ministerio': self.request.query_params.get('ministerio'),
            'tipo': self.request.query_params.get('tipo'),
        })


class IdeaComunicacionViewSet(viewsets.ModelViewSet):
    queryset = IdeaComunicacion.objects.all()
    serializer_class = IdeaComunicacionSerializer

    def get_queryset(self):
        return comunicacion_selectors.listar_ideas({
            'ministerio': self.request.query_params.get('ministerio'),
            'completada': self.request.query_params.get('completada'),
        })


class MiembroViewSet(viewsets.ModelViewSet):
    queryset = Miembro.objects.all()
    serializer_class = MiembroSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'cumpleanos']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return miembro_selectors.listar_miembros({
            'ministerio': self.request.query_params.get('ministerio'),
            'clase': self.request.query_params.get('clase'),
            'estado_civil': self.request.query_params.get('estado_civil'),
            'search': self.request.query_params.get('search'),
        })

    def perform_destroy(self, instance):
        miembro_services.desactivar_miembro(instance)

    @action(detail=False, methods=['get'])
    def cumpleanos(self, request):
        return Response(miembro_selectors.listar_cumpleanos_del_mes())


class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [CanEditEvento()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return eventos_selectors.listar_eventos({
            'ministerio': self.request.query_params.get('ministerio'),
            'fecha_inicio': self.request.query_params.get('fecha_inicio'),
            'fecha_fin': self.request.query_params.get('fecha_fin'),
            'tipo': self.request.query_params.get('tipo'),
        })

    @action(detail=False, methods=['get'])
    def calendario(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        ministerio = request.query_params.get('ministerio')

        if not year or not month:
            return Response(
                {'error': 'Parámetros year y month son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        eventos = eventos_selectors.listar_eventos_calendario(
            int(year), int(month), ministerio
        )
        return Response(EventoSerializer(eventos, many=True).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        forzar = request.data.get('forzar', False)

        try:
            data = dict(serializer.validated_data)
            ministry = data.pop('ministry')
            ministerios_relacionados = data.pop('ministerios_relacionados', None)
            data.pop('creado_por', None)
            evento = eventos_services.crear_evento(
                ministry=ministry,
                creado_por=request.user,
                ministerios_relacionados=ministerios_relacionados,
                forzar=forzar,
                **data
            )
            return Response(EventoSerializer(evento).data, status=status.HTTP_201_CREATED)
        except ConflictoHorarioException as e:
            return Response({'error': e.data}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            error_data = e.message_dict if hasattr(e, 'message_dict') else str(e)
            return Response({'error': error_data}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        forzar = request.data.get('forzar', False)

        try:
            data = dict(serializer.validated_data)
            ministerios_relacionados = data.pop('ministerios_relacionados', None)
            data.pop('ministry', None)
            data.pop('creado_por', None)
            evento = eventos_services.actualizar_evento(
                instance,
                ministerios_relacionados=ministerios_relacionados,
                forzar=forzar,
                **data
            )
            return Response(EventoSerializer(evento).data)
        except ConflictoHorarioException as e:
            return Response({'error': e.data}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            error_data = e.message_dict if hasattr(e, 'message_dict') else str(e)
            return Response({'error': error_data}, status=status.HTTP_400_BAD_REQUEST)


class UsuarioViewSet(viewsets.ViewSet):
    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def list(self, request):
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        usuarios = usuarios_selectors.listar_usuarios()
        return Response(UsuarioCompletoSerializer(usuarios, many=True).data)

    def retrieve(self, request, pk=None):
        usuario = usuarios_selectors.obtener_usuario(pk)
        if not usuario:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        if not self._puede_acceder(request, usuario):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        return Response(UsuarioCompletoSerializer(usuario).data)

    def create(self, request):
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UsuarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = usuarios_services.crear_usuario(
            creado_por=request.user,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            email=serializer.validated_data['email'],
            rol=serializer.validated_data['rol'],
            telefono=serializer.validated_data.get('telefono', ''),
            permisos_especificos=serializer.validated_data.get('permisos_especificos', {}),
            is_active=serializer.validated_data.get('is_active', True),
            ministerios_lidera_ids=serializer.validated_data.get('ministerios_lidera', []),
        )
        return Response(UsuarioCompletoSerializer(usuario).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        usuario = usuarios_selectors.obtener_usuario(pk)
        if not usuario:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UsuarioUpdateSerializer(data=request.data, context={'user': usuario})
        serializer.is_valid(raise_exception=True)

        update_data = {k: v for k, v in serializer.validated_data.items()
                       if k not in ('password_confirm', 'password_nueva', 'ministerios_lidera')}
        if 'ministerios_lidera' in serializer.validated_data:
            update_data['ministerios_lidera_ids'] = serializer.validated_data['ministerios_lidera']
        if 'password_nueva' in serializer.validated_data and serializer.validated_data['password_nueva']:
            update_data['password_nueva'] = serializer.validated_data['password_nueva']

        usuario = usuarios_services.actualizar_usuario(usuario, **update_data)
        return Response(UsuarioCompletoSerializer(usuario).data)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        usuario = usuarios_selectors.obtener_usuario(pk)
        if not usuario:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        if usuario == request.user:
            return Response({'error': 'No puedes desactivarte a ti mismo'}, status=status.HTTP_400_BAD_REQUEST)
        usuarios_services.desactivar_usuario(usuario)
        return Response({'success': True, 'message': 'Usuario desactivado'})

    @action(detail=False, methods=['get'])
    def roles(self, request):
        return Response(usuarios_selectors.listar_roles())

    @action(detail=True, methods=['post'], url_path='cambiar-rol')
    def cambiar_rol(self, request, pk=None):
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        usuario = usuarios_selectors.obtener_usuario(pk)
        if not usuario:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        nuevo_rol = request.data.get('rol')
        if nuevo_rol not in dict(User.ROLES):
            return Response({'error': 'Rol inválido'}, status=status.HTTP_400_BAD_REQUEST)
        usuario = usuarios_services.cambiar_rol_usuario(usuario, nuevo_rol)
        return Response(UsuarioCompletoSerializer(usuario).data)

    @action(detail=True, methods=['post'], url_path='asignar-ministerios')
    def asignar_ministerios(self, request, pk=None):
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        usuario = usuarios_selectors.obtener_usuario(pk)
        if not usuario:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        ministerios_ids = request.data.get('ministerios', [])
        usuario = usuarios_services.asignar_ministerios_usuario(usuario, ministerios_ids)
        return Response(UsuarioCompletoSerializer(usuario).data)

    @action(detail=False, methods=['get'], url_path='ministerios-disponibles')
    def ministerios_disponibles(self, request):
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        return Response(list(usuarios_selectors.listar_ministerios_para_asignacion()))

    @action(detail=False, methods=['get'], url_path='simples')
    def usuarios_simples(self, request):
        if not (request.user.is_authenticated and request.user.rol in ['admin', 'pastora']):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        search = request.query_params.get('search')
        return Response(list(usuarios_selectors.listar_usuarios_simples(search)))

    def _es_admin(self, request):
        return request.user.is_authenticated and request.user.rol == 'admin'

    def _puede_acceder(self, request, usuario):
        return self._es_admin(request) or request.user == usuario


class PermisoViewSet(viewsets.ModelViewSet):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def list(self, request):
        if not request.user.is_authenticated or request.user.rol != 'admin':
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request)
