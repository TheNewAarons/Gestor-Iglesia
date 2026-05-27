import { api } from '../utils/api';

export interface ActaReunion {
  id: number;
  titulo: string;
  tipo: string;
  tipo_display: string;
  fecha_reunion: string;
  hora_reunion: string | null;
  lugar: string;
  presidida_por: string;
  asistentes: Array<{ nombre: string; rol?: string }>;
  orden_del_dia: Array<{ punto: string; descripcion?: string }>;
  acuerdos: Array<{ numero: number; descripcion: string; responsable?: string }>;
  observaciones: string;
  estado: string;
  estado_display: string;
  aprobada_en: string | null;
  creado_por_nombre: string | null;
  aprobada_por_nombre: string | null;
  created_at: string;
  updated_at: string;
}

export interface SolicitudTramite {
  id: number;
  tipo: string;
  tipo_display: string;
  solicitante_nombre: string;
  solicitante_miembro: number | null;
  miembro_nombre: string | null;
  ministerio: number | null;
  ministerio_nombre: string | null;
  descripcion: string;
  datos_adicionales: Record<string, unknown>;
  estado: string;
  estado_display: string;
  prioridad: string;
  prioridad_display: string;
  fecha_solicitud: string;
  fecha_resolucion: string | null;
  resolucion_notas: string;
  documento_generado: string | null;
  created_at: string;
}

export interface VisitaIglesia {
  id: number;
  nombre: string;
  telefono: string;
  email: string;
  direccion: string;
  fecha_primera_visita: string;
  cantidad_visitas: number;
  ultima_visita: string | null;
  ministerio_interes: number | null;
  ministerio_nombre: string | null;
  seguimiento: string;
  seguimiento_display: string;
  responsable_seguimiento: number | null;
  responsable_nombre: string | null;
  notas: string;
  convertido_miembro: boolean;
  miembro_vinculado: number | null;
  miembro_vinculado_nombre: string | null;
  activo: boolean;
}

export interface ComunicadoInterno {
  id: number;
  titulo: string;
  contenido: string;
  destinatarios: string;
  destinatarios_display: string;
  ministerios_destino: number[];
  ministerios_destino_nombres: string[];
  roles_destino: string[];
  archivo_adjunto: string | null;
  requiere_confirmacion: boolean;
  publicado: boolean;
  fecha_publicacion: string | null;
  fecha_vencimiento: string | null;
  creado_por_nombre: string | null;
  total_lecturas: number;
  created_at: string;
}

export interface HistorialEstado {
  id: number;
  miembro: number;
  miembro_nombre: string | null;
  evento: string;
  evento_display: string;
  fecha_evento: string;
  descripcion: string;
  iglesia_origen: string;
  iglesia_destino: string;
  documentado_por_nombre: string | null;
  documento_adjunto: string | null;
  created_at: string;
}

export interface MensajeWhatsApp {
  id: number;
  numero: number;
  texto: string;
  imagen: string | null;
  activo: boolean;
}

export interface ConfiguracionWhatsApp {
  id: number;
  grupo_jid: string;
  hora_envio: string;
  activo: boolean;
  rotacion_index: number;
}

export interface EnvioLog {
  id: number;
  mensaje: number | null;
  mensaje_numero: number | null;
  texto_enviado: string;
  grupo_jid: string;
  estado: string;
  estado_display: string;
  error_detalle: string;
  enviado_en: string;
}

export interface EstadisticasResumen {
  total_activos: number;
  total_inactivos: number;
  nuevos_ultimo_mes: number;
  por_clase: Array<{ clase: string; cantidad: number }>;
  por_ministerio: Array<{ nombre: string; miembros_activos: number }>;
  actas_mes: number;
  actas_pendientes: number;
  solicitudes_pendientes: number;
  visitantes_sin_seguimiento: number;
  comunicados_publicados: number;
}

interface SecretariaState {
  actas: ActaReunion[];
  solicitudes: SolicitudTramite[];
  visitas: VisitaIglesia[];
  comunicados: ComunicadoInterno[];
  historial: HistorialEstado[];
  estadisticas: EstadisticasResumen | null;
  waMensajes: MensajeWhatsApp[];
  waConfig: ConfiguracionWhatsApp | null;
  waHistorial: EnvioLog[];
  waStatus: string;
  waQr: string | null;
  isLoading: boolean;
  error: string | null;
}

class SecretariaStore {
  private state: SecretariaState = {
    actas: [],
    solicitudes: [],
    visitas: [],
    comunicados: [],
    historial: [],
    estadisticas: null,
    waMensajes: [],
    waConfig: null,
    waHistorial: [],
    waStatus: 'disconnected',
    waQr: null,
    isLoading: false,
    error: null,
  };

  private listeners: Set<(state: SecretariaState) => void> = new Set();

  getState() {
    return this.state;
  }

  subscribe(listener: (state: SecretariaState) => void) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    this.listeners.forEach((l) => l(this.state));
  }

  private setState(partial: Partial<SecretariaState>) {
    this.state = { ...this.state, ...partial };
    this.notify();
  }

  // ─── ESTADÍSTICAS ──────────────────────────────────────────────────────────

  async fetchEstadisticas() {
    this.setState({ isLoading: true, error: null });
    try {
      const data = await api.get<EstadisticasResumen>('/secretaria/estadisticas/resumen/');
      this.setState({ estadisticas: data, isLoading: false });
    } catch (e: any) {
      this.setState({ isLoading: false, error: e.message });
    }
  }

  // ─── ACTAS ─────────────────────────────────────────────────────────────────

  async fetchActas(params?: { estado?: string; tipo?: string; search?: string; fecha_desde?: string; fecha_hasta?: string }) {
    this.setState({ isLoading: true, error: null });
    try {
      const query = new URLSearchParams(params as Record<string, string>).toString();
      const data = await api.get<{ results: ActaReunion[] }>(`/secretaria/actas/${query ? '?' + query : ''}`);
      this.setState({ actas: data.results ?? (data as any), isLoading: false });
    } catch (e: any) {
      this.setState({ isLoading: false, error: e.message });
    }
  }

  async createActa(data: Partial<ActaReunion>) {
    const nueva = await api.post<ActaReunion>('/secretaria/actas/', data);
    this.setState({ actas: [nueva, ...this.state.actas] });
    return nueva;
  }

  async updateActa(id: number, data: Partial<ActaReunion>) {
    const updated = await api.patch<ActaReunion>(`/secretaria/actas/${id}/`, data);
    this.setState({ actas: this.state.actas.map((a) => (a.id === id ? updated : a)) });
    return updated;
  }

  async deleteActa(id: number) {
    await api.delete(`/secretaria/actas/${id}/`);
    this.setState({ actas: this.state.actas.filter((a) => a.id !== id) });
  }

  async aprobarActa(id: number) {
    const updated = await api.post<ActaReunion>(`/secretaria/actas/${id}/aprobar/`, {});
    this.setState({ actas: this.state.actas.map((a) => (a.id === id ? updated : a)) });
    return updated;
  }

  // ─── SOLICITUDES ───────────────────────────────────────────────────────────

  async fetchSolicitudes(params?: { estado?: string; tipo?: string; search?: string; fecha_desde?: string; fecha_hasta?: string }) {
    this.setState({ isLoading: true, error: null });
    try {
      const query = new URLSearchParams(params as Record<string, string>).toString();
      const data = await api.get<{ results: SolicitudTramite[] }>(`/secretaria/solicitudes/${query ? '?' + query : ''}`);
      this.setState({ solicitudes: data.results ?? (data as any), isLoading: false });
    } catch (e: any) {
      this.setState({ isLoading: false, error: e.message });
    }
  }

  async createSolicitud(data: Partial<SolicitudTramite>) {
    const nueva = await api.post<SolicitudTramite>('/secretaria/solicitudes/', data);
    this.setState({ solicitudes: [nueva, ...this.state.solicitudes] });
    return nueva;
  }

  async cambiarEstadoSolicitud(id: number, estado: string, notas: string = '') {
    const updated = await api.post<SolicitudTramite>(`/secretaria/solicitudes/${id}/cambiar_estado/`, { estado, notas });
    this.setState({ solicitudes: this.state.solicitudes.map((s) => (s.id === id ? updated : s)) });
    return updated;
  }

  async generarDocumentoSolicitud(id: number) {
    const updated = await api.post<SolicitudTramite>(`/secretaria/solicitudes/${id}/generar_documento/`, {});
    this.setState({ solicitudes: this.state.solicitudes.map((s) => (s.id === id ? updated : s)) });
    return updated;
  }

  // ─── VISITAS ───────────────────────────────────────────────────────────────

  async fetchVisitas(params?: { activo?: string; seguimiento?: string; search?: string; fecha_desde?: string; fecha_hasta?: string }) {
    this.setState({ isLoading: true, error: null });
    try {
      const query = new URLSearchParams(params as Record<string, string>).toString();
      const data = await api.get<{ results: VisitaIglesia[] }>(`/secretaria/visitas/${query ? '?' + query : ''}`);
      this.setState({ visitas: data.results ?? (data as any), isLoading: false });
    } catch (e: any) {
      this.setState({ isLoading: false, error: e.message });
    }
  }

  async createVisita(data: Partial<VisitaIglesia>) {
    const nueva = await api.post<VisitaIglesia>('/secretaria/visitas/', data);
    this.setState({ visitas: [nueva, ...this.state.visitas] });
    return nueva;
  }

  async actualizarSeguimiento(id: number, seguimiento: string, responsable_id?: number) {
    const updated = await api.post<VisitaIglesia>(`/secretaria/visitas/${id}/actualizar_seguimiento/`, { seguimiento, responsable_id });
    this.setState({ visitas: this.state.visitas.map((v) => (v.id === id ? updated : v)) });
    return updated;
  }

  async vincularMiembro(visitaId: number, miembro_id: number) {
    const updated = await api.post<VisitaIglesia>(`/secretaria/visitas/${visitaId}/vincular_miembro/`, { miembro_id });
    this.setState({ visitas: this.state.visitas.map((v) => (v.id === visitaId ? updated : v)) });
    return updated;
  }

  // ─── COMUNICADOS ───────────────────────────────────────────────────────────

  async fetchComunicados(params?: { publicado?: boolean | string; search?: string; fecha_desde?: string; fecha_hasta?: string }) {
    this.setState({ isLoading: true, error: null });
    try {
      const p = params ? { ...params } : {};
      const query = new URLSearchParams(p as Record<string, string>).toString();
      const data = await api.get<{ results: ComunicadoInterno[] }>(`/secretaria/comunicados/${query ? '?' + query : ''}`);
      this.setState({ comunicados: data.results ?? (data as any), isLoading: false });
    } catch (e: any) {
      this.setState({ isLoading: false, error: e.message });
    }
  }

  async createComunicado(data: Partial<ComunicadoInterno>) {
    const nuevo = await api.post<ComunicadoInterno>('/secretaria/comunicados/', data);
    this.setState({ comunicados: [nuevo, ...this.state.comunicados] });
    return nuevo;
  }

  async publicarComunicado(id: number) {
    const updated = await api.post<ComunicadoInterno>(`/secretaria/comunicados/${id}/publicar/`, {});
    this.setState({ comunicados: this.state.comunicados.map((c) => (c.id === id ? updated : c)) });
    return updated;
  }

  async marcarLeido(id: number) {
    return await api.post(`/secretaria/comunicados/${id}/marcar_leido/`, {});
  }

  async updateComunicado(id: number, data: Partial<ComunicadoInterno>) {
    const updated = await api.patch<ComunicadoInterno>(`/secretaria/comunicados/${id}/`, data);
    this.setState({ comunicados: this.state.comunicados.map((c) => (c.id === id ? updated : c)) });
    return updated;
  }

  async deleteComunicado(id: number) {
    await api.delete(`/secretaria/comunicados/${id}/`);
    this.setState({ comunicados: this.state.comunicados.filter((c) => c.id !== id) });
  }

  // ─── HISTORIAL ─────────────────────────────────────────────────────────────

  async fetchHistorial(miembro_id?: number) {
    this.setState({ isLoading: true, error: null });
    try {
      const query = miembro_id ? `?miembro=${miembro_id}` : '';
      const data = await api.get<{ results: HistorialEstado[] }>(`/secretaria/historial/${query}`);
      this.setState({ historial: data.results ?? (data as any), isLoading: false });
    } catch (e: any) {
      this.setState({ isLoading: false, error: e.message });
    }
  }

  async createHistorial(data: Partial<HistorialEstado>) {
    const nuevo = await api.post<HistorialEstado>('/secretaria/historial/', data);
    this.setState({ historial: [nuevo, ...this.state.historial] });
    return nuevo;
  }

  // ─── WHATSAPP ──────────────────────────────────────────────────────────────

  async fetchWaStatus() {
    try {
      const data = await api.get<{ status: string }>('/secretaria/whatsapp/status/');
      this.setState({ waStatus: data.status });
    } catch {
      this.setState({ waStatus: 'unavailable' });
    }
  }

  async fetchWaQr() {
    try {
      const data = await api.get<{ qr: string | null; status: string }>('/secretaria/whatsapp/qr/');
      this.setState({ waQr: data.qr, waStatus: data.status });
    } catch {
      this.setState({ waStatus: 'unavailable', waQr: null });
    }
  }

  async fetchWaConfig() {
    const data = await api.get<ConfiguracionWhatsApp>('/secretaria/whatsapp/config/');
    this.setState({ waConfig: data });
    return data;
  }

  async updateWaConfig(data: Partial<ConfiguracionWhatsApp>) {
    const updated = await api.patch<ConfiguracionWhatsApp>('/secretaria/whatsapp/config/', data);
    this.setState({ waConfig: updated });
    return updated;
  }

  async fetchWaMensajes() {
    const data = await api.get<MensajeWhatsApp[]>('/secretaria/whatsapp/mensajes/');
    this.setState({ waMensajes: Array.isArray(data) ? data : [] });
    return data;
  }

  async createWaMensaje(formData: FormData) {
    const nuevo = await api.postForm<MensajeWhatsApp>('/secretaria/whatsapp/mensajes/', formData);
    this.setState({ waMensajes: [...this.state.waMensajes, nuevo] });
    return nuevo;
  }

  async limpiarImagenMensaje(id: number) {
    const updated = await api.post<MensajeWhatsApp>(`/secretaria/whatsapp/mensajes/${id}/limpiar_imagen/`, {});
    this.setState({ waMensajes: this.state.waMensajes.map((m) => (m.id === id ? updated : m)) });
    return updated;
  }

  async updateWaMensaje(id: number, formData: FormData) {
    const updated = await api.patchForm<MensajeWhatsApp>(`/secretaria/whatsapp/mensajes/${id}/`, formData);
    this.setState({ waMensajes: this.state.waMensajes.map((m) => (m.id === id ? updated : m)) });
    return updated;
  }

  async waSendTest() {
    return await api.post<EnvioLog>('/secretaria/whatsapp/test_send/', {});
  }

  async waLogout() {
    return await api.delete('/secretaria/whatsapp/logout/');
  }

  async fetchWaHistorial() {
    const data = await api.get<EnvioLog[]>('/secretaria/whatsapp/historial/');
    this.setState({ waHistorial: Array.isArray(data) ? data : [] });
  }
}

export const secretariaStore = new SecretariaStore();
