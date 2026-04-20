import { useState, useEffect } from 'react';
import {
  getAreaPriorities,
  getAllocationRecommendation,
  approveAllocation,
} from '../lib/api';
import {
  Users,
  MapPin,
  Brain,
  CheckCircle,
  Loader2,
} from 'lucide-react';

export default function AllocatePage() {
  const [areas, setAreas] = useState<any[]>([]);
  const [plan, setPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [approving, setApproving] = useState(false);
  const [approved, setApproved] = useState(false);

  // Fetch Areas
  useEffect(() => {
    async function fetchData() {
      try {
        const res = await getAreaPriorities();
        setAreas(res?.data || []);
      } catch (err) {
        console.error('Failed to load areas:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Generate AI Plan
  const handleGeneratePlan = async () => {
    setGenerating(true);
    try {
      const res = await getAllocationRecommendation();
      setPlan(res?.data || null);
      setApproved(false); // reset approval if new plan
    } catch (err) {
      console.error('Failed to generate plan:', err);
    } finally {
      setGenerating(false);
    }
  };

  // Approve Plan
  const handleApprovePlan = async () => {
    if (!plan?.allocations) return;

    setApproving(true);
    try {
      await approveAllocation(plan.allocations);
      setApproved(true);
    } catch (err) {
      console.error('Failed to approve:', err);
    } finally {
      setApproving(false);
    }
  };

  // Loading UI
  if (loading) {
    return (
      <div className="flex items-center gap-2 p-6">
        <Loader2 className="animate-spin" size={20} />
        Loading allocation data...
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4">

      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">
          Smart Allocation
        </h1>

        <button
          onClick={handleGeneratePlan}
          disabled={generating}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 flex items-center gap-2"
        >
          {generating ? (
            <>
              <Loader2 className="animate-spin" size={16} />
              Generating...
            </>
          ) : (
            <>
              <Brain size={16} />
              Generate AI Plan
            </>
          )}
        </button>
      </div>

      {/* Priority Areas */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <MapPin size={18} className="text-red-500" />
          Priority Areas (Ranked by AI)
        </h2>

        {areas.length === 0 && (
          <p className="text-sm text-gray-500">No areas found</p>
        )}

        <div className="space-y-3">
          {areas.map((area: any, i: number) => (
            <div
              key={area.id || i}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
            >
              <div className="flex items-center gap-4">
                <span className="text-lg font-bold text-gray-400 w-6">
                  #{i + 1}
                </span>

                <div>
                  <p className="font-medium text-gray-800">
                    {area?.name || 'Unknown Area'}
                  </p>

                  <p className="text-xs text-gray-500">
                    {Object.entries(area?.needs_by_category || {})
                      .map(([k, v]) => `${k}: ${v}`)
                      .join(' | ')}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4 text-sm">
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    area?.area_priority === 'critical'
                      ? 'bg-red-100 text-red-700'
                      : area?.area_priority === 'high'
                      ? 'bg-orange-100 text-orange-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}
                >
                  Score: {area?.compound_score ?? 0}
                </span>

                <span className="text-gray-500">
                  <Users size={14} className="inline mr-1" />
                  {area?.volunteers_assigned ?? 0}/
                  {area?.volunteers_recommended ?? 0}

                  {area?.volunteer_gap > 0 && (
                    <span className="text-red-500 ml-1">
                      (gap: {area.volunteer_gap})
                    </span>
                  )}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Allocation Plan */}
      {plan && (
        <div className="bg-white rounded-xl border p-6">
          <h2 className="font-semibold mb-2 flex items-center gap-2">
            <Brain size={18} className="text-purple-500" />
            AI Allocation Plan
          </h2>

          <p className="text-sm text-gray-500 mb-4">
            {plan?.plan_summary || 'No summary available'}
          </p>

          <div className="space-y-4">
            {plan?.allocations?.map((alloc: any, i: number) => (
              <div
                key={i}
                className="border rounded-lg p-4 bg-purple-50"
              >
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="font-medium text-gray-800">
                      {alloc?.volunteer_name}
                    </span>
                    <span className="mx-2 text-gray-400">→</span>
                    <span className="font-medium text-purple-700">
                      {alloc?.area_name}
                    </span>
                  </div>

                  <span className="text-xs text-gray-500">
                    {alloc?.estimated_hours ?? 0}h | ~
                    {alloc?.estimated_impact ?? 0} people
                  </span>
                </div>

                <p className="text-xs text-gray-600 mb-2">
                  {alloc?.reason}
                </p>

                <div className="flex flex-wrap gap-1">
                  {alloc?.action_steps?.map((step: string, j: number) => (
                    <span
                      key={j}
                      className="text-xs bg-white px-2 py-1 rounded border"
                    >
                      {step}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Approve Button */}
          {!approved && (
            <button
              onClick={handleApprovePlan}
              disabled={approving}
              className="mt-4 w-full py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 disabled:bg-gray-300 flex items-center justify-center gap-2"
            >
              {approving ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Approving...
                </>
              ) : (
                <>
                  <CheckCircle size={20} />
                  Approve Allocation Plan
                </>
              )}
            </button>
          )}

          {/* Approved Message */}
          {approved && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-xl text-center">
              <CheckCircle
                size={24}
                className="mx-auto mb-2 text-green-600"
              />
              <p className="font-medium text-green-800">
                Allocation Plan Approved!
              </p>
              <p className="text-sm text-green-600">
                Volunteers have been assigned and notified.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}