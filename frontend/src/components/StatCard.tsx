import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: number | string;
  color: 'red' | 'yellow' | 'blue' | 'green' | 'purple' | 'orange';
  subtitle?: string;
}

const colorMap = {
  red: 'text-red-500 bg-red-50',
  yellow: 'text-yellow-500 bg-yellow-50',
  blue: 'text-blue-500 bg-blue-50',
  green: 'text-green-500 bg-green-50',
  purple: 'text-purple-500 bg-purple-50',
  orange: 'text-orange-500 bg-orange-50',
};

export default function StatCard({ icon: Icon, label, value, color, subtitle }: StatCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-shadow">
      <div className={`w-10 h-10 rounded-lg ${colorMap[color]} flex items-center justify-center mb-3`}>
        <Icon size={20} />
      </div>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
      <p className="text-xs text-gray-500 mt-0.5">{label}</p>
      {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
    </div>
  );
}