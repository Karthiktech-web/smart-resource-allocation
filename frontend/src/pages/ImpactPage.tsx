import { useState, useEffect } from 'react';
import { getImpact } from '../lib/api';

export default function ImpactPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getImpact()
      .then(res => setLogs(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6 text-gray-500">Loading impact logs...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">❤️ Impact Logs</h1>
      {logs.length === 0 ? (
        <div className="text-center text-gray-400 py-20">
          <p>No impact logs yet!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {logs.map((log, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-800">{log.description}</h3>
              <div className="flex gap-4 mt-2 text-sm text-gray-600">
                <span>👥 {log.people_helped} helped</span>
                <span>⏰ {log.volunteer_hours} hours</span>
                <span>📂 {log.category}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}