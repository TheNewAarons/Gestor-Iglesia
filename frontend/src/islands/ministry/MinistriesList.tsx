import React, { useEffect, useState } from 'react';
import { api } from '@/utils/api';
import MinistryIcon from '@/components/MinistryIcon';
import type { Ministerio } from '@/stores/ministerios';

export default function MinistriesList() {
  const [ministerios, setMinisterios] = useState<Ministerio[]>([]);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    api.get<{ results: Ministerio[] }>('/ministerios/')
      .then(data => setMinisterios(data.results || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [mounted]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="h-28 bg-gray-100 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {ministerios.map((m) => (
        <a
          key={m.id}
          href={`/ministerios/${m.slug}`}
          className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-accent/30
            transition-all cursor-pointer no-underline block"
        >
          <div className="flex items-center gap-3 mb-3">
            <div
              className="w-10 h-10 rounded-md flex items-center justify-center text-white"
              style={{ backgroundColor: m.color || '#3B82F6' }}
            >
              <MinistryIcon name={m.icono || 'church'} className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-gray-900">{m.nombre}</h3>
              <p className="text-xs text-gray-500 truncate max-w-[180px]">{m.descripcion || ''}</p>
            </div>
          </div>
          <div className="flex gap-4 pt-3 border-t border-gray-100">
            <span className="text-xs text-gray-500">
              <b className="text-gray-900">{m.miembros_count || 0}</b> miembros
            </span>
            {m.lideres_nombres?.length ? (
              <span className="text-xs text-gray-500">
                <b className="text-gray-900">{m.lideres_nombres.length}</b> líder{m.lideres_nombres.length > 1 ? 'es' : ''}
              </span>
            ) : null}
          </div>
        </a>
      ))}
    </div>
  );
}
