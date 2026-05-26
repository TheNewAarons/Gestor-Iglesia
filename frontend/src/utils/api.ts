const API_BASE = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface FetchOptions extends RequestInit {
  skipAuth?: boolean;
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  getToken(): string | null {
    return this.token;
  }

  private async refreshAccessToken(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE}/auth/refresh/`, {
        method: 'POST',
        credentials: 'include',
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  private async request<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { skipAuth, ...fetchOptions } = options;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };

    if (!skipAuth && this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    let response = await fetch(`${API_BASE}${endpoint}`, {
      ...fetchOptions,
      headers,
      credentials: 'include',
    });

    if (response.status === 401 && !skipAuth) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        response = await fetch(`${API_BASE}${endpoint}`, {
          ...fetchOptions,
          headers,
          credentials: 'include',
        });
      }
    }

    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: 'Error desconocido' }));
      let message;
      if (body.errors && typeof body.errors === 'object') {
        const details = Object.entries(body.errors)
          .map(([k, v]) => k + ': ' + (Array.isArray(v) ? v.join(', ') : v))
          .join('; ');
        message = (body.message || 'Error de validación') + ' (' + details + ')';
      } else if (typeof body.error === 'object' && body.error !== null) {
        message = body.error.mensaje || JSON.stringify(body.error);
      } else {
        message = body.message || body.detail || body.error || 'Error en la solicitud';
      }
      const err = new Error(message);
      (err as any).body = body;
      (err as any).status = response.status;
      throw err;
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  async get<T>(endpoint: string, options?: FetchOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(endpoint: string, data?: unknown, options?: FetchOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data: unknown, options?: FetchOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch<T>(endpoint: string, data: unknown, options?: FetchOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string, options?: FetchOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  async postForm<T>(endpoint: string, formData: FormData): Promise<T> {
    return this.requestForm<T>(endpoint, 'POST', formData);
  }

  async putForm<T>(endpoint: string, formData: FormData): Promise<T> {
    return this.requestForm<T>(endpoint, 'PUT', formData);
  }

  async patchForm<T>(endpoint: string, formData: FormData): Promise<T> {
    return this.requestForm<T>(endpoint, 'PATCH', formData);
  }

  async deleteForm<T>(endpoint: string, formData?: FormData): Promise<T> {
    return this.requestForm<T>(endpoint, 'DELETE', formData);
  }

  private async requestForm<T>(endpoint: string, method: string, formData?: FormData): Promise<T> {
    const headers: HeadersInit = {};

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    let response = await fetch(`${API_BASE}${endpoint}`, {
      method,
      headers,
      body: formData,
      credentials: 'include',
    });

    if (response.status === 401) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        if (this.token) {
          (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
        }
        response = await fetch(`${API_BASE}${endpoint}`, {
          method,
          headers,
          body: formData,
          credentials: 'include',
        });
      }
    }

    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: 'Error desconocido' }));
      let message;
      if (body.errors && typeof body.errors === 'object') {
        const details = Object.entries(body.errors)
          .map(([k, v]) => k + ': ' + (Array.isArray(v) ? v.join(', ') : v))
          .join('; ');
        message = (body.message || 'Error de validación') + ' (' + details + ')';
      } else if (typeof body.error === 'object' && body.error !== null) {
        message = body.error.mensaje || JSON.stringify(body.error);
      } else {
        message = body.message || body.detail || body.error || 'Error en la solicitud';
      }
      const err = new Error(message);
      (err as any).body = body;
      (err as any).status = response.status;
      throw err;
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  async login(username: string, password: string) {
    const response = await fetch(`${API_BASE}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
      credentials: 'include',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Credenciales inválidas' }));
      throw new Error(error.error || 'Error al iniciar sesión');
    }

    return response.json();
  }

  async logout() {
    const response = await fetch(`${API_BASE}/auth/logout/`, {
      method: 'POST',
      credentials: 'include',
    });
    this.clearToken();
    return response.json();
  }
}

export const api = new ApiClient();
export default api;
