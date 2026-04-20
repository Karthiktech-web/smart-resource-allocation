import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getAreaById, getAreaNeeds, getAreaInsights } from '../lib/api';
import { TrendingUp, Brain, Loader2 } from 'lucide-react';

export default function AreaDetailPage() {
  const { id } = useParams();

  const [area, setArea] = useState<any>(null);
  const [needs, setNeeds] = useState<any[]>([]);
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [analyzingInsights, setAnalyzingInsights] = useState(false);

  // Fetch Area Data
  useEffect(() => {
    if (!id) return;

    async function fetchData() {
      try {
        const [areaRes, needsRes] = await Promise.all([
          getAreaById(id),
          getAreaNeeds(id),
        ]);

        setArea(areaRes?.data || null);
        setNeeds(needsRes?.data || []);
      } catch (err) {
        console.error('Failed to load area:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [id]);

  // AI Insights
  const handleAnalyze = async () => {
    if (!id) return;

    setAnalyzingInsights(true);
    try {
      const res = await getAreaInsights(id);
      setInsights(res?.data || null);
    } catch (err) {
      console.error('Failed to get insights:', err);
    } finally {
      setAnalyzingInsights(false);
    }
  };

  // Loading UI
  if (loading) {
    return (
      <div className="flex items-center gap-2 p-6">
        <Loader2 className="animate-spin" size={20} />
        Loading area details...
      </div>
    );
  }

  // Invalid Area
  if (!area) {
    return <div className="p-6 text-red-500">Area not found</div>;
  }

  // Priority Colors
  const priorityColors: any = {
    critical: 'bg-red-100 text-red-800 border-red-300',
    high: 'bg-orange-100 text-orange-800 border-orange-300',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    low: 'bg-green-100 text-green-800 border-green-300',
  };

  // Safe Insights List
  const insightList = Array.isArray(insights?.analysis?.cross_program_insights)
    ? insights.analysis.cross_program_insights
    : Array.isArray(area?.ai_insights)
    ? area.ai_insights
    : [];

  return (
    <div className="space-y-6 p-4">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            {area?.name || 'Unknown Area'}
          </h1>
          <p className="text-gray-500">
            {area?.district}, {area?.state}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium border ${
              priorityColors[area?.area_priority] || priorityColors.low
            }`}
          >
            {(area?.area_priority || 'low').toUpperCase()} PRIORITY
          </span>

          <span className="text-3xl font-bold text-gray-800">
            {area?.compound_score || 0}/10
          </span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard label="Total Needs" value={area?.total_needs} />
        <StatCard label="Open Needs" value={area?.open_needs} color="text-red-600" />
        <StatCard label="Critical" value={area?.critical_needs_count} color="text-red-700" />
        <StatCard
          label="Volunteers"
          value={`${area?.volunteers_assigned || 0}/${area?.volunteers_recommended || 0}`}
          color="text-blue-600"
        />
        <StatCard label="Volunteer Gap" value={area?.volunteer_gap} color="text-orange-600" />
      </div>

      {/* Needs by Category */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold mb-3">Needs by Category</h2>

        <div className="flex flex-wrap gap-2">
          {Object.entries(area?.needs_by_category || {}).map(([cat, count]) => (
            <span
              key={cat}
              className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
            >
              {cat}: {count as number}
            </span>
          ))}
        </div>
      </div>

      {/* AI Insights */}
      <div className="bg-white rounded-xl border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold flex items-center gap-2">
            <Brain size={20} className="text-purple-500" />
            AI Cross-Program Insights
          </h2>

          <button
            onClick={handleAnalyze}
            disabled={analyzingInsights}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 disabled:bg-gray-300 flex items-center gap-2"
          >
            {analyzingInsights ? (
              <>
                <Loader2 className="animate-spin" size={16} />
                Analyzing...
              </>
            ) : (
              'Re-Analyze with AI'
            )}
          </button>
        </div>

        {insightList.length === 0 && (
          <p className="text-sm text-gray-500">No insights available</p>
        )}

        {insightList.map((insight: string, i: number) => (
          <div
            key={i}
            className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg mb-2"
          >
            <TrendingUp size={16} className="text-purple-500 mt-0.5" />
            <p className="text-sm text-gray-700">{insight}</p>
          </div>
        ))}
      </div>

      {/* Needs List */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold mb-4">All Needs ({needs.length})</h2>

        <div className="space-y-3">
          {needs.map((need: any) => (
            <div key={need.id} className="border rounded-lg p-4 hover:bg-gray-50">
              <div className="flex justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-800">
                    {need.title}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {need.description?.slice(0, 120)}...
                  </p>
                </div>

                <span className="text-xs px-2 py-1 rounded-full bg-gray-100">
                  {need.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Programs */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold mb-3">Active Programs</h2>

        <p className="text-sm text-gray-500">
          {area?.programs_active?.length || 0} NGO programs active in this area.
        </p>
      </div>
    </div>
  );
}

// Reusable Stat Card
function StatCard({ label, value, color = 'text-gray-800' }: any) {
  return (
    <div className="bg-white rounded-xl border p-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>
        {value ?? 0}
      </p>
    </div>
  );
}