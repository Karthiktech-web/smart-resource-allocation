import { useState } from 'react';
import { AlertTriangle, CheckCircle2, Loader2, Upload } from 'lucide-react';
import { uploadProof } from '../lib/api';

interface ProofResult {
  validation?: {
    valid?: boolean;
    reason?: string;
    distance_km?: number | null;
  };
  flagged?: boolean;
}

export default function ProofUpload({ taskId }: { taskId: string }) {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<ProofResult | null>(null);

  const submit = async () => {
    if (!file) return;
    setBusy(true);
    try {
      setResult((await uploadProof(taskId, file)) as ProofResult);
    } catch (error) {
      console.error(error);
    } finally {
      setBusy(false);
    }
  };

  const valid = result?.validation?.valid;

  return (
    <div className="space-y-3 rounded-xl border border-gray-200 bg-white p-4">
      <h3 className="flex items-center gap-2 text-sm font-semibold text-gray-700">
        <Upload size={16} /> Proof of work
      </h3>
      <input
        type="file"
        accept="image/*"
        onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        className="block text-sm"
      />
      <button
        type="button"
        onClick={() => void submit()}
        disabled={!file || busy}
        className="flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm text-white transition hover:bg-blue-700 disabled:opacity-50"
      >
        {busy ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
        Upload &amp; verify
      </button>

      {result && (
        <div
          className={`flex items-start gap-2 rounded-lg p-3 text-sm ${
            valid ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'
          }`}
        >
          {valid ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
          <span>{result.validation?.reason || (valid ? 'Verified' : 'Flagged for review')}</span>
        </div>
      )}
    </div>
  );
}
