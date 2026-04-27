import { useEffect, useState } from 'react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  Heart,
  TrendingUp,
  Users,
  Clock,
  MapPin,
  ShieldCheck,
} from 'lucide-react';
import { getEfficiency, getTrends } from '../lib/api';
import { EmptyState, ErrorState, LoadingState } from '../components/ui/StateDisplay';

const COLORS = ['#4285f4', '#ea4335', '#fbbc05', '#34a853', '#ff6d01', '#46bdc6'];

export default function ImpactPage() {
  const [efficiency, setEfficiency] = useState<any>(null);
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        const [effRes, trendRes] = await Promise.all([
          getEfficiency(),
          getTrends(30),
        ]);
        setEfficiency(effRes.data);
        setTrends(trendRes.data);
      } catch (err) {
        console.error('Impact analytics failed:', err);
        setError('Unable to load impact analytics. Please try again later.');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return <LoadingState text="Loading impact analytics..." />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  const categoryData = Object.entries(trends?.needs_by_category || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value: value as number,
  }));

  const urgencyData = Object.entries(trends?.urgency_distribution || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value: value as number,
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Impact & Analytics</h1>
          <p className="text-sm text-gray-500">Track volunteer efficiency, need resolution, and community impact across your programs.</p>
        </div>
        <div className="rounded-2xl bg-blue-50 px-4 py-3 text-sm text-blue-700">
          Last 30 days of impact analytics
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          icon={<Heart className="text-red-500" />}
          label="People Helped"
          value={trends?.summary?.total_people_helped ?? 0}
        />
        <MetricCard
          icon={<TrendingUp className="text-green-500" />}
          label="Resolution Rate"
          value={`${efficiency?.needs_metrics?.resolution_rate ?? 0}%`}
        />
        <MetricCard
          icon={<Users className="text-blue-500" />}
          label="Volunteer Utilization"
          value={`${efficiency?.volunteer_metrics?.utilization_rate ?? 0}%`}
        />
        <MetricCard
          icon={<Clock className="text-purple-500" />}
          label="Volunteer Hours"
          value={trends?.summary?.total_volunteer_hours ?? 0}
        />
      </div>

      <div className="bg-white rounded-3xl border border-gray-100 p-6 text-center shadow-sm">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between mb-6">
          <div>
            <p className="text-sm text-gray-500 mb-1">Overall Allocation Efficiency Score</p>
            <p className="text-5xl font-bold text-blue-600">{efficiency?.allocation_efficiency?.overall_efficiency_score ?? 0}</p>
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 text-left">
            <StatBlock title="Fill Rate" value={`${efficiency?.allocation_efficiency?.fill_rate ?? 0}%`} />
            <StatBlock title="Coverage" value={`${efficiency?.area_metrics?.coverage_rate ?? 0}%`} />
            <StatBlock title="Critical Areas" value={efficiency?.area_metrics?.critical_areas ?? 0} />
            <StatBlock title="Volunteer Gap" value={efficiency?.area_metrics?.total_volunteer_gap ?? 0} />
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="bg-white rounded-3xl border border-gray-100 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-800">Needs Created vs Resolved</h2>
              <p className="text-sm text-gray-500">Track progress across the last 30 days.</p>
            </div>
            <MapPin size={20} className="text-red-500" />
          </div>
          {trends?.needs_timeline?.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trends.needs_timeline} margin={{ top: 10, right: 0, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="needs_created" stroke="#ea4335" fill="#ea433520" name="Created" />
                <Area type="monotone" dataKey="needs_resolved" stroke="#34a853" fill="#34a85320" name="Resolved" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState title="No needs timeline" description="Collect needs data to see trends over time." />
          )}
        </div>

        <div className="bg-white rounded-3xl border border-gray-100 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-800">People Helped Over Time</h2>
              <p className="text-sm text-gray-500">Measure the impact of volunteer work.</p>
            </div>
            <ShieldCheck size={20} className="text-green-500" />
          </div>
          {trends?.impact_timeline?.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trends.impact_timeline} margin={{ top: 10, right: 0, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="people_helped" fill="#4285f4" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState title="No impact timeline" description="Impact logs will appear here once activities are recorded." />
          )}
        </div>

        <div className="bg-white rounded-3xl border border-gray-100 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Needs by Category</h2>
          {categoryData.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ name, percent }) => `${name}: ${Math.round((percent ?? 0) * 100)}%`}
                >
                  {categoryData.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState title="No category data" description="Needs categories will appear after survey digitization." />
          )}
        </div>

        <div className="bg-white rounded-3xl border border-gray-100 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Urgency Distribution</h2>
          {urgencyData.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={urgencyData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ name, percent }) => `${name}: ${Math.round((percent ?? 0) * 100)}%`}
                >
                  {urgencyData.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState title="No urgency distribution" description="Urgency levels will populate as needs are tagged." />
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | number }) {
  return (
    <div className="rounded-3xl border border-gray-100 bg-white p-5 shadow-sm">
      <div className="mb-4 inline-flex items-center gap-2 rounded-2xl bg-blue-50 px-3 py-2 text-sm text-blue-700">
        {icon}
        <span>{label}</span>
      </div>
      <p className="text-3xl font-semibold text-gray-900">{value}</p>
    </div>
  );
}

function StatBlock({ title, value }: { title: string; value: string | number }) {
  return (
    <div className="rounded-3xl bg-slate-50 p-4 text-center">
      <p className="text-xs uppercase tracking-wide text-gray-500">{title}</p>
      <p className="mt-2 text-xl font-semibold text-gray-900">{value}</p>
    </div>
  );
}
