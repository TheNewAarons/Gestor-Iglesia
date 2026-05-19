import React, { useEffect, useState } from 'react';
import { authStore, User } from '@/stores/auth';
import MinistryIcon from '@/components/MinistryIcon';

const STATS = [
  { label: 'Ministerios', value: '13', color: 'primary' as const },
  { label: 'Finanzas', value: 'PYG', color: 'success' as const },
  { label: 'Calendario', value: 'Próximo', color: 'accent' as const },
  { label: 'Secretaría', value: 'Miembros', color: 'warning' as const },
];

export default function DashboardHome() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    const unsub = authStore.subscribe((state) => {
      if (!state.isLoading) {
        if (!state.isAuthenticated) {
          window.location.href = '/login';
        } else {
          setUser(state.user);
          setLoading(false);
        }
      }
    });
    authStore.checkAuth();
    return unsub;
  }, [mounted]);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-48" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-gray-100 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          Bienvenido{user?.first_name ? `, ${user.first_name}` : ''}
        </h2>
        <p className="text-sm text-gray-500">Panel de control de la iglesia</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {STATS.map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className="text-xl font-bold text-gray-900 mt-1">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { slug: 'mni', name: 'MNI', icon: 'user-plus' },
          { slug: 'dni', name: 'DNI', icon: 'book-open' },
          { slug: 'alabanza', name: 'Alabanza', icon: 'microphone' },
          { slug: 'comunicaciones', name: 'Comunicaciones', icon: 'broadcast' },
        ].map((m) => (
          <a
            key={m.slug}
            href={`/ministerios/${m.slug}`}
            className="flex items-center gap-3 p-4 rounded-lg border border-gray-200
              hover:border-accent/30 hover:bg-accent/5 transition-colors"
          >
            <MinistryIcon name={m.icon} className="w-8 h-8 text-accent" />
            <span className="text-sm font-medium text-gray-700">{m.name}</span>
          </a>
        ))}
      </div>
    </div>
  );
}
