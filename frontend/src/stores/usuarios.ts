import { api } from '../utils/api';

export interface Usuario {
  id: number;
  user_id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  rol: string;
  rol_display: string;
  ministerios_lidera: number[];
  ministerios_lidera_detalles: { id: number; nombre: string; slug: string }[];
  permisos_especificos: Record<string, string[]>;
  telefono: string;
  foto: string | null;
  activo: boolean;
  fecha_creacion: string | null;
  ultimo_login: string | null;
  creado_por: number | null;
  creado_por_nombre: string | null;
}

interface UsuariosState {
  usuarios: Usuario[];
  usuarioActual: Usuario | null;
  roles: [string, string][];
  ministeriosDisponibles: { id: number; nombre: string; slug: string }[];
  isLoading: boolean;
  error: string | null;
}

class UsuariosStore {
  private state: UsuariosState = {
    usuarios: [],
    usuarioActual: null,
    roles: [],
    ministeriosDisponibles: [],
    isLoading: false,
    error: null,
  };

  private listeners: Set<(state: UsuariosState) => void> = new Set();

  getState(): UsuariosState {
    return this.state;
  }

  subscribe(listener: (state: UsuariosState) => void) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    this.listeners.forEach(listener => listener(this.state));
  }

  setState(newState: Partial<UsuariosState>) {
    this.state = { ...this.state, ...newState };
    this.notify();
  }

  async fetchUsuarios() {
    this.setState({ isLoading: true, error: null });
    try {
      const usuarios = await api.get<Usuario[]>('/usuarios/');
      this.setState({ usuarios, isLoading: false });
    } catch (error) {
      this.setState({ error: (error as Error).message, isLoading: false });
    }
  }

  async fetchUsuario(id: number) {
    this.setState({ isLoading: true, error: null });
    try {
      const usuario = await api.get<Usuario>(`/usuarios/${id}/`);
      this.setState({ usuarioActual: usuario, isLoading: false });
    } catch (error) {
      this.setState({ error: (error as Error).message, isLoading: false });
    }
  }

  async fetchRoles() {
    try {
      const roles = await api.get<[string, string][]>('/usuarios/roles/');
      this.setState({ roles });
    } catch (error) {
      this.setState({ error: (error as Error).message });
    }
  }

  async fetchMinisteriosDisponibles() {
    try {
      const ministerios = await api.get<{ id: number; nombre: string; slug: string }[]>('/usuarios/ministerios-disponibles/');
      this.setState({ ministeriosDisponibles: ministerios });
    } catch (error) {
      this.setState({ error: (error as Error).message });
    }
  }

  async createUsuario(data: Partial<Usuario> & { password: string; password_confirm: string }) {
    this.setState({ isLoading: true, error: null });
    try {
      const usuario = await api.post<Usuario>('/usuarios/', data);
      this.setState({
        usuarios: [...this.state.usuarios, usuario],
        isLoading: false,
      });
      return usuario;
    } catch (error) {
      this.setState({ error: (error as Error).message, isLoading: false });
      throw error;
    }
  }

  async updateUsuario(id: number, data: Partial<Usuario> & { password_nueva?: string }) {
    this.setState({ isLoading: true, error: null });
    try {
      const usuario = await api.put<Usuario>(`/usuarios/${id}/`, data);
      this.setState({
        usuarios: this.state.usuarios.map(u => u.id === id ? usuario : u),
        usuarioActual: this.state.usuarioActual?.id === id ? usuario : this.state.usuarioActual,
        isLoading: false,
      });
      return usuario;
    } catch (error) {
      this.setState({ error: (error as Error).message, isLoading: false });
      throw error;
    }
  }

  async deleteUsuario(id: number) {
    this.setState({ isLoading: true, error: null });
    try {
      await api.delete(`/usuarios/${id}/`);
      this.setState({
        usuarios: this.state.usuarios.filter(u => u.id !== id),
        isLoading: false,
      });
    } catch (error) {
      this.setState({ error: (error as Error).message, isLoading: false });
      throw error;
    }
  }

  async cambiarRol(id: number, rol: string) {
    try {
      const usuario = await api.post<Usuario>(`/usuarios/${id}/cambiar-rol/`, { rol });
      this.setState({
        usuarios: this.state.usuarios.map(u => u.id === id ? usuario : u),
      });
      return usuario;
    } catch (error) {
      this.setState({ error: (error as Error).message });
      throw error;
    }
  }

  async asignarMinisterios(id: number, ministerios: number[]) {
    try {
      const usuario = await api.post<Usuario>(`/usuarios/${id}/asignar-ministerios/`, { ministerios });
      this.setState({
        usuarios: this.state.usuarios.map(u => u.id === id ? usuario : u),
      });
      return usuario;
    } catch (error) {
      this.setState({ error: (error as Error).message });
      throw error;
    }
  }

  async fetchUsuariosSimples(search?: string) {
    try {
      const params = search ? `?search=${encodeURIComponent(search)}` : '';
      return await api.get<{ id: number; username: string; first_name: string; last_name: string; email: string; telefono: string; rol: string }[]>(`/usuarios/simples/${params}`);
    } catch (error) {
      return [];
    }
  }

  clearUsuarioActual() {
    this.setState({ usuarioActual: null });
  }

  clearError() {
    this.setState({ error: null });
  }
}

export const usuariosStore = new UsuariosStore();
