import { useState } from 'react';
import { FileText, Brain, Loader2, AlertTriangle, TrendingUp, Target } from 'lucide-react';
import { generateReport } from '../lib/api';
import { EmptyState, LoadingState } from '../components/ui/StateDisplay';

export default function ReportsPage() {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [days, setDays] = useState(30);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await generateReport(days);
      setReport(res.data);
    } catch (err) {
      console.error(err);
      setError('Could not generate the report. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">AI Impact Reports</h1>
          <p className="text-sm text-gray-500">Generate executive reports for stakeholder review in one click.</p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <select
            value={days}
            onChange={e => setDays(Number(e.target.value))}
            className="rounded-2xl border border-gray-200 bg-white px-4 py-2 text-sm text-gray-700 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button
            type="button"
            onClick={handleGenerate}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-purple-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-purple-700 disabled:bg-gray-300 disabled:text-gray-500"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Brain className="h-4 w-4" />}
            {loading ? 'Generating...' : 'Generate Report'}
          </button>
        </div>
      </div>

      {loading && <LoadingState text="Generating impact report..." />}
      {error && <EmptyState title="Report failed" description={error} />}

      {report && !loading && (
        <div className="space-y-6">
          <div className="rounded-3xl bg-gradient-to-r from-indigo-600 to-blue-600 p-6 text-white shadow-sm">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-blue-100">Impact Report</p>
                <h2 className="text-3xl font-bold">{report.title || 'Impact report'}</h2>
              </div>
              <div className="space-y-1 text-right text-sm text-blue-100">
                <p>Generated: {report.generated_at ?? 'n/a'}</p>
                <p>Range: {report.time_range ?? `${days} days`}</p>
              </div>
            </div>
          </div>

          {report.executive_summary && (
            <div className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center gap-3 text-gray-900">
                <FileText className="h-5 w-5" />
                <h3 className="text-xl font-semibold">Executive Summary</h3>
              </div>
              <p className="whitespace-pre-line text-gray-700">{report.executive_summary}</p>
            </div>
          )}

          {report.key_metrics && (
            <div className="grid gap-4 md:grid-cols-3">
              {Object.entries(report.key_metrics).map(([key, value]) => (
                <div key={key} className="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm">
                  <p className="text-xs uppercase tracking-[0.15em] text-gray-500">{key.replace(/_/g, ' ')}</p>
                  <p className="mt-3 text-2xl font-semibold text-gray-900">{String(value)}</p>
                </div>
              ))}
            </div>
          )}

          {report.success_stories?.length > 0 && (
            <div className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center gap-3 text-gray-900">
                <Target className="h-5 w-5 text-green-600" />
                <h3 className="text-xl font-semibold">Success Stories</h3>
              </div>
              <div className="space-y-3">
                {report.success_stories.map((story: any, index: number) => (
                  <div key={index} className="rounded-2xl bg-green-50 p-4 text-sm text-gray-700">
                    {typeof story === 'string' ? story : JSON.stringify(story)}
                  </div>
                ))}
              </div>
            </div>
          )}

          {report.recommendations?.length > 0 && (
            <div className="rounded-3xl border border-gray-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center gap-3 text-gray-900">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                <h3 className="text-xl font-semibold">Recommendations</h3>
              </div>
              <ol className="space-y-3 list-decimal pl-5 text-sm text-gray-700">
                {report.recommendations.map((item: any, index: number) => (
                  <li key={index}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
                ))}
              </ol>
            </div>
          )}

          {report.risk_alerts?.length > 0 && (
            <div className="rounded-3xl border border-red-200 bg-red-50 p-6 shadow-sm">
              <div className="mb-4 flex items-center gap-3 text-gray-900">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <h3 className="text-xl font-semibold">Risk Alerts</h3>
              </div>
              <div className="space-y-3 text-sm text-gray-700">
                {report.risk_alerts.map((alert: any, index: number) => (
                  <div key={index} className="rounded-2xl bg-red-100 p-4">
                    {typeof alert === 'string' ? alert : JSON.stringify(alert)}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!report && !loading && !error && (
        <EmptyState
          title="No report generated yet"
          description="Click the button above to generate an AI-powered impact report for your current deployment."
        />
      )}
    </div>
  );
}
