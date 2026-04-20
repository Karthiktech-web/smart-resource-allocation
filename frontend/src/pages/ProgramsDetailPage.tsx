

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  getProgramById,
  getProgramSurveys,
  getProgramNeeds,
} from '../lib/api';
import { FileText, AlertTriangle, Loader2 } from 'lucide-react';

export default function ProgramDetailPage() {
  const { id } = useParams();

  const [program, setProgram] = useState<any>(null);
  const [surveys, setSurveys] = useState<any[]>([]);
  const [needs, setNeeds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch Data
  useEffect(() => {
    if (!id) return;

    async function fetchData() {
      try {
        const [progRes, surveyRes, needsRes] = await Promise.all([
          getProgramById(id),
          getProgramSurveys(id),
          getProgramNeeds(id),
        ]);

        setProgram(progRes?.data || null);
        setSurveys(surveyRes?.data || []);
        setNeeds(needsRes?.data || []);
      } catch (err) {
        console.error('Failed to load program:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [id]);

  // Loading UI
  if (loading) {
    return (
      <div className="flex items-center gap-2 p-6">
        <Loader2 className="animate-spin" size={20} />
        Loading program...
      </div>
    );
  }

  // Not Found
  if (!program) {
    return <div className="p-6 text-red-500">Program not found</div>;
  }

  return (
    <div className="space-y-6 p-4">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800">
          {program?.name || 'Unknown Program'}
        </h1>
        <p className="text-gray-500">
          {program?.organization} | {program?.category}
        </p>
        <p className="text-sm text-gray-600 mt-2">
          {program?.description}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Surveys" value={surveys.length} color="text-blue-600" />
        <StatCard label="Needs Discovered" value={needs.length} color="text-red-600" />
        <StatCard
          label="Regions"
          value={(program?.regions || []).join(', ') || 'N/A'}
          color="text-green-600"
        />
      </div>

      {/* Surveys List */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <FileText size={18} /> Surveys ({surveys.length})
        </h2>

        {surveys.length === 0 && (
          <p className="text-sm text-gray-500">No surveys found</p>
        )}

        {surveys.map((s: any) => (
          <div key={s.id} className="border-b py-3 last:border-0">
            <p className="text-sm font-medium">
              {s?.location_name || 'Unknown Location'}
            </p>

            <p className="text-xs text-gray-500">
              {s?.source_type} | Language: {s?.language_detected || 'en'} | Needs found: {s?.ai_analysis?.needs_extracted?.length || 0}
            </p>
          </div>
        ))}
      </div>

      {/* Needs List */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle size={18} /> Discovered Needs ({needs.length})
        </h2>

        {needs.length === 0 && (
          <p className="text-sm text-gray-500">No needs found</p>
        )}

        {needs.map((n: any) => (
          <div key={n.id} className="border-b py-3 last:border-0">
            <div className="flex items-center gap-2 mb-1">
              <span
                className={`text-xs font-medium uppercase px-2 py-0.5 rounded-full ${
                  n?.urgency === 'critical'
                    ? 'bg-red-100 text-red-700'
                    : n?.urgency === 'high'
                    ? 'bg-orange-100 text-orange-700'
                    : 'bg-yellow-100 text-yellow-700'
                }`}
              >
                {n?.urgency || 'medium'}
              </span>

              <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                {n?.category || 'General'}
              </span>
            </div>

            <p className="text-sm">
              {n?.title || 'No title available'}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

// Reusable Stat Card
function StatCard({ label, value, color }: any) {
  return (
    <div className="bg-white rounded-xl border p-4 text-center">
      <p className={`text-2xl font-bold ${color}`}>
        {value ?? 0}
      </p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  );
}