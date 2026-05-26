import { api, API_BASE } from '../utils/api';

export interface Ministerio {
  id: number;
  nombre: string;
  slug: string;
  descripcion: string;
  color: string;
  icono: string;
  logo: string | null;
  activo: boolean;
  miembros_count: number;
  lideres_nombres: string[];
}

export interface Miembro {
  id: number;
  ministry: number;
  ministry_nombre: string;
  primer_nombre: string;
  segundo_nombre: string;
  primer_apellido: string;
  segundo_apellido: string;
  nombre_completo: string;
  fecha_nacimiento: string;
  edad: number;
  estado_civil: string;
  telefono: string;
  email: string;
  clase: string;
  rol_en_ministerio: string;
  usuario_rol?: string;
  activo: boolean;
}

export interface MovimientoCaja {
  id: number;
  tipo: 'ingreso' | 'egreso';
  monto: number;
  descripcion: string;
  fecha: string;
  imagen: string | null;
  registrado_por_nombre: string;
  enviado_tesoreria: boolean;
  aprobado: boolean;
}

export interface CajaMinisterio {
  id: number;
  ministry: number;
  ministry_nombre: string;
  saldo_actual: number;
  saldo_calculado: number;
  movimientos: MovimientoCaja[];
}

export interface Inventario {
  id: number;
  nombre: string;
  categoria: string;
  cantidad: number;
  ubicacion: string;
  descripcion: string;
  estado: string;
  imagen: string | null;
}

export interface Ofrenda {
  id: number;
  fecha: string;
  monto: number;
  categoria: string;
  clase: string;
  envidada_tesoreria: boolean;
  fecha_envio: string | null;
  aprobado: boolean;
  observaciones: string;
}

export interface Asistencia {
  id: number;
  fecha: string;
  miembro: number | null;
  miembro_nombre: string;
  presente: boolean;
  es_visita: boolean;
  nombre_visita: string;
  clase: string;
  tiene_biblia: boolean;
  observaciones: string;
}

export interface ResumenAsistencia {
  fecha: string;
  total_asistencia: number;
  total_visitas: number;
  total_biblias: number;
  total_ofrendas: number;
  por_clase: Record<string, number>;
}

export interface AsistenciaAcumulativa {
  miembros: {
    miembro_id: number;
    nombre_completo: string;
    clase: string;
    asistencias_count: number;
  }[];
  visitas_total: number;
  total_asistencias: number;
}

export interface Cumpleanero {
  id: number;
  nombre_completo: string;
  fecha_nacimiento: string;
  dia: number;
  dias_faltantes: number;
}

export interface OfrendaPorClase {
  clase: string;
  total: number;
  count: number;
}

export interface BibliasPorClaseResponse {
  por_clase: { clase: string; biblias: number }[];
  total_general: number;
}

export interface OfrendaTotalesPorCategoria {
  categoria: string;
  total: number;
  count: number;
}

export interface ReporteOfrendas {
  fecha_inicio: string;
  fecha_fin: string;
  total_general: number;
  por_categoria: OfrendaTotalesPorCategoria[];
}

export interface Cancion {
  id: number;
  titulo: string;
  artista: string;
  categoria: string;
  tono: string;
  letra: string;
  acordes: string;
  link_youtube: string;
}

export interface ProgramaAlabanza {
  id: number;
  ministry: number;
  ministry_nombre: string;
  fecha: string;
  alabanzas: any[];
  creado_por_nombre: string;
}

export interface LeccionEXPLO {
  id: number;
  titulo: string;
  descripcion: string;
  contenido: string;
  link_material: string;
  archivo: string;
}

export interface RecursoComunicacion {
  id: number;
  titulo: string;
  tipo: string;
  descripcion: string;
  archivo: string;
  url_externa: string;
}

export interface IdeaComunicacion {
  id: number;
  titulo: string;
  descripcion: string;
  prioridad: string;
  completada: boolean;
  fecha_completada: string | null;
}

export interface PlanificacionActividad {
  id: number;
  ministry: number;
  ministry_nombre: string;
  titulo: string;
  descripcion: string;
  fecha_planificada: string;
  hora: string | null;
  ubicacion: string;
  tipo: 'propia' | 'compartida';
  ministerios_relacionados_nombres: string[];
  responsable: number | null;
  responsable_nombre: string;
  presupuesto: number;
  estado: 'planificada' | 'en_proceso' | 'completada' | 'cancelada';
}

export interface Nota {
  id: number;
  ministry: number;
  titulo: string;
  contenido: string;
  evento: number | null;
  evento_titulo: string | null;
  color: string;
  creado_por: number | null;
  creado_por_nombre: string | null;
  created_at: string;
}

export interface Evento {
  id: number;
  titulo: string;
  descripcion: string;
  fecha_inicio: string;
  hora_inicio: string | null;
  fecha_fin: string | null;
  hora_fin: string | null;
  ubicacion: string;
  tipo: 'propio' | 'compartido';
  ministerios_relacionados_nombres: string[];
  creado_por_nombre: string;
}

export interface EnfoqueMNI {
  id: number;
  mes: number;
  titulo: string;
  descripcion: string;
}

export interface ProgramaDomingo {
  id: number;
  ministry: number;
  titulo: string;
  fecha: string;
  secciones: Record<string, string>;
  creado_por_nombre: string;
  created_at: string;
  updated_at: string;
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

interface MinisteriosState {
  ministerios: Ministerio[];
  selectedMinisterio: Ministerio | null;
  dashboard: any | null;
  miembros: Miembro[];
  caja: CajaMinisterio | null;
  inventario: Inventario[];
  ofrendas: Ofrenda[];
  eventos: Evento[];
  asistencia: Asistencia[];
  asistencia_resumen: ResumenAsistencia[];
  asistencia_acumulativa: AsistenciaAcumulativa | null;
  cumpleaneros: Cumpleanero[];
  canciones: Cancion[];
  programas: ProgramaAlabanza[];
  lecciones: LeccionEXPLO[];
  recursos: RecursoComunicacion[];
  ideas: IdeaComunicacion[];
  planificaciones: PlanificacionActividad[];
  notas: Nota[];
  enfoques: EnfoqueMNI[];
  enfoque_actual: EnfoqueMNI | null;
  mes_actual: number;
  programas_domingo: ProgramaDomingo[];
  ofrendas_por_clase: OfrendaPorClase[];
  biblias_por_clase: BibliasPorClaseResponse | null;
  ofrendas_totales: OfrendaTotalesPorCategoria[];
  reporte_ofrendas: ReporteOfrendas | null;
  isLoading: boolean;
  error: string | null;
}

class MinisteriosStore {
  private state: MinisteriosState = {
    ministerios: [],
    selectedMinisterio: null,
    dashboard: null,
    miembros: [],
    caja: null,
    inventario: [],
    ofrendas: [],
    eventos: [],
    asistencia: [],
    asistencia_resumen: [],
    asistencia_acumulativa: null,
    cumpleaneros: [],
    canciones: [],
    programas: [],
    lecciones: [],
    recursos: [],
    ideas: [],
    planificaciones: [],
    notas: [],
    enfoques: [],
    enfoque_actual: null,
    mes_actual: 0,
    programas_domingo: [],
    ofrendas_por_clase: [],
    biblias_por_clase: null,
    ofrendas_totales: [],
    reporte_ofrendas: null,
    isLoading: false,
    error: null,
  };

  private listeners: Set<(state: MinisteriosState) => void> = new Set();

  getState(): MinisteriosState {
    return this.state;
  }

  subscribe(listener: (state: MinisteriosState) => void) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    this.listeners.forEach(listener => listener(this.state));
  }

  private setState(partial: Partial<MinisteriosState>) {
    this.state = { ...this.state, ...partial };
    this.notify();
  }

  async fetchMinisterios() {
    this.setState({ isLoading: true, error: null });
    try {
      const response = await api.get<PaginatedResponse<Ministerio>>('/ministerios/');
      this.setState({ ministerios: response.results, isLoading: false });
    } catch (error) {
      this.setState({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Error al cargar ministerios',
      });
    }
  }

  async fetchMinisterio(slug: string) {
    this.setState({ isLoading: true, error: null });
    try {
      const ministry = await api.get<Ministerio>(`/ministerios/${slug}/`);
      this.setState({ selectedMinisterio: ministry, isLoading: false });
    } catch (error) {
      this.setState({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Error al cargar ministerio',
      });
    }
  }

  async fetchDashboard(slug: string) {
    this.setState({ isLoading: true, error: null });
    try {
      const dashboard = await api.get<any>(`/ministerios/${slug}/dashboard/`);
      this.setState({ dashboard, isLoading: false });
    } catch (error) {
      this.setState({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Error al cargar dashboard',
      });
    }
  }

  async fetchMiembros(slug: string) {
    try {
      const miembros = await api.get<Miembro[]>(`/ministerios/${slug}/miembros/`);
      this.setState({ miembros });
    } catch (error) {
      console.error('Error fetching miembros:', error);
    }
  }

  async addMiembro(slug: string, data: Partial<Miembro>) {
    try {
      const nuevo = await api.post<Miembro>(`/ministerios/${slug}/miembros/`, data);
      this.setState({ miembros: [...this.state.miembros, nuevo] });
      return nuevo;
    } catch (error) {
      throw error;
    }
  }

  async updateMiembro(id: number, data: Partial<Miembro>) {
    try {
      const updated = await api.patch<Miembro>(`/miembros/${id}/`, data);
      const miembros = this.state.miembros.map(m =>
        m.id === id ? { ...m, ...updated } : m
      );
      this.setState({ miembros });
      return updated;
    } catch (error) {
      throw error;
    }
  }

  async deleteMiembro(id: number) {
    try {
      await api.delete(`/miembros/${id}/`);
      const miembros = this.state.miembros.filter(m => m.id !== id);
      this.setState({ miembros });
    } catch (error) {
      throw error;
    }
  }

  async fetchCaja(slug: string) {
    try {
      const caja = await api.get<CajaMinisterio>(`/ministerios/${slug}/caja/`);
      this.setState({ caja });
    } catch (error) {
      console.error('Error fetching caja:', error);
    }
  }

  async addMovimiento(slug: string, data: Partial<MovimientoCaja> | FormData) {
    try {
      if (data instanceof FormData) {
        await api.postForm(`/ministerios/${slug}/caja/`, data);
      } else {
        await api.post(`/ministerios/${slug}/caja/`, data);
      }
      await this.fetchCaja(slug);
    } catch (error) {
      throw error;
    }
  }

  async fetchInventario(slug: string) {
    try {
      const inventario = await api.get<Inventario[]>(`/ministerios/${slug}/inventario/`);
      this.setState({ inventario });
    } catch (error) {
      console.error('Error fetching inventario:', error);
    }
  }

  async addInventarioItem(slug: string, data: Partial<Inventario> | FormData) {
    try {
      let nuevo: Inventario;
      if (data instanceof FormData) {
        nuevo = await api.postForm<Inventario>(`/ministerios/${slug}/inventario/`, data);
      } else {
        nuevo = await api.post<Inventario>(`/ministerios/${slug}/inventario/`, data);
      }
      this.setState({ inventario: [...this.state.inventario, nuevo] });
      return nuevo;
    } catch (error) {
      throw error;
    }
  }

  async updateInventarioItem(slug: string, itemId: number, data: Partial<Inventario> | FormData) {
    try {
      let actualizado: Inventario;
      if (data instanceof FormData) {
        actualizado = await api.putForm<Inventario>(`/ministerios/${slug}/inventario/${itemId}/`, data);
      } else {
        actualizado = await api.put<Inventario>(`/ministerios/${slug}/inventario/${itemId}/`, data);
      }
      this.setState({
        inventario: this.state.inventario.map(it => it.id === itemId ? actualizado : it)
      });
      return actualizado;
    } catch (error) {
      throw error;
    }
  }

  async deleteInventarioItem(slug: string, itemId: number) {
    try {
      await api.delete(`/ministerios/${slug}/inventario/${itemId}/`);
      this.setState({ inventario: this.state.inventario.filter(it => it.id !== itemId) });
    } catch (error) {
      throw error;
    }
  }

  async fetchOfrendas(slug: string) {
    try {
      const ofrendas = await api.get<Ofrenda[]>(`/ministerios/${slug}/ofrendas/`);
      this.setState({ ofrendas });
    } catch (error) {
      console.error('Error fetching ofrendas:', error);
    }
  }

  async addOfrenda(slug: string, data: Partial<Ofrenda>) {
    try {
      const nueva = await api.post<Ofrenda>(`/ministerios/${slug}/ofrendas/`, data);
      this.setState({ ofrendas: [...this.state.ofrendas, nueva] });
      return nueva;
    } catch (error) {
      throw error;
    }
  }

  async updateOfrenda(slug: string, id: number, data: Partial<Ofrenda>) {
    try {
      const actualizada = await api.put<Ofrenda>(`/ministerios/${slug}/ofrendas/${id}/`, data);
      this.setState({ ofrendas: this.state.ofrendas.map(o => o.id === id ? actualizada : o) });
      return actualizada;
    } catch (error) {
      throw error;
    }
  }

  async deleteOfrenda(slug: string, id: number) {
    try {
      await api.delete(`/ministerios/${slug}/ofrendas/${id}/`);
      this.setState({ ofrendas: this.state.ofrendas.filter(o => o.id !== id) });
    } catch (error) {
      throw error;
    }
  }

  async fetchEventos(slug: string) {
    try {
      const eventos = await api.get<Evento[]>(`/ministerios/${slug}/eventos/`);
      this.setState({ eventos });
    } catch (error) {
      console.error('Error fetching eventos:', error);
    }
  }

  async addEvento(slug: string, data: Partial<Evento>) {
    try {
      const nuevo = await api.post<Evento>(`/ministerios/${slug}/eventos/`, data);
      this.setState({ eventos: [...this.state.eventos, nuevo] });
      return nuevo;
    } catch (error) {
      throw error;
    }
  }

  async fetchAsistencia(slug: string, fecha?: string, clase?: string) {
    try {
      let url = `/ministerios/${slug}/asistencia/`;
      const params = new URLSearchParams();
      if (fecha) params.append('fecha', fecha);
      if (clase) params.append('clase', clase);
      const queryString = params.toString();
      if (queryString) url += '?' + queryString;
      const asistencia = await api.get<Asistencia[]>(url);
      this.setState({ asistencia });
    } catch (error) {
      console.error('Error fetching asistencia:', error);
    }
  }

  async addAsistencia(slug: string, data: Partial<Asistencia>) {
    try {
      const nueva = await api.post<Asistencia>(`/ministerios/${slug}/asistencia/`, data);
      this.setState({ asistencia: [...this.state.asistencia, nueva] });
      return nueva;
    } catch (error) {
      throw error;
    }
  }

  async fetchAsistenciaResumen(slug: string, mes?: number, anio?: number) {
    try {
      let url = `/ministerios/${slug}/asistencia/resumen/`;
      const params = new URLSearchParams();
      if (mes) params.append('mes', mes.toString());
      if (anio) params.append('anio', anio.toString());
      const queryString = params.toString();
      if (queryString) url += '?' + queryString;
      const resumen = await api.get<ResumenAsistencia[]>(url);
      this.setState({ asistencia_resumen: resumen });
    } catch (error) {
      console.error('Error fetching asistencia resumen:', error);
    }
  }

  async fetchAsistenciaAcumulativa(slug: string, mes?: number, anio?: number, clase?: string) {
    try {
      let url = `/ministerios/${slug}/asistencia/acumulativa/`;
      const params = new URLSearchParams();
      if (mes) params.append('mes', mes.toString());
      if (anio) params.append('anio', anio.toString());
      if (clase) params.append('clase', clase);
      const queryString = params.toString();
      if (queryString) url += '?' + queryString;
      const acumulativa = await api.get<AsistenciaAcumulativa>(url);
      this.setState({ asistencia_acumulativa: acumulativa });
    } catch (error) {
      console.error('Error fetching asistencia acumulativa:', error);
    }
  }

  async fetchCumpleanos(ministrySlug?: string) {
    try {
      let url = '/miembros/cumpleanos/';
      if (ministrySlug) url += `?ministerio=${ministrySlug}`;
      const cumpleaneros = await api.get<Cumpleanero[]>(url);
      this.setState({ cumpleaneros });
    } catch (error) {
      console.error('Error fetching cumpleaños:', error);
    }
  }

  async fetchCanciones() {
    try {
      const canciones = await api.get<Cancion[]>('/canciones/');
      this.setState({ canciones });
    } catch (error) {
      console.error('Error fetching canciones:', error);
    }
  }

  async addCancion(data: Partial<Cancion>) {
    try {
      const nueva = await api.post<Cancion>('/canciones/', data);
      this.setState({ canciones: [...this.state.canciones, nueva] });
      return nueva;
    } catch (error) {
      throw error;
    }
  }

  async updateCancion(id: number, data: Partial<Cancion>) {
    try {
      const actualizada = await api.put<Cancion>(`/canciones/${id}/`, data);
      this.setState({ canciones: this.state.canciones.map(c => c.id === id ? actualizada : c) });
      return actualizada;
    } catch (error) {
      throw error;
    }
  }

  async deleteCancion(id: number) {
    try {
      await api.delete(`/canciones/${id}/`);
      this.setState({ canciones: this.state.canciones.filter(c => c.id !== id) });
    } catch (error) {
      throw error;
    }
  }

  async fetchProgramas(slug?: string) {
    try {
      let url = '/programas/';
      if (slug) url += `?ministerio=${slug}`;
      const programas = await api.get<ProgramaAlabanza[]>(url);
      this.setState({ programas });
    } catch (error) {
      console.error('Error fetching programas:', error);
    }
  }

  async generarPrograma(fecha: string, ministrySlug: string) {
    try {
      const programa = await api.post<ProgramaAlabanza>('/canciones/generar_programa/', {
        fecha,
        ministry: ministrySlug
      });
      this.setState({ programas: [...this.state.programas, programa] });
      return programa;
    } catch (error) {
      throw error;
    }
  }

  async fetchLecciones() {
    try {
      const lecciones = await api.get<LeccionEXPLO[]>('/lecciones/');
      this.setState({ lecciones });
    } catch (error) {
      console.error('Error fetching lecciones:', error);
    }
  }

  async addLeccion(data: Partial<LeccionEXPLO>) {
    try {
      const nueva = await api.post<LeccionEXPLO>('/lecciones/', data);
      this.setState({ lecciones: [...this.state.lecciones, nueva] });
      return nueva;
    } catch (error) {
      throw error;
    }
  }

  async fetchRecursos(slug?: string) {
    try {
      let url = '/recursos/';
      const params = new URLSearchParams();
      if (slug) params.append('ministerio', slug);
      const queryString = params.toString();
      if (queryString) url += '?' + queryString;
      const recursos = await api.get<RecursoComunicacion[]>(url);
      this.setState({ recursos });
    } catch (error) {
      console.error('Error fetching recursos:', error);
    }
  }

  async addRecurso(data: Partial<RecursoComunicacion>) {
    try {
      const nuevo = await api.post<RecursoComunicacion>('/recursos/', data);
      this.setState({ recursos: [...this.state.recursos, nuevo] });
      return nuevo;
    } catch (error) {
      throw error;
    }
  }

  async fetchIdeas(slug?: string) {
    try {
      let url = '/ideas/';
      const params = new URLSearchParams();
      if (slug) params.append('ministerio', slug);
      const queryString = params.toString();
      if (queryString) url += '?' + queryString;
      const ideas = await api.get<IdeaComunicacion[]>(url);
      this.setState({ ideas });
    } catch (error) {
      console.error('Error fetching ideas:', error);
    }
  }

  async addIdea(data: Partial<IdeaComunicacion>) {
    try {
      const nueva = await api.post<IdeaComunicacion>('/ideas/', data);
      this.setState({ ideas: [...this.state.ideas, nueva] });
      return nueva;
    } catch (error) {
      throw error;
    }
  }

  async toggleIdeaCompletada(id: number, completada: boolean) {
    try {
      await api.patch(`/ideas/${id}/`, { completada });
      const ideas = this.state.ideas.map(idea =>
        idea.id === id ? { ...idea, completada } : idea
      );
      this.setState({ ideas });
    } catch (error) {
      throw error;
    }
  }

  async fetchPlanificaciones(slug: string) {
    try {
      const planificaciones = await api.get<PlanificacionActividad[]>(`/ministerios/${slug}/planificaciones/`);
      this.setState({ planificaciones });
    } catch (error) {
      console.error('Error fetching planificaciones:', error);
    }
  }

  async addPlanificacion(slug: string, data: Partial<PlanificacionActividad>) {
    try {
      const nueva = await api.post<PlanificacionActividad>(`/ministerios/${slug}/planificaciones/`, data);
      this.setState({ planificaciones: [...this.state.planificaciones, nueva] });
      return nueva;
    } catch (error) {
      throw error;
    }
  }

  async updatePlanificacion(slug: string, id: number, data: Partial<PlanificacionActividad>) {
    try {
      const actualizada = await api.put<PlanificacionActividad>(`/ministerios/${slug}/planificaciones/${id}/`, data);
      this.setState({ planificaciones: this.state.planificaciones.map(p => p.id === id ? actualizada : p) });
      return actualizada;
    } catch (error) {
      throw error;
    }
  }

  async deletePlanificacion(slug: string, id: number) {
    try {
      await api.delete(`/ministerios/${slug}/planificaciones/${id}/`);
      this.setState({ planificaciones: this.state.planificaciones.filter(p => p.id !== id) });
    } catch (error) {
      throw error;
    }
  }

  async fetchOfrendasPorClase(slug: string, mes?: number, anio?: number) {
    try {
      let url = `/ministerios/${slug}/ofrendas/por-clase/`;
      const params = new URLSearchParams();
      if (mes) params.append('mes', mes.toString());
      if (anio) params.append('anio', anio.toString());
      const queryString = params.toString();
      if (queryString) url += '?' + queryString;
      const data = await api.get<OfrendaPorClase[]>(url);
      this.setState({ ofrendas_por_clase: data });
    } catch (error) {
      console.error('Error fetching ofrendas por clase:', error);
    }
  }

  async fetchBibliasPorClase(slug: string, mes?: number, anio?: number) {
    try {
      let url = `/ministerios/${slug}/biblias/por-clase/`;
      const params = new URLSearchParams();
      if (mes) params.append('mes', mes.toString());
      if (anio) params.append('anio', anio.toString());
      const queryString = params.toString();
      if (queryString) url += '?' + queryString;
      const data = await api.get<BibliasPorClaseResponse>(url);
      this.setState({ biblias_por_clase: data });
    } catch (error) {
      console.error('Error fetching biblias por clase:', error);
    }
  }

  async fetchOfrendasTotales(slug: string, mes?: number, anio?: number) {
    try {
      let url = `/ministerios/${slug}/ofrendas/totales/`;
      const params = new URLSearchParams();
      if (mes) params.append('mes', mes.toString());
      if (anio) params.append('anio', anio.toString());
      const queryString = params.toString();
      if (queryString) url += '?' + queryString;
      const data = await api.get<OfrendaTotalesPorCategoria[]>(url);
      this.setState({ ofrendas_totales: data });
    } catch (error) {
      console.error('Error fetching ofrendas totales:', error);
    }
  }

  async fetchReporteOfrendas(slug: string, fechaInicio: string, fechaFin: string) {
    try {
      const url = `/ministerios/${slug}/ofrendas/reporte/?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`;
      const data = await api.get<ReporteOfrendas>(url);
      this.setState({ reporte_ofrendas: data });
      return data;
    } catch (error) {
      throw error;
    }
  }

  descargarReporteCSV(slug: string, fechaInicio: string, fechaFin: string) {
    window.open(`${API_BASE}/ministerios/${slug}/ofrendas/reporte/?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}&formato=csv`, '_blank');
  }

  descargarCajaCSV(slug: string, tipo?: string) {
    let url = `${API_BASE}/ministerios/${slug}/caja/exportar-csv/`;
    if (tipo) url += `?tipo=${tipo}`;
    window.open(url, '_blank');
  }

  async fetchNotas(slug: string) {
    try {
      const notas = await api.get<Nota[]>(`/ministerios/${slug}/notas/`);
      this.setState({ notas });
    } catch (error) {
      throw error;
    }
  }

  async addNota(slug: string, data: Partial<Nota>) {
    try {
      const nueva = await api.post<Nota>(`/ministerios/${slug}/notas/`, data);
      this.setState({ notas: [nueva, ...this.state.notas] });
      return nueva;
    } catch (error) {
      throw error;
    }
  }

  async updateNota(slug: string, id: number, data: Partial<Nota>) {
    try {
      const actualizada = await api.put<Nota>(`/ministerios/${slug}/notas/${id}/`, data);
      this.setState({ notas: this.state.notas.map(n => n.id === id ? actualizada : n) });
      return actualizada;
    } catch (error) {
      throw error;
    }
  }

  async deleteNota(slug: string, id: number) {
    try {
      await api.delete(`/ministerios/${slug}/notas/${id}/`);
      this.setState({ notas: this.state.notas.filter(n => n.id !== id) });
    } catch (error) {
      throw error;
    }
  }

  async fetchEnfoques(slug: string) {
    try {
      const data = await api.get<{ mes_actual: number; enfoque_actual: EnfoqueMNI | null; enfoques: EnfoqueMNI[] }>(`/ministerios/${slug}/enfoques/`);
      this.setState({ enfoques: data.enfoques, enfoque_actual: data.enfoque_actual, mes_actual: data.mes_actual });
    } catch (error) {
      throw error;
    }
  }

  async fetchProgramasDomingo(slug: string) {
    try {
      const data = await api.get<ProgramaDomingo[]>(`/ministerios/${slug}/programas-domingo/`);
      this.setState({ programas_domingo: data });
    } catch (error) {
      throw error;
    }
  }

  async addProgramaDomingo(slug: string, data: { titulo: string; fecha: string; secciones: Record<string, string> }) {
    try {
      const creado = await api.post<ProgramaDomingo>(`/ministerios/${slug}/programas-domingo/`, data);
      this.setState({ programas_domingo: [creado, ...this.state.programas_domingo] });
      return creado;
    } catch (error) {
      throw error;
    }
  }

  async updateProgramaDomingo(slug: string, id: number, data: Partial<ProgramaDomingo>) {
    try {
      const actualizado = await api.put<ProgramaDomingo>(`/ministerios/${slug}/programas-domingo/${id}/`, data);
      this.setState({ programas_domingo: this.state.programas_domingo.map(p => p.id === id ? actualizado : p) });
      return actualizado;
    } catch (error) {
      throw error;
    }
  }

  async deleteProgramaDomingo(slug: string, id: number) {
    try {
      await api.delete(`/ministerios/${slug}/programas-domingo/${id}/`);
      this.setState({ programas_domingo: this.state.programas_domingo.filter(p => p.id !== id) });
    } catch (error) {
      throw error;
    }
  }

  clearSelected() {
    this.setState({
      selectedMinisterio: null,
      dashboard: null,
      miembros: [],
      caja: null,
      inventario: [],
      ofrendas: [],
      eventos: [],
      asistencia: [],
      asistencia_resumen: [],
      asistencia_acumulativa: null,
      cumpleaneros: [],
      canciones: [],
      programas: [],
      lecciones: [],
      recursos: [],
      ideas: [],
      planificaciones: [],
      notas: [],
      enfoques: [],
      enfoque_actual: null,
      mes_actual: 0,
      programas_domingo: [],
      ofrendas_por_clase: [],
      biblias_por_clase: null,
      ofrendas_totales: [],
      reporte_ofrendas: null,
    });
  }
}

export const ministeriosStore = new MinisteriosStore();