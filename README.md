# Gestor Iglesia

Sistema de gestión integral para iglesias. Centraliza y digitaliza la administración de ministerios, tesorería, usuarios y calendario en una sola plataforma web, eliminando los procesos manuales y registros dispersos que generan desorden e ineficiencia.

---

## ¿Qué es?

Gestor Iglesia es una aplicación web diseñada para iglesias que necesitan mantener el orden y trazabilidad de sus operaciones internas. Permite que cada ministerio gestione su propia caja, inventario y actividades, mientras la tesorería central consolida todo el flujo financiero de la iglesia y genera los informes mensuales automáticamente.

---

## Módulos

### Ministerios

Administra los 13 ministerios de la iglesia. Cada ministerio tiene acceso a:

- **Caja propia** — registro de ingresos y egresos con soporte de comprobantes fotográficos
- **Inventario** — control de bienes del ministerio con categorías y estados
- **Eventos** — creación de eventos en el calendario general con detección de conflictos de horario y lugar
- **Planificación** — gestión de actividades con estado, responsable y presupuesto estimado
- **Ofrendas** — registro de ofrendas con opción de envío a tesorería central

Los ministerios principales (MNI, DNI, JNI) tienen funcionalidades adicionales:

| Ministerio | Funcionalidades extra |
|---|---|
| **MNI** (Nuevos Creyentes) | Enfoques mensuales bíblicos, programa del último domingo, categorías especiales de ofrenda (Alabastro, FEM, DIP, etc.) |
| **DNI** (Departamento de Niños) | Registro de asistencia dominical por clase, acumulación mensual, sistema de cumpleaños, control de biblias, estadísticas por domingo |
| **JNI** (Juventud Nazarena) | Ofrendas semanales y mensuales con seguimiento por período |

Lista de ministerios:

| Ministerio | Slug |
|---|---|
| Ministerio de Nuevos Creyentes | `mni` |
| Departamento de Niños | `dni` |
| Juventud Nazarena Internacional | `jni` |
| Ministerio de Mujeres | `mam` |
| Ministerio de Varones | `vid` |
| Exploradores del Rey | `explo` |
| Ministerio de Danza | `danza` |
| Ministerio de Teatro | `teatro` |
| Ministerio de Alabanza | `alabanza` |
| Ministerio de Comunicaciones | `comunicaciones` |
| Ministerio de Compasión | `compasion` |
| Ministerio de Niños NazaKids | `nazakids` |
| Ministerio de Adulto Mayor | `adulto-mayor` |

### Tesorería

Centraliza el flujo financiero de toda la iglesia:

- Consolidación de cajas de todos los ministerios
- Flujo de caja mensual con desglose por fuente (iglesia local, ministerios, DNI, JNI, MNI)
- Cálculo automático de porcentajes (PRES distrital, educacional, evangelismo)
- Visualización de boletas y comprobantes de gastos
- Informe mensual completo con ingresos, egresos y saldo fin de mes
- Historial de flujo de caja entre meses

### Calendario

Vista unificada de todos los eventos de los ministerios con filtros por ministerio, lugar y fecha. Detecta conflictos de horario/lugar automáticamente y permite forzar la creación cuando sea necesario.

### Usuarios

Sistema de roles con acceso granular por módulo:

| Rol | Acceso |
|---|---|
| `admin` | Todo |
| `pastora` | Todos los ministerios y finanzas |
| `tesorera` | Caja, ofrendas y reportes |
| `secretaria` | Miembros, asistencia y eventos |
| `lider_ministerio` | Su propio ministerio |
| `concilio` | Solo lectura |

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Django REST Framework (Python) |
| Frontend | Astro (islands architecture) |
| Base de datos | PostgreSQL (SQLite en desarrollo) |
| Autenticación | JWT con cookies HttpOnly |

### Arquitectura

**Backend** — Patrón selectors/services: los `selectors` encapsulan consultas complejas a la base de datos y los `services` contienen la lógica de negocio. Las vistas se mantienen delgadas usando ViewSets y serializers de DRF.

**Frontend** — Astro con islands para componentes interactivos. Cada página es estática por defecto; solo las partes que necesitan reactividad se hidratan como islands. El estado de la UI se gestiona con nano-stores (`@nanostores/vue` o equivalente).

```
backend/
  apps/
    ministerios/    # Modelo central: usuarios, ministerios, caja, inventario, eventos
    tesoreria/      # Flujo de caja consolidado e informes mensuales

frontend/
  src/
    pages/          # Rutas estáticas de Astro
    islands/        # Componentes interactivos (ministry, treasury, users)
    stores/         # Estado compartido entre islands
    components/     # Componentes UI reutilizables
```

---

## Estado del proyecto

En desarrollo activo desde octubre de 2025.

Fases completadas:
- Ministerios base (caja, inventario, eventos)
- Funcionalidades específicas de DNI y MNI
- Tesorería e informes mensuales
- Sistema de usuarios y roles
- Subida de comprobantes en movimientos de caja
- Sistema de aprobación y auditoría

En desarrollo:
- Módulo de Alabanza (banco de canciones, programa dominical)
- Módulo de Comunicaciones (checklist de ideas, recursos gráficos)
- Secretaría (fase posterior)
