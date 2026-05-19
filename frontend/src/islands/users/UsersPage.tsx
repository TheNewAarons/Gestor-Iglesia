import React, { useEffect, useState, useCallback } from 'react';
import { authStore } from '@/stores/auth';
import { usuariosStore } from '@/stores/usuarios';
import type { Usuario } from '@/stores/usuarios';
import { Button } from '@/components/ui';
import { Card } from '@/components/ui/Card';
import Input, { Select } from '@/components/ui/Input';
import Badge from '@/components/ui/Badge';
import Modal from '@/components/ui/Modal';

const ROLE_DISPLAY: Record<string, string> = {
  admin: 'Admin',
  pastora: 'Pastora',
  secretaria: 'Secretaria',
  tesorera: 'Tesorera',
  lider_ministerio: 'Líder Ministerio',
  concilio: 'Concilio',
};

const ROLE_BADGE: Record<string, 'default' | 'danger' | 'info' | 'warning' | 'success'> = {
  admin: 'danger',
  pastora: 'default',
  secretaria: 'info',
  tesorera: 'warning',
  lider_ministerio: 'success',
  concilio: 'default',
};

export default function UsersPage() {
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<Usuario | null>(null);
  const [form, setForm] = useState({
    username: '', password: '', password_confirm: '',
    first_name: '', last_name: '', email: '', rol: 'concilio',
    telefono: '', is_active: true, ministerios_lidera: [] as number[],
  });
  const [search, setSearch] = useState('');

  const state = usuariosStore.getState();

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    const check = async () => {
      await authStore.checkAuth();
      const authState = authStore.getState();
      if (!authState.isAuthenticated || authState.user?.rol !== 'admin') {
        window.location.href = '/login';
        return;
      }
      await usuariosStore.fetchUsuarios();
      await usuariosStore.fetchRoles();
      setLoading(false);
    };
    check();

    const unsub = usuariosStore.subscribe(() => forceUpdate());
    return unsub;
  }, [mounted]);

  const [, forceUpdate] = useState(0);
  const refresh = useCallback(() => forceUpdate(n => n + 1), []);

  const usuarios: Usuario[] = state.usuarios || [];
  const filtered = usuarios.filter((u) =>
    u.username.toLowerCase().includes(search.toLowerCase()) ||
    (u.first_name + ' ' + u.last_name).toLowerCase().includes(search.toLowerCase())
  );

  const openCreate = () => {
    setEditingUser(null);
    setForm({ username: '', password: '', password_confirm: '', first_name: '', last_name: '', email: '', rol: 'concilio', telefono: '', is_active: true, ministerios_lidera: [] });
    setShowModal(true);
  };

  const openEdit = (user: Usuario) => {
    setEditingUser(user);
    setForm({
      username: user.username, password: '', password_confirm: '',
      first_name: user.first_name || '', last_name: user.last_name || '',
      email: user.email || '', rol: user.rol || 'concilio',
      telefono: user.telefono || '', is_active: user.is_active ?? true,
      ministerios_lidera: user.ministerios_lidera?.map((m: any) => m.id) || [],
    });
    setShowModal(true);
  };

  const handleSubmit = async () => {
    if (editingUser) {
      await usuariosStore.updateUsuario(editingUser.id, form);
    } else {
      await usuariosStore.createUsuario(form);
    }
    setShowModal(false);
    refresh();
  };

  const handleDelete = async (id: number) => {
    if (confirm('¿Desactivar este usuario?')) {
      await usuariosStore.deleteUsuario(id);
      refresh();
    }
  };

  if (!mounted || loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-40" />
        <div className="h-64 bg-gray-100 rounded-lg" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Input
          placeholder="Buscar usuarios..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <Button onClick={openCreate}>+ Nuevo Usuario</Button>
      </div>

      <Card padding={false}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Usuario</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Nombre</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Rol</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Email</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Estado</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((user) => (
                <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{user.username}</td>
                  <td className="px-4 py-3">{user.first_name} {user.last_name}</td>
                  <td className="px-4 py-3">
                    <Badge variant={ROLE_BADGE[user.rol] || 'default'}>
                      {ROLE_DISPLAY[user.rol] || user.rol}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{user.email || '-'}</td>
                  <td className="px-4 py-3">
                    <Badge variant={user.is_active ? 'success' : 'danger'}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-2">
                      <Button size="sm" variant="ghost" onClick={() => openEdit(user)}>Editar</Button>
                      <Button size="sm" variant="ghost" onClick={() => handleDelete(user.id)} className="text-danger">Desactivar</Button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={6} className="px-4 py-12 text-center text-gray-500">No se encontraron usuarios</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Modal open={showModal} onClose={() => setShowModal(false)} title={editingUser ? 'Editar Usuario' : 'Nuevo Usuario'} size="lg">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input label="Usuario" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} disabled={!!editingUser} />
          <Input label="Email" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          <Input label="Nombre" value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} />
          <Input label="Apellido" value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} />
          <Input label="Teléfono" value={form.telefono} onChange={e => setForm({ ...form, telefono: e.target.value })} />
          <Select label="Rol" value={form.rol} onChange={e => setForm({ ...form, rol: e.target.value })}>
            {Object.entries(ROLE_DISPLAY).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </Select>
          {!editingUser && (
            <>
              <Input label="Contraseña" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
              <Input label="Confirmar contraseña" type="password" value={form.password_confirm} onChange={e => setForm({ ...form, password_confirm: e.target.value })} />
            </>
          )}
        </div>
        <div className="flex justify-end gap-2 mt-6">
          <Button variant="ghost" onClick={() => setShowModal(false)}>Cancelar</Button>
          <Button onClick={handleSubmit}>{editingUser ? 'Actualizar' : 'Crear'}</Button>
        </div>
      </Modal>
    </div>
  );
}
