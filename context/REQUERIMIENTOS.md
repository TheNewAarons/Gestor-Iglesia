# Gestor Iglesia - Requerimientos del Proyecto

## Información General
- **Nombre del proyecto**: Gestor Iglesia
- **Tipo**: Sistema de gestión para iglesias
- **Stack tecnológico**: Django REST Framework (backend) + Astro (frontend estático)

## Requerimientos Técnicos

### Backend
- Framework: Django REST Framework con Python
- Base de datos: PostgreSQL (desarrollo con SQLite)
- Autenticación: API REST con sesiones Django mediante tokens
- Modelos: 15 modelos completos con serializers, views, URLs y permisos
- seed command para crear 13 ministerios por defecto

### Frontend
- Framework: Astro (modo estático, sin dependencias externas)
- Conexión: API REST consume datos del backend
- Diseño: Sobrio, blanco/negro con colores de acento solo para botones
- Responsive: Mobile-first con BottomNav
- Navegación: Sidebar (desktop) + BottomNav (mobile)

## Ministerios
13 ministerios por defecto:
1. mni - Ministerio de Nuevos Creyentes
2. dni - Departamento de Niños
3. jni - Juventud
4. mam - Mujeres
5. vid - Varones
6. explo - Expedición de Líderes
7. Danza
8. Teatro
9. Alabanza
10. Comunicaciones
11. Compasión
12. Nazakids
13. Adulto Mayor

## Diseño UI/UX
- Colores: Blanco y negro como base, acentos solo en botones
- Colores por ministerio: Cada ministerio tiene su color y gradiente específico
- Responsive: Soporte para móvil y desktop
- Navegación: Sidebar fijo para desktop, BottomNav fijo para móvil
- Logo: IDN Juan noe_gris.png disponible en /logos

### Vista de Detalle de Ministerio
- Hero banner con gradiente de color según el ministerio
- Icono del ministerio centrado en el hero (32x32px)
- Título y descripción del ministerio en el hero
- 4 stat cards con métricas: Miembros, Caja, Ofrendas, Eventos
- 6 tabs de navegación: Dashboard, Miembros, Caja, Inventario, Ofrendas, Eventos
- Animaciones suaves en transiciones y hover
- Skeleton loading states para mejor UX

## URLs del Proyecto
- Backend: http://localhost:8000
- Frontend: http://localhost:4321

## Estado Actual
- Backend completo con 15 modelos, seed command, serializers, views, URLs
- Frontend con layouts, componentes, páginas, stores, API utility
- Sidebar y BottomNav funcionando con highlight activo dinámico (cliente)
- 17 páginas generadas estáticamente
- Vista de detalle de ministerio completamente diseñada y funcional
- Módulo de usuarios con diseño moderno de panel lateral

## Corrección de Bugs

### Bug: Módulo de Usuarios - JSON en lugar de valores legibles
**Fecha:** 2026-05-09
**Severidad:** Alta

**Síntoma:** En la lista de usuarios, el campo "Usuario" mostraba un string JSON en lugar del nombre real del usuario:
```
USUARIO                                    ROL    MINISTERIOS
{'username': 'aaron.soto', ...}          Admin  Alabanza...
```

**Causa raíz:** El `UsuarioCompletoSerializer` en `backend/apps/ministerios/serializers.py` usaba campos con `source='user.username'` para acceder a campos del modelo `User` relacionado, pero también incluía `username`, `first_name`, `last_name`, `email` en el `Meta.fields`. Esto causaba un conflicto en Django REST Framework donde intentaba acceder a campos que no existen directamente en `PerfilUsuario`.

**Solución:**
1. Cambiar los campos `username`, `first_name`, `last_name`, `email` de `serializers.CharField(source='user.username')` a `SerializerMethodField()` con métodos `get_username()`, `get_first_name()`, etc. que acceden correctamente a `obj.user.username`.
2. Agregar estos campos explícitamente a `Meta.fields` para evitar el error "declared on serializer but not included in fields".

**Archivos modificados:**
- `backend/apps/ministerios/serializers.py` - Refactorizado `UsuarioCompletoSerializer` para usar `SerializerMethodField` en lugar de `source` paths.

**Datos corruptos:** El usuario con `id=6` tenía los campos `User.username`, `User.first_name`, `User.last_name` guardados como strings de representación de dict Python. Esto fue corregido directamente en la base de datos.

### Bug: Creación de usuarios guardaba datos corruptos en User.username
**Fecha:** 2026-05-09
**Severidad:** Alta

**Síntoma:** Al crear un nuevo usuario, el campo `User.username` se guardaba como string JSON:
```
username: "{'username': 'camila.lopes', 'first_name': 'Camila', ...}"
```

**Causa raíz:** En `views.py` método `UsuarioViewSet.create()`, se llamaba incorrectamente:
```python
user = User.objects.create_user(user_data, password=serializer.validated_data['password'])
```
Pasaba un diccionario `user_data` como primer argumento en lugar de kwargs.

**Solución:**
```python
user = User.objects.create_user(
    username=serializer.validated_data['username'],
    first_name=serializer.validated_data['first_name'],
    last_name=serializer.validated_data['last_name'],
    email=serializer.validated_data['email'],
    password=serializer.validated_data['password']
)
```

**Archivos modificados:**
- `backend/apps/ministerios/views.py` - Corregido `UsuarioViewSet.create()` para pasar argumentos correctamente.

## Mejoras de Diseño

### Panel de Detalles de Usuario (Sidebar)
**Fecha:** 2026-05-09

Diseño moderno con:
- Header con gradiente púrpura, avatar circular con iniciales y punto de estado (activo/inactivo)
- Body con secciones organizadas (Contacto, Información) con grid de label-valor
- Chips de ministerios con ícono de inicial
- Footer con botón de editar prominente

### Tabla de Usuarios - Ministerios
**Fecha:** 2026-05-09

Diseño compacto "Tag con tooltip":
- Tags horizontales con nombres completos (max-width: 100px, truncado con ellipsis)
- Límite de 3 tags visibles, resto mostrado como "+X más"
- Tooltip en cada tag y en el contador mostrando todos los ministerios
- Espaciado de 0.5rem entre tags
- Hover con cambio de color de fondo

**Archivos modificados:**
- `frontend/src/pages/usuarios.astro` - Nuevo diseño de panel de detalles y tabla de ministerios

## Próximos Pasos
1. ~~Terminar funcionalidad de detalle para cada ministerio~~ ✅
2. Completar vistas de Finanzas, Secretaría, Calendario, Usuarios
3. Integración completa de datos entre backend y frontend