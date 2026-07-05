import { useEffect, useState } from 'react';
import { Activity, CheckCircle, ListChecks, Loader2, MessageSquare, RotateCcw, ShieldCheck } from 'lucide-react';
import ProofUpload from '../components/ProofUpload';
import TaskRoom from '../components/TaskRoom';
import { broadcastTask, getTasks, matchTask, requeueScan, verifyTask } from '../lib/api';

type Task = {
  id: string;
  need_id?: string;
  title?: string;
  category?: string;
  quantity?: number;
  unit?: string;
  area_id?: string;
  lat?: number;
  lng?: number;
  status?: string;
  parent_task_id?: string | null;
  assigned_ngo_id?: string;
  created_at?: string;
  updated_at?: string;
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyTaskId, setBusyTaskId] = useState<string | null>(null);
  const [busyRequeue, setBusyRequeue] = useState(false);
  const [expandedTaskId, setExpandedTaskId] = useState<string | null>(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadTasks();
  }, []);

  async function loadTasks() {
    setLoading(true);
    setMessage('');
    try {
      const response = await getTasks();
      setTasks(response as Task[]);
    } catch (error) {
      setMessage('Unable to load tasks.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  async function handleBroadcast(taskId: string) {
    setBusyTaskId(taskId);
    setMessage('');
    try {
      const result = await broadcastTask(taskId, 3) as {
        split: boolean;
        subtask_ids: string[];
      };
      setMessage(
        result.split
          ? `Task broadcast and split into ${result.subtask_ids.length} subtasks.`
          : 'Task broadcast successfully.'
      );
      await loadTasks();
    } catch (error) {
      setMessage('Broadcast failed.');
      console.error(error);
    } finally {
      setBusyTaskId(null);
    }
  }

  async function handleMatch(taskId: string) {
    setBusyTaskId(taskId);
    setMessage('');
    try {
      const result = await matchTask(taskId) as { candidates: unknown[] };
      setMessage(`Matched ${result.candidates.length} candidate NGOs.`);
    } catch (error) {
      setMessage('Match failed.');
      console.error(error);
    } finally {
      setBusyTaskId(null);
    }
  }

  async function handleRequeue() {
    setBusyRequeue(true);
    setMessage('');
    try {
      const result = await requeueScan() as { count: number };
      setMessage(`Requeue scan completed: ${result.count} tasks requeued.`);
      await loadTasks();
    } catch (error) {
      setMessage('Requeue scan failed.');
      console.error(error);
    } finally {
      setBusyRequeue(false);
    }
  }

  async function handleVerify(task: Task) {
    if (!task.assigned_ngo_id) {
      setMessage('Assign an NGO before verifying this task.');
      return;
    }
    setBusyTaskId(task.id);
    setMessage('');
    try {
      await verifyTask(task.id, task.assigned_ngo_id);
      setMessage('Task verified, room archived, and NGO completion credited.');
      await loadTasks();
    } catch (error) {
      setMessage('Verification failed.');
      console.error(error);
    } finally {
      setBusyTaskId(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Task Board</h1>
          <p className="text-sm text-gray-500">
            Review open tasks, match them to NGOs, broadcast assignments, and requeue stale work.
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <button
            type="button"
            onClick={loadTasks}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
          >
            <RotateCcw size={16} /> Refresh
          </button>
          <button
            type="button"
            onClick={handleRequeue}
            disabled={busyRequeue}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:opacity-60"
          >
            {busyRequeue ? <Loader2 size={16} className="animate-spin" /> : <Activity size={16} />}
            Requeue Scan
          </button>
        </div>
      </div>

      {message && (
        <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-700">
          {message}
        </div>
      )}

      {loading ? (
        <div className="rounded-xl border border-gray-200 bg-white p-8 text-center text-gray-500">
          <Loader2 className="mx-auto mb-3 animate-spin" size={24} />
          Loading tasks...
        </div>
      ) : tasks.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white p-10 text-center text-gray-500">
          <ListChecks size={32} className="mx-auto mb-3 text-gray-400" />
          No tasks found. Ingest data or create needs to start task generation.
        </div>
      ) : (
        <div className="grid gap-4">
          {tasks.map((task) => (
            <div key={task.id} className="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm">
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2 text-sm text-gray-500">
                    <span className="rounded-full bg-slate-100 px-2 py-1">Status: {task.status || 'unknown'}</span>
                    {task.parent_task_id && (
                      <span className="rounded-full bg-slate-100 px-2 py-1">Subtask</span>
                    )}
                  </div>
                  <h2 className="mt-3 text-xl font-semibold text-gray-900">{task.title || 'Untitled task'}</h2>
                  <p className="mt-1 text-sm text-gray-600">
                    {task.category || 'General'} · {task.quantity ?? 0} {task.unit || 'units'}
                  </p>
                </div>
                <div className="flex flex-col gap-2 sm:flex-row">
                  <button
                    type="button"
                    onClick={() => setExpandedTaskId((current) => (current === task.id ? null : task.id))}
                    className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
                  >
                    <MessageSquare size={14} />
                    Collaborate
                  </button>
                  <button
                    type="button"
                    onClick={() => handleMatch(task.id)}
                    disabled={busyTaskId === task.id}
                    className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-60"
                  >
                    {busyTaskId === task.id ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle size={14} />}
                    Match
                  </button>
                  <button
                    type="button"
                    onClick={() => handleBroadcast(task.id)}
                    disabled={busyTaskId === task.id}
                    className="inline-flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-purple-700 disabled:opacity-60"
                  >
                    {busyTaskId === task.id ? <Loader2 size={14} className="animate-spin" /> : <ListChecks size={14} />}
                    Broadcast
                  </button>
                  <button
                    type="button"
                    onClick={() => handleVerify(task)}
                    disabled={busyTaskId === task.id || !task.assigned_ngo_id || task.status === 'verified'}
                    className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700 disabled:opacity-60"
                  >
                    {busyTaskId === task.id ? <Loader2 size={14} className="animate-spin" /> : <ShieldCheck size={14} />}
                    Verify
                  </button>
                </div>
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-xs uppercase tracking-wide text-gray-500">Need ID</p>
                  <p className="mt-2 text-sm font-medium text-gray-800">{task.need_id || '—'}</p>
                </div>
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-xs uppercase tracking-wide text-gray-500">Area</p>
                  <p className="mt-2 text-sm font-medium text-gray-800">{task.area_id || 'Unknown'}</p>
                </div>
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-xs uppercase tracking-wide text-gray-500">NGO assigned</p>
                  <p className="mt-2 text-sm font-medium text-gray-800">{task.assigned_ngo_id || 'None'}</p>
                </div>
              </div>

              {expandedTaskId === task.id && (
                <div className="mt-4 grid gap-4 lg:grid-cols-2">
                  <TaskRoom taskId={task.id} />
                  <ProofUpload taskId={task.id} />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
