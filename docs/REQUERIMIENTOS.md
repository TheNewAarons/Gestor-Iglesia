# Gestor Iglesia - Requerimientos Funcionales

## 1. Información General

- **Nombre del proyecto**: Gestor Iglesia
- **Tipo**: Sistema de gestión para iglesias
- **Stack tecnológico**: Django REST Framework (backend) + Astro (frontend estático)
- **Base de datos**: PostgreSQL (desarrollo con SQLite)
- **Autenticación**: JWT con cookies HttpOnly

---

## 2. Módulos del Sistema

| Módulo | Descripción | Prioridad |
|--------|-------------|-----------|
| Ministerios | Gestión de los 13 ministerios de la iglesia | Alta |
| Finanzas | Tesorería central, flujo de caja, informes | Alta |
| Calendario | Eventos compartidos entre ministerios | Alta |
| Usuarios | Gestión de usuarios y permisos | Alta |

> **Nota**: El módulo de Secretaría queda pendiente para una fase posterior.

---

## 3. Módulo de Ministerios

### 3.1 Lista de Ministerios

13 ministerios por defecto:

| Slug | Nombre | Color | Icono |
|------|--------|-------|-------|
| `mni` | Ministerio de Nuevos Creyentes | #10B981 | user-plus |
| `dni` | Departamento de Niños | #3B82F6 | book-open |
| `jni` | Juventud Nazarena Internacional | #8B5CF6 | users |
| `mam` | Ministerio de Mujeres | #EC4899 | heart |
| `vid` | Ministerio de Varones | #F59E0B | home |
| `explo` | Exploradores del Rey | #EF4444 | graduation-cap |
| `danza` | Ministerio de Danza | #14B8A6 | music |
| `teatro` | Ministerio de Teatro | #6366F1 | theater-masks |
| `alabanza` | Ministerio de Alabanza | #F97316 | microphone |
| `comunicaciones` | Ministerio de Comunicaciones | #06B6D4 | broadcast |
| `compasion` | Ministerio de Compasión | #84CC16 | hand-holding-heart |
| `nazakids` | Ministerio de Niños | #FBBF24 | child |
| `adulto-mayor` | Ministerio de Adulto Mayor | #78716C | users |

### 3.2 Clasificación de Ministerios

#### Ministerios Principales (3)
- **MNI** - Ministerio de Nuevos Creyentes
- **DNI** - Departamento de Niños
- **JNI** - Juventud Nazarena Internacional

Estos tres ministerios tienen funcionalidades adicionales específicas que los demás no poseen.

#### Ministerios Secundarios (10)
- MAM, VID, EXPLO, Danza, Teatro, Alabanza, Comunicaciones, Compasión, NazaKids, Adulto Mayor

### 3.3 Funcionalidades Comunes a Todos los Ministerios

Todas las funcionalidades de esta sección aplican a TODOS los ministerios (principales y secundarios).

#### 3.3.1 Caja Propia del Ministerio

**Descripción**: Cada ministerio gestiona su propia caja de forma independiente.

**Campos**:
- `saldo_actual`: Decimal, calculado automáticamente (suma ingresos - suma egresos)
- Lista de movimientos con filtros por fecha, tipo

**Movimientos de Caja**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `tipo` | Enum | `ingreso` o `egreso` |
| `monto` | Decimal | Monto del movimiento |
| `descripcion` | Texto | Descripción del movimiento |
| `fecha` | DateTime | Fecha y hora del registro |
| `imagen` | Archivo | Foto de boleta (opcional) |
| `registrado_por` | FK User | Usuario que registró |

**Requerimientos**:
- R-001: Registrar ingresos con descripción y monto
- R-002: Registrar egresos con descripción, monto y foto de boleta (opcional)
- R-003: Visualizar saldo actual de la caja
- R-004: Listar todos los movimientos con filtros por fecha y tipo
- R-005: Ver historial completo de movimientos

#### 3.3.2 Inventario

**Descripción**: Hoja de inventario para gestionar los bienes del ministerio.

**Campos**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | String(100) | Nombre del item |
| `categoria` | Enum | `muebles`, `electronicos`, `decoracion`, `utensilios`, `musica`, `otro` |
| `cantidad` | Integer | Cantidad disponible |
| `ubicacion` | String(100) | Dónde se encuentra |
| `descripcion` | Texto | Descripción adicional |
| `estado` | Enum | `nuevo`, `bueno`, `regular`, `mal_estado` |

**Requerimientos**:
- R-006: Agregar items al inventario
- R-007: Editar items existentes
- R-008: Eliminar items
- R-009: Filtrar por categoría y estado
- R-010: Ver lista completa del inventario

#### 3.3.3 Eventos en Calendario General

**Descripción**: Los ministerios pueden crear eventos que aparecen en el calendario general de la iglesia.

**Campos**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `titulo` | String(200) | Título del evento |
| `descripcion` | Texto | Descripción del evento |
| `fecha_inicio` | DateTime | Fecha y hora de inicio |
| `hora_inicio` | Time | Hora de inicio (opcional) |
| `fecha_fin` | DateTime | Fecha y hora de fin (opcional) |
| `hora_fin` | Time | Hora de fin (opcional) |
| `ubicacion` | String(200) | Lugar del evento |
| `tipo` | Enum | `propio` o `compartido` |
| `ministerios_relacionados` | M2M | Ministerios con los que se comparte |
| `creado_por` | FK User | Usuario que creó |

**Requerimientos**:
- R-011: Crear eventos propios
- R-012: Crear eventos compartidos con otros ministerios
- R-013: Visualizar eventos del ministerio en el calendario general
- R-014: Detectar conflictos de horario y ubicación
- R-015: Permitir forzar creación de evento aunque haya conflicto

#### 3.3.4 Planificación de Actividades

**Descripción**: Planificar actividades propias del ministerio.

**Campos**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `titulo` | String(200) | Título de la actividad |
| `descripcion` | Texto | Descripción |
| `responsable` | String(100) | Persona responsable |
| `fecha` | Date | Fecha planeada |
| `presupuesto` | Decimal | Presupuesto estimado |
| `estado` | Enum | `planificada`, `en_proceso`, `completada`, `cancelada` |

**Requerimientos**:
- R-016: Crear planificación de actividades
- R-017: Editar planificaciones existentes
- R-018: Cambiar estado de la planificación
- R-019: Ver lista de planificaciones del ministerio

#### 3.3.5 Ofrendas

**Descripción**: Registro de ofrendas del ministerio (excepto DNI que tiene sistema especial).

**Campos**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `fecha` | Date | Fecha de la ofrenda |
| `monto` | Decimal | Monto de la ofrenda |
| `observaciones` | Texto | Notas adicionales |

**Requerimientos**:
- R-020: Registrar ofrendas
- R-021: Ver historial de ofrendas
- R-022: Enviar ofrenda a tesorería (marcar como enviada)

---

## 4. Ministerio MNI (Ministerio de Nuevos Creyentes)

### 4.1 Funcionalidades Específicas

#### 4.1.1 Enfoques Mensuales

**Descripción**: El MNI tiene 12 enfoques mensuales bíblicos/teológicos.

**Lista de enfoques por mes**:

| Mes | Enfoque |
|-----|---------|
| Enero | Ofrenda Especial Génesis |
| Febrero | Ofrenda de Alabastro |
| Marzo | Movilización "El Llamado" |
| Abril | Movilización "Oportunidades para Servir" |
| Mayo | Cuenta la Historia |
| Junio | Jóvenes y Niños |
| Julio | Movilización "La Iglesia Enviando" |
| Agosto | Ofrenda de Alabastro |
| Septiembre | Eslabones |
| Octubre | La Iglesia Perseguida |
| Noviembre | FEM |
| Diciembre | Ofrenda de Acción de Gracias |

**Requerimientos**:
- R-023: Visualizar el enfoque del mes actual
- R-024: Ver lista completa de los 12 enfoques
- R-025: Filtrar por mes específico

#### 4.1.2 Programa del Último Domingo del Mes

**Descripción**: Espacio para redactar el flujo del programa del último domingo del mes.

**Campos**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `titulo` | String(200) | Título del programa |
| `fecha` | Date | Fecha del programa |
| `secciones` | JSON | Secciones del programa (inicio, especiales, reflexión, etc.) |

**Estructura de secciones**:
```json
{
  "inicio": "Descripción del momento de inicio",
  "especiales": "Descripción de momentos especiales",
  "reflexion": "Descripción de la reflexión",
  "ofrenda": "Descripción del momento de ofrenda",
  "cierre": "Descripción del cierre"
}
```

**Requerimientos**:
- R-026: Crear programa para el último domingo del mes
- R-027: Editar programa
- R-028: Ver programa creado
- R-029: Visualizar flujo estructurado del programa

#### 4.1.3 Tipos de Ofrenda Específicos

**Descripción**: El MNI tiene categorías específicas de ofrenda.

**Categorías**:
| Categoría | Descripción |
|-----------|-------------|
| `ofrenda_general` | Ofrenda general del domingo |
| `caja_alabastro` | Ofrenda de caja de alabastro |
| `accion_gracias` | Ofrenda de acción de gracias |
| `dip` | Ofrenda DIP |
| `oracion_ayuno` | Ofrenda de oración y ayuno |
| `fem` | Ofrenda FEM (se recauda en noviembre) |
| `otros` | Otras ofrendas |

**Requerimientos**:
- R-030: Registrar ofrenda por categoría
- R-031: Ver totales por categoría
- R-032: Generar reporte de ofrendas por período

---

## 5. Ministerio DNI (Departamento de Niños)

### 5.1 Registro de Asistencia y Ofrendas

#### 5.1.1 Registro Dominical

**Descripción**: Registrar ofrendas y asistencia cada domingo del mes.

**Campos de Asistencia**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `fecha` | Date | Fecha del registro |
| `miembro` | FK Miembro | Niño/a registrado (opcional para visitas) |
| `presente` | Boolean | Si asistió o no |
| `es_visita` | Boolean | Si es visita |
| `nombre_visita` | String(100) | Nombre de la visita (si aplica) |
| `clase` | String(30) | Clase a la que pertenece |
| `tiene_biblia` | Boolean | Si trajo biblia |
| `observaciones` | Texto | Notas adicionales |

**Requerimientos**:
- R-033: Registrar asistencia por domingo
- R-034: Marcar niños como presentes o ausentes
- R-035: Registrar visitas que no están en la lista
- R-036: Marcar si el niño trae biblia

#### 5.1.2 Asistencia Acumulativa

**Descripción**: La asistencia se acumula por nombre. Si un niño asiste los 4 domingos, se le acumulan.

**Requerimientos**:
- R-037: Ver asistencia acumulativa por persona en el mes
- R-038: Filtrar por clase
- R-039: Filtrar por mes y año
- R-040: Ver cantidad de domingos asistidos por cada niño

#### 5.1.3 Búsqueda y Filtros

**Requerimientos**:
- R-041: Buscar por nombre de niño
- R-042: Filtrar por clase
- R-043: Filtrar por rango de fechas
- R-044: Filtrar por asistencia (presentes/ausentes)

#### 5.1.4 Ofrendas por Clase

**Descripción**: Cada clase tiene su propio registro de ofrendas.

**Campos**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `fecha` | Date | Fecha de la ofrenda |
| `monto` | Decimal | Monto |
| `clase` | String(30) | Clase específica |

**Requerimientos**:
- R-045: Registrar ofrendas por clase
- R-046: Ver resumen de ofrendas por clase
- R-047: Las ofrendas se juntan a la caja general de DNI

### 5.2 Datos de los Miembros (Niños)

**Descripción**: Cada niño registrado debe tener los siguientes datos.

**Campos**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `primer_nombre` | String(50) | Primer nombre |
| `segundo_nombre` | String(50) | Segundo nombre (opcional) |
| `primer_apellido` | String(50) | Primer apellido |
| `segundo_apellido` | String(50) | Segundo apellido (opcional) |
| `fecha_nacimiento` | Date | Fecha de nacimiento |
| `edad` | Integer | Edad calculada automáticamente |
| `estado_civil` | Enum | `soltero`, `casado`, `viudo`, `divorciado` |

**Requerimientos**:
- R-048: Registrar niños con todos los datos
- R-049: Editar información del niño
- R-050: Ver perfil completo del niño

### 5.3 Sistema de Cumpleaños

**Descripción**: Recordatorio de quién está de cumpleaños.

**Requerimientos**:
- R-051: Ver lista de cumpleaños del mes
- R-052: Mostrar recordatorio en el dashboard
- R-053: Ver próxima fecha de cumpleaños por niño

### 5.4 Biblias por Clase

**Descripción**: Conteo de biblias disponibles por clase.

**Requerimientos**:
- R-054: Registrar cantidad de biblias por clase
- R-055: Ver total de biblias por clase
- R-056: Ver total de biblias de todas las clases juntas

### 5.5 Visitas

**Descripción**: Registrar visitas que no están en la lista de asistencia regular.

**Requerimientos**:
- R-057: Registrar visita con nombre
- R-058: Especificar a qué clase pertenece la visita
- R-059: Ver total de visitas por período
- R-060: Ver visitas acumuladas en el mes

### 5.6 Estadísticas por Domingo

**Descripción**: Visualizar sumas totales por cada domingo.

**Requerimientos**:
- R-061: Ver total de asistencia del domingo
- R-062: Ver total de visitas del domingo
- R-063: Ver total de ofrendas del domingo
- R-064: Ver total de biblias del domingo

### 5.7 Clases por Edades

**Descripción**: La asistencia se organiza por clases según edades.

**Nota**: Las clases específicas por edad serán definidas posteriormente.

**Requerimientos**:
- R-065: Definir clases por edades (pendiente)
- R-066: Asignar niños a su clase correspondiente
- R-067: Ver estadísticas por clase

---

## 6. Ministerio JNI (Juventud Nazarena Internacional)

### 6.1 Funcionalidades Específicas

#### 6.1.1 Caja Propia
Misma funcionalidad que en sección 3.3.1.

#### 6.1.2 Eventos en Calendario
Misma funcionalidad que en sección 3.3.3.

#### 6.1.3 Planificación de Actividades
Misma funcionalidad que en sección 3.3.4.

#### 6.1.4 Registro de Ofrendas

**Descripción**: Registro de ofrendas semanales y mensuales.

**Requerimientos**:
- R-068: Registrar ofrendas semanales
- R-069: Ver ofrendas mensuales
- R-070: Ver totales por período

---

## 7. Ministerios Secundarios

Los siguientes ministerios comparten las mismas funcionalidades base:

### 7.1 MAM (Ministerio de Mujeres)

**Requerimientos**:
- R-071: Planificación de actividades propias
- R-072: Caja propia (ingresos, egresos, fotos boletas)
- R-073: Eventos en calendario general
- R-074: Registro de ofrendas semanales y mensuales
- R-075: Actividades compartidas con otros ministerios

### 7.2 VID (Ministerio de Varones)

**Requerimientos**:
- R-076: Planificación de actividades propias
- R-077: Caja propia
- R-078: Eventos en calendario general
- R-079: Registro de ofrendas semanales y mensuales
- R-080: Actividades compartidas

### 7.3 EXPLO (Exploradores del Rey)

**Requerimientos**:
- R-081: Planificación de actividades propias
- R-082: Caja propia
- R-083: Eventos en calendario general
- R-084: Registro de ofrendas semanales y mensuales
- R-085: Actividades compartidas
- R-086: Apartado de lecciones (gestión de lecciones)

### 7.4 Danza

**Requerimientos**:
- R-087: Planificación de actividades propias
- R-088: Caja propia
- R-089: Eventos en calendario general
- R-090: Registro de ofrendas semanales y mensuales
- R-091: Actividades compartidas

### 7.5 Teatro

**Requerimientos**:
- R-092: Planificación de actividades propias
- R-093: Caja propia
- R-094: Eventos en calendario general
- R-095: Registro de ofrendas semanales y mensuales
- R-096: Actividades compartidas

### 7.6 Alabanza

**Requerimientos**:
- R-097: Planificación de actividades propias
- R-098: Caja propia
- R-099: Eventos en calendario general
- R-100: Registro de ofrendas semanales y mensuales
- R-101: Actividades compartidas

#### 7.6.1 Banco de Alabanzas

**Descripción**: Repertorio de canciones de alabanza organizadas por categoría.

**Campos**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `titulo` | String(200) | Nombre de la canción |
| `categoria` | Enum | `rapida`, `media`, `lenta` |
| `letra` | Texto | Letra de la canción |
| `acordes` | String | Acordes de la canción |
| `tono` | String(10) | Tono de la canción |

**Requerimientos**:
- R-102: Agregar canciones al banco
- R-103: Editar canciones
- R-104: Eliminar canciones
- R-105: Buscar por título
- R-106: Filtrar por categoría

#### 7.6.2 Generación de Programa Dominical

**Descripción**: Generar programa de alabanzas para el domingo.

**Reglas**:
- 5 alabanzas totales
- 2 alabanzas rápidas
- 1 alabanza media
- 2 alabanzas lentas
- No repetir una alabanza del domingo anterior

**Requerimientos**:
- R-107: Generar programa automático
- R-108: No repetir alabanzas del domingo anterior
- R-109: Ver programa generado
- R-110: Editar programa manualmente
- R-111: Ver historial de programas

### 7.7 Comunicaciones

**Requerimientos**:
- R-112: Planificación de actividades propias
- R-113: Caja propia
- R-114: Eventos en calendario general
- R-115: Registro de ofrendas semanales y mensuales
- R-116: Actividades compartidas

#### 7.7.1 Checklist de Ideas

**Descripción**: Lista de ideas para contenido de comunicaciones.

**Campos**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `idea` | String(200) | Descripción de la idea |
| `completada` | Boolean | Si está completada o no |
| `prioridad` | Enum | `alta`, `media`, `baja` |

**Requerimientos**:
- R-117: Agregar ideas
- R-118: Marcar ideas como completadas
- R-119: Filtrar por prioridad
- R-120: Filtrar por estado (completada/pendiente)

#### 7.7.2 Recursos Gráficos

**Descripción**: Almacenar recursos gráficos de la iglesia.

**Campos**:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | String(100) | Nombre del recurso |
| `tipo` | Enum | `foto`, `video`, `plantilla`, `logo`, `documento` |
| `archivo` | File | Archivo del recurso |
| `descripcion` | Texto | Descripción |

**Recursos incluidos**:
- Colorimetría de redes sociales
- Plantillas de posts
- Recursos gráficos
- Fotos
- Videos
- Logos
- Misión y visión de la iglesia

**Requerimientos**:
- R-121: Agregar recursos
- R-122: Descargar recursos
- R-123: Ver recursos por tipo
- R-124: Gestionar misión y visión

### 7.8 Compasión

**Requerimientos**:
- R-125: Planificación de actividades propias
- R-126: Caja propia
- R-127: Actividades compartidas

### 7.9 NazaKids

**Requerimientos**:
- R-128: Planificación de actividades propias
- R-129: Caja propia
- R-130: Eventos en calendario general
- R-131: Registro de ofrendas semanales y mensuales
- R-132: Actividades compartidas

### 7.10 Adulto Mayor

**Requerimientos**:
- R-133: Planificación de actividades propias
- R-134: Caja propia
- R-135: Eventos en calendario general
- R-136: Registro de ofrendas semanales y mensuales
- R-137: Actividades compartidas

---

## 8. Módulo de Finanzas (Tesorería)

### 8.1 Visión General

El módulo de finanzas centraliza la gestión de fondos de todos los ministerios, consolida el flujo de caja de la iglesia y genera informes mensuales.

### 8.2 Traspaso de Fondos

**Descripción**: Los fondos de cada ministerio se traspasan a tesorería.

**Requerimientos**:
- R-138: Ver saldos de cajas de todos los ministerios
- R-139: Registrar traspaso de fondos a tesorería
- R-140: Ver historial de traspasos

### 8.3 Flujo de Caja General

**Descripción**: Flujo de caja de toda la iglesia.

**Requerimientos**:
- R-141: Ver flujo de caja mensual
- R-142: Ver ingresos por categoría
- R-143: Ver egresos por categoría
- R-144: Ver saldo disponible

### 8.4 Visualización de Boletas

**Descripción**: Ver boletas de gastos mensuales para transparencia.

**Requerimientos**:
- R-145: Ver boletas de gastos de todos los ministerios
- R-146: Buscar boletas por fecha
- R-147: Ver detalle de cada gasto

### 8.5 Configuración de Finanzas

**Descripción**: Configuración de porcentajes y montos fijos para cálculos automáticos.

**Parámetros configurables**:

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `pres_distrital_pct` | Porcentaje de PRES.DISTRITAL | 10% |
| `pres_educacional_pct` | Porcentaje de PRES EDUCACIONAL | 3% |
| `pres_evangelismo_pct` | Porcentaje de PRES.EVANGELISMO | 2% |
| `jubilacion_monto` | Monto fijo de jubilación | 0 |

**Base de cálculo**: Todos los porcentajes se calculan sobre el saldo total (flujo de caja mensual).

**Requerimientos**:
- R-148: Configurar porcentajes de PRES
- R-149: Configurar monto de jubilación
- R-150: Ver configuración actual

### 8.6 Informe Mensual

**Descripción**: Generar informe mensual con todos los detalles de ingresos y egresos.

#### Estructura del Informe

##### INGRESOS

**1. SALDO DEL MES PASADO**

Flujo de caja mensual - montos que se traspasan mes a mes.

| Campo | Descripción |
|-------|-------------|
| `otros_ministerios` | Suma de montos totales de ministerios secundarios |
| `iglesia` | Suma de montos excluyendo ministerios |
| `dni` | Monto total de DNI |
| `jni` | Monto total de JNI |
| `mni` | Monto total de MNI |

**2. POR IGLESIA LOCAL**

| Campo | Descripción |
|-------|-------------|
| `ofrendas` | Total de todas las ofrendas (ministerios + otras) |
| `diezmos` | Suma total de diezmos (no va sumada con ofrendas) |
| `especiales` | Suma total de donaciones especiales |

**3. INGRESO POR OTROS MINISTERIOS**

Desglose de ingresos de ministerios secundarios:
- Adulto Mayor
- MAM
- Nazakids
- Alabanza
- Exploradores
- Danza
- VID
- Teatro
- Comunicaciones
- Compasión

**Fondos especiales** (no son ministerios):
- `ahorro`: Monto invertido que va incrementando mensualmente
- `proyectos`: Fondo específico para proyectos de la Iglesia

**4. POR DNI**

Suma total de ofrendas de DNI.

**5. POR JNI**

Suma total de ofrendas de JNI.

**6. POR MNI**

Incluye:
- Ofrendas totales de MNI
- Caja de Alabastro
- Acción de Gracias
- DIP
- Oración y Ayuno
- FEM
- Otros

**7. TOTAL DE ENTRADAS DEL AÑO**

Suma de: saldo del mes pasado + total ingreso del año.

##### EGRESOS

**1. POR IGLESIA LOCAL**

| Campo | Descripción |
|-------|-------------|
| `sosten_pastoral` | Sostén pastoral |
| `beneficios_pastorales` | Beneficios pastorales |
| `varios_iglesia` | Gastos varios de iglesia (luz, agua, etc.) |
| `pres_distrital` | 10% del saldo total |
| `pres_educacional` | 3% del saldo total |
| `pres_evangelismo` | 2% del saldo total |
| `jubilacion` | Monto fijo para jubilación de la pastora |
| `coce` | Goce dado por DNI, JNI, MNI |
| `fondo_contingencia` | Egreso especificado mensual del saldo total |

**2. TOTAL GASTOS OTROS MINISTERIOS**

Suma de egresos de ministerios secundarios.

**3. POR DNI**

| Campo | Descripción |
|-------|-------------|
| `gastos_locales` | Gastos en eventos u otras cosas |
| `cuota_distrital` | Monto específico para el distrito |
| `coce` | Monto específico mensual |

**4. POR JNI**

| Campo | Descripción |
|-------|-------------|
| `gastos_locales` | Gastos en eventos u otros |
| `cuota_distrital` | Monto específico para el distrito |
| `coce` | Monto específico mensual |

**5. POR MNI**

| Campo | Descripción |
|-------|-------------|
| `gastos_locales` | Gastos en eventos, compra de material |
| `cuota_distrital` | Monto destinado para el distrito (manual) |
| `coce` | Monto específico mensual |
| `caja_alabastro` | Egreso para caja de alabastro |
| `fem` | Egreso igual al ingreso del FEM |

**6. TOTAL GASTOS**

Suma de: gastos iglesia + gastos otros ministerios + gastos DNI + gastos JNI + gastos MNI.

##### SALDO FIN DE MES

| Campo | Descripción |
|-------|-------------|
| `saldo_mes_pasado` | Saldo anterior |
| `total_ingresos` | Suma de todos los ingresos |
| `total_gastos` | Suma de todos los gastos |
| `saldo_final` | Resultado (ingresos - gastos) |

##### FLUJO CAJA

- Este procedimiento se hace continuamente mes a mes
- El saldo final de un mes se convierte en el saldo inicial del siguiente

**Requerimientos**:
- R-151: Generar informe mensual completo
- R-152: Ver desglose de ingresos
- R-153: Ver desglose de egresos
- R-154: Ver saldo fin de mes
- R-155: Ver flujo de caja histórico
- R-156: Exportar informe a PDF

---

## 9. Módulo de Calendario

### 9.1 Lista de Eventos

**Descripción**: Visualizar eventos de todos los ministerios.

**Requerimientos**:
- R-157: Ver todos los eventos en calendario mensual
- R-158: Ver eventos pasados y futuros
- R-159: Navegar entre meses

### 9.2 Detección de Conflictos

**Descripción**: No permitir dos eventos a la misma hora y en el mismo lugar.

**Requerimientos**:
- R-160: Detectar conflictos automáticamente
- R-161: Mostrar mensaje de conflicto
- R-162: Permitir forzar creación de evento

### 9.3 Detalles de Eventos

**Requerimientos**:
- R-163: Ver detalles completos del evento
- R-164: Ver qué ministerios están involucrados
- R-165: Ver quién creó el evento

### 9.4 Filtros y Búsqueda

**Requerimientos**:
- R-166: Filtrar por ministerio
- R-167: Filtrar por lugar
- R-168: Filtrar por hora
- R-169: Buscar eventos por nombre

---

## 10. Módulo de Usuarios

### 10.1 Roles del Sistema

| Rol | Descripción |
|-----|-------------|
| `admin` | Administrador del sistema |
| `pastora` | Pastora (acceso completo) |
| `secretaria` | Secretaria |
| `tesorera` | Tesorera |
| `lider_ministerio` | Líder de un ministerio |
| `concilio` | Miembro del concilio (solo lectura) |

### 10.2 Roles de Ministerio

| Rol | Descripción |
|-----|-------------|
| `miembro` | Miembro regular |
| `lider` | Líder del ministerio |
| `sublider` | Sublíder |
| `tesorero` | Tesorero del ministerio |
| `secretario` | Secretario del ministerio |

### 10.3 Estados de Usuario

| Estado | Descripción |
|--------|-------------|
| `activo` | Puede vincularse a ministerios y tener roles |
| `inactivo` | No puede hacer ninguna acción, se desvincula de todo |

**Comportamiento de desactivación**:
- R-170: Al desactivar, el usuario se desvincula de todos los ministerios
- R-171: Al desactivar, pierde acceso al sistema
- R-172: Los datos básicos y rol del sistema se mantienen
- R-173: Si un usuario ya vinculado es desactivado, se limpia su vinculación

### 10.4 Gestión de Usuarios

**Requerimientos**:
- R-174: Listar todos los usuarios del sistema
- R-175: Crear usuarios
- R-176: Editar usuarios
- R-177: Desactivar usuarios
- R-178: Asignar roles del sistema
- R-179: Asignar ministerios a usuarios
- R-180: Ver usuarios activos e inactivos

### 10.5 Permisos

**Por rol**:

| Rol | Permisos |
|-----|----------|
| `admin` | Todos los permisos |
| `pastora` | Todos los permisos de ministerios y finanzas |
| `tesorera` | Caja: ver, crear, editar, aprobar; Ofrendas: ver, crear, editar; Reportes: ver, exportar |
| `secretaria` | Miembros: ver, crear, editar; Asistencia: ver, registrar; Eventos: ver, crear, editar |
| `concilio` | Solo lectura |
| `lider_ministerio` | Acceso al propio ministerio |

---

## 11. Anexos

### Glosario

| Término | Descripción |
|---------|-------------|
| MNI | Ministerio de Nuevos Creyentes |
| DNI | Departamento de Niños |
| JNI | Juventud Nazarena Internacional |
| MAM | Ministerio de Mujeres |
| VID | Ministerio de Varones |
| EXPLO | Exploradores del Rey |
| FEM | Ofrenda especial de noviembre |
| COCE | Goce de los tres ministerios principales |
| PRES | Prescindentes (porcentajes del presupuesto) |
| DIP | Donación o aporte especial |

### Símbolos

| Símbolo | Significado |
|---------|-------------|
| FK | Foreign Key (relación) |
| M2M | Many-to-Many (relación muchos a muchos) |
| Enum | Lista de valores predefinidos |
| Decimal | Número decimal (para montos de dinero) |
| DateTime | Fecha y hora |
| Date | Solo fecha |
| Time | Solo hora |

---

## 12. Notas de Implementación

### Prioridades de desarrollo

1. **Fase 1**: Ministerios base (caja, inventario, eventos)
2. **Fase 2**: DNI (funcionalidades específicas)
3. **Fase 3**: Alabanza (banco de alabanzas)
4. **Fase 4**: Finanzas (tesorería e informes)
5. **Fase 5**: MNI (enfoques y programa)
6. **Fase 6**: Comunicaciones

### Base de datos

- Usar PostgreSQL para producción
- Cada modelo debe tener timestamps (created_at, updated_at)
- Soft delete donde aplique

### API REST

- Seguir el patrón del proyecto actual (Django REST Framework)
- Mantener autenticación JWT con cookies HttpOnly
- Usar ViewSets para CRUD genérico
- Selectors para consultas complejas
- Services para lógica de negocio

### Frontend

- Mantener estructura actual de Astro
- Usar islands para componentes interactivos
- Mantener el patrón de stores existente
- Seguir el diseño UI/UX actual

---

## 13. Requerimientos No Funcionales

### 13.1 Rendimiento

| ID | Descripción | Meta |
|----|-------------|------|
| RNF-001 | Tiempo de respuesta de API para consultas simples (listados, GET) | < 200ms |
| RNF-002 | Tiempo de respuesta de API para operaciones complejas (informes, cálculos agregados) | < 1s |
| RNF-003 | Tiempo de carga inicial del frontend | < 3s en conexión 4G |
| RNF-004 | Soporte de usuarios concurrentes | 50+ usuarios simultáneos |
| RNF-005 | Generación de informe mensual | < 5s |

### 13.2 Seguridad

| ID | Descripción |
|----|-------------|
| RNF-006 | Autenticación mediante JWT con cookies HttpOnly (ya implementado) |
| RNF-007 | HTTPS obligatorio en entorno de producción |
| RNF-008 | Validación de inputs en backend (serializers, forms) |
| RNF-009 | Validación de inputs en frontend (formularios) |
| RNF-010 | Rate limiting en endpoint de login (máx. 5 intentos por minuto) |
| RNF-011 | Contraseñas hasheadas con Django (pbkdf2_sha256) |
| RNF-012 | Permisos basados en roles verificados en cada request |
| RNF-013 | Sanitización de uploads de archivos (imágenes) |
| RNF-014 | Logs de auditoría para acciones sensibles (creación/edición de usuarios, movimientos de caja) |

### 13.3 Escalabilidad

| ID | Descripción | Meta |
|----|-------------|------|
| RNF-015 | Capacidad de ministerios soportados | 13+ ministerios |
| RNF-016 | Capacidad de miembros registrados | 5,000+ registros |
| RNF-017 | Capacidad de eventos históricos | 10,000+ registros |
| RNF-018 | Diseño preparado para multi-iglesia (futuro) |

### 13.4 Disponibilidad

| ID | Descripción | Meta |
|----|-------------|------|
| RNF-019 | Uptime del sistema | > 99.5% |
| RNF-020 | Página de error 404 personalizada |
| RNF-021 | Página de error 500 personalizada |
| RNF-022 | Manejo graceful de errores (sin crashes) |
| RNF-023 | Logs centralizados de errores |
| RNF-024 | Notificaciones toast para errores de usuario |

### 13.5 Compatibilidad

| ID | Descripción |
|----|-------------|
| RNF-025 | Responsive design: móvil (320px) hasta desktop (1920px+) |
| RNF-026 | Navegadores soportados: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |
| RNF-027 | Navegación mobile: BottomNav |
| RNF-028 | Navegación desktop: Sidebar |
| RNF-029 | Progressive Web App (PWA) opcional para futuras iterations |

### 13.6 Persistencia

| ID | Descripción |
|----|-------------|
| RNF-030 | Base de datos: PostgreSQL en producción |
| RNF-031 | Base de datos: SQLite en desarrollo |
| RNF-032 | Backups automáticos diarios |
| RNF-033 | Retención mínima de datos: 5 años |
| RNF-034 | Migraciones de base de datos versionadas |
| RNF-035 | Índices en campos de búsqueda frecuente |

### 13.7 UX/UI

| ID | Descripción |
|----|-------------|
| RNF-036 | Diseño mobile-first |
| RNF-037 | Skeleton loading states para mejor UX |
| RNF-038 | Notificaciones toast para acciones exitosas |
| RNF-039 | Confirmaciones antes de acciones destructivas (eliminar) |
| RNF-040 | Estados vacíos con mensajes informativos |
| RNF-041 | Feedback visual inmediato en formularios |
| RNF-042 | Animaciones suaves en transiciones (300ms) |
| RNF-043 | Colores por ministerio consistentes en toda la app |

### 13.8 Mantenibilidad

| ID | Descripción | Meta |
|----|-------------|------|
| RNF-044 | Cobertura de tests en backend | > 70% |
| RNF-045 | Cobertura de tests en frontend | > 50% |
| RNF-046 | Docstrings en todas las funciones y clases |
| RNF-047 | Code review obligatorio antes de merge |
| RNF-048 | Conventional commits (git) |
| RNF-049 | Documentación actualizada de API (OpenAPI/Swagger) |
| RNF-050 | Arquitectura basada en servicios (selectors/services) |

### 13.9 Accesibilidad

| ID | Descripción | Meta |
|----|-------------|------|
| RNF-051 | Contraste de colores | WCAG 2.1 nivel AA |
| RNF-052 | Navegación completa por teclado |
| RNF-053 | Focus visible en elementos interactivos |
| RNF-054 | Labels ARIA en formularios |
| RNF-055 | Textos alternativos en imágenes |
| RNF-056 | Jerarquía de encabezados correcta (h1-h6) |
| RNF-057 | Soporte para lectores de pantalla |