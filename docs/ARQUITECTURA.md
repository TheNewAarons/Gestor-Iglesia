# 📐 Documento de Arquitectura - Gestor Iglesia

---

## 1. Visión General del Sistema

**Gestor-Iglesia** es una aplicación web full-stack para gestión integral de iglesiasEvangélicas Nazaret. Centraliza la administración de 13 ministerios, finanzas centralizadas, calendario compartido y control de asistencia.

### Metas del Sistema
- Unificar la gestión de todos los ministerios en una sola plataforma
- Centralizar finanzas con traspasos automáticos a tesorería
- Automatizar informes mensuales consolidados
- Gestionar asistencia y miembros por ministerio
- Mantener transparencia financiera con imágenes de boletas

---

## 2. Stack Tecnológico

| Capa | Tecnología | Propósito |
|------|------------|-----------|
| **Backend** | Django REST Framework | API REST + lógica de negocio |
| **Frontend** | Astro 4.0 + Islands | HTML estático + componentes interactivos |
| **Base de Datos** | PostgreSQL (SQLite dev) | Persistencia relacional |
| **Auth** | SimpleJWT + Cookies HttpOnly | Autenticación sin tokens en localStorage |
| **API Docs** | drf-spectacular | OpenAPI/Swagger auto-generado |
| **CSS** | Tailwind CSS 3.4 | Estilos utility-first |
| **Python** | 3.14+ | Runtime |

---

## 3. Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Astro)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Islands    │  │   Stores     │  │   Layouts + Pages    │ │
│  │  (Reactivos)│  │  (Estado)    │  │    (Estáticos)       │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────────┘ │
└─────────┼─────────────────┼────────────────────────────────────┘
          │    HTTP/JWT     │
          │    (cookies)   │
┌─────────┴─────────────────┴────────────────────────────────────┐
│                         BACKEND (Django)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Layer (ViewSets)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│           │                    │                    │           │
│  ┌────────┴────────┐ ┌────────┴────────┐ ┌────────┴────────┐  │
│  │   Selectors     │ │   Services      │ │  Permissions    │  │
│  │  (Consultas)   │ │ (Lógica)        │ │  (Auth/RBAC)    │  │
│  └────────┬────────┘ └────────┬────────┘ └────────────────┘  │
│           │                    │                               │
│  ┌────────┴───────────────────┴────────────────────────────┐  │
│  │                    Models (27 entidades)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────┐
│   PostgreSQL     │
│   / SQLite       │
└──────────────────┘
```

---

## 4. Modelo de Datos (ERD Simplificado)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           APP: ministerios                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    ┌──────────┐     M    ┌──────────────┐     1    ┌──────────────────┐ │
│    │   User   │─────────<│   Miembro    │──────────│   Ministerio     │ │
│    └──────────┘          └──────────────┘          └────────┬─────────┘ │
│         │                                                  │           │
│         │                M                    M           │           │
│         │                 │                  │            │           │
│         ▼    ┌────────────┼────────┐  ┌──────┴───────┐    │           │
│    ┌────────────┐   ┌─────────────────────┐    ┌──────────────┐   ┌─────┴─────┐
│    │ Asistencia │   │  MovimientoCaja     │    │    Evento    │   │   Caja    │
│    │ (DNI)     │   │  (Ingresos/Egresos)│    │  (Calendario)│   │ Ministerio│
│    └────────────┘   └─────────────────────┘    └──────────────┘   └───────────┘
│                                                    │
│         ┌──────────────────┐                       │
│         │   Planificacion  │◄───── M2M ─────► Ministerios
│         │   Actividad      │
│         └──────────────────┘
│
│    ┌───────────┐  ┌────────────┐  ┌──────────────┐  ┌──────────────┐
│    │ Ofrenda   │  │ Inventario│  │   Cancion    │  │    Nota      │
│    │ (MNI/JNI) │  │           │  │ (Alabanza)   │  │              │
│    └───────────┘  └────────────┘  └──────────────┘  └──────────────┘
│
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                            APP: tesoreria                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    ┌──────────────────────┐     M    ┌─────────────────────────────┐   │
│    │  ConfiguracionFinanza │─────────<│    MovimientoTesoreria      │   │
│    │  (Singleton)          │          │                            │   │
│    └──────────────────────┘          └─────────────────────────────┘   │
│                                                     ▲                  │
│    ┌──────────────────────┐                         │                  │
│    │    InformeMensual     │                         │                  │
│    │    (JSON datos)       │                         │                  │
│    └──────────────────────┘                          │                  │
│                                                     │                  │
│    ┌──────────────────────┐          ┌──────────────┴──────────────┐   │
│    │    HistorialLog      │          │  Ofrenda.enviada_tesoreria  │───┘
│    │    (Auditoría)       │          │  → crea MovimientoTesoreria │
│    └──────────────────────┘          └─────────────────────────────┘
│
│    ┌──────────────────────┐
│    │      CuotaFija       │
│    │  (COECE/Cuota Dist)  │
│    └──────────────────────┘
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Modelo de Datos Detallado

### 5.1 App: `ministerios`

#### User (Usuario)
```
┌─────────────────────────────────────────────────────────────────┐
│ User                                                            │
├─────────────────────────────────────────────────────────────────┤
│ Campo                    │ Tipo          │ Notas                │
├──────────────────────────┼───────────────┼─────────────────────┤
│ id                       │ BigAutoField  │ PK                   │
│ username                 │ CharField     │ Unique               │
│ first_name               │ CharField     │                      │
│ last_name                │ CharField     │                      │
│ email                    │ EmailField    │                      │
│ rol                      │ CharField     │ choices: 6 roles     │
│ ministerios_lidera       │ ManyToMany    │ → Ministerio         │
│ permisos_especificos     │ JSONField     │ Permisos granulares  │
│ telefono                 │ CharField     │ Opcional             │
│ foto                     │ ImageField    │ Opcional             │
│ activo                   │ BooleanField  │ Default: True        │
│ created_at               │ DateTimeField │ Auto                 │
│ updated_at               │ DateTimeField │ Auto                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Ministerio
```
┌─────────────────────────────────────────────────────────────────┐
│ Ministerio                                                      │
├─────────────────────────────────────────────────────────────────┤
│ Campo        │ Tipo          │ Notas                           │
├──────────────┼───────────────┼─────────────────────────────────┤
│ slug         │ SlugField     │ PK, unique                     │
│ nombre       │ CharField     │                                │
│ descripcion  │ TextField     │ Opcional                       │
│ color        │ CharField     │ Hex color                      │
│ icono        │ CharField     │ Nombre del icono               │
│ logo         │ ImageField    │ Opcional                       │
│ activo       │ BooleanField  │ Default: True                  │
│ created_at   │ DateTimeField│                                │
│ updated_at   │ DateTimeField│                                │
└─────────────────────────────────────────────────────────────────┘
Relaciones:
- User (lidera) ←→ Ministerio (M2M)
- Miembro (1→M)
- CajaMinisterio (1→1)
- MovimientoCaja, Ofrenda, Asistencia, Evento, Inventario (1→M)
```

#### Miembro
```
┌─────────────────────────────────────────────────────────────────┐
│ Miembro                                                         │
├─────────────────────────────────────────────────────────────────┤
│ Campo                │ Tipo          │ Notas                    │
├──────────────────────┼───────────────┼─────────────────────────┤
│ id                   │ BigAutoField  │ PK                       │
│ ministry             │ ForeignKey    │ → Ministerio            │
│ primer_nombre        │ CharField     │                         │
│ segundo_nombre       │ CharField     │ Opcional                │
│ primer_apellido      │ CharField     │                         │
│ segundo_apellido     │ CharField     │ Opcional                │
│ fecha_nacimiento     │ DateField     │                         │
│ edad                 │ IntegerField  │ Calculada (property)    │
│ estado_civil         │ CharField     │ choices                 │
│ telefono             │ CharField     │ Opcional                │
│ email                │ EmailField    │ Opcional                │
│ direccion            │ TextField     │ Opcional                │
│ clase                │ CharField     │ Solo DNI                │
│ rol_en_ministerio    │ CharField     │ choices                 │
│ observaciones        │ TextField     │ Opcional                │
│ origen               │ CharField     │ Como llegó              │
│ activo               │ BooleanField  │ Default: True           │
│ created_at           │ DateTimeField │                         │
│ updated_at           │ DateTimeField │                         │
└─────────────────────────────────────────────────────────────────┘
```

#### CajaMinisterio y MovimientoCaja
```
┌───────────────────────────┐  ┌─────────────────────────────────────┐
│ CajaMinisterio            │  │ MovimientoCaja                     │
├───────────────────────────┤  ├─────────────────────────────────────┤
│ Campo       │ Tipo        │  │ Campo            │ Tipo             │
├─────────────┼─────────────┤  ├──────────────────┼──────────────────┤
│ id          │ BigAutoField│  │ id               │ BigAutoField     │
│ ministry    │ OneToOne    │  │ caja             │ ForeignKey       │
│ saldo_actual│ Decimal     │  │ tipo             │ CharField        │
│ updated_at  │ DateTimeField│ │ monto            │ Decimal          │
└─────────────┴─────────────┘  │ descripcion       │ TextField        │
                               │ fecha             │ DateTimeField    │
                               │ imagen            │ ImageField       │
                               │ registrado_por    │ ForeignKey →User │
                               │ enviado_tesoreria│ BooleanField     │
                               │ aprobado          │ BooleanField     │
                               │ ofrenda_origen    │ ForeignKey       │
                               │                   │ (→Ofrenda, null) │
                               └─────────────────────────────────────┘
```

#### Asistencia
```
┌─────────────────────────────────────────────────────────────────┐
│ Asistencia                                                       │
├─────────────────────────────────────────────────────────────────┤
│ Campo            │ Tipo          │ Notas                        │
├──────────────────┼───────────────┼─────────────────────────────┤
│ id               │ BigAutoField  │ PK                           │
│ ministry         │ ForeignKey    │ → Ministerio                │
│ fecha            │ DateField    │                              │
│ miembro          │ ForeignKey    │ → Miembro (nullable)        │
│ presente         │ BooleanField  │                              │
│ es_visita        │ BooleanField  │                              │
│ nombre_visita    │ CharField     │ Si es_visita=True           │
│ clase            │ CharField     │                              │
│ tiene_biblia      │ BooleanField  │                              │
│ observaciones    │ TextField     │ Opcional                    │
└─────────────────────────────────────────────────────────────────┘
```

#### Ofrenda
```
┌─────────────────────────────────────────────────────────────────┐
│ Ofrenda                                                          │
├─────────────────────────────────────────────────────────────────┤
│ Campo                  │ Tipo          │ Notas                  │
├────────────────────────┼───────────────┼───────────────────────┤
│ id                     │ BigAutoField  │ PK                     │
│ ministry               │ ForeignKey    │ → Ministerio          │
│ fecha                  │ DateField    │                        │
│ monto                  │ Decimal      │                        │
│ categoria              │ CharField    │ Choices (MNI: 7 opts) │
│ clase                  │ CharField    │ Solo DNI              │
│ movimiento_tesoreria   │ OneToOne     │ → MovimientoTesoreria │
│ enviada_tesoreria       │ BooleanField │ Default: False        │
│ fecha_envio            │ DateTimeField│ Nullable               │
│ aprobado               │ BooleanField │ Default: False        │
│ observaciones          │ TextField    │ Opcional               │
└─────────────────────────────────────────────────────────────────┘
```

#### Evento
```
┌─────────────────────────────────────────────────────────────────┐
│ Evento                                                           │
├─────────────────────────────────────────────────────────────────┤
│ Campo                  │ Tipo          │ Notas                  │
├────────────────────────┼───────────────┼───────────────────────┤
│ id                     │ BigAutoField  │ PK                     │
│ ministry               │ ForeignKey    │ → Ministerio          │
│ titulo                 │ CharField     │                        │
│ descripcion            │ TextField     │ Opcional               │
│ fecha_inicio           │ DateTimeField │                        │
│ hora_inicio            │ TimeField     │ Opcional               │
│ fecha_fin              │ DateTimeField │ Opcional               │
│ hora_fin               │ TimeField     │ Opcional               │
│ ubicacion              │ CharField     │                        │
│ tipo                   │ CharField     │ 'propio' o 'compartido'│
│ ministerios_relacionados│ ManyToMany  │ → Ministerio           │
│ creado_por              │ ForeignKey    │ → User                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Cancion (Alabanza)
```
┌─────────────────────────────────────────────────────────────────┐
│ Cancion                                                          │
├─────────────────────────────────────────────────────────────────┤
│ Campo      │ Tipo          │ Notas                              │
├────────────┼───────────────┼────────────────────────────────────┤
│ titulo     │ CharField     │                                    │
│ artista    │ CharField     │ Opcional                           │
│ categoria  │ CharField     │ rapida, media, lenta               │
│ tono       │ CharField     │ Opcional                           │
│ letra      │ TextField     │ Opcional                           │
│ acordes    │ TextField     │ Opcional                           │
│ link_youtube│ URLField     │ Opcional                           │
└─────────────────────────────────────────────────────────────────┘
```

#### PlanificacionActividad
```
┌─────────────────────────────────────────────────────────────────┐
│ PlanificacionActividad                                          │
├─────────────────────────────────────────────────────────────────┤
│ Campo                 │ Tipo          │ Notas                   │
├───────────────────────┼───────────────┼─────────────────────────┤
│ id                    │ BigAutoField  │ PK                      │
│ ministry              │ ForeignKey    │ → Ministerio            │
│ titulo                │ CharField     │                        │
│ descripcion           │ TextField     │ Opcional               │
│ fecha_planificada     │ DateField    │                        │
│ hora                  │ TimeField     │ Opcional               │
│ ubicacion             │ CharField     │ Opcional               │
│ tipo                  │ CharField     │                        │
│ ministerios_relacionados│ ManyToMany │ → Ministerio           │
│ responsable           │ CharField     │                        │
│ presupuesto           │ Decimal      │ Opcional               │
│ estado                │ CharField    │ Planificada/Proceso/etc │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 App: `tesoreria`

```
┌──────────────────────────────┐  ┌──────────────────────────────┐
│ ConfiguracionFinanzas       │  │ MovimientoTesoreria           │
├──────────────────────────────┤  ├──────────────────────────────┤
│ Campo         │ Tipo        │  │ Campo       │ Tipo           │
├───────────────┼─────────────┤  ├─────────────┼────────────────┤
│ id            │ BigAutoField│  │ id          │ BigAutoField   │
│ nombre_iglesia │ CharField   │  │ tipo        │ CharField      │
│ nombre_distrito│ CharField  │  │ ministry    │ FK (nullable)  │
│ ciudad        │ CharField   │  │ monto       │ Decimal        │
│ pres_distrital_pct│ Decimal │  │ descripcion │ TextField     │
│ pres_educacional_pct│Decimal│  │ fecha       │ DateTimeField │
│ pres_evangelismo_pct│Decimal│  │ imagen      │ ImageField    │
│ jubilacion_monto│ Decimal  │  │ registrado_por│ FK → User    │
│ actualizado_por│ FK → User  │  └─────────────┴────────────────┘
└───────────────┴─────────────┘

┌──────────────────────────────┐  ┌──────────────────────────────┐
│ InformeMensual              │  │ CuotaFija                    │
├──────────────────────────────┤  ├──────────────────────────────┤
│ Campo         │ Tipo        │  │ Campo       │ Tipo           │
├───────────────┼─────────────┤  ├─────────────┼────────────────┤
│ id            │ BigAutoField│  │ id          │ BigAutoField   │
│ anio          │ IntegerField│  │ ministry    │ FK → Ministerio│
│ mes           │ IntegerField│  │ tipo        │ CharField      │
│ datos         │ JSONField   │  │ monto       │ Decimal        │
│ generado_por  │ FK → User   │  └─────────────┴────────────────┘
│ fecha_generacion│ DateTime │  ┌──────────────────────────────┐
└───────────────┴─────────────┘  │ HistorialLog                 │
                                 ├──────────────────────────────┤
                                 │ Campo         │ Tipo          │
                                 ├───────────────┼───────────────┤
                                 │ entidad_tipo  │ CharField     │
                                 │ entidad_id    │ IntegerField  │
                                 │ accion        │ CharField     │
                                 │ resumen       │ TextField     │
                                 │ ministry      │ FK (nullable) │
                                 │ usuario       │ FK → User     │
                                 │ fecha         │ DateTimeField │
                                 └───────────────┴───────────────┘
```

---

## 6. API REST - Endpoints

### 6.1 Autenticación
```
POST   /api/v1/auth/login/       → { access, refresh } (cookies HttpOnly)
POST   /api/v1/auth/logout/      → Blacklist refresh token
POST   /api/v1/auth/refresh/    → { access } (nueva cookie)
GET    /api/v1/auth/me/         → { user data }
```

### 6.2 Ministerios (Router: `/ministerios/`)
```
GET/POST           /ministerios/                          → Lista/Crea ministerios
GET/PUT/PATCH/DELETE /ministerios/{slug}/                 → CRUD

# Sub-routers por slug:
GET/POST           /ministerios/{slug}/miembros/           → Miembros
GET/PUT/PATCH/DELETE /ministerios/{slug}/miembros/{id}/   → CRUD miembro

GET/POST           /ministerios/{slug}/caja/               → Caja + movimientos
GET/POST           /ministerios/{slug}/inventario/          → Inventario
GET/POST           /ministerios/{slug}/ofrendas/           → Ofrendas
GET/POST           /ministerios/{slug}/asistencia/         → Asistencia
GET                /ministerios/{slug}/asistencia/resumen/→ Resumen semanal
GET                /ministerios/{slug}/asistencia/acumulativa/ → Acumulada por persona
GET/POST           /ministerios/{slug}/eventos/            → Eventos
GET/POST           /ministerios/{slug}/planificaciones/    → Planificaciones
GET/POST           /ministerios/{slug}/notas/              → Notas
GET                /ministerios/{slug}/dashboard/           → Dashboard completo
GET                /ministerios/{slug}/enfoques/           → Enfoques MNI
GET/POST           /ministerios/{slug}/programas-domingo/  → Programas último domingo
```

### 6.3 Recursos Globales
```
GET/POST   /miembros/                      → Todos los miembros
GET        /miembros/cumpleanos/            → Cumpleaños del mes

GET/POST   /canciones/                     → Banco de canciones
POST       /canciones/generar_programa/    → Generar programa auto

GET/POST   /programas/                     → Programas alabanza
GET/POST   /lecciones/                     → Lecciones EXPLO
GET/POST   /recursos/                      → Recursos comunicación
GET/POST   /ideas/                         → Ideas comunicación

GET        /eventos/                        → Todos los eventos
GET        /eventos/calendario/?year=&month=→ Calendario mensual
```

### 6.4 Tesorería (Router: `/tesoreria/`)
```
GET         /tesoreria/dashboard/            → Dashboard tesorería
GET         /tesoreria/flujo-caja/          → Flujo mensual
GET         /tesoreria/boletas/             → Lista boletas (paginada)
GET         /tesoreria/boleta-detalle/{id}/ → Detalle boleta
GET/POST    /tesoreria/traspasos/           → Traspasos
GET         /tesoreria/informe/             → Generar informe mensual
GET         /tesoreria/exportar-pdf/         → PDF del informe
GET         /tesoreria/exportar-excel/        → Excel del informe
GET/PUT     /tesoreria/configuracion/        → Config. finanzas
GET         /tesoreria/informes/            → Informes históricos
GET         /tesoreria/historial/           → Historial unificado
GET         /tesoreria/pendientes/          → Pendientes aprobación
POST        /tesoreria/pendientes/aprobar/  → Aprobar pendiente
GET/POST    /tesoreria/movimientos/         → Movimientos directos
GET/PUT     /tesoreria/cuotas/              → Cuotas fijas
```

### 6.5 Usuarios (Router: `/usuarios/`)
```
GET/POST       /usuarios/                    → Lista/Crea usuarios
GET/PUT/PATCH/DELETE /usuarios/{id}/        → CRUD
GET            /usuarios/roles/              → Lista roles
POST           /usuarios/{id}/cambiar-rol/   → Cambiar rol
POST           /usuarios/{id}/asignar-ministerios/ → Asignar ministerios
```

---

## 7. Autenticación y Autorización

### 7.1 Flujo de Autenticación JWT
```
┌─────────┐                              ┌──────────────┐
│  Client │                              │   Backend    │
└────┬────┘                              └──────┬───────┘
     │                                          │
     │  1. POST /api/v1/auth/login/
     │     { username, password }
     │ ───────────────────────────────────────► │
     │                                          │
     │  2. Validate credentials
     │     Generate access + refresh tokens
     │                                          │
     │  3. Set-Cookie: access_token (HttpOnly)
     │     Set-Cookie: refresh_token (HttpOnly)
     │ ◄─────────────────────────────────────── │
     │                                          │
     │  4. GET /api/v1/auth/me/
     │     Cookie: access_token
     │ ───────────────────────────────────────► │
     │                                          │
     │  5. JWTCookieAuthentication
     │     Returns user data
     │ ◄─────────────────────────────────────── │
```

### 7.2 Roles y Permisos
```
┌──────────────┬────────────────────────────────────────────────┐
│ Rol           │ Permisos                                      │
├──────────────┼────────────────────────────────────────────────┤
│ admin         │ Todos                                         │
│ pastora        │ Todos los módulos                             │
│ secretaria     │ Miembros(CRUD), Asistencia(ver/registrar),   │
│               │ Eventos(ver/crear/editar)                      │
│ tesorera       │ Caja(ver/crear/editar/aprobar),              │
│               │ Ofrendas(ver/crear/editar), Reportes           │
│ lider_ministerio│ Solo su ministerio                           │
│ concilio       │ Solo lectura                                 │
└──────────────┴────────────────────────────────────────────────┘
```

---

## 8. Arquitectura Frontend (Astro Islands)

### 8.1 Estructura de Islands
```
┌────────────────────────────────────────────────────────────┐
│                    DashboardLayout.astro                    │
│  ┌──────────────────┐          ┌───────────────────────┐ │
│  │    Sidebar       │          │   Content Area        │ │
│  │  (Static HTML)   │          │                       │ │
│  │                  │          │  ┌─────────────────┐   │ │
│  │  - Logo          │          │  │   Island        │   │ │
│  │  - Nav Links     │          │  │  (Hydrated)     │   │ │
│  │                  │          │  │                 │   │ │
│  │                  │          │  │  DashboardHome  │   │ │
│  │                  │          │  │  MinistryPage    │   │ │
│  │                  │          │  │  TreasuryPage     │   │ │
│  │                  │          │  │  Calendario       │   │ │
│  │                  │          │  │                 │   │ │
│  └──────────────────┘          │  └─────────────────┘   │ │
│                                └───────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                  BottomNav (Mobile)                  │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### 8.2 Stores (Estado Global)
```
┌─────────────────────────────────────────────────────────┐
│                     AuthStore                            │
├─────────────────────────────────────────────────────────┤
│ State: { user, isAuthenticated, isLoading, error }       │
├─────────────────────────────────────────────────────────┤
│ Methods:                                                │
│   checkAuth() → Valida token con /auth/me/              │
│   login(username, password) → POST /auth/login/           │
│   logout() → POST /auth/logout/                         │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                  MinisteriosStore                        │
├─────────────────────────────────────────────────────────┤
│ State: { ministerios[], currentMinistry, ... }          │
├─────────────────────────────────────────────────────────┤
│ Methods (40+):                                          │
│   fetchMinisterios()                                    │
│   fetchDashboard(slug)                                  │
│   fetchMiembros(slug)                                   │
│   addMiembro(slug, data)                                │
│   fetchCaja(slug)                                       │
│   addMovimiento(slug, data)                             │
│   fetchAsistencia(slug, filters)                        │
│   ...                                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 9. Flujos de Datos Principales

### 9.1 Flujo: Registrar Asistencia (DNI)
```
Usuario ──► Island:MinistryPage
                │
                ▼
         MinisteriosStore
         .fetchAsistencia(slug, { fecha })
                │
                ▼
         API GET /ministerios/dni/asistencia/?fecha=...
                │
                ▼
         Render tabla con checkboxes
                │
                ▼
         Usuario marca presentes/ausentes
                │
                ▼
         MinisteriosStore.addAsistencia(slug, data)
                │
                ▼
         API POST /ministerios/dni/asistencia/
                │
                ▼
         Toast: "Asistencia guardada"
```

### 9.2 Flujo: Enviar Ofrenda a Tesorería
```
Usuario (Tesorero Ministerio)
    │
    ▼
MinisteriosStore.fetchOfrendas(slug)
    │
    ▼
Selecciona ofrenda → Click "Enviar a Tesorería"
    │
    ▼
MinisteriosStore.enviarOfrendaATesoreria(ofrendaId)
    │
    ▼
API: POST /ministerios/{slug}/ofrendas/{id}/enviar/
    │
    ├─► Crea MovimientoTesoreria
    ├─► Marca ofrenda como enviada
    └─► Registra en HistorialLog
    │
    ▼
Tesorera ve ofrenda en /tesoreria/pendientes/
    │
    ▼
Tesorera aprueba → /tesoreria/pendientes/aprobar/
    │
    ▼
Ofrenda aparece en flujo de caja mensual
```

### 9.3 Flujo: Generar Informe Mensual
```
Tesorera → /tesoreria/informe/?año=2026&mes=5
    │
    ▼
TesoreriaService.generar_informe(año, mes)
    │
    ├─► Selectors: obtener_saldos_ministerios()
    ├─► Selectors: obtener_ingresos_mes()
    ├─► Selectors: obtener_egresos_mes()
    ├─► Selectors: calcular_pres_porcentajes()
    └─► Selectors: calcular_totales_por_ministerio()
    │
    ▼
Genera estructura JSON con:
{
  ingresos: { saldo_mes_pasado, iglesia_local, ... },
  egresos: { iglesia_local, otros_ministerios, ... },
  totales: { saldo_mes_pasado, total_ingresos, ... }
}
    │
    ▼
InformeMensual.objects.create(datos=json)
    │
    ▼
API returns InformeMensualSerializer
    │
    ▼
TreasuryPage renderiza el informe
```

---

## 10. Patrones Arquitectónicos

### 10.1 Selectors (Consultas)
```python
# apps/ministerios/selectors/asistencia.py
def listar_asistencia(ministry, filters):
    queryset = Asistencia.objects.filter(ministry=ministry)

    if fecha := filters.get('fecha'):
        queryset = queryset.filter(fecha=fecha)
    if clase := filters.get('clase'):
        queryset = queryset.filter(clase=clase)
    if presente := filters.get('presente'):
        queryset = queryset.filter(presente=presente)

    return queryset.select_related('miembro').order_by('-fecha', 'miembro__primer_nombre')
```

### 10.2 Services (Lógica de Negocio)
```python
# apps/ministerios/services/finanzas.py
def enviar_ofrenda_a_tesoreria(ofrenda, usuario):
    movimiento = MovimientoTesoreria.objects.create(
        tipo='ingreso_ofrenda',
        ministry=ofrenda.ministry,
        monto=ofrenda.monto,
        descripcion=f"Ofrenda {ofrenda.fecha} - {ofrenda.get_categoria_display()}",
        fecha=timezone.now(),
        registrado_por=usuario,
        imagen=ofrenda.imagen,
    )

    ofrenda.movimiento_tesoreria = movimiento
    ofrenda.envidada_tesoreria = True
    ofrenda.fecha_envio = timezone.now()
    ofrenda.save()

    HistorialLog.objects.create(
        entidad_tipo='Ofrenda',
        entidad_id=ofrenda.id,
        accion='envio_tesoreria',
        resumen=f"Ofrenda enviada a tesorería: {ofrenda.monto}",
        ministry=ofrenda.ministry,
        usuario=usuario,
    )

    return ofrenda
```

### 10.3 Views (Thin Controllers)
```python
class AsistenciaViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return asistencia_selectors.listar_asistencia(
            ministry=self.ministry,
            filters=self.request.query_params
        )

    @action(detail=False, methods=['get'])
    def resumen(self, request, slug=None):
        data = asistencia_services.obtener_resumen(self.ministry)
        return Response(data)
```

---

## 11. Middleware y Configuraciones

### CORS
```
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SAMESITE = 'Lax'
Access-Control-Allow-Credentials: true
```

### JWT
```
ACCESS_TOKEN_LIFETIME: 15 minutos
REFRESH_TOKEN_LIFETIME: 7 días
ROTATE_REFRESH_TOKENS: True
BLACKLIST_AFTER_ROTATION: True
```

### API Pagination
```
PageNumberPagination
page_size: 20
```

---

## 12. Resumen de Modelos (27 total)

| # | Modelo | App | Descripción |
|---|--------|-----|-------------|
| 1 | User | ministerios | Usuario personalizado |
| 2 | Rol | ministerios | Rol del sistema |
| 3 | Permiso | ministerios | Permiso granular |
| 4 | Ministerio | ministerios | Ministerio de la iglesia |
| 5 | Miembro | ministerios | Miembro de ministerio |
| 6 | CajaMinisterio | ministerios | Caja financiera |
| 7 | MovimientoCaja | ministerios | Ingreso/egreso |
| 8 | Inventario | ministerios | Bienes del ministerio |
| 9 | Ofrenda | ministerios | Ofrenda registrada |
| 10 | Asistencia | ministerios | Registro de asistencia |
| 11 | Evento | ministerios | Evento en calendario |
| 12 | Cancion | ministerios | Canción de alabanza |
| 13 | ProgramaAlabanza | ministerios | Programa dominical |
| 14 | LeccionEXPLO | ministerios | Lección de EXPLO |
| 15 | RecursoComunicacion | ministerios | Recurso gráfico |
| 16 | IdeaComunicacion | ministerios | Idea de contenido |
| 17 | PlanificacionActividad | ministerios | Actividad planificada |
| 18 | EnfoqueMNI | ministerios | Enfoque mensual bíblico |
| 19 | ProgramaUltimoDomingo | ministerios | Programa especial MNI |
| 20 | Nota | ministerios | Nota del ministerio |
| 21 | ConfiguracionFinanzas | tesoreria | Config singleton |
| 22 | InformeMensual | tesoreria | Informe mensual |
| 23 | MovimientoTesoreria | tesoreria | Movimiento directo |
| 24 | HistorialLog | tesoreria | Log de auditoría |
| 25 | CuotaFija | tesoreria | Cuota fija mensual |

---

## 13. Lista Completa de Ministerios

| Slug | Nombre | Color |
|------|--------|-------|
| mni | Ministerio de Nuevos Creyentes | #10B981 |
| dni | Departamento de Niños | #3B82F6 |
| jni | Juventud Nazarena Internacional | #8B5CF6 |
| mam | Ministerio de Mujeres | #EC4899 |
| vid | Ministerio de Varones | #F59E0B |
| explo | Exploradores del Rey | #EF4444 |
| danza | Ministerio de Danza | #14B8A6 |
| teatro | Ministerio de Teatro | #6366F1 |
| alabanza | Ministerio de Alabanza | #F97316 |
| comunicaciones | Ministerio de Comunicaciones | #06B6D4 |
| compasion | Ministerio de Compasión | #84CC16 |
| nazakids | Ministerio de Niños NazaKids | #FBBF24 |
| adulto-mayor | Ministerio de Adulto Mayor | #78716C |

---

## 14. Funcionalidades Específicas por Ministerio

### MNI (Ministerio de Nuevos Creyentes)
- Enfoques mensuales bíblicos (12 enfoques predefinidos)
- Categorías especiales de ofrenda: Caja de Alabastro, DIP, FEM, Acción de Gracias
- Programa del último domingo del mes

### DNI (Departamento de Niños)
- Registro de asistencia por clase (bebes, niños, jóvenes, adultos jóvenes, adultos, adultos mayores)
- Resumen semanal y mensual de asistencia
- Estadísticas de asistencia
- Control de biblias (`tiene_biblia` en asistencia)
- Sistema de cumpleaños
- Visitas con registro específico

### JNI (Juventud Nazarena Internacional)
- Ofrendas semanales y mensuales con seguimiento por período

### Alabanza
- Banco de canciones con categorías (rápida, media, lenta)
- Generación automática de programa dominical (5 alabanzas: 2 rápidas, 1 media, 2 lentas)

### Comunicaciones
- Checklist de ideas con prioridades
- Recursos gráficos (fotos, videos, plantillas, logos)
- Gestión de misión y visión

### EXPLO (Exploradores del Rey)
- Gestión de lecciones con materiales adjuntos
