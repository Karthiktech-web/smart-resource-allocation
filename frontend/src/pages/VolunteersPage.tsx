import { useState, useEffect } from 'react';
import { getVolunteers } from '../lib/api';

interface Volunteer {
  id: string;
  name: string;
  email: string;
  phone: string;
  location_name: string;
  skills: string[];
  availability: string;
  reliability_score: number;
  tasks_completed: number;
}

export default function VolunteersPage() {
  const [volunteers, setVolunteers] = useState<Volunteer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getVolunteers()
      .then(res => setVolunteers(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6 text-gray-500">Loading volunteers...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">🙋 Volunteers</h1>
      {volunteers.length === 0 ? (
        <div className="text-center text-gray-400 py-20">
          <p>No volunteers yet. Add seed data first!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {volunteers.map(v => (
            <div key={v.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-800">{v.name}</h3>
              <p className="text-sm text-gray-500">{v.email}</p>
              <p className="text-xs text-gray-400 mt-1">📍 {v.location_name}</p>
              <p className="text-xs text-gray-400">⏰ {v.availability}</p>
              <div className="flex flex-wrap gap-1 mt-3">
                {v.skills?.map(s => (
                  <span key={s} className="text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-600">
                    {s}
                  </span>
                ))}
              </div>
              <div className="flex gap-4 mt-3 text-xs text-gray-500">
                <span>⭐ {v.reliability_score?.toFixed(1)}</span>
                <span>✅ {v.tasks_completed} tasks</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}