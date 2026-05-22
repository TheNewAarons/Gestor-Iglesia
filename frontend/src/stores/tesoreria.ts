import { api } from '../utils/api';

export interface SaldoMinistry {
  ministry_slug: string;
  ministry_nombre: string;
  ministry_color: string;
  saldo: number;
  total_ingresos: number;
  total_egresos: number;
}

export interface ConfiguracionFinanzas {
  id: number;
  pres_distrital_pct: string;
  pres_educacional_pct: string;
  pres_evangelismo_pct: string;
  jubilacion_monto: string;
  actualizado_por: number | null;
  updated_at: string;
}

export interface FlujoCaja {
  mes: number;
  anio: number;
  total_ofrendas: number;
  total_ingresos_caja: number;
  total_egresos: number;
  saldo_neto: number;
  saldos_ministerios: SaldoMinistry[];
}

export interface BoletaEgreso {
  id: number;
  tipo: string;
  monto: number;
  descripcion: string;
  fecha: string;
  imagen: string | null;
  caja: number;
  ministry_nombre: string;
  ministry_color: string;
  registrado_por_nombre: string;
  enviado_tesoreria: boolean;
}

export interface InformeMensual {
  id: number;
  anio: number;
  mes: number;
  datos: any;
  generado_por: number | null;
  generado_por_nombre: string | null;
  fecha_generacion: string;
  updated_at: string;
}

type Listener = () => void;

class TesoreriaStore {
  private listeners: Set<Listener> = new Set();

  private state = {
    saldos: [] as SaldoMinistry[],
    config: null as ConfiguracionFinanzas | null,
    flujo: null as FlujoCaja | null,
    boletas: { count: 0, next: null as string | null, previous: null as string | null, results: [] as BoletaEgreso[] },
    traspasos: { count: 0, next: null as string | null, previous: null as string | null, results: [] as BoletaEgreso[] },
    informe: null as InformeMensual | null,
    informes: [] as InformeMensual[],
    loading: false,
    error: null as string | null,
    successMessage: null as string | null,
  };

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    this.listeners.forEach((fn) => fn());
  }

  public getState() {
    return this.state;
  }

  private setState(partial: Partial<typeof this.state>) {
    this.state = { ...this.state, ...partial };
    this.notify();
  }

  public clearMessages(): void {
    this.setState({ error: null, successMessage: null });
  }

  async fetchDashboard(): Promise<void> {
    this.setState({ loading: true, error: null });
    try {
      const data = await api.get<{ saldos: SaldoMinistry[]; configuracion: ConfiguracionFinanzas }>('/tesoreria/dashboard/');
      this.setState({ saldos: data.saldos, config: data.configuracion, loading: false });
    } catch (err: any) {
      this.setState({ loading: false, error: err.message });
    }
  }

  async fetchFlujoCaja(mes?: number, anio?: number): Promise<void> {
    this.setState({ loading: true, error: null });
    const now = new Date();
    const params = new URLSearchParams();
    if (mes) params.set('mes', String(mes));
    if (anio) params.set('anio', String(anio));
    const qs = params.toString();
    try {
      const data = await api.get<FlujoCaja>(`/tesoreria/flujo-caja/${qs ? '?' + qs : ''}`);
      this.setState({ flujo: data, loading: false });
    } catch (err: any) {
      this.setState({ loading: false, error: err.message });
    }
  }

  async fetchBoletas(fechaInicio?: string, fechaFin?: string): Promise<void> {
    this.setState({ loading: true, error: null });
    const params = new URLSearchParams();
    if (fechaInicio) params.set('fecha_inicio', fechaInicio);
    if (fechaFin) params.set('fecha_fin', fechaFin);
    const qs = params.toString();
    try {
      const data = await api.get<any>(`/tesoreria/boletas/${qs ? '?' + qs : ''}`);
      this.setState({ boletas: data, loading: false });
    } catch (err: any) {
      this.setState({ loading: false, error: err.message });
    }
  }

  async fetchTraspasos(): Promise<void> {
    this.setState({ loading: true, error: null });
    try {
      const data = await api.get<any>('/tesoreria/traspasos/');
      this.setState({ traspasos: data, loading: false });
    } catch (err: any) {
      this.setState({ loading: false, error: err.message });
    }
  }

  async fetchInforme(mes?: number, anio?: number, force?: boolean): Promise<void> {
    this.setState({ loading: true, error: null });
    const params = new URLSearchParams();
    if (mes) params.set('mes', String(mes));
    if (anio) params.set('anio', String(anio));
    if (force) params.set('force', 'true');
    const qs = params.toString();
    try {
      const data = await api.get<InformeMensual>(`/tesoreria/informe/${qs ? '?' + qs : ''}`);
      this.setState({ informe: data, loading: false });
    } catch (err: any) {
      this.setState({ loading: false, error: err.message });
    }
  }

  async fetchInformes(): Promise<void> {
    this.setState({ loading: true, error: null });
    try {
      const data = await api.get<InformeMensual[]>('/tesoreria/informes/');
      this.setState({ informes: data, loading: false });
    } catch (err: any) {
      this.setState({ loading: false, error: err.message });
    }
  }

  async updateConfig(data: Partial<ConfiguracionFinanzas>): Promise<void> {
    this.setState({ loading: true, error: null });
    try {
      const updated = await api.put<ConfiguracionFinanzas>('/tesoreria/configuracion/', data);
      this.setState({ config: updated, loading: false, successMessage: 'Configuración actualizada correctamente' });
    } catch (err: any) {
      this.setState({ loading: false, error: err.message });
    }
  }

  async exportarInforme(mes?: number, anio?: number): Promise<void> {
    const params = new URLSearchParams();
    if (mes) params.set('mes', String(mes));
    if (anio) params.set('anio', String(anio));
    const qs = params.toString();
    const API_BASE = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    const url = `${API_BASE}/tesoreria/exportar-informe/${qs ? '?' + qs : ''}`;
    window.open(url, '_blank');
  }
}

export const tesoreriaStore = new TesoreriaStore();
