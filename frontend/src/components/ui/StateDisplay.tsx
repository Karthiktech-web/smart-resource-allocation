import { AlertTriangle, CircleDollarSign, Loader2 } from 'lucide-react';

export function LoadingState({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-3xl border border-gray-200 bg-white p-8 text-center shadow-sm">
      <Loader2 className="mb-4 h-10 w-10 animate-spin text-blue-500" />
      <p className="text-gray-600">{text}</p>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-3xl border border-red-100 bg-red-50 p-8 text-center shadow-sm">
      <AlertTriangle className="mb-4 h-10 w-10 text-red-500" />
      <p className="mb-2 text-lg font-semibold text-red-700">Something went wrong</p>
      <p className="mb-4 text-sm text-red-600 max-w-md">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-full bg-red-600 px-6 py-2 text-sm font-semibold text-white transition hover:bg-red-700"
        >
          Retry
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-3xl border border-gray-200 bg-white p-8 text-center shadow-sm">
      <CircleDollarSign className="mb-4 h-10 w-10 text-gray-400" />
      <p className="mb-2 text-lg font-semibold text-gray-800">{title}</p>
      <p className="text-sm text-gray-500 max-w-md">{description}</p>
    </div>
  );
}
