import React, { useEffect, useState, useCallback } from 'react';
import { ministeriosStore } from '@/stores/ministerios';
import type { Ministerio, Miembro, MovimientoCaja, Inventario, Ofrenda, Asistencia } from '@/stores/ministerios';
import { authStore } from '@/stores/auth';
import { api } from '@/utils/api';
import MinistryIcon, { MINISTRY_COLORS } from '@/components/MinistryIcon';
import { Button } from '@/components/ui';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import Input, { Select, Textarea } from '@/components/ui/Input';
import Badge from '@/components/ui/Badge';
import StatsCard from '@/components/ui/StatsCard';

const TAB_LABELS: Record<string, string> = {
  dashboard: 'Dashboard',
  miembros: 'Miembros',
  caja: 'Caja',
  inventario: 'Inventario',
  ofrendas: 'Ofrendas',
  eventos: 'Eventos',
  asistencia: 'Asistencia',
  lecciones: 'Lecciones',
  canciones: 'Canciones',
  programas: 'Programas',
  recursos: 'Recursos',
  ideas: 'Ideas',
  planificacion: 'Planificación',
};

interface Props {
  slug: string;
  tabs: string[];
}

export default function MinistryPage({ slug, tabs }: Props) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [ministry, setMinistry] = useState<Ministerio | null>(null);
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [formData, setFormData] = useState<Record<string, any>>({});

  const colors = MINISTRY_COLORS[slug] || MINISTRY_COLORS.mni;

  useEffect(() => {
    setMounted(true);
  }, []);

  const loadTab = useCallback(async (tab: string) => {
    if (!mounted) return;
    try {
      switch (tab) {
        case 'dashboard': {
          const [ministro, dash] = await Promise.all([
            api.get<Ministerio>(`/ministerios/${slug}/`),
            api.get<any>(`/ministerios/${slug}/dashboard/`),
          ]);
          setMinistry(ministro);
          setDashboard(dash);
          break;
        }
        default:
          await ministeriosStore[`fetch${tab.charAt(0).toUpperCase() + tab.slice(1)}` as keyof typeof ministeriosStore]?.(slug);
      }
    } catch (e) {
      console.error(`Error loading tab ${tab}:`, e);
    }
  }, [slug]);

  useEffect(() => {
    if (!mounted) return;
    const check = async () => {
      await authStore.checkAuth();
      const state = authStore.getState();
      if (!state.isAuthenticated) {
        window.location.href = '/login';
        return;
      }
      setLoading(false);
      await loadTab('dashboard');
    };
    check();
  }, [mounted, loadTab]);

  const switchTab = (tab: string) => {
    setActiveTab(tab);
    loadTab(tab);
  };

  const storeState = ministeriosStore.getState();

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-40 bg-gray-200 rounded-lg" />
        <div className="h-10 bg-gray-200 rounded w-1/3" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <div key={i} className="h-32 bg-gray-100 rounded-lg" />)}
        </div>
      </div>
    );
  }

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('es-PY', { style: 'currency', currency: 'PYG', minimumFractionDigits: 0 }).format(v);

  const formatDate = (d: string) => new Date(d).toLocaleDateString('es-PY');

  const renderDashboard = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatsCard label="Miembros" value={dashboard?.miembros_count ?? 0} color="primary"
          icon={<MinistryIcon name="users" className="w-5 h-5" />} />
        <StatsCard label="Saldo Caja" value={formatCurrency(dashboard?.saldo_caja ?? 0)} color="success"
          icon={<span className="text-lg">₲</span>} />
        <StatsCard label="Ofrendas Mes" value={formatCurrency(dashboard?.ofertas_mes ?? 0)} color="warning"
          icon={<MinistryIcon name="heart" className="w-5 h-5" />} />
        <StatsCard label="Eventos" value={dashboard?.eventos_proximos?.length ?? 0} color="accent"
          icon={<MinistryIcon name="users" className="w-5 h-5" />} />
      </div>
    </div>
  );

  const renderTab = () => {
    switch (activeTab) {
      case 'dashboard': return renderDashboard();
      case 'miembros': return <MembersTab slug={slug} store={storeState} formatDate={formatDate} />;
      case 'caja': return <FinanceTab slug={slug} store={storeState} formatCurrency={formatCurrency} formatDate={formatDate} />;
      case 'inventario': return <InventoryTab slug={slug} store={storeState} />;
      case 'ofrendas': return <OfferingTab slug={slug} store={storeState} formatCurrency={formatCurrency} />;
      case 'eventos': return <EventsTab slug={slug} store={storeState} formatDate={formatDate} />;
      case 'asistencia': return <AttendanceTab slug={slug} store={storeState} />;
      case 'lecciones': return <LessonsTab slug={slug} store={storeState} />;
      case 'canciones': return <SongsTab slug={slug} store={storeState} />;
      case 'programas': return <ProgramsTab slug={slug} store={storeState} formatDate={formatDate} />;
      case 'recursos': return <ResourcesTab slug={slug} store={storeState} />;
      case 'ideas': return <IdeasTab slug={slug} store={storeState} />;
      case 'planificacion': return <PlansTab slug={slug} store={storeState} formatDate={formatDate} />;
      default: return <p className="text-gray-500">Selecciona una pestaña</p>;
    }
  };

  return (
    <div>
      {/* Hero */}
      <div
        className="relative rounded-xl overflow-hidden mb-6 min-h-[160px] flex items-end"
        style={{ background: colors.gradient }}
      >
        <div className="absolute inset-0 opacity-20"
          style={{ backgroundImage: `repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.1) 10px, rgba(255,255,255,0.1) 20px)` }}
        />
        <div className="relative p-6 flex items-center gap-4">
          <div className="w-14 h-14 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center">
            <MinistryIcon name={ministry?.icono || 'church'} className="w-8 h-8 text-white" />
          </div>
          <div className="text-white">
            <h1 className="text-2xl font-bold">{ministry?.nombre || slug.toUpperCase()}</h1>
            <p className="text-sm text-white/80">{ministry?.descripcion || ''}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-0 overflow-x-auto border-b border-gray-200 mb-6 -mx-2 px-2">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => switchTab(tab)}
            className={`inline-flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap
              ${activeTab === tab ? 'border-accent text-accent' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            {TAB_LABELS[tab] || tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div>{renderTab()}</div>
    </div>
  );
}

/* ─── Tab Components ─── */

function MembersTab({ slug, store, formatDate }: { slug: string; store: any; formatDate: (d: string) => string }) {
  const miembros = store.miembros || [];
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ primer_nombre: '', primer_apellido: '', telefono: '', email: '', clase: '', rol_en_ministerio: 'miembro' });

  const handleAdd = async () => {
    await ministeriosStore.addMiembro(slug, form);
    setShowForm(false);
    setForm({ primer_nombre: '', primer_apellido: '', telefono: '', email: '', clase: '', rol_en_ministerio: 'miembro' });
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold text-gray-900">Miembros ({miembros.length})</h3>
        <Button size="sm" onClick={() => setShowForm(!showForm)}>+ Agregar</Button>
      </div>

      {showForm && (
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input label="Primer Nombre" value={form.primer_nombre} onChange={e => setForm({ ...form, primer_nombre: e.target.value })} />
            <Input label="Primer Apellido" value={form.primer_apellido} onChange={e => setForm({ ...form, primer_apellido: e.target.value })} />
            <Input label="Teléfono" value={form.telefono} onChange={e => setForm({ ...form, telefono: e.target.value })} />
            <Input label="Email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
            <Select label="Clase" value={form.clase} onChange={e => setForm({ ...form, clase: e.target.value })}>
              <option value="">Sin clase</option>
              <option value="ninos">Niños (0-12)</option>
              <option value="jovenes">Jóvenes (13-17)</option>
              <option value="adultos_jovenes">Adultos Jóvenes (18-35)</option>
              <option value="adultos">Adultos (36-60)</option>
              <option value="adultos_mayores">Adultos Mayores (60+)</option>
            </Select>
            <Select label="Rol" value={form.rol_en_ministerio} onChange={e => setForm({ ...form, rol_en_ministerio: e.target.value })}>
              <option value="miembro">Miembro</option>
              <option value="lider">Líder</option>
              <option value="sublider">Sublíder</option>
              <option value="tesorero">Tesorero</option>
              <option value="secretario">Secretario</option>
            </Select>
          </div>
          <div className="flex gap-2 mt-4">
            <Button onClick={handleAdd}>Guardar</Button>
            <Button variant="ghost" onClick={() => setShowForm(false)}>Cancelar</Button>
          </div>
        </Card>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Nombre</th>
              <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Rol</th>
              <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Clase</th>
              <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Teléfono</th>
            </tr>
          </thead>
          <tbody>
            {miembros.map((m: Miembro) => (
              <tr key={m.id} className="border-b border-gray-100">
                <td className="px-4 py-2">{m.nombre_completo}</td>
                <td className="px-4 py-2 capitalize">{m.rol_en_ministerio}</td>
                <td className="px-4 py-2 capitalize">{m.clase?.replace('_', ' ') || '-'}</td>
                <td className="px-4 py-2">{m.telefono || '-'}</td>
              </tr>
            ))}
            {miembros.length === 0 && <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">Sin miembros</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function FinanceTab({ slug, store, formatCurrency, formatDate }: any) {
  const caja = store.caja;
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ tipo: 'ingreso', monto: '', descripcion: '' });

  const handleAdd = async () => {
    await ministeriosStore.addMovimiento(slug, { ...form, monto: parseFloat(form.monto) });
    setShowForm(false);
    setForm({ tipo: 'ingreso', monto: '', descripcion: '' });
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <p className="text-sm text-gray-500">Saldo actual</p>
          <p className="text-2xl font-bold text-gray-900">{formatCurrency(caja?.saldo_calculado ?? 0)}</p>
        </div>
        <Button size="sm" onClick={() => setShowForm(!showForm)}>+ Movimiento</Button>
      </div>

      {showForm && (
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Select label="Tipo" value={form.tipo} onChange={e => setForm({ ...form, tipo: e.target.value })}>
              <option value="ingreso">Ingreso</option>
              <option value="egreso">Egreso</option>
            </Select>
            <Input label="Monto" type="number" value={form.monto} onChange={e => setForm({ ...form, monto: e.target.value })} />
            <Input label="Descripción" value={form.descripcion} onChange={e => setForm({ ...form, descripcion: e.target.value })} />
          </div>
          <div className="flex gap-2 mt-4">
            <Button onClick={handleAdd}>Guardar</Button>
            <Button variant="ghost" onClick={() => setShowForm(false)}>Cancelar</Button>
          </div>
        </Card>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Tipo</th>
              <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Monto</th>
              <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase w-6/12">Descripción</th>
              <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Fecha</th>
            </tr>
          </thead>
          <tbody>
            {(caja?.movimientos || []).map((m: MovimientoCaja) => (
              <tr key={m.id} className="border-b border-gray-100">
                <td className="px-4 py-2">
                  <Badge variant={m.tipo === 'ingreso' ? 'success' : 'danger'}>{m.tipo}</Badge>
                </td>
                <td className="px-4 py-2 font-medium">{formatCurrency(m.monto)}</td>
                <td className="px-4 py-2 text-gray-600 w-6/12">{m.descripcion}</td>
                <td className="px-4 py-2 text-gray-500 text-xs">{formatDate(m.fecha)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function InventoryTab({ slug, store }: any) {
  const inventario = store.inventario || [];
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ nombre: '', categoria: 'otro', cantidad: '1', estado: 'bueno' });

  const handleAdd = async () => {
    await ministeriosStore.addInventario(slug, { ...form, cantidad: parseInt(form.cantidad) });
    setShowForm(false);
    setForm({ nombre: '', categoria: 'otro', cantidad: '1', estado: 'bueno' });
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <h3 className="font-semibold text-gray-900">Inventario ({inventario.length})</h3>
        <Button size="sm" onClick={() => setShowForm(!showForm)}>+ Item</Button>
      </div>
      {showForm && (
        <Card>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Input label="Nombre" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} />
            <Select label="Categoría" value={form.categoria} onChange={e => setForm({ ...form, categoria: e.target.value })}>
              <option value="muebles">Muebles</option><option value="electronicos">Electrónicos</option>
              <option value="decoracion">Decoración</option><option value="utensilios">Utensilios</option>
              <option value="musica">Música</option><option value="otro">Otro</option>
            </Select>
            <Input label="Cantidad" type="number" value={form.cantidad} onChange={e => setForm({ ...form, cantidad: e.target.value })} />
            <Select label="Estado" value={form.estado} onChange={e => setForm({ ...form, estado: e.target.value })}>
              <option value="nuevo">Nuevo</option><option value="bueno">Bueno</option>
              <option value="regular">Regular</option><option value="mal_estado">Mal Estado</option>
            </Select>
          </div>
          <div className="flex gap-2 mt-4"><Button onClick={handleAdd}>Guardar</Button><Button variant="ghost" onClick={() => setShowForm(false)}>Cancelar</Button></div>
        </Card>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-gray-200">
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Nombre</th>
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Categoría</th>
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Cantidad</th>
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Estado</th>
          </tr></thead>
          <tbody>
            {inventario.map((item: Inventario) => (
              <tr key={item.id} className="border-b border-gray-100">
                <td className="px-4 py-2">{item.nombre}</td>
                <td className="px-4 py-2 capitalize">{item.categoria}</td>
                <td className="px-4 py-2">{item.cantidad}</td>
                <td className="px-4 py-2"><Badge variant={item.estado === 'bueno' || item.estado === 'nuevo' ? 'success' : 'warning'}>{item.estado}</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function OfferingTab({ slug, store, formatCurrency }: any) {
  const ofrendas = store.ofrendas || [];
  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-gray-200">
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Fecha</th>
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Monto</th>
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Clase</th>
          </tr></thead>
          <tbody>
            {ofrendas.map((o: Ofrenda) => (
              <tr key={o.id} className="border-b border-gray-100">
                <td className="px-4 py-2">{o.fecha}</td>
                <td className="px-4 py-2 font-medium">{formatCurrency(o.monto)}</td>
                <td className="px-4 py-2 capitalize">{o.clase || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function EventsTab({ slug, store, formatDate }: any) {
  const eventos = store.eventos || [];
  return (
    <div className="space-y-4">
      <div className="grid gap-3">
        {eventos.map((ev: any) => (
          <Card key={ev.id}>
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-medium text-gray-900">{ev.titulo}</h4>
                <p className="text-sm text-gray-500 mt-1">{formatDate(ev.fecha_inicio)}</p>
              </div>
              <Badge variant={ev.tipo === 'compartido' ? 'info' : 'default'}>{ev.tipo}</Badge>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function AttendanceTab({ slug, store }: any) {
  const asistencias = store.asistencias || [];
  return (
    <div className="space-y-4">
      <Button size="sm" onClick={() => {}}>Registrar Asistencia</Button>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-gray-200">
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Nombre</th>
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Fecha</th>
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Presente</th>
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Clase</th>
          </tr></thead>
          <tbody>
            {asistencias.map((a: Asistencia) => (
              <tr key={a.id} className="border-b border-gray-100">
                <td className="px-4 py-2">{a.miembro_nombre || a.nombre_visita || '(visita)'}</td>
                <td className="px-4 py-2">{a.fecha}</td>
                <td className="px-4 py-2"><Badge variant={a.presente ? 'success' : 'danger'}>{a.presente ? 'Sí' : 'No'}</Badge></td>
                <td className="px-4 py-2 capitalize">{a.clase || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function LessonsTab({ slug, store }: any) {
  const lecciones = store.lecciones || [];
  return (
    <div className="space-y-4">
      {lecciones.map((lec: any) => (
        <Card key={lec.id}>
          <h4 className="font-medium text-gray-900">{lec.titulo}</h4>
          <p className="text-sm text-gray-500 mt-1">{lec.descripcion}</p>
        </Card>
      ))}
    </div>
  );
}

function SongsTab({ slug, store }: any) {
  const canciones = store.canciones || [];
  return (
    <div className="space-y-4">
      <Button size="sm" onClick={() => ministeriosStore.fetchCanciones(slug)}>Refrescar</Button>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-gray-200">
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Título</th>
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Artista</th>
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Categoría</th>
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Tono</th>
          </tr></thead>
          <tbody>
            {canciones.map((c: any) => (
              <tr key={c.id} className="border-b border-gray-100">
                <td className="px-4 py-2">{c.titulo}</td>
                <td className="px-4 py-2">{c.artista || '-'}</td>
                <td className="px-4 py-2 capitalize">{c.categoria}</td>
                <td className="px-4 py-2">{c.tono || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ProgramsTab({ slug, store, formatDate }: any) {
  const programas = store.programas || [];
  return (
    <div className="space-y-4">
      {programas.map((p: any) => (
        <Card key={p.id}>
          <div className="flex justify-between items-start">
            <h4 className="font-medium text-gray-900">Programa - {formatDate(p.fecha)}</h4>
            <span className="text-sm text-gray-500">{p.alabanzas?.length || 0} canciones</span>
          </div>
        </Card>
      ))}
    </div>
  );
}

function ResourcesTab({ slug, store }: any) {
  const recursos = store.recursos || [];
  return (
    <div className="space-y-4">
      {recursos.map((r: any) => (
        <Card key={r.id}>
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-medium text-gray-900">{r.titulo}</h4>
              <p className="text-sm text-gray-500 mt-1">{r.descripcion}</p>
            </div>
            <Badge variant="info">{r.tipo}</Badge>
          </div>
        </Card>
      ))}
    </div>
  );
}

function IdeasTab({ slug, store }: any) {
  const ideas = store.ideas || [];
  return (
    <div className="space-y-4">
      {ideas.map((i: any) => (
        <Card key={i.id}>
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">{i.titulo}</h4>
              <p className="text-sm text-gray-500">{i.descripcion}</p>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant={i.completada ? 'success' : 'warning'}>{i.completada ? 'Completada' : 'Pendiente'}</Badge>
              <button onClick={() => ministeriosStore.toggleIdeaCompletada(slug, i.id)} className="text-sm text-accent hover:underline">
                {i.completada ? 'Reabrir' : 'Completar'}
              </button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}

function PlansTab({ slug, store, formatDate }: any) {
  const planificaciones = store.planificaciones || [];
  return (
    <div className="space-y-4">
      <Button size="sm" onClick={() => ministeriosStore.fetchPlanificaciones?.(slug)}>Refrescar</Button>
      <div className="grid gap-3">
        {planificaciones.map((p: any) => (
          <Card key={p.id}>
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-medium text-gray-900">{p.titulo}</h4>
                <p className="text-sm text-gray-500 mt-1">{formatDate(p.fecha_planificada)}</p>
              </div>
              <Badge variant={p.estado === 'completada' ? 'success' : p.estado === 'en_proceso' ? 'info' : 'warning'}>
                {p.estado?.replace('_', ' ')}
              </Badge>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
