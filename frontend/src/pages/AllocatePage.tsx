import { useState, useEffect } from 'react';
import { getAllocation } from '../lib/api';

export default function AllocatePage() {
  const [plan, setPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAllocation()
      .then(res => setPlan(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6 text-gray-500">Loading allocation plan...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">🤖 AI Allocation Plan</h1>
      {plan?.recommendations?.length === 0 ? (
        <div className="text-center text-gray-400 py-20">
          <p>No recommendations yet. Add needs and volunteers first!</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="bg-blue-50 rounded-xl p-4 mb-4">
            <p className="text-blue-800 text-sm">{plan?.ai_summary}</p>
          </div>
          {plan?.recommendations?.map((rec: any, i: number) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-800">{rec.need_title}</h3>
              <p className="text-sm text-gray-600 mt-1">
                👤 Recommended: {rec.recommended_volunteer_name}
              </p>
              <p className="text-sm text-gray-500 mt-1">{rec.reasoning}</p>
              <div className="flex gap-2 mt-2">
                <span className="text-xs px-2 py-1 bg-green-50 text-green-600 rounded-full">
                  Match: {(rec.match_score * 100).toFixed(0)}%
                </span>
                <span className="text-xs px-2 py-1 bg-red-50 text-red-600 rounded-full">
                  {rec.need_urgency}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}