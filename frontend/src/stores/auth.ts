import { api } from '../utils/api';

export interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  rol: string;
  ministerios_lidera: { id: number; nombre: string; slug: string }[];
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

class AuthStore {
  private state: AuthState = {
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  };

  private listeners: Set<(state: AuthState) => void> = new Set();

  getState(): AuthState {
    return this.state;
  }

  subscribe(listener: (state: AuthState) => void) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    this.listeners.forEach(listener => listener(this.state));
  }

  async checkAuth() {
    try {
      const user = await api.get<User>('/auth/me/');
      this.state = {
        ...this.state,
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    } catch {
      this.state = {
        ...this.state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
      };
    }
    this.notify();
  }

  async login(username: string, password: string) {
    this.state = { ...this.state, isLoading: true, error: null };
    this.notify();

    try {
      const data = await api.login(username, password);
      if (data.user) {
        this.state = {
          ...this.state,
          user: data.user,
          isAuthenticated: true,
          isLoading: false,
        };
      } else {
        await this.checkAuth();
      }
    } catch (error) {
      this.state = {
        ...this.state,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Error al iniciar sesión',
      };
    }
    this.notify();
  }

  async logout() {
    try {
      await api.logout();
    } finally {
      this.state = {
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
      this.notify();
    }
  }

  clearError() {
    this.state = { ...this.state, error: null };
    this.notify();
  }
}

export const authStore = new AuthStore();