import { useState } from 'react';
import { Flame, Loader2, ShieldAlert, Truck } from 'lucide-react';
import { anomalyScan, heatmapForecast, synergyScan } from '../lib/api';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

type Zone = {
  area_id: string;
  predicted_intensity: number;
};

type Anomaly = {
  task_id?: string;
  id?: string;
  reasons?: string[];
};

type Synergy = {
  message: string;
};

export default function InsightsPage() {
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [zones, setZones] = useState<Zone[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [synergies, setSynergies] = useState<Synergy[]>([]);
  const [busy, setBusy] = useState<string | null>(null);

  const run = async <T,>(key: string, fn: () => Promise<unknown>, pick: (response: unknown) => T[], set: (value: T[]) => void) => {
    setBusy(key);
    try {
      set(pick(await fn()));
    } catch (error) {
      console.error(error);
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Intelligence</h1>
        <p className="text-sm text-gray-500">
          Forecast demand, scan proof integrity, and find transport-sharing opportunities.
        </p>
      </div>

      <section className="rounded-xl border border-gray-200 bg-white p-4">
        <div className="mb-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="flex items-center gap-2 font-semibold text-gray-700">
            <Flame size={18} className="text-orange-500" /> Predicted hot zones
          </h2>
          <div className="flex items-center gap-2">
            <select
              value={month}
              onChange={(event) => setMonth(Number(event.target.value))}
              className="rounded-lg border border-gray-200 px-2 py-1 text-sm"
            >
              {MONTHS.map((label, index) => (
                <option key={label} value={index + 1}>
                  {label}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() =>
                void run<Zone>(
                  'heatmap',
                  () => heatmapForecast(month),
                  (response) => ((response as { zones?: Zone[] }).zones ?? []),
                  setZones,
                )
              }
              disabled={busy === 'heatmap'}
              className="rounded-lg bg-orange-500 px-3 py-1.5 text-sm text-white transition hover:bg-orange-600 disabled:opacity-60"
            >
              {busy === 'heatmap' ? <Loader2 size={14} className="animate-spin" /> : 'Forecast'}
            </button>
          </div>
        </div>
        <ul className="space-y-1 text-sm text-gray-600">
          {zones.map((zone) => (
            <li key={zone.area_id} className="flex justify-between border-b py-1">
              <span>{zone.area_id}</span>
              <span className="font-medium">intensity {zone.predicted_intensity}</span>
            </li>
          ))}
          {zones.length === 0 && <li className="text-gray-400">No forecast run yet.</li>}
        </ul>
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="flex items-center gap-2 font-semibold text-gray-700">
            <ShieldAlert size={18} className="text-red-500" /> Anomaly scan
          </h2>
          <button
            type="button"
            onClick={() =>
              void run<Anomaly>(
                'anomaly',
                anomalyScan,
                (response) => ((response as { items?: Anomaly[] }).items ?? []),
                setAnomalies,
              )
            }
            disabled={busy === 'anomaly'}
            className="rounded-lg bg-red-500 px-3 py-1.5 text-sm text-white transition hover:bg-red-600 disabled:opacity-60"
          >
            {busy === 'anomaly' ? <Loader2 size={14} className="animate-spin" /> : 'Scan proofs'}
          </button>
        </div>
        <ul className="space-y-1 text-sm text-gray-600">
          {anomalies.map((item, index) => (
            <li key={`${item.id ?? item.task_id ?? 'anomaly'}-${index}`} className="border-b py-1">
              <span className="font-medium">{item.task_id || item.id || 'Proof'}: </span>
              {(item.reasons || []).join('; ')}
            </li>
          ))}
          {anomalies.length === 0 && <li className="text-gray-400">No anomalies shown.</li>}
        </ul>
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="flex items-center gap-2 font-semibold text-gray-700">
            <Truck size={18} className="text-blue-500" /> Logistics synergy
          </h2>
          <button
            type="button"
            onClick={() =>
              void run<Synergy>(
                'synergy',
                synergyScan,
                (response) => ((response as { suggestions?: Synergy[] }).suggestions ?? []),
                setSynergies,
              )
            }
            disabled={busy === 'synergy'}
            className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm text-white transition hover:bg-blue-700 disabled:opacity-60"
          >
            {busy === 'synergy' ? <Loader2 size={14} className="animate-spin" /> : 'Find'}
          </button>
        </div>
        <ul className="space-y-1 text-sm text-gray-600">
          {synergies.map((item, index) => (
            <li key={`${item.message}-${index}`} className="border-b py-1">
              {item.message}
            </li>
          ))}
          {synergies.length === 0 && <li className="text-gray-400">No synergies shown.</li>}
        </ul>
      </section>
    </div>
  );
}
