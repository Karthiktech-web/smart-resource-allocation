import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getPrograms } from '../lib/api';

interface Program {
  id: string;
  name: string;
  organization: string;
  category: string;
  description: string;
  status: string;
  survey_count: number;
  needs_discovered: number;
}

export default function ProgramsPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPrograms()
      .then(res => setPrograms(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6 text-gray-500">Loading programs...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">📋 Programs</h1>
      {programs.length === 0 ? (
        <div className="text-center text-gray-400 py-20">
          <p>No programs yet. Add seed data first!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {programs.map(p => (
            <Link
              key={p.id}
              to={`/programs/${p.id}`}
              className="block bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:border-blue-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label={`View ${p.name} details`}
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold text-gray-800">{p.name}</h3>
                <span className="text-xs px-2 py-1 rounded-full bg-blue-50 text-blue-600">
                  {p.category}
                </span>
              </div>
              <p className="text-sm text-gray-500 mb-3">{p.description}</p>
              <p className="text-xs text-gray-400">🏢 {p.organization}</p>
              <div className="flex gap-4 mt-3 text-sm">
                <span className="text-gray-600">📊 {p.survey_count} surveys</span>
                <span className="text-gray-600">🆘 {p.needs_discovered} needs</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}