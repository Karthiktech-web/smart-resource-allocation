import { useCallback, useEffect, useRef, useState } from 'react';
import { Archive, Loader2, Send } from 'lucide-react';
import { getMessages, getRoom, postMessage } from '../lib/api';

interface Message {
  id: string;
  text: string;
  sender_name?: string;
  sender_uid?: string;
  created_at?: string;
}

export default function TaskRoom({ taskId }: { taskId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState('');
  const [archived, setArchived] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const endRef = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    try {
      setError('');
      const room = (await getRoom(taskId)) as { status?: string };
      setArchived(room.status === 'archived');
      setMessages((await getMessages(taskId)) as Message[]);
    } catch (error) {
      setError('No task room found yet. A room is created when an NGO accepts the task.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    void load();
    const timer = window.setInterval(load, 5000);
    return () => window.clearInterval(timer);
  }, [load]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async () => {
    if (!text.trim()) return;
    const body = text;
    setText('');
    await postMessage(taskId, body);
    await load();
  };

  if (loading) {
    return (
      <div className="flex h-40 items-center justify-center">
        <Loader2 className="animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="flex h-96 flex-col rounded-xl border border-gray-200 bg-white">
      <div className="flex items-center justify-between border-b px-4 py-2">
        <span className="text-sm font-semibold text-gray-700">Task Room</span>
        {archived && (
          <span className="flex items-center gap-1 text-xs text-gray-400">
            <Archive size={12} /> Archived
          </span>
        )}
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto p-4">
        {error ? (
          <p className="text-sm text-amber-600">{error}</p>
        ) : messages.length === 0 ? (
          <p className="text-sm text-gray-400">No messages yet.</p>
        ) : (
          messages.map((message) => (
            <div key={message.id} className="text-sm">
              <span className="font-medium text-gray-700">{message.sender_name || 'User'}: </span>
              <span className="text-gray-600">{message.text}</span>
            </div>
          ))
        )}
        <div ref={endRef} />
      </div>
      {!archived && !error && (
        <div className="flex gap-2 border-t p-3">
          <input
            value={text}
            onChange={(event) => setText(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') void send();
            }}
            placeholder="Message..."
            className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />
          <button
            type="button"
            onClick={() => void send()}
            className="rounded-lg bg-blue-600 px-3 text-white transition hover:bg-blue-700"
            aria-label="Send message"
          >
            <Send size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
