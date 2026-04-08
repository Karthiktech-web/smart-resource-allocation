import { useState, useEffect } from 'react';
import { getNeeds } from '../lib/api';
import { getUrgencyColor } from '../lib/utils';

interface Need {
  id: string;
  title: string;
  description: string;
  category: string;
  urgency: string;
  location_name: string;
  status: string;
}

export default function NeedsPage() {
  const [needs, setNeeds] = useState<Need[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getNeeds()
      .then(res => setNeeds(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6 text-gray-500">Loading needs...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">🆘 Community Needs</h1>
      {needs.length === 0 ? (
        <div className="text-center text-gray-400 py-20">
          <p>No needs found. Add seed data first!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {needs.map(need => (
            <div
              key={need.id}
              className="bg-white rounded-xl shadow-sm border border-gray-100 p-5"
              style={{ borderLeft: `4px solid ${getUrgencyColor(need.urgency)}` }}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-800">{need.title}</h3>
                  <p className="text-sm text-gray-500 mt-1">{need.description}</p>
                  <p className="text-xs text-gray-400 mt-1">📍 {need.location_name}</p>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <span
                    className="text-xs px-2 py-1 rounded-full text-white"
                    style={{ backgroundColor: getUrgencyColor(need.urgency) }}
                  >
                    {need.urgency}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
