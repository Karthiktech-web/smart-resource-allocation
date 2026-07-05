import { useState, useEffect } from 'react';
import { getDashboard, getHeatmapData, getAreaPriorities } from '../lib/api';
import { 
  AlertTriangle, 
  Users, 
  Heart, 
  FileText, 
  MapPin, 
  BarChart3, 
  PieChart as PieIcon, 
  Loader2,
  RefreshCcw
} from 'lucide-react';
import HeatMap from '../components/HeatMap';
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
  CartesianGrid, 
  Legend 
} from 'recharts';

type DashboardStats = {
  total_needs?: number;
  open_needs?: number;
  critical_needs?: number;
  total_volunteers?: number;
  people_helped?: number;
  surveys_digitized?: number;
  needs_by_category?: Record<string, number>;
};

type DashboardArea = {
  id: string;
  name?: string;
  area_priority?: string;
  compound_score?: number;
  volunteers_assigned?: number;
  volunteers_recommended?: number;
  volunteer_gap?: number;
  needs_by_category?: Record<string, number>;
  lat: number;
  lng: number;
};

type StatCardProps = {
  icon: React.ComponentType<{ size?: number }>;
  label: string;
  value: string | number;
  color: 'red' | 'yellow' | 'blue' | 'green' | 'purple';
};

const COLORS = ['#ea4335', '#fbbc05', '#4285f4', '#34a853', '#ff6d01', '#46bdc6'];

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [heatmapData, setHeatmapData] = useState<{ lat: number; lng: number; weight?: number }[]>([]);
  const [areas, setAreas] = useState<DashboardArea[]>([]); 
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [dashRes, heatRes, areaRes] = await Promise.all([
        getDashboard(),
        getHeatmapData(),
        getAreaPriorities(), 
      ]);
      setStats(dashRes.data);
      setHeatmapData(heatRes.data);
      setAreas(areaRes.data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
      setError("Synchronizing with Regional Cloud Server failed. Please check connection.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh]">
        <Loader2 className="animate-spin text-blue-600 mb-4" size={48} />
        <h2 className="text-xl font-semibold text-gray-700">SRA Intelligence Engine</h2>
        <p className="text-gray-500 animate-pulse">Aggregating cross-program data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] p-6 text-center">
        <div className="bg-red-50 p-8 rounded-3xl border border-red-100 max-w-md">
          <AlertTriangle className="text-red-500 mx-auto mb-4" size={48} />
          <h2 className="text-lg font-bold text-red-800 mb-2">Connection Error</h2>
          <p className="text-red-600 mb-6">{error}</p>
          <button 
            onClick={fetchData}
            className="flex items-center gap-2 mx-auto px-6 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors"
          >
            <RefreshCcw size={18} /> Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const categoryData = stats?.needs_by_category 
    ? Object.entries(stats.needs_by_category).map(([name, value]) => ({ 
        name: name.charAt(0).toUpperCase() + name.slice(1), 
        value 
      })) 
    : [];

  const urgencyData = [
    { name: 'Critical', value: stats?.critical_needs ?? 0 },
    { name: 'Open', value: (stats?.open_needs ?? 0) - (stats?.critical_needs ?? 0) },
    { name: 'Resolved', value: (stats?.total_needs ?? 0) - (stats?.open_needs ?? 0) }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Operational Overview</h1>
          <p className="text-gray-500">Real-time resource visibility across Andhra Pradesh</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard icon={AlertTriangle} label="Total Needs" value={stats?.total_needs || 0} color="red" />
        <StatCard icon={AlertTriangle} label="Open Needs" value={stats?.open_needs || 0} color="yellow" />
        <StatCard icon={AlertTriangle} label="Critical" value={stats?.critical_needs || 0} color="red" />
        <StatCard icon={Users} label="Volunteers" value={stats?.total_volunteers || 0} color="blue" />
        <StatCard icon={Heart} label="People Helped" value={stats?.people_helped || 0} color="green" />
        <StatCard icon={FileText} label="Surveys" value={stats?.surveys_digitized || 0} color="purple" />
      </div>

      <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6">
        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <MapPin size={24} className="text-red-500" />
            Impact Heat Map
          </h2>
        </div>
        <HeatMap data={heatmapData} areas={areas} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
            <BarChart3 size={20} className="text-blue-500" />
            Needs by Category
          </h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip cursor={{fill: '#f8fafc'}} />
                <Bar dataKey="value" fill="#4285f4" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
            <PieIcon size={20} className="text-red-500" />
            Resolution & Urgency
          </h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={urgencyData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={100}
                  paddingAngle={8}
                  // FIX for Ln 195: Added null check for percent
                  label={({name, percent}) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                >
                  {/* Using the COLORS constant to fix Ln 29 warning */}
                  {urgencyData.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" height={36}/>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }: StatCardProps) {
  const colorMap: Record<StatCardProps['color'], string> = {
    red: 'text-red-600 bg-red-50',
    yellow: 'text-yellow-600 bg-yellow-50',
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    purple: 'text-purple-600 bg-purple-50',
  };
  
  return (
    <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-5">
      <div className={`w-12 h-12 rounded-2xl ${colorMap[color]} flex items-center justify-center mb-4`}>
        <Icon size={24} />
      </div>
      <p className="text-4xl font-black text-gray-800 tracking-tight">{value.toLocaleString()}</p>
      <p className="text-xs font-bold text-gray-400 mt-2 uppercase tracking-widest">{label}</p>
    </div>
  );
}