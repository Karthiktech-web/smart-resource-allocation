import { useEffect, useState, useCallback } from 'react';
import { getEvents, toggleEvent, getEventLive, downloadEventReport } from '../lib/api';
import { Radio, FileDown, Loader2 } from 'lucide-react';

type LiveStats = {
  tasks_total: number;
  tasks_verified: number;
  tasks_in_progress: number;
  quantity_delivered: number;
  proofs_submitted: number;
  progress_pct: number;
};

export default function EventModePage() {
  const [events, setEvents] = useState<any[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [live, setLive] = useState<LiveStats | null>(null);
  const [busy, setBusy] = useState(false);

  const loadEvents = useCallback(async () => {
    try {
      const r: any = await getEvents();
      setEvents(r.events ?? []);
      if (!selected && r.events?.length) setSelected(r.events[0].id);
    } catch (e) {
      console.error(e);
    }
  }, [selected]);

  useEffect(() => { loadEvents(); }, [loadEvents]);

  useEffect(() => {
    if (!selected) return;
    let active = true;
    const tick = async () => {
      try {
        const stats = await getEventLive(selected);
        if (active) setLive(stats as LiveStats);
      } catch (e) {
        console.error(e);
      }
    };
    tick();
    const id = setInterval(tick, 5000);
    return () => { active = false; clearInterval(id); };
  }, [selected]);

  const onToggle = async (id: string) => {
    await toggleEvent(id);
    loadEvents();
  };

  const onDownload = async (id: string) => {
    setBusy(true);
    try {
      const blob = await downloadEventReport(id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `event_${id}_report.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setBusy(false);
    }
  };

  const stat = (label: string, value: number | string) => (
    <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
      <div className="text-2xl font-bold text-gray-800">{value}</div>
      <div className="text-xs uppercase tracking-wide text-gray-500">{label}</div>
    </div>
  );

  return (
    <div className="p-4 md:p-6 space-y-6">
      <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
        <Radio size={20} className="text-red-500" /> Event Command Center
      </h1>

      <div className="flex flex-wrap gap-3">
        {events.map((e) => (
          <button
            key={e.id}
            onClick={() => setSelected(e.id)}
            className={`px-3 py-2 rounded-lg border text-sm ${
              selected === e.id ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700'
            }`}
          >
            {e.name} {e.active && <span className="ml-1 text-green-400">●</span>}
          </button>
        ))}
        {events.length === 0 && <p className="text-sm text-gray-500">No events yet.</p>}
      </div>

      {selected && (
        <>
          <div className="flex gap-3">
            <button
              onClick={() => onToggle(selected)}
              className="text-sm bg-gray-800 text-white rounded-lg px-4 py-2 hover:bg-black"
            >
              Toggle Event Mode
            </button>
            <button
              onClick={() => onDownload(selected)}
              disabled={busy}
              className="text-sm bg-red-600 text-white rounded-lg px-4 py-2 hover:bg-red-700 flex items-center gap-2"
            >
              {busy ? <Loader2 size={14} className="animate-spin" /> : <FileDown size={14} />}
              Post-event PDF
            </button>
          </div>

          {live && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {stat('Tasks', live.tasks_total)}
              {stat('Verified', live.tasks_verified)}
              {stat('In progress', live.tasks_in_progress)}
              {stat('Delivered', live.quantity_delivered)}
              {stat('Proofs', live.proofs_submitted)}
              {stat('Progress', `${live.progress_pct}%`)}
            </div>
          )}
        </>
      )}
    </div>
  );
}