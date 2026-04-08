import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import API from '../lib/api';

export default function AreaDetailPage() {
  const { id } = useParams();
  const [area, setArea] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.get(`/api/areas/${id}`)
      .then(res => setArea(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="p-6 text-gray-500">Loading area...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">🗺️ {area?.name}</h1>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <p className="text-gray-600">📍 {area?.district}, {area?.state}</p>
        <p className="text-gray-600 mt-2">Total Needs: {area?.total_needs}</p>
        <p className="text-gray-600">Priority: {area?.area_priority}</p>
        <p className="text-gray-600">Score: {area?.compound_score}</p>
        {area?.ai_insights?.length > 0 && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">AI Insights:</h3>
            {area.ai_insights.map((insight: string, i: number) => (
              <p key={i} className="text-sm text-gray-600 mb-1">• {insight}</p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}