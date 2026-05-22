# Guía Maestra de Ingeniería de Requisitos: Gestor Iglesia
## Estructuras, Campos y Mejores Prácticas

---

## 1. El Rol Estratégico de los Requisitos en el Éxito del Software

La ingeniería de requisitos trasciende la mera captura técnica; representa la creación del "plano" maestro que determina la viabilidad de cualquier ecosistema digital. Como Arquitectos de Sistemas, debemos entender que una Especificación de Requisitos de Software (ERS) robusta no es solo documentación, sino un contrato estratégico que alinea las expectativas de los stakeholders con las capacidades del equipo de desarrollo.

Para el proyecto **Gestor Iglesia**, este documento establece la spécification completa que gobernará el desarrollo del sistema de gestión para iglesias, asegurando que todas las partes interesadas compartan una comprensión común de los objetivos, funcionalidades y restricciones del sistema.

---

## 2. Diagnóstico de Fallas: Errores Comunes y Anti-patrones

### 2.1 La Trampa del Enunciado de Solución

Un error crítico en el levantamiento ocurre cuando los stakeholders presentan una "solución" en lugar de un "problema".

**Ejemplo en Gestor Iglesia:**
- Enunciado de solución: "Necesito un módulo de caja para cada ministerio"
- Problema real: "Necesito que cada ministerio gestione sus fondos de forma independiente Y centralizada en tesorería para generar informes consolidados"

**Acción requerida:** Retroceder siempre hasta identificar la necesidad de negocio real antes de especificar funcionalidades.

### 2.2 Catálogo de Errores a Evitar en Gestor Iglesia

| # | Error | Mitigación en Gestor Iglesia |
|---|-------|------------------------------|
| 1 | Falta de comprensión del dominio | Consultar con liderazgo eclesial y tesoreras |
| 2 | Ambigüedad | Usar campos estructurados (ver Sección 3) |
| 3 | Incompletitud | Definir respuestas para entradas inválidas |
| 4 | Cambios incontrolados | Control de versiones del documento ERS |
| 5 | Exclusión de usuarios finales | Incluir líderes de ministerio en validación |
| 6 | Dependencia de documentación estática | Revisión trimestral del documento |
| 7 | Falta de validación | Sesiones de prototypación visual |
| 8 | Sobreingeniería | Enfoque en funcionalidades de alto valor |
| 9 | Falta de trazabilidad | Matriz RTM con IDs únicos |
| 10 | Ignorar limitaciones técnicas | Verificar con stack existente (Django/Astro) |

---

## 3. Anatomía de un Requisito de Alta Calidad: Campos Esenciales

### 3.1 Estructura de Campos Propuesta

Cada requisito del Gestor Iglesia sigue esta estructura:

| Campo | Propósito | Fuente de Verificación |
|-------|-----------|------------------------|
| **Identificador** | R-001 a R-180 (funcionales), RNF-001 a RNF-057 (no funcionales) | Matriz RTM |
| **Actor/Persona** | Lider de Ministerio, Tesorera, Admin, Pastor, etc. | User Personas |
| **Descripción** | El "Qué" y el "Para qué" con valor de negocio | Sesiones de levantamiento |
| **Criterios de Aceptación** | Condiciones verificables para validar el éxito | UAT |
| **Prioridad** | Must, Should, Could, Won't (MoSCoW) | Framework RICE |
| **Dependencias** | Técnicas: requiere API, Frontend, DB | Especificaciones técnicas |
| **Módulo** | Ministerios, Finanzas, Calendario, Usuarios | Arquitectura del sistema |

### 3.2 Plantilla de Requisito Funcional

```
ID: R-XXX
NOMBRE: [Título descriptivo]
ACTOR: [Quién lo necesita]
DESCRIPCIÓN: [Qué debe hacer el sistema y por qué]
CRITERIOS DE ACEPTACIÓN:
  1. [Condición verificable 1]
  2. [Condición verificable 2]
  3. [Condición verificable 3]
PRIORIDAD: Must | Should | Could | Won't
DEPENDENCIAS: [IDs de otros requisitos relacionados]
MÓDULO: [Ministerios | Finanzas | Calendario | Usuarios]
```

### 3.3 Plantilla de Requisito No Funcional

```
ID: RNF-XXX
NOMBRE: [Título descriptivo]
MÉTRICA: [Indicador medible]
META: [Valor objetivo]
RESTRICCIÓN TÉCNICA: [Limitación de HW/SW/Red]
PRIORIDAD: Must | Should | Could | Won't
```

---

## 4. Estándares de Calidad y Atributos de una Buena ERS

### 4.1 Los 9 Atributos de Oro (según IEEE 830)

| Atributo | Aplicación en Gestor Iglesia |
|----------|----------------------------|
| **Correcta** | Cada requisito describe con precisión lo acordado con stakeholders |
| **No ambigua** | "Caja" = caja del ministerio, no tesorería central |
| **Completa** | Incluye casos de error y edge cases |
| **Verificable** | "Tiempo de respuesta < 200ms" es medible |
| **Consistente** | No contradecir otros requisitos del mismo módulo |
| **Clasificada** | Por prioridad (MoSCoW) y tipo (funcional/no funcional) |
| **Modificable** | Control de versiones, historial de cambios |
| **Trazable** | Matriz RTM vincula requisitos con código |
| **Utilizable** | Diseño práctico para desarrollo y testing |

### 4.2 Validación vs Verificación

- **Validación:** ¿Estamos construyendo el producto correcto? → Sesiones con usuarios finales
- **Verificación:** ¿Estamos construyendo correctamente? → Tests automatizados

---

## 5. Marcos de Generación: De Historias de Usuario a Requisitos Formales

### 5.1 Método INVEST Adaptado

Cada requisito evalúa:
- **I**ndependiente: No depende de otros requisitos
- **N**egociable: Flexible en implementación
- **V**aliosa: Aporta valor de negocio real
- **E**stimable: Puede estimarse el esfuerzo
- **P**equeña: Atoms para sprint planning
- **T**esteable: Criterios de aceptación claros

### 5.2 Organización por Tipo de Usuario (IEEE 830)

Para Gestor Iglesia:
- **Por actor:** Admin, Pastor, Tesorera, Secretaria, Líder de Ministerio, Miembro
- **Por objeto:** Ministerios, Caja, Eventos, Asistencia, Usuarios, Ofrendas
- **Por objetivo:** Gestión financiera, Planificación, Reportes, Comunicación

---

## 6. Frameworks de Priorización

### 6.1 MoSCoW Aplicado

| Prioridad | Descripción | Requisitos Clave |
|-----------|-------------|------------------|
| **Must** | Crítico, sin esto el sistema no funciona | R-001 a R-022 (base ministerios) |
| **Should** | Importante, mejora significativa | R-107 (generación programa), R-151 (informe mensual) |
| **Could** | Deseable, si hay tiempo | R-053 (cumpleaños), R-156 (exportar PDF) |
| **Won't** | Excluido de esta iteración | Secretaría (futuro) |

### 6.2 RICE Scoring (opcional para roadmap)

```
Score = (Reach × Impact × Confidence) / Effort
```

---

## 7. Protocolo de Sesiones de Levantamiento: Mejores Prácticas

### 7.1 Preparación de Sesiones

1. **Agenda distribuida 48h antes**
2. **Material de lectura previa:** Historia de la iglesia, estructura de ministerios
3. **Invitar por conocimiento, no por jerarquía**
4. **Duración máxima:** 90 minutos

### 7.2 Ejecución: Método Bezos Adaptado

1. **Lectura silenciosa (15 min):** Repasar requisitos del módulo
2. **Discusión (45 min):** Clarificar dudas, proponer mejoras
3. **Validación visual (30 min):** Wireframes o prototipos

### 7.3 Validación Continua

- Prototipos interactivos antes de desarrollo
- Checklist de sign-off por módulo

---

## 8. Conclusión: Hacia una Cultura de Requisitos Sólidos

La ingeniería de requisitos no es un evento estático al inicio del proyecto, sino un proceso iterativo de descubrimiento y refinamiento. Este documento ERS representa el estado actual del conocimiento y debe ser vivant evidence de la evolución del proyecto.

**Compromiso:** Revisión trimestral de este documento con stakeholders clave.

---

# SPECIFICACIÓN FORMAL: GESTOR IGLESIA

---

## A. Información General del Proyecto

| Campo | Valor |
|-------|-------|
| **Nombre** | Gestor Iglesia |
| **Tipo** | Sistema de gestión para iglesias |
| **Versión ERS** | 1.0 |
| **Fecha** | 2026-05-22 |
| **Stack tecnológico** | Django REST Framework + Astro |
| **Base de datos** | PostgreSQL (prod) / SQLite (dev) |
| **Autenticación** | JWT con cookies HttpOnly |

---

## B. Módulos del Sistema

| Módulo | Descripción | Prioridad | Estado |
|--------|-------------|-----------|--------|
| Ministerios | Gestión de los 13 ministerios | Alta | Parcial |
| Finanzas | Tesorería central, flujo de caja | Alta | Por hacer |
| Calendario | Eventos compartidos | Alta | Parcial |
| Usuarios | Gestión de usuarios y permisos | Alta | Funcional |

---

## C. Requerimientos Funcionales

### C.1 Ministerios - Funcionalidades Comunes (R-001 a R-022)

#### R-001: Registrar ingresos en caja de ministerio
- **ACTOR:** Tesorero de Ministerio
- **DESCRIPCIÓN:** El tesorero debe poder registrar un ingreso especificando monto, descripción y fecha. El movimiento incrementará el saldo de la caja del ministerio.
- **CRITERIOS DE ACEPTACIÓN:**
  1. El sistema muestra formulario con campos: tipo (preseleccionado "ingreso"), monto (decimal, requerido), descripción (texto, requerido)
  2. El monto debe ser mayor a 0
  3. Al guardar, el saldo de la caja se actualiza automáticamente
  4. Se registra el usuario que realizó el movimiento
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios

#### R-002: Registrar egresos con foto de boleta
- **ACTOR:** Tesorero de Ministerio
- **DESCRIPCIÓN:** El tesorero debe poder registrar un egreso con monto, descripción y opcionalmente subir una foto de la boleta como comprobante.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Formulario con campos: tipo (preseleccionado "egreso"), monto, descripción
  2. Campo opcional para upload de imagen (jpg, png, máx 5MB)
  3. Validación de monto mayor a 0
  4. Al guardar, el saldo se decrementa
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios

#### R-003: Visualizar saldo actual de caja
- **ACTOR:** Líder de Ministerio, Tesorero
- **DESCRIPCIÓN:** El sistema debe mostrar el saldo actual de la caja calculado como suma de ingresos menos egresos.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Dashboard del ministerio muestra saldo con formato monetario
  2. Saldo se actualiza en tiempo real tras cada movimiento
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-001, R-002
- **MÓDULO:** Ministerios

#### R-004: Listar movimientos con filtros
- **ACTOR:** Tesorero, Líder
- **DESCRIPCIÓN:** Listar todos los movimientos de caja con filtros por fecha y tipo.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Tabla con columnas: Fecha, Tipo, Monto, Descripción
  2. Filtro por rango de fechas
  3. Filtro por tipo (ingreso/egreso)
  4. Paginación de 20 registros por página
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-001, R-002
- **MÓDULO:** Ministerios

#### R-005: Ver historial completo de movimientos
- **ACTOR:** Líder, Tesorero, Admin
- **DESCRIPCIÓN:** Acceso al historial completo sin límites de paginación.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Opción de exportar a CSV
  2. Orden cronológico inverso
- **PRIORIDAD:** Should
- **DEPENDENCIAS:** R-004
- **MÓDULO:** Ministerios

#### R-006: Agregar items al inventario
- **ACTOR:** Líder de Ministerio
- **DESCRIPCIÓN:** Agregar items al inventario del ministerio con nombre, categoría, cantidad, ubicación, descripción y estado.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Formulario con todos los campos
  2. Categorías predefinidas: muebles, electronicos, decoracion, utensilios, musica, otro
  3. Estados: nuevo, bueno, regular, mal_estado
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios

#### R-007: Editar items existentes
- **ACTOR:** Líder de Ministerio
- **DESCRIPCIÓN:** Modificar datos de items existentes en el inventario.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Mismos campos que agregar
  2. Historial de cambios
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-006
- **MÓDULO:** Ministerios

#### R-008: Eliminar items
- **ACTOR:** Líder de Ministerio
- **DESCRIPCIÓN:** Eliminar items del inventario.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Confirmación antes de eliminar
  2. Soft delete (marcado como inactivo)
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-006
- **MÓDULO:** Ministerios

#### R-009: Filtrar inventario por categoría y estado
- **ACTOR:** Líder de Ministerio
- **DESCRIPCIÓN:** Filtrar items del inventario por categoría y estado.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Dropdowns de categoría y estado
  2. Resultados actualizados en tiempo real
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-006
- **MÓDULO:** Ministerios

#### R-010: Ver lista completa del inventario
- **ACTOR:** Líder, Tesorero
- **DESCRIPCIÓN:** Ver todos los items del inventario del ministerio.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Tabla con todos los campos
  2. Paginación
  3. Ordenable por nombre, categoría, cantidad
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-006
- **MÓDULO:** Ministerios

#### R-011: Crear eventos propios
- **ACTOR:** Líder de Ministerio
- **DESCRIPCIÓN:** Crear eventos que aparecen en el calendario general de la iglesia.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Formulario con título, descripción, fecha_inicio, fecha_fin, ubicación
  2. Tipo "propio" seleccionado por defecto
  3. Evento visible en calendario general
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios

#### R-012: Crear eventos compartidos
- **ACTOR:** Líder de Ministerio
- **DESCRIPCIÓN:** Crear eventos compartidos con otros ministerios.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Selector de tipo "compartido"
  2. Checkbox para seleccionar ministerios relacionados
  3. Evento visible en ministerios seleccionados
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-011
- **MÓDULO:** Ministerios

#### R-013: Visualizar eventos del ministerio
- **ACTOR:** Todos los usuarios
- **DESCRIPCIÓN:** Ver eventos del ministerio propio en el calendario general.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Filtro por ministry disponible
  2. Indicador visual de evento compartido
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-011, R-012
- **MÓDULO:** Ministerios

#### R-014: Detectar conflictos de horario y ubicación
- **ACTOR:** Sistema
- **DESCRIPCIÓN:** Al crear evento, detectar si existe conflicto de horario y lugar.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Validación al guardar
  2. Lista de eventos conflictivos si aplica
  3. Mensaje de error claro
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios

#### R-015: Permitir forzar creación de evento
- **ACTOR:** Líder de Ministerio, Admin
- **DESCRIPCIÓN:** Permitir guardar evento aunque haya conflicto, con confirmación.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Opción "Forzar de todos modos"
  2. Registro del conflicto en logs
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-014
- **MÓDULO:** Ministerios

#### R-016: Crear planificación de actividades
- **ACTOR:** Líder de Ministerio
- **DESCRIPCIÓN:** Planificar actividades propias del ministerio con título, descripción, responsable, fecha, presupuesto.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Formulario completo
  2. Estados: planificada, en_proceso, completada, cancelada
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios

#### R-017: Editar planificaciones existentes
- **ACTOR:** Líder de Ministerio
- **DESCRIPCIÓN:** Modificar planificaciones de actividades.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-016
- **MÓDULO:** Ministerios

#### R-018: Cambiar estado de planificación
- **ACTOR:** Líder de Ministerio
- **DESCRIPCIÓN:** Cambiar el estado de una planificación.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Dropdown de estados
  2. Registro de fecha de cambio
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-016
- **MÓDULO:** Ministerios

#### R-019: Ver lista de planificaciones
- **ACTOR:** Líder de Ministerio
- **DESCRIPCIÓN:** Ver todas las planificaciones del ministerio.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-016
- **MÓDULO:** Ministerios

#### R-020: Registrar ofrendas
- **ACTOR:** Tesorero de Ministerio
- **DESCRIPCIÓN:** Registrar ofrendas con fecha, monto y observaciones.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Formulario con campos requeridos
  2. Historial de ofrendas
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios

#### R-021: Ver historial de ofrendas
- **ACTOR:** Tesorero, Líder
- **DESCRIPCIÓN:** Ver historial completo de ofrendas del ministerio.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-020
- **MÓDULO:** Ministerios

#### R-022: Enviar ofrenda a tesorería
- **ACTOR:** Tesorero de Ministerio
- **DESCRIPCIÓN:** Marcar ofrenda como enviada a tesorería.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Checkbox o botón "Enviar a Tesorería"
  2. Registro de fecha de envío
  3. Ofrenda visible en módulo de finanzas
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-020
- **MÓDULO:** Ministerios

---

### C.2 MNI - Funcionalidades Específicas (R-023 a R-032)

#### R-023: Visualizar enfoque del mes actual
- **ACTOR:** Líder de MNI
- **DESCRIPCIÓN:** Mostrar automáticamente el enfoque bíblico/teológico correspondiente al mes actual.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Al abrir MNI, se muestra el enfoque del mes actual
  2. Tabla de 12 enfoques accesible
  3. Filtro por mes específico disponible
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > MNI

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

#### R-024: Ver lista completa de los 12 enfoques
- **ACTOR:** Líder de MNI
- **DESCRIPCIÓN:** Ver tabla con todos los enfoques mensuales.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-023
- **MÓDULO:** Ministerios > MNI

#### R-025: Filtrar por mes específico
- **ACTOR:** Líder de MNI
- **DESCRIPCIÓN:** Filtrar y ver enfoque de un mes específico.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-023
- **MÓDULO:** Ministerios > MNI

#### R-026: Crear programa para el último domingo del mes
- **ACTOR:** Líder de MNI
- **DESCRIPCIÓN:** Permitir redactar el flujo del programa del último domingo con secciones definidas.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Formulario con título, fecha, y 5 secciones de texto (inicio, especiales, reflexión, ofrenda, cierre)
  2. Vista previa del flujo estructurado
  3. Edición y eliminación de programas anteriores
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > MNI

#### R-027: Editar programa
- **ACTOR:** Líder de MNI
- **DESCRIPCIÓN:** Modificar programa creado.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-026
- **MÓDULO:** Ministerios > MNI

#### R-028: Ver programa creado
- **ACTOR:** Líder de MNI
- **DESCRIPCIÓN:** Visualizar programa del último domingo.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-026
- **MÓDULO:** Ministerios > MNI

#### R-029: Visualizar flujo estructurado del programa
- **ACTOR:** Líder de MNI
- **DESCRIPCIÓN:** Mostrar programa con formato visual de secciones.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-026
- **MÓDULO:** Ministerios > MNI

#### R-030: Registrar ofrenda por categoría
- **ACTOR:** Tesorero de MNI
- **DESCRIPCIÓN:** Registrar ofrendas específicas con categorías predefinidas.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Dropdown con 7 categorías: ofrenda_general, caja_alabastro, accion_gracias, dip, oracion_ayuno, fem, otros
  2. Historial agrupado por categoría
  3. Totales por categoría visibles
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > MNI

#### R-031: Ver totales por categoría
- **ACTOR:** Tesorero de MNI
- **DESCRIPCIÓN:** Ver сумario de ofrendas por categoría.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-030
- **MÓDULO:** Ministerios > MNI

#### R-032: Generar reporte de ofrendas por período
- **ACTOR:** Tesorero de MNI, Admin
- **DESCRIPCIÓN:** Generar reporte de ofrendas filtrado por rango de fechas.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Selector de fechas
  2. Totales por categoría
  3. Exportar a PDF/CSV
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-030
- **MÓDULO:** Ministerios > MNI

---

### C.3 DNI - Funcionalidades Específicas (R-033 a R-067)

#### R-033: Registrar asistencia dominical
- **ACTOR:** Líder de DNI, Secretaria
- **DESCRIPCIÓN:** Registro de asistencia cada domingo con opciones de presente/ausente, visita, biblia.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Lista de niños del mes con checkboxes
  2. Campo para nombre de visita (si es_visita=true)
  3. Selector de clase
  4. Checkbox "trae_biblia"
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > DNI

#### R-034: Marcar niños como presentes o ausentes
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Marcar asistencia de cada niño.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-033
- **MÓDULO:** Ministerios > DNI

#### R-035: Registrar visitas
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Registrar visitas que no están en la lista regular.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Nombre de visita obligatorio
  2. Clase asignada
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-033
- **MÓDULO:** Ministerios > DNI

#### R-036: Marcar si el niño trae biblia
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Registrar si el niño trajo biblia.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-033
- **MÓDULO:** Ministerios > DNI

#### R-037: Asistencia acumulativa por persona
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Acumular asistencia por cada niño mostrando cuántos domingos asistió.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Tabla con nombre y cantidad de domingos presentes
  2. Filtro por clase
  3. Filtro por mes/año
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-033
- **MÓDULO:** Ministerios > DNI

#### R-038: Filtrar asistencia acumulativa por clase
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Filtrar reporte acumulativo por clase.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-037
- **MÓDULO:** Ministerios > DNI

#### R-039: Filtrar por mes y año
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Seleccionar período específico para reporte.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-037
- **MÓDULO:** Ministerios > DNI

#### R-040: Ver cantidad de domingos por niño
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver cuántos domingos asistió cada niño.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-037
- **MÓDULO:** Ministerios > DNI

#### R-041: Buscar por nombre de niño
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Búsqueda textual de niños en el sistema.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > DNI

#### R-042: Filtrar por clase
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Filtrar lista de niños por clase.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > DNI

#### R-043: Filtrar por rango de fechas
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Seleccionar período para filtrar asistencia.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > DNI

#### R-044: Filtrar por asistencia (presentes/ausentes)
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Filtrar por estado de asistencia.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > DNI

#### R-045: Registrar ofrendas por clase
- **ACTOR:** Tesorero de DNI
- **DESCRIPCIÓN:** Registrar ofrendas específicas por cada clase.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Selector de clase obligatorio
  2. Monto y fecha
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > DNI

#### R-046: Ver resumen de ofrendas por clase
- **ACTOR:** Tesorero de DNI
- **DESCRIPCIÓN:** Ver totales de ofrendas agrupados por clase.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-045
- **MÓDULO:** Ministerios > DNI

#### R-047: Integrar ofrendas a caja general de DNI
- **ACTOR:** Sistema
- **DESCRIPCIÓN:** Las ofrendas por clase se juntan a la caja general de DNI.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-045
- **MÓDULO:** Ministerios > DNI

#### R-048: Registrar niños con datos completos
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Registrar niños con: primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, fecha_nacimiento, estado_civil.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Formulario con todos los campos
  2. Edad calculada automáticamente
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > DNI

#### R-049: Editar información del niño
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Modificar datos del niño registrado.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-048
- **MÓDULO:** Ministerios > DNI

#### R-050: Ver perfil completo del niño
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver todos los datos del niño en un perfil.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-048
- **MÓDULO:** Ministerios > DNI

#### R-051: Ver lista de cumpleaños del mes
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Mostrar niños que cumplen años en el mes actual.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Lista ordenable por fecha
  2. Datos: nombre, fecha, edad
- **PRIORIDAD:** Should
- **DEPENDENCIAS:** R-048
- **MÓDULO:** Ministerios > DNI

#### R-052: Mostrar recordatorio en dashboard
- **ACTOR:** Sistema
- **DESCRIPCIÓN:** Widget en dashboard con cumpleaños del mes.
- **PRIORIDAD:** Should
- **DEPENDENCIAS:** R-051
- **MÓDULO:** Ministerios > DNI

#### R-053: Ver próxima fecha de cumpleaños
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver fecha del próximo cumpleaños por niño.
- **PRIORIDAD:** Should
- **DEPENDENCIAS:** R-051
- **MÓDULO:** Ministerios > DNI

#### R-054: Registrar cantidad de biblias por clase
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Registrar cuántas biblias tiene cada clase.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > DNI

#### R-055: Ver total de biblias por clase
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver cantidad de biblias por clase.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-054
- **MÓDULO:** Ministerios > DNI

#### R-056: Ver total de biblias de todas las clases
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver suma total de biblias de todas las clases.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-054
- **MÓDULO:** Ministerios > DNI

#### R-057: Registrar visita con nombre
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Registrar visita con nombre y clase asignada.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-035
- **MÓDULO:** Ministerios > DNI

#### R-058: Especificar clase de la visita
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Asignar la visita a una clase específica.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-057
- **MÓDULO:** Ministerios > DNI

#### R-059: Ver total de visitas por período
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver cantidad de visitas en un período.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-057
- **MÓDULO:** Ministerios > DNI

#### R-060: Ver visitas acumuladas en el mes
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver total de visitas del mes actual.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-057
- **MÓDULO:** Ministerios > DNI

#### R-061: Ver total de asistencia del domingo
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver cantidad de niños presentes ese domingo.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-033
- **MÓDULO:** Ministerios > DNI

#### R-062: Ver total de visitas del domingo
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver cantidad de visitas ese domingo.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-033
- **MÓDULO:** Ministerios > DNI

#### R-063: Ver total de ofrendas del domingo
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver monto total de ofrendas ese domingo.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-045
- **MÓDULO:** Ministerios > DNI

#### R-064: Ver total de biblias del domingo
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver cuántos niños trajeron biblia ese domingo.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-033
- **MÓDULO:** Ministerios > DNI

#### R-065: Definir clases por edades
- **ACTOR:** Admin, Líder de DNI
- **DESCRIPCIÓN:** Definir las clases por edades (pendiente).
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > DNI

#### R-066: Asignar niños a clase correspondiente
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Asignar cada niño a su clase según edad.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-065, R-048
- **MÓDULO:** Ministerios > DNI

#### R-067: Ver estadísticas por clase
- **ACTOR:** Líder de DNI
- **DESCRIPCIÓN:** Ver asistencia, visitas, ofrendas agrupadas por clase.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-065
- **MÓDULO:** Ministerios > DNI

---

### C.4 JNI - Funcionalidades Específicas (R-068 a R-070)

#### R-068: Registrar ofrendas semanales
- **ACTOR:** Tesorero de JNI
- **DESCRIPCIÓN:** Registro de ofrendas con granularidad semanal.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Ministerios > JNI

#### R-069: Ver ofrendas mensuales
- **ACTOR:** Tesorero de JNI
- **DESCRIPCIÓN:** Ver ofrendas consolidadas por mes.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-068
- **MÓDULO:** Ministerios > JNI

#### R-070: Ver totales por período
- **ACTOR:** Tesorero de JNI
- **DESCRIPCIÓN:** Ver сумма de ofrendas por semana/mes.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-068
- **MÓDULO:** Ministerios > JNI

---

### C.5 Ministerios Secundarios (R-071 a R-137)

#### MAM - Ministerio de Mujeres (R-071 a R-075)
- R-071: Planificación de actividades propias
- R-072: Caja propia (ingresos, egresos, fotos boletas)
- R-073: Eventos en calendario general
- R-074: Registro de ofrendas semanales y mensuales
- R-075: Actividades compartidas con otros ministerios

#### VID - Ministerio de Varones (R-076 a R-080)
- R-076: Planificación de actividades propias
- R-077: Caja propia
- R-078: Eventos en calendario general
- R-079: Registro de ofrendas semanales y mensuales
- R-080: Actividades compartidas

#### EXPLO - Exploradores del Rey (R-081 a R-086)
- R-081: Planificación de actividades propias
- R-082: Caja propia
- R-083: Eventos en calendario general
- R-084: Registro de ofrendas semanales y mensuales
- R-085: Actividades compartidas
- R-086: Apartado de lecciones (gestión de lecciones)

#### Danza (R-087 a R-091)
- R-087: Planificación de actividades propias
- R-088: Caja propia
- R-089: Eventos en calendario general
- R-090: Registro de ofrendas semanales y mensuales
- R-091: Actividades compartidas

#### Teatro (R-092 a R-096)
- R-092: Planificación de actividades propias
- R-093: Caja propia
- R-094: Eventos en calendario general
- R-095: Registro de ofrendas semanales y mensuales
- R-096: Actividades compartidas

#### Alabanza (R-097 a R-111)
- R-097: Planificación de actividades propias
- R-098: Caja propia
- R-099: Eventos en calendario general
- R-100: Registro de ofrendas semanales y mensuales
- R-101: Actividades compartidas
- R-102: Agregar canciones al banco
- R-103: Editar canciones
- R-104: Eliminar canciones
- R-105: Buscar por título
- R-106: Filtrar por categoría
- R-107: Generar programa automático dominical
- R-108: No repetir alabanzas del domingo anterior
- R-109: Ver programa generado
- R-110: Editar programa manualmente
- R-111: Ver historial de programas

#### Comunicaciones (R-112 a R-124)
- R-112: Planificación de actividades propias
- R-113: Caja propia
- R-114: Eventos en calendario general
- R-115: Registro de ofrendas semanales y mensuales
- R-116: Actividades compartidas
- R-117: Agregar ideas
- R-118: Marcar ideas como completadas
- R-119: Filtrar por prioridad
- R-120: Filtrar por estado
- R-121: Agregar recursos
- R-122: Descargar recursos
- R-123: Ver recursos por tipo
- R-124: Gestionar misión y visión

#### Compasión (R-125 a R-127)
- R-125: Planificación de actividades propias
- R-126: Caja propia
- R-127: Actividades compartidas

#### NazaKids (R-128 a R-132)
- R-128: Planificación de actividades propias
- R-129: Caja propia
- R-130: Eventos en calendario general
- R-131: Registro de ofrendas semanales y mensuales
- R-132: Actividades compartidas

#### Adulto Mayor (R-133 a R-137)
- R-133: Planificación de actividades propias
- R-134: Caja propia
- R-135: Eventos en calendario general
- R-136: Registro de ofrendas semanales y mensuales
- R-137: Actividades compartidas

---

### C.6 Finanzas/Tesorería (R-138 a R-156)

#### R-138: Ver saldos de cajas de todos los ministerios
- **ACTOR:** Tesorera, Admin, Pastor
- **DESCRIPCIÓN:** Dashboard de tesorería mostrando saldo actual de cada caja de ministerio.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Tarjetas con nombre de ministerio y saldo
  2. Actualización en tiempo real
  3. Ordenable por saldo
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-003 (cada ministerio)
- **MÓDULO:** Finanzas

#### R-139: Registrar traspaso de fondos a tesorería
- **ACTOR:** Tesorera
- **DESCRIPCIÓN:** Registrar el traspaso de fondos de un ministerio a tesorería.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-138
- **MÓDULO:** Finanzas

#### R-140: Ver historial de traspasos
- **ACTOR:** Tesorera, Admin
- **DESCRIPCIÓN:** Ver registro de todos los traspasos a tesorería.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-139
- **MÓDULO:** Finanzas

#### R-141: Ver flujo de caja mensual
- **ACTOR:** Tesorera
- **DESCRIPCIÓN:** Visualizar flujo de caja general con ingresos y egresos consolidados.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-138
- **MÓDULO:** Finanzas

#### R-142: Ver ingresos por categoría
- **ACTOR:** Tesorera
- **DESCRIPCIÓN:** Desglose de ingresos por fuente.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-141
- **MÓDULO:** Finanzas

#### R-143: Ver egresos por categoría
- **ACTOR:** Tesorera
- **DESCRIPCIÓN:** Desglose de egresos por destino.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-141
- **MÓDULO:** Finanzas

#### R-144: Ver saldo disponible
- **ACTOR:** Tesorera
- **DESCRIPCIÓN:** Mostrar saldo disponible calculado.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-141
- **MÓDULO:** Finanzas

#### R-145: Ver boletas de gastos de todos los ministerios
- **ACTOR:** Tesorera, Admin
- **DESCRIPCIÓN:** Ver imágenes de boletas de todos los ministerios.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Finanzas

#### R-146: Buscar boletas por fecha
- **ACTOR:** Tesorera
- **DESCRIPCIÓN:** Filtrar boletas por rango de fechas.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-145
- **MÓDULO:** Finanzas

#### R-147: Ver detalle de cada gasto
- **ACTOR:** Tesorera
- **DESCRIPCIÓN:** Ver información detallada del gasto con imagen de boleta.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-145
- **MÓDULO:** Finanzas

#### R-148: Configurar porcentajes de PRES
- **ACTOR:** Admin
- **DESCRIPCIÓN:** Panel de configuración para porcentajes configurables.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Campos numéricos con labels: PRES.DISTRITAL, PRES EDUCACIONAL, PRES.EVANGELISMO
  2. Valores por defecto: 10%, 3%, 2%
  3. Validación de rangos (0-100%)
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Finanzas

#### R-149: Configurar monto de jubilación
- **ACTOR:** Admin
- **DESCRIPCIÓN:** Configurar monto fijo de jubilación.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-148
- **MÓDULO:** Finanzas

#### R-150: Ver configuración actual
- **ACTOR:** Admin, Tesorera
- **DESCRIPCIÓN:** Ver valores actuales de configuración de finanzas.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-148
- **MÓDULO:** Finanzas

#### R-151: Generar informe mensual completo
- **ACTOR:** Tesorera, Pastor, Admin
- **DESCRIPCIÓN:** Generar informe mensual con estructura detallada.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Secciones: Saldo mes pasado, Ingresos, Egresos, Saldo fin de mes
  2. Cálculos automáticos basados en configuración
  3. Desglose por ministry
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-138, R-141, R-148
- **MÓDULO:** Finanzas

#### R-152: Ver desglose de ingresos
- **ACTOR:** Tesorera
- **DESCRIPCIÓN:** Ver estructura detallada de ingresos.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-151
- **MÓDULO:** Finanzas

#### R-153: Ver desglose de egresos
- **ACTOR:** Tesorera
- **DESCRIPCIÓN:** Ver estructura detallada de egresos.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-151
- **MÓDULO:** Finanzas

#### R-154: Ver saldo fin de mes
- **ACTOR:** Tesorera
- **DESCRIPCIÓN:** Ver cálculo de saldo fin de mes.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-151
- **MÓDULO:** Finanzas

#### R-155: Ver flujo de caja histórico
- **ACTOR:** Tesorera, Admin
- **DESCRIPCIÓN:** Ver flujo de caja de meses anteriores.
- **PRIORIDAD:** Should
- **DEPENDENCIAS:** R-141
- **MÓDULO:** Finanzas

#### R-156: Exportar informe a PDF
- **ACTOR:** Tesorera, Admin, Pastor
- **DESCRIPCIÓN:** Exportar informe mensual a formato PDF.
- **PRIORIDAD:** Should
- **DEPENDENCIAS:** R-151
- **MÓDULO:** Finanzas

---

### C.7 Calendario (R-157 a R-169)

#### R-157: Ver todos los eventos en calendario mensual
- **ACTOR:** Todos los usuarios
- **DESCRIPCIÓN:** Vista de calendario mensual con eventos de todos los ministerios.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-011, R-012
- **MÓDULO:** Calendario

#### R-158: Ver eventos pasados y futuros
- **ACTOR:** Todos los usuarios
- **DESCRIPCIÓN:** Visualizar eventos tanto pasados como futuros.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-157
- **MÓDULO:** Calendario

#### R-159: Navegar entre meses
- **ACTOR:** Todos los usuarios
- **DESCRIPCIÓN:** Botones para navegar meses anteriores/siguientes.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-157
- **MÓDULO:** Calendario

#### R-160: Detectar conflictos automáticamente
- **ACTOR:** Sistema
- **DESCRIPCIÓN:** Detectar si existe conflicto de horario y lugar.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Calendario

#### R-161: Mostrar mensaje de conflicto
- **ACTOR:** Sistema
- **DESCRIPCIÓN:** Mensaje claro indicando evento conflictivo.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-160
- **MÓDULO:** Calendario

#### R-162: Permitir forzar creación de evento
- **ACTOR:** Líder de Ministerio, Admin
- **DESCRIPCIÓN:** Guardar evento ignorando conflicto.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-160
- **MÓDULO:** Calendario

#### R-163: Ver detalles completos del evento
- **ACTOR:** Todos los usuarios
- **DESCRIPCIÓN:** Modal con toda la información del evento.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-157
- **MÓDULO:** Calendario

#### R-164: Ver ministerios involucrados
- **ACTOR:** Todos los usuarios
- **DESCRIPCIÓN:** Ver qué ministerios están en el evento compartido.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-157
- **MÓDULO:** Calendario

#### R-165: Ver quién creó el evento
- **ACTOR:** Todos los usuarios
- **DESCRIPCIÓN:** Mostrar nombre del usuario que creó el evento.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-157
- **MÓDULO:** Calendario

#### R-166: Filtrar por ministerio
- **ACTOR:** Todos los usuarios
- **DESCRIPCIÓN:** Mostrar solo eventos de un ministry seleccionado.
- **PRIORIDAD:** Should
- **DEPENDENCIAS:** R-157
- **MÓDULO:** Calendario

#### R-167: Filtrar por lugar
- **ACTOR:** Todos los usuarios
- **DESCRIPCIÓN:** Filtrar eventos por ubicación.
- **PRIORIDAD:** Should
- **DEPENDENCIAS:** R-157
- **MÓDULO:** Calendario

#### R-168: Filtrar por hora
- **ACTOR:** Todos los usuarios
- **DESCRIPCIÓN:** Filtrar eventos por rango de horas.
- **PRIORIDAD:** Should
- **DEPENDENCIAS:** R-157
- **MÓDULO:** Calendario

#### R-169: Buscar eventos por nombre
- **ACTOR:** Todos los usuarios
- **DESCRIPCIÓN:** Búsqueda textual por título de evento.
- **PRIORIDAD:** Should
- **DEPENDENCIAS:** R-157
- **MÓDULO:** Calendario

---

### C.8 Usuarios (R-170 a R-180)

#### R-170: Desvincular usuario al desactivar
- **ACTOR:** Admin
- **DESCRIPCIÓN:** Al desactivar, el usuario se desvincula de todos los ministerios.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Miembro records asociados se marcan como inactivos
  2. Datos básicos se mantienen
  3. Rol del sistema se mantiene
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Usuarios

#### R-171: Desactivar pierde acceso
- **ACTOR:** Sistema
- **DESCRIPCIÓN:** Usuario inactivo no puede iniciar sesión.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-170
- **MÓDULO:** Usuarios

#### R-172: Datos básicos se mantienen
- **ACTOR:** Sistema
- **DESCRIPCIÓN:** Al desactivar se mantienen username, email, nombre, rol.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-170
- **MÓDULO:** Usuarios

#### R-173: Limpiar vinculación al desactivar
- **ACTOR:** Sistema
- **DESCRIPCIÓN:** Si usuario ya vinculado es desactivado, se limpia todo.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-170
- **MÓDULO:** Usuarios

#### R-174: Listar todos los usuarios
- **ACTOR:** Admin
- **DESCRIPCIÓN:** Panel con tabla de usuarios del sistema.
- **CRITERIOS DE ACEPTACIÓN:**
  1. Columnas: Nombre, Username, Email, Rol, Estado, Ministerios
  2. Filtros por rol y estado
  3. Acciones: Editar, Desactivar
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Usuarios

#### R-175: Crear usuarios
- **ACTOR:** Admin
- **DESCRIPCIÓN:** Formulario para crear nuevo usuario.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** Ninguna
- **MÓDULO:** Usuarios

#### R-176: Editar usuarios
- **ACTOR:** Admin
- **DESCRIPCIÓN:** Modificar datos de usuario existente.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-174
- **MÓDULO:** Usuarios

#### R-177: Desactivar usuarios
- **ACTOR:** Admin
- **DESCRIPCIÓN:** Cambiar estado a inactivo.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-174
- **MÓDULO:** Usuarios

#### R-178: Asignar roles del sistema
- **ACTOR:** Admin
- **DESCRIPCIÓN:** Asignar rol: admin, pastora, secretaria, tesorera, lider_ministerio, concilio.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-175
- **MÓDULO:** Usuarios

#### R-179: Asignar ministerios a usuarios
- **ACTOR:** Admin
- **DESCRIPCIÓN:** Vincular usuario a uno o más ministerios.
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-175
- **MÓDULO:** Usuarios

#### R-180: Ver usuarios activos e inactivos
- **ACTOR:** Admin
- **DESCRIPCIÓN:** Badge visual de estado (verde/rojo).
- **PRIORIDAD:** Must
- **DEPENDENCIAS:** R-174
- **MÓDULO:** Usuarios

---

## D. Requerimientos No Funcionales

### D.1 Rendimiento (RNF-001 a RNF-005)

| ID | Descripción | Métrica | Meta |
|----|-------------|---------|------|
| RNF-001 | Tiempo de respuesta API consultas simples | < | 200ms |
| RNF-002 | Tiempo de respuesta API operaciones complejas | < | 1s |
| RNF-003 | Tiempo de carga inicial frontend | < | 3s en 4G |
| RNF-004 | Soporte usuarios concurrentes | ≥ | 50 usuarios |
| RNF-005 | Generación de informe mensual | < | 5s |

### D.2 Seguridad (RNF-006 a RNF-014)

| ID | Descripción |
|----|-------------|
| RNF-006 | JWT con HttpOnly cookies |
| RNF-007 | HTTPS obligatorio en producción |
| RNF-008 | Validación de inputs backend |
| RNF-009 | Validación de inputs frontend |
| RNF-010 | Rate limiting login (5 intentos/min) |
| RNF-011 | Contraseñas hasheadas (pbkdf2_sha256) |
| RNF-012 | Permisos por rol verificados en cada request |
| RNF-013 | Sanitización de uploads |
| RNF-014 | Logs de auditoría |

### D.3 Escalabilidad (RNF-015 a RNF-018)

| ID | Descripción | Meta |
|----|-------------|------|
| RNF-015 | Ministerios soportados | 13+ |
| RNF-016 | Miembros registrados | 5,000+ |
| RNF-017 | Eventos históricos | 10,000+ |
| RNF-018 | Diseño multi-iglesia (futuro) | Preparado |

### D.4 Disponibilidad (RNF-019 a RNF-024)

| ID | Descripción | Meta |
|----|-------------|------|
| RNF-019 | Uptime | > 99.5% |
| RNF-020 | Página error 404 personalizada |
| RNF-021 | Página error 500 personalizada |
| RNF-022 | Manejo graceful de errores |
| RNF-023 | Logs centralizados |
| RNF-024 | Notificaciones toast |

### D.5 Compatibilidad (RNF-025 a RNF-029)

| ID | Descripción |
|----|-------------|
| RNF-025 | Responsive: 320px - 1920px+ |
| RNF-026 | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |
| RNF-027 | BottomNav en mobile |
| RNF-028 | Sidebar en desktop |
| RNF-029 | PWA (futuro) |

### D.6 Persistencia (RNF-030 a RNF-035)

| ID | Descripción |
|----|-------------|
| RNF-030 | PostgreSQL en producción |
| RNF-031 | SQLite en desarrollo |
| RNF-032 | Backups automáticos diarios |
| RNF-033 | Retención mínima: 5 años |
| RNF-034 | Migraciones versionadas |
| RNF-035 | Índices en campos de búsqueda |

### D.7 UX/UI (RNF-036 a RNF-043)

| ID | Descripción |
|----|-------------|
| RNF-036 | Diseño mobile-first |
| RNF-037 | Skeleton loading states |
| RNF-038 | Toast notifications |
| RNF-039 | Confirmaciones de eliminación |
| RNF-040 | Estados vacíos informativos |
| RNF-041 | Feedback visual inmediato |
| RNF-042 | Animaciones suaves (300ms) |
| RNF-043 | Colores consistentes por ministry |

### D.8 Mantenibilidad (RNF-044 a RNF-050)

| ID | Descripción | Meta |
|----|-------------|------|
| RNF-044 | Cobertura tests backend | > 70% |
| RNF-045 | Cobertura tests frontend | > 50% |
| RNF-046 | Docstrings completos |
| RNF-047 | Code review obligatorio |
| RNF-048 | Conventional commits |
| RNF-049 | Documentación API (OpenAPI) |
| RNF-050 | Arquitectura selectors/services |

### D.9 Accesibilidad (RNF-051 a RNF-057)

| ID | Descripción | Meta |
|----|-------------|------|
| RNF-051 | Contraste WCAG 2.1 | AA |
| RNF-052 | Navegación por teclado | Completa |
| RNF-053 | Focus visible |
| RNF-054 | Labels ARIA |
| RNF-055 | Textos alternativos |
| RNF-056 | Jerarquía encabezados correcta |
| RNF-057 | Soporte lectores de pantalla |

---

## E. Matriz de Trazabilidad Requisitos-Funcionalidad

| Requisito | Módulo | Tipo | Prioridad | Dependencias | Estado |
|-----------|--------|------|-----------|--------------|--------|
| R-001 a R-005 | Ministerios/Caja | Funcional | Must | - | Parcial |
| R-006 a R-010 | Ministerios/Inventario | Funcional | Must | - | Parcial |
| R-011 a R-015 | Ministerios/Eventos | Funcional | Must | - | Parcial |
| R-016 a R-019 | Ministerios/Planificación | Funcional | Must | - | No |
| R-020 a R-022 | Ministerios/Ofrendas | Funcional | Must | - | Parcial |
| R-023 a R-025 | MNI/Enfoques | Funcional | Must | - | No |
| R-026 a R-029 | MNI/Programa | Funcional | Must | - | No |
| R-030 a R-032 | MNI/Ofrendas | Funcional | Must | - | No |
| R-033 a R-044 | DNI/Asistencia | Funcional | Must | - | Parcial |
| R-045 a R-047 | DNI/Ofrendas | Funcional | Must | - | No |
| R-048 a R-050 | DNI/Miembros | Funcional | Must | - | Funcional |
| R-051 a R-053 | DNI/Cumpleaños | Funcional | Should | - | No |
| R-054 a R-056 | DNI/Biblias | Funcional | Must | - | No |
| R-057 a R-060 | DNI/Visitas | Funcional | Must | - | No |
| R-061 a R-064 | DNI/Estadísticas | Funcional | Must | - | Parcial |
| R-065 a R-067 | DNI/Clases | Funcional | Must | - | No |
| R-068 a R-070 | JNI/Ofrendas | Funcional | Must | - | No |
| R-071 a R-137 | Ministerios Secundarios | Funcional | Must | - | Parcial |
| R-138 a R-140 | Finanzas/Traspaso | Funcional | Must | - | No |
| R-141 a R-144 | Finanzas/Flujo | Funcional | Must | - | No |
| R-145 a R-147 | Finanzas/Boletas | Funcional | Must | - | No |
| R-148 a R-150 | Finanzas/Config | Funcional | Must | - | No |
| R-151 a R-156 | Finanzas/Informe | Funcional | Must | - | No |
| R-157 a R-159 | Calendario/Vista | Funcional | Must | - | Funcional |
| R-160 a R-162 | Calendario/Conflictos | Funcional | Must | - | Funcional |
| R-163 a R-165 | Calendario/Detalles | Funcional | Must | - | Funcional |
| R-166 a R-169 | Calendario/Filtros | Funcional | Should | - | Funcional |
| R-170 a R-173 | Usuarios/Estados | Funcional | Must | - | Funcional |
| R-174 a R-180 | Usuarios/CRUD | Funcional | Must | - | Funcional |
| RNF-001 a RNF-057 | Global | No Funcional | Varía | - | Varía |

---

## F. Glosario

| Término | Definición |
|---------|------------|
| MNI | Ministerio de Nuevos Creyentes |
| DNI | Departamento de Niños |
| JNI | Juventud Nazarena Internacional |
| MAM | Ministerio de Mujeres |
| VID | Ministerio de Varones |
| EXPLO | Exploradores del Rey |
| FEM | Ofrenda especial de novembre (recogida y enviada) |
| COCE | Goce de los tres ministerios principales |
| PRES | Prescindentes (porcentajes del presupuesto) |
| DIP | Donación o aporte especial |
| ERS | Especificación de Requisitos de Software |
| RTM | Requirements Traceability Matrix |
| UAT | User Acceptance Testing |

---

## G. Historial de Versiones

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2026-05-22 | Sistema | Creación inicial |

---

Este documento constituye la especificación formal de requisitos (ERS) para el proyecto Gestor Iglesia versión 1.0.