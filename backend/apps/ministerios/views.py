from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta

from .models import (
    Ministerio, Miembro, CajaMinisterio, MovimientoCaja,
    Inventario, Ofrenda, Asistencia, Evento, Cancion,
    ProgramaAlabanza, LeccionEXPLO, RecursoComunicacion, IdeaComunicacion,
    PerfilUsuario, Permiso
)
from .serializers import (
    MinisterioSerializer, MiembroSerializer, CajaMinisterioSerializer,
    MovimientoCajaSerializer, InventarioSerializer, OfrendaSerializer,
    AsistenciaSerializer, EventoSerializer, CancionSerializer,
    ProgramaAlabanzaSerializer, LeccionEXPLOSerializer,
    RecursoComunicacionSerializer, IdeaComunicacionSerializer,
    PerfilUsuarioSerializer, LoginSerializer, UsuarioCompletoSerializer,
    UsuarioCreateSerializer, UsuarioUpdateSerializer, PermisoSerializer
)
from .permissions import IsAdminOrReadOnly, IsLiderOrAdmin, CanAccessMinisterio


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """Inicio de sesión"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                login(request, user)
                perfil = getattr(user, 'perfil', None)
                return Response({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'rol': perfil.rol if perfil else None
                    }
                })
            return Response(
                {'success': False, 'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Cierre de sesión"""

    def post(self, request):
        logout(request)
        return Response({'success': True, 'message': 'Sesión cerrada'})


class MeView(APIView):
    """Datos del usuario actual"""

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'No autenticado'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        user = request.user
        perfil = getattr(user, 'perfil', None)
        return Response({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'rol': perfil.rol if perfil else None,
            'ministerios_lidera': [
                {'id': m.id, 'nombre': m.nombre, 'slug': m.slug}
                for m in perfil.ministerios_lidera.all()
            ] if perfil else []
        })


class MinisterioViewSet(viewsets.ModelViewSet):
    """CRUD de Ministerios"""
    queryset = Ministerio.objects.all()
    serializer_class = MinisterioSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminOrReadOnly()]

    def get_queryset(self):
        queryset = Ministerio.objects.annotate(
            miembros_count=Count('miembros', filter=Q(miembros__activo=True))
        )
        return queryset

    @action(detail=True, methods=['get'])
    def dashboard(self, request, slug=None):
        """Dashboard del ministerio"""
        ministry = self.get_object()

        miembros_count = ministry.miembros.filter(activo=True).count()

        caja = getattr(ministry, 'caja', None)
        saldo_caja = caja.calcular_saldo() if caja else 0

        eventos_proximos = ministry.eventos.filter(
            fecha_inicio__gte=date.today()
        ).order_by('fecha_inicio')[:5]

        ofertas_mes = ministry.ofrendas.filter(
            fecha__month=date.today().month,
            fecha__year=date.today().year
        ).aggregate(total=Sum('monto'))['total'] or 0

        return Response({
            'ministerio': MinisterioSerializer(ministry).data,
            'miembros_count': miembros_count,
            'saldo_caja': float(saldo_caja),
            'ofertas_mes': float(ofertas_mes),
            'eventos_proximos': EventoSerializer(eventos_proximos, many=True).data,
            'miembros': MiembroSerializer(
                ministry.miembros.filter(activo=True)[:10],
                many=True
            ).data
        })

    @action(detail=True, methods=['get', 'post'])
    def miembros(self, request, slug=None):
        """Lista/crear miembros del ministerio"""
        ministry = self.get_object()

        if request.method == 'GET':
            miembros = ministry.miembros.filter(activo=True)
            filtro_clase = request.query_params.get('clase')
            if filtro_clase:
                miembros = miembros.filter(clase=filtro_clase)
            return Response(MiembroSerializer(miembros, many=True).data)

        serializer = MiembroSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ministry=ministry)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def caja(self, request, slug=None):
        """Ver/crear movimientos de caja"""
        ministry = self.get_object()

        caja, created = CajaMinisterio.objects.get_or_create(ministry=ministry)

        if request.method == 'GET':
            return Response(CajaMinisterioSerializer(caja).data)

        serializer = MovimientoCajaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(caja=caja, registrado_por=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def inventario(self, request, slug=None):
        """Ver/crear items de inventario"""
        ministry = self.get_object()

        if request.method == 'GET':
            inventario = ministry.inventario.all()
            return Response(InventarioSerializer(inventario, many=True).data)

        serializer = InventarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ministry=ministry)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def ofrendas(self, request, slug=None):
        """Ver/crear ofrendas"""
        ministry = self.get_object()

        if request.method == 'GET':
            filtro_fecha_inicio = request.query_params.get('fecha_inicio')
            filtro_fecha_fin = request.query_params.get('fecha_fin')

            ofrendas = ministry.ofrendas.all()
            if filtro_fecha_inicio:
                ofrendas = ofrendas.filter(fecha__gte=filtro_fecha_inicio)
            if filtro_fecha_fin:
                ofrendas = ofrendas.filter(fecha__lte=filtro_fecha_fin)

            return Response(OfrendaSerializer(ofrendas, many=True).data)

        serializer = OfrendaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ministry=ministry)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def asistencia(self, request, slug=None):
        """Ver/registrar asistencia (especialmente DNI)"""
        ministry = self.get_object()

        if request.method == 'GET':
            fecha = request.query_params.get('fecha')
            filtro_clase = request.query_params.get('clase')

            if fecha:
                asistencia = ministry.asistencias.filter(fecha=fecha)
            else:
                asistencia = ministry.asistencias.filter(
                    fecha__gte=date.today() - timedelta(days=7)
                )

            if filtro_clase:
                asistencia = asistencia.filter(clase=filtro_clase)

            return Response(AsistenciaSerializer(asistencia, many=True).data)

        serializer = AsistenciaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ministry=ministry)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='asistencia/resumen')
    def asistencia_resumen(self, request, slug=None):
        """Resumen de asistencia por domingo"""
        ministry = self.get_object()
        
        mes = request.query_params.get('mes')
        anio = request.query_params.get('anio')
        
        queryset = ministry.asistencias.all()
        
        if mes and anio:
            queryset = queryset.filter(fecha__month=int(mes), fecha__year=int(anio))
        else:
            queryset = queryset.filter(fecha__month=date.today().month, fecha__year=date.today().year)
        
        from django.db.models import Count, Sum, Q
        from django.db.models.functions import TruncDate
        
        fechas_unicas = queryset.values('fecha').distinct().order_by('fecha')
        
        resultados = []
        for item in fechas_unicas:
            fecha = item['fecha']
            registros = queryset.filter(fecha=fecha)
            
            total_presentes = registros.filter(presente=True).count()
            total_visitas = registros.filter(es_visita=True).count()
            total_biblias = registros.filter(tiene_biblia=True).count()
            
            ofrendas_dia = ministry.ofrendas.filter(fecha=fecha).aggregate(total=Sum('monto'))['total'] or 0
            
            por_clase = {}
            for clase in ['ninos', 'jovenes', 'adultos_jovenes', 'adultos', 'adultos_mayores']:
                count = registros.filter(clase=clase).count()
                if count > 0:
                    por_clase[clase] = count
            
            resultados.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'total_asistencia': total_presentes,
                'total_visitas': total_visitas,
                'total_biblias': total_biblias,
                'total_ofrendas': float(ofrendas_dia),
                'por_clase': por_clase
            })
        
        return Response(resultados)

    @action(detail=True, methods=['get'], url_path='asistencia/acumulativa')
    def asistencia_acumulativa(self, request, slug=None):
        """Asistencia acumulativa por persona en el mes"""
        from django.db.models import Count
        
        ministry = self.get_object()
        
        mes = request.query_params.get('mes')
        anio = request.query_params.get('anio')
        filtro_clase = request.query_params.get('clase')
        
        if not mes:
            mes = date.today().month
        if not anio:
            anio = date.today().year
        
        queryset = ministry.asistencias.filter(
            fecha__month=int(mes),
            fecha__year=int(anio),
            presente=True
        )
        
        if filtro_clase:
            queryset = queryset.filter(clase=filtro_clase)
        
        miembros_ids = queryset.values_list('miembro', flat=True).distinct()
        
        resultados = []
        for miembro_id in miembros_ids:
            if miembro_id is None:
                continue
            try:
                miembro = Miembro.objects.get(id=miembro_id)
                count = queryset.filter(miembro=miembro_id).count()
                resultados.append({
                    'miembro_id': miembro.id,
                    'nombre_completo': miembro.nombre_completo,
                    'clase': miembro.clase,
                    'asistencias_count': count
                })
            except Miembro.DoesNotExist:
                continue
        
        visitas_query = queryset.filter(es_visita=True)
        visitas_count = visitas_query.values('nombre_visita').distinct().count()
        
        return Response({
            'miembros': sorted(resultados, key=lambda x: x['asistencias_count'], reverse=True),
            'visitas_total': visitas_count,
            'total_asistencias': sum(r['asistencias_count'] for r in resultados)
        })

    @action(detail=True, methods=['get'], url_path='asistencia/estadisticas')
    def asistencia_estadisticas(self, request, slug=None):
        """Estadísticas generales de asistencia por clase"""
        from django.db.models import Count
        
        ministry = self.get_object()
        
        mes = request.query_params.get('mes')
        anio = request.query_params.get('anio')
        
        if not mes:
            mes = date.today().month
        if not anio:
            anio = date.today().year
        
        queryset = ministry.asistencias.filter(
            fecha__month=int(mes),
            fecha__year=int(anio)
        )
        
        miembros = ministry.miembros.filter(activo=True)
        
        clases = ['ninos', 'jovenes', 'adultos_jovenes', 'adultos', 'adultos_mayores']
        estadisticas = {}
        
        for clase in clases:
            clase_query = queryset.filter(clase=clase)
            estadisticas[clase] = {
                'miembros_registrados': miembros.filter(clase=clase).count(),
                'asistencias_totales': clase_query.filter(presente=True).count(),
                'visitas': clase_query.filter(es_visita=True).count(),
                'biblias': clase_query.filter(tiene_biblia=True).count()
            }
        
        return Response(estadisticas)

    @action(detail=True, methods=['get', 'post'])
    def eventos(self, request, slug=None):
        """Ver/crear eventos"""
        ministry = self.get_object()

        if request.method == 'GET':
            eventos = ministry.eventos.all()
            return Response(EventoSerializer(eventos, many=True).data)

        serializer = EventoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ministry=ministry, creado_por=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def planificaciones(self, request, slug=None):
        """Ver/crear planificaciones de actividades"""
        from .serializers import PlanificacionActividadSerializer
        from .models import PlanificacionActividad
        
        ministry = self.get_object()

        if request.method == 'GET':
            planificaciones = ministry.planificaciones.all()
            filtro_estado = request.query_params.get('estado')
            if filtro_estado:
                planificaciones = planificaciones.filter(estado=filtro_estado)
            return Response(PlanificacionActividadSerializer(planificaciones, many=True).data)

        serializer = PlanificacionActividadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ministry=ministry, responsable=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancionViewSet(viewsets.ModelViewSet):
    """CRUD de canciones (Banco de alabanzas)"""
    queryset = Cancion.objects.all()
    serializer_class = CancionSerializer

    def get_queryset(self):
        queryset = Cancion.objects.all()
        categoria = self.request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        return queryset

    @action(detail=False, methods=['post'])
    def generar_programa(self, request):
        """Generar programa dominical automático"""
        fecha_str = request.data.get('fecha')
        ministry_slug = request.data.get('ministerio')

        try:
            fecha = date.fromisoformat(fecha_str)
            ministry = Ministerio.objects.get(slug=ministerio_slug)
        except (ValueError, Ministerio.DoesNotExist):
            return Response(
                {'error': 'Fecha o ministry inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ultimo_programa = ProgramaAlabanza.objects.filter(
            ministry=ministry,
            fecha__lt=fecha
        ).order_by('-fecha').first()

        canciones_usadas = []
        if ultimo_programa:
            canciones_usadas = [a['id'] for a in ultimo_programa.alabanzas]

        programa = []
        categorias = ['rapida', 'rapida', 'media', 'lenta', 'lenta']

        for cat in categorias:
            disponibles = Cancion.objects.filter(
                categoria=cat
            ).exclude(id__in=canciones_usadas)

            if disponibles.exists():
                cancion = disponibles.first()
            else:
                disponibles = Cancion.objects.filter(categoria=cat)
                cancion = disponibles.order_by('?').first() if disponibles.exists() else None

            if cancion:
                programa.append({
                    'id': cancion.id,
                    'titulo': cancion.titulo,
                    'categoria': cancion.categoria,
                    'tono': cancion.tono
                })
                canciones_usadas.append(cancion.id)

        programa_obj = ProgramaAlabanza.objects.create(
            ministry=ministry,
            fecha=fecha,
            alabanzas=programa,
            creado_por=request.user
        )

        return Response(ProgramaAlabanzaSerializer(programa_obj).data)


class ProgramaAlabanzaViewSet(viewsets.ModelViewSet):
    """CRUD de programas de alabanzas"""
    queryset = ProgramaAlabanza.objects.all()
    serializer_class = ProgramaAlabanzaSerializer

    def get_queryset(self):
        queryset = ProgramaAlabanza.objects.all()
        ministry_slug = self.request.query_params.get('ministerio')
        if ministry_slug:
            queryset = queryset.filter(ministry__slug=ministry_slug)
        return queryset


class LeccionEXPLOViewSet(viewsets.ModelViewSet):
    """CRUD de lecciones EXPLO"""
    queryset = LeccionEXPLO.objects.all()
    serializer_class = LeccionEXPLOSerializer


class RecursoComunicacionViewSet(viewsets.ModelViewSet):
    """CRUD de recursos de comunicaciones"""
    queryset = RecursoComunicacion.objects.all()
    serializer_class = RecursoComunicacionSerializer

    def get_queryset(self):
        queryset = RecursoComunicacion.objects.all()
        ministry_slug = self.request.query_params.get('ministerio')
        tipo = self.request.query_params.get('tipo')

        if ministry_slug:
            queryset = queryset.filter(ministry__slug=ministry_slug)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset


class IdeaComunicacionViewSet(viewsets.ModelViewSet):
    """CRUD de ideas de comunicaciones"""
    queryset = IdeaComunicacion.objects.all()
    serializer_class = IdeaComunicacionSerializer

    def get_queryset(self):
        queryset = IdeaComunicacion.objects.all()
        ministry_slug = self.request.query_params.get('ministerio')
        completada = self.request.query_params.get('completada')

        if ministry_slug:
            queryset = queryset.filter(ministry__slug=ministry_slug)
        if completada is not None:
            queryset = queryset.filter(completada=completada.lower() == 'true')
        return queryset


class MiembroViewSet(viewsets.ModelViewSet):
    """CRUD de miembros (global)"""
    queryset = Miembro.objects.all()
    serializer_class = MiembroSerializer

    def get_queryset(self):
        queryset = Miembro.objects.all()
        ministry_slug = self.request.query_params.get('ministerio')
        clase = self.request.query_params.get('clase')
        estado_civil = self.request.query_params.get('estado_civil')
        search = self.request.query_params.get('search')

        if ministry_slug:
            queryset = queryset.filter(ministry__slug=ministry_slug)
        if clase:
            queryset = queryset.filter(clase=clase)
        if estado_civil:
            queryset = queryset.filter(estado_civil=estado_civil)
        if search:
            queryset = queryset.filter(
                Q(primer_nombre__icontains=search) |
                Q(segundo_nombre__icontains=search) |
                Q(primer_apellido__icontains=search) |
                Q(segundo_apellido__icontains=search)
            )

        return queryset

    @action(detail=False, methods=['get'])
    def cumpleanos(self, request):
        """Lista de cumpleaños del mes"""
        today = date.today()
        mes_actual = today.month

        miembros = Miembro.objects.filter(
            activo=True,
            fecha_nacimiento__month=mes_actual
        ).order_by('fecha_nacimiento__day')

        resultado = []
        for m in miembros:
            dias_faltantes = (m.fecha_nacimiento.replace(year=today.year) - today).days
            resultado.append({
                'id': m.id,
                'nombre_completo': m.nombre_completo,
                'fecha_nacimiento': m.fecha_nacimiento,
                'dia': m.fecha_nacimiento.day,
                'dias_faltantes': dias_faltantes if dias_faltantes >= 0 else 365 + dias_faltantes
            })

        return Response(resultado)


class EventoViewSet(viewsets.ModelViewSet):
    """CRUD de eventos (global)"""
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer

    def get_queryset(self):
        queryset = Evento.objects.all()
        ministry_slug = self.request.query_params.get('ministerio')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        tipo = self.request.query_params.get('tipo')

        if ministry_slug:
            queryset = queryset.filter(
                Q(ministry__slug=ministry_slug) |
                Q(ministerios_relacionados__slug=ministry_slug)
            ).distinct()
        if fecha_inicio:
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_inicio__lte=fecha_fin)
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        return queryset


class UsuarioViewSet(viewsets.ViewSet):
    """ViewSet para gestión de usuarios"""

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'roles']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def list(self, request):
        """Listar todos los usuarios"""
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)

        perfiles = PerfilUsuario.objects.select_related('user', 'creado_por').order_by('-fecha_creacion')
        serializer = UsuarioCompletoSerializer(perfiles, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Obtener detalle de un usuario"""
        try:
            perfil = PerfilUsuario.objects.select_related('user').get(pk=pk)
        except PerfilUsuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if not self._puede_acceder(request, perfil):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UsuarioCompletoSerializer(perfil)
        return Response(serializer.data)

    def create(self, request):
        """Crear nuevo usuario"""
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UsuarioCreateSerializer(data=request.data)
        if serializer.is_valid():
            from django.contrib.auth.models import User
            from django.db import transaction

            with transaction.atomic():
                user = User.objects.create_user(
                    username=serializer.validated_data['username'],
                    first_name=serializer.validated_data['first_name'],
                    last_name=serializer.validated_data['last_name'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password']
                )

                perfil_data = {
                    'user': user,
                    'rol': serializer.validated_data['rol'],
                    'telefono': serializer.validated_data.get('telefono', ''),
                    'permisos_especificos': serializer.validated_data.get('permisos_especificos', {}),
                    'activo': serializer.validated_data.get('activo', True),
                    'creado_por': request.user,
                }
                perfil = PerfilUsuario.objects.create(**perfil_data)

                ministerios_ids = serializer.validated_data.get('ministerios_lidera', [])
                if ministerios_ids:
                    ministerios = Ministerio.objects.filter(id__in=ministerios_ids)
                    perfil.ministerios_lidera.set(ministerios)

            return Response(UsuarioCompletoSerializer(perfil).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Actualizar usuario"""
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)

        try:
            perfil = PerfilUsuario.objects.select_related('user').get(pk=pk)
        except PerfilUsuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UsuarioUpdateSerializer(data=request.data, context={'user': perfil})
        if serializer.is_valid():
            user = perfil.user

            if 'first_name' in serializer.validated_data:
                user.first_name = serializer.validated_data['first_name']
            if 'last_name' in serializer.validated_data:
                user.last_name = serializer.validated_data['last_name']
            if 'email' in serializer.validated_data:
                user.email = serializer.validated_data['email']
            user.save()

            if 'rol' in serializer.validated_data:
                perfil.rol = serializer.validated_data['rol']
            if 'telefono' in serializer.validated_data:
                perfil.telefono = serializer.validated_data['telefono']
            if 'activo' in serializer.validated_data:
                perfil.activo = serializer.validated_data['activo']
            if 'permisos_especificos' in serializer.validated_data:
                perfil.permisos_especificos = serializer.validated_data['permisos_especificos']
            if 'ministerios_lidera' in serializer.validated_data:
                ministerios = Ministerio.objects.filter(id__in=serializer.validated_data['ministerios_lidera'])
                perfil.ministerios_lidera.set(ministerios)

            perfil.save()

            if serializer.validated_data.get('password_nueva'):
                user.set_password(serializer.validated_data['password_nueva'])
                user.save()

            return Response(UsuarioCompletoSerializer(perfil).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        """Eliminar usuario (desactivar)"""
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)

        try:
            perfil = PerfilUsuario.objects.get(pk=pk)
        except PerfilUsuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if perfil.user == request.user:
            return Response({'error': 'No puedes eliminarte a ti mismo'}, status=status.HTTP_400_BAD_REQUEST)

        perfil.activo = False
        perfil.save()
        return Response({'success': True, 'message': 'Usuario desactivado'})

    @action(detail=False, methods=['get'])
    def roles(self, request):
        """Listar roles disponibles"""
        return Response(PerfilUsuario.ROLES)

    @action(detail=True, methods=['post'], url_path='cambiar-rol')
    def cambiar_rol(self, request, pk=None):
        """Cambiar rol de usuario"""
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)

        try:
            perfil = PerfilUsuario.objects.get(pk=pk)
        except PerfilUsuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        nuevo_rol = request.data.get('rol')
        if nuevo_rol not in dict(PerfilUsuario.ROLES):
            return Response({'error': 'Rol inválido'}, status=status.HTTP_400_BAD_REQUEST)

        perfil.rol = nuevo_rol
        perfil.save()
        return Response(UsuarioCompletoSerializer(perfil).data)

    @action(detail=True, methods=['post'], url_path='asignar-ministerios')
    def asignar_ministerios(self, request, pk=None):
        """Asignar ministerios que lidera un usuario"""
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)

        try:
            perfil = PerfilUsuario.objects.get(pk=pk)
        except PerfilUsuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        ministerios_ids = request.data.get('ministerios', [])
        ministerios = Ministerio.objects.filter(id__in=ministerios_ids)
        perfil.ministerios_lidera.set(ministerios)
        perfil.save()

        return Response(UsuarioCompletoSerializer(perfil).data)

    @action(detail=False, methods=['get'], url_path='ministerios-disponibles')
    def ministerios_disponibles(self, request):
        """Listar todos los ministerios para asignación"""
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)

        ministerios = Ministerio.objects.filter(activo=True).values('id', 'nombre', 'slug')
        return Response(list(ministerios))

    def _es_admin(self, request):
        perfil = getattr(request.user, 'perfil', None)
        return perfil and perfil.rol == 'admin'

    def _puede_acceder(self, request, perfil):
        if self._es_admin(request):
            return True
        perfil_actual = getattr(request.user, 'perfil', None)
        return perfil_actual and perfil_actual.id == perfil.id


class PermisoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de permisos"""
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def list(self, request):
        if not self._es_admin(request):
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request)

    def _es_admin(self, request):
        perfil = getattr(request.user, 'perfil', None)
        return perfil and perfil.rol == 'admin'