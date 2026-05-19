import React from 'react';

interface StatsCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: { value: number; positive: boolean };
  color?: 'primary' | 'accent' | 'success' | 'warning' | 'danger';
  className?: string;
}

const colorMap = {
  primary: { bg: 'bg-primary/5', text: 'text-primary', icon: 'text-primary/70' },
  accent: { bg: 'bg-accent/5', text: 'text-accent', icon: 'text-accent/70' },
  success: { bg: 'bg-green-50', text: 'text-green-700', icon: 'text-green-600' },
  warning: { bg: 'bg-amber-50', text: 'text-amber-700', icon: 'text-amber-600' },
  danger: { bg: 'bg-red-50', text: 'text-red-700', icon: 'text-red-600' },
};

export default function StatsCard({ label, value, icon, trend, color = 'primary', className = '' }: StatsCardProps) {
  const c = colorMap[color];

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-100 p-5 ${className}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{label}</p>
          <p className={`text-2xl font-bold ${c.text}`}>{value}</p>
          {trend && (
            <p className={`text-xs mt-1.5 ${trend.positive ? 'text-green-600' : 'text-red-600'}`}>
              {trend.positive ? '↑' : '↓'} {Math.abs(trend.value)}%
            </p>
          )}
        </div>
        {icon && (
          <div className={`p-2.5 rounded-lg ${c.bg}`}>
            <span className={`h-5 w-5 ${c.icon}`}>{icon}</span>
          </div>
        )}
      </div>
    </div>
  );
}
