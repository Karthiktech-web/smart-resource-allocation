import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Upload,
  FileText,
  CheckCircle,
  Loader2,
  AlertTriangle,
  MapPin,
} from 'lucide-react';
import { digitizeSurvey, getPrograms } from '../lib/api';
import { getUrgencyColor, getCategoryColor } from '../lib/utils';

export default function IngestPage() {
  const [programs, setPrograms] = useState<any[]>([]);
  const [selectedProgram, setSelectedProgram] = useState('');
  const [locationName, setLocationName] = useState('');
  const [lat, setLat] = useState('');
  const [lng, setLng] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState('');

  // Load programs on mount
  useEffect(() => {
    getPrograms()
      .then((res) => setPrograms(res.data))
      .catch(console.error);
  }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
    setResults(null);
    setError('');
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png'],
      'application/pdf': ['.pdf'],
    },
    multiple: true,
  });

  const handleProcess = async () => {
    if (files.length === 0) return;
    setProcessing(true);
    setResults(null);
    setError('');

    try {
      const formData = new FormData();
      formData.append('image', files[0]);
      formData.append('program_id', selectedProgram);
      formData.append('location_name', locationName);
      formData.append('lat', lat || '0');
      formData.append('lng', lng || '0');

      const res = await digitizeSurvey(formData);
      setResults(res.data);
    } catch (err: any) {
      console.error('Processing failed:', err);
      setError(
        err?.response?.data?.detail || 'Processing failed. Please try again.'
      );
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Ingest Data</h1>
        <p className="text-gray-500 text-sm mt-1">
          Upload survey photos and field reports. AI will extract and categorize
          community needs automatically.
        </p>
      </div>

      {/* Step 1: Select Program */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <span className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">
            1
          </span>
          Select Program / Drive
        </h3>
        <select
          value={selectedProgram}
          onChange={(e) => setSelectedProgram(e.target.value)}
          className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">-- Select a program --</option>
          {programs.map((p: any) => (
            <option key={p.id} value={p.id}>
              {p.name} ({p.organization})
            </option>
          ))}
        </select>
      </div>

      {/* Step 2: Upload Files */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <span className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">
            2
          </span>
          Upload Survey Photo
        </h3>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto mb-3 text-gray-400" size={40} />
          <p className="text-gray-600 font-medium">
            Drag & drop survey photos here, or click to browse
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Supports: JPG, PNG, PDF
          </p>
        </div>

        {files.length > 0 && (
          <div className="mt-3 space-y-2">
            {files.map((file, i) => (
              <div
                key={i}
                className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 rounded-lg px-3 py-2"
              >
                <FileText size={16} className="text-blue-500" />
                {file.name}{' '}
                <span className="text-gray-400">
                  ({(file.size / 1024).toFixed(0)} KB)
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Step 3: Location */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <span className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">
            3
          </span>
          Location
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            placeholder="Location name (e.g., Anantapur Village)"
            value={locationName}
            onChange={(e) => setLocationName(e.target.value)}
            className="col-span-1 md:col-span-3 border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            placeholder="Latitude (e.g., 14.68)"
            value={lat}
            onChange={(e) => setLat(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            placeholder="Longitude (e.g., 77.60)"
            value={lng}
            onChange={(e) => setLng(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Process Button */}
      <button
        onClick={handleProcess}
        disabled={files.length === 0 || processing}
        className="w-full bg-blue-600 text-white py-3.5 rounded-xl font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors shadow-sm"
      >
        {processing ? (
          <>
            <Loader2 className="animate-spin" size={20} />
            Processing with AI...
          </>
        ) : (
          <>
            <Upload size={20} />
            Process with AI
          </>
        )}
      </button>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Results */}
      {results && !results.error && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
          <h3 className="font-semibold flex items-center gap-2 text-green-700">
            <CheckCircle size={20} /> Processing Complete
          </h3>

          {/* Raw Text */}
          <div>
            <p className="text-xs text-gray-500 mb-1 font-medium">
              Raw Text (OCR)
            </p>
            <p className="text-sm bg-gray-50 p-3 rounded-lg text-gray-700">
              {results.raw_text?.substring(0, 300)}
              {results.raw_text?.length > 300 ? '...' : ''}
            </p>
          </div>

          {/* Translation */}
          <div>
            <p className="text-xs text-gray-500 mb-1 font-medium">
              Language Detected:{' '}
              <span className="text-blue-600">
                {results.language_detected}
              </span>{' '}
              → Translated to English
            </p>
            <p className="text-sm bg-gray-50 p-3 rounded-lg text-gray-700">
              {results.translated_text?.substring(0, 300)}
              {results.translated_text?.length > 300 ? '...' : ''}
            </p>
          </div>

          {/* Needs Discovered */}
          <div>
            <p className="text-xs text-gray-500 mb-2 font-medium">
              Needs Discovered by AI:
            </p>
            <div className="space-y-2">
              {results.needs_extracted?.map((need: any, i: number) => (
                <div
                  key={i}
                  className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
                >
                  <AlertTriangle
                    size={16}
                    className={
                      need.urgency === 'critical'
                        ? 'text-red-500 mt-0.5'
                        : need.urgency === 'high'
                        ? 'text-orange-500 mt-0.5'
                        : need.urgency === 'medium'
                        ? 'text-yellow-500 mt-0.5'
                        : 'text-green-500 mt-0.5'
                    }
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={`text-xs font-medium uppercase px-2 py-0.5 rounded-full ${getCategoryColor(
                          need.category
                        )}`}
                      >
                        {need.category}
                      </span>
                      <span
                        className={`text-xs font-medium uppercase px-2 py-0.5 rounded-full border ${getUrgencyColor(
                          need.urgency
                        )}`}
                      >
                        {need.urgency}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">{need.description}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      Confidence: {(need.confidence * 100).toFixed(0)}% |
                      People affected: ~{need.estimated_people_affected}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Summary */}
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              <strong>Summary:</strong> {results.summary}
            </p>
            <p className="text-xs text-blue-600 mt-1">
              Sentiment: {results.sentiment} | Overall confidence:{' '}
              {(results.confidence * 100).toFixed(0)}%
            </p>
          </div>
        </div>
      )}
    </div>
  );
}