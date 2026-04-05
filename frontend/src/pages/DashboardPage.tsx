import { useState, useEffect } from 'react';
import { getDashboard, getHeatmapData } from '../lib/api';
import {
  AlertTriangle,
  Users,
  Heart,
  FileText,
  MapPin,
} from 'lucide-react';
import HeatMap from '../components/HeatMap';
import StatCard from '../components/StatCard';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
} from 'recharts';

// ✅ Types (VERY IMPORTANT)
interface DashboardStats {
  total_needs: number;
  open_needs: number;
  critical_needs: number;
  total_volunteers: number;
  people_helped: number;
  surveys_digitized: number;
  needs_by_category: Record<string, number>;
  urgency_distribution: Record<string, number>;
}

const COLORS = ['#ea4335', '#fbbc05', '#34a853', '#4285f4', '#ff6d01', '#46bdc6'];

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [heatmapData, setHeatmapData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [dashRes, heatRes] = await Promise.all([
          getDashboard(),
          getHeatmapData(),
        ]);

        setStats(dashRes.data);
        setHeatmapData(heatRes.data);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  // ✅ Loading Skeleton
  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-48" />
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-28 bg-gray-200 rounded-xl" />
          ))}
        </div>
        <div className="h-[400px] bg-gray-200 rounded-xl" />
      </div>
    );
  }

  // ✅ Transform Data Safely
  const categoryData =
    stats?.needs_by_category
      ? Object.entries(stats.needs_by_category).map(([name, value]) => ({
          name: name.charAt(0).toUpperCase() + name.slice(1),
          value,
        }))
      : [];

  const urgencyData =
    stats?.urgency_distribution
      ? Object.entries(stats.urgency_distribution).map(([name, value]) => ({
          name: name.charAt(0).toUpperCase() + name.slice(1),
          value,
        }))
      : [];

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
        <span className="text-xs text-gray-400">
          Last updated: {new Date().toLocaleTimeString()}
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard icon={AlertTriangle} label="Total Needs" value={stats?.total_needs ?? 0} color="red" />
        <StatCard icon={AlertTriangle} label="Open Needs" value={stats?.open_needs ?? 0} color="yellow" />
        <StatCard icon={AlertTriangle} label="Critical" value={stats?.critical_needs ?? 0} color="red" />
        <StatCard icon={Users} label="Volunteers" value={stats?.total_volunteers ?? 0} color="blue" />
        <StatCard icon={Heart} label="People Helped" value={stats?.people_helped ?? 0} color="green" />
        <StatCard icon={FileText} label="Surveys" value={stats?.surveys_digitized ?? 0} color="purple" />
      </div>

      {/* Heatmap */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <MapPin size={20} className="text-red-500" />
          Community Needs Heat Map
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          Red = critical areas | Green = low severity
        </p>
        <HeatMap data={heatmapData} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Bar Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 className="font-semibold mb-4">Needs by Category</h3>
          {categoryData.length ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={categoryData}>
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#4285f4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState text="Upload surveys to see charts" />
          )}
        </div>

        {/* Pie Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 className="font-semibold mb-4">Urgency Distribution</h3>
          {urgencyData.length ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={urgencyData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {urgencyData.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState text="No data yet" />
          )}
        </div>

      </div>
    </div>
  );
}

// ✅ Reusable Empty State
function EmptyState({ text }: { text: string }) {
  return (
    <div className="h-[250px] flex items-center justify-center text-gray-400 text-sm">
      {text}
    </div>
  );
}