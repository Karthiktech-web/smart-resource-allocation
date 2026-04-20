import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import API from '../lib/api';

export default function AreaDetailPage() {
  const { id } = useParams();
  const [area, setArea] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadArea = async () => {
    try {
      const res = await API.get(`/api/areas/${id}`);
      setArea(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const refreshInsights = async () => {
    if (!id) return;

    setRefreshing(true);
    try {
      const res = await API.get(`/api/areas/${id}/insights`);
      const result = res.data;
      const updatedInsights = result.analysis?.cross_program_insights || area?.ai_insights || [];

      setAnalysis(result.analysis || null);
      setArea((prev: any) => ({
        ...prev,
        ...result,
        ai_insights: updatedInsights,
        compound_score: result.analysis?.compound_score ?? prev?.compound_score,
        area_priority: result.analysis?.area_priority ?? prev?.area_priority,
        volunteers_recommended: result.analysis?.total_volunteers_recommended ?? prev?.volunteers_recommended,
        volunteer_gap: result.volunteer_gap ?? prev?.volunteer_gap,
      }));
    } catch (err) {
      console.error(err);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const initialize = async () => {
      setLoading(true);
      await loadArea();
      setLoading(false);
    };

    initialize();
  }, [id]);

  useEffect(() => {
    if (area && area.ai_insights?.length === 0) {
      refreshInsights();
    }
  }, [area]);

  if (loading) return <div className="p-6 text-gray-500">Loading area...</div>;

  return (
    <div className="p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-800">🗺️ {area?.name}</h1>
        <button
          className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
          onClick={refreshInsights}
          disabled={refreshing}
        >
          {refreshing ? 'Refreshing insights…' : 'Refresh AI Insights'}
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 space-y-3">
        <div className="grid gap-3 sm:grid-cols-2">
          <p className="text-gray-600">📍 {area?.district}, {area?.state}</p>
          <p className="text-gray-600">Last analyzed: {area?.last_analyzed_at || 'Not analyzed yet'}</p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <p className="text-gray-600">Total Needs: {area?.total_needs}</p>
          <p className="text-gray-600">Priority: {area?.area_priority}</p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <p className="text-gray-600">Score: {area?.compound_score}</p>
          <p className="text-gray-600">Volunteer gap: {area?.volunteer_gap ?? '—'}</p>
        </div>
      </div>

      {area?.ai_insights?.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mt-6">
          <h3 className="text-lg font-semibold mb-3">AI Insights</h3>
          {area.ai_insights.map((insight: string, i: number) => (
            <p key={i} className="text-sm text-gray-600 mb-2">• {insight}</p>
          ))}
        </div>
      )}

      {analysis && (
        <div className="grid gap-4 sm:grid-cols-2 mt-6">
          {analysis.skill_mix_needed?.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h4 className="font-semibold mb-2">Skill mix needed</h4>
              {analysis.skill_mix_needed.map((skill: string, index: number) => (
                <p key={index} className="text-sm text-gray-600 mb-1">• {skill}</p>
              ))}
            </div>
          )}

          {analysis.risk_factors?.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h4 className="font-semibold mb-2">Risk factors</h4>
              {analysis.risk_factors.map((risk: string, index: number) => (
                <p key={index} className="text-sm text-gray-600 mb-1">• {risk}</p>
              ))}
            </div>
          )}

          {analysis.recommended_actions?.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 sm:col-span-2">
              <h4 className="font-semibold mb-2">Recommended actions</h4>
              {analysis.recommended_actions.map((action: string, index: number) => (
                <p key={index} className="text-sm text-gray-600 mb-1">• {action}</p>
              ))}
            </div>
          )}

          {analysis.estimated_impact && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 sm:col-span-2">
              <h4 className="font-semibold mb-2">Estimated impact</h4>
              <p className="text-sm text-gray-600">{analysis.estimated_impact}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
