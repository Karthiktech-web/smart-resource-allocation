import { useState, useEffect } from 'react';
import { getVolunteers, registerVolunteer } from '../lib/api';
import { Plus, MapPin, Star, Clock } from 'lucide-react';

interface Volunteer {
  id: string;
  name: string;
  email: string;
  phone: string;
  location_name: string;
  lat: number;
  lng: number;
  skills: string[];
  availability: string;
  total_hours: number;
  tasks_completed: number;
  reliability_score: number;
  active_assignments: number;
}

interface FormData {
  name: string;
  email: string;
  phone: string;
  location_name: string;
  lat: string;
  lng: string;
  skills: string;
  availability: 'weekdays' | 'weekends' | 'full_time';
}

const INITIAL_FORM_DATA: FormData = {
  name: '',
  email: '',
  phone: '',
  location_name: '',
  lat: '',
  lng: '',
  skills: '',
  availability: 'weekends',
};

export default function VolunteersPage() {
  const [volunteers, setVolunteers] = useState<Volunteer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormData>(INITIAL_FORM_DATA);

  useEffect(() => {
    fetchVolunteers();
  }, []);

  const fetchVolunteers = async () => {
    try {
      setError('');
      const res = await getVolunteers();
      setVolunteers(res.data || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load volunteers';
      setError(message);
      console.error('Failed to load volunteers:', err);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData(INITIAL_FORM_DATA);
    setShowForm(false);
  };

  const validateForm = (): boolean => {
    if (!formData.name.trim() || !formData.email.trim()) {
      setError('Name and email are required');
      return false;
    }

    const lat = parseFloat(formData.lat);
    const lng = parseFloat(formData.lng);

    if (isNaN(lat) || isNaN(lng)) {
      setError('Please enter valid latitude and longitude values');
      return false;
    }

    if (lat < -90 || lat > 90) {
      setError('Latitude must be between -90 and 90');
      return false;
    }

    if (lng < -180 || lng > 180) {
      setError('Longitude must be between -180 and 180');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) return;

    setSubmitting(true);

    try {
      const lat = parseFloat(formData.lat);
      const lng = parseFloat(formData.lng);

      await registerVolunteer({
        ...formData,
        lat,
        lng,
        skills: formData.skills
          .split(',')
          .map(s => s.trim())
          .filter(s => s.length > 0),
        total_hours: 0,
        tasks_completed: 0,
        reliability_score: 0.5,
        active_assignments: 0,
      });

      resetForm();
      await fetchVolunteers();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to register volunteer';
      setError(message);
      console.error('Failed to register volunteer:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse p-6 text-center">Loading volunteers...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Volunteers</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          disabled={submitting}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2 transition"
        >
          <Plus size={16} /> Register Volunteer
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg animate-in">
          {error}
        </div>
      )}

      {/* Registration Form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl border p-6 space-y-4 shadow-sm">
          <div className="grid grid-cols-2 gap-3">
            <input
              placeholder="Full Name"
              required
              disabled={submitting}
              value={formData.name}
              onChange={e => setFormData({ ...formData, name: e.target.value })}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
            <input
              placeholder="Email"
              type="email"
              required
              disabled={submitting}
              value={formData.email}
              onChange={e => setFormData({ ...formData, email: e.target.value })}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
            <input
              placeholder="Phone"
              disabled={submitting}
              value={formData.phone}
              onChange={e => setFormData({ ...formData, phone: e.target.value })}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
            <input
              placeholder="Location"
              disabled={submitting}
              value={formData.location_name}
              onChange={e => setFormData({ ...formData, location_name: e.target.value })}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
            <input
              placeholder="Latitude"
              type="number"
              step="0.000001"
              required
              disabled={submitting}
              value={formData.lat}
              onChange={e => setFormData({ ...formData, lat: e.target.value })}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
            <input
              placeholder="Longitude"
              type="number"
              step="0.000001"
              required
              disabled={submitting}
              value={formData.lng}
              onChange={e => setFormData({ ...formData, lng: e.target.value })}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
          </div>

          <input
            placeholder="Skills (comma-separated): Water purification, First Aid, Teaching"
            disabled={submitting}
            value={formData.skills}
            onChange={e => setFormData({ ...formData, skills: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />

          <select
            value={formData.availability}
            disabled={submitting}
            onChange={e => setFormData({ ...formData, availability: e.target.value as FormData['availability'] })}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          >
            <option value="weekdays">Weekdays</option>
            <option value="weekends">Weekends</option>
            <option value="full_time">Full Time</option>
          </select>

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
            >
              {submitting ? 'Registering...' : 'Register'}
            </button>
            <button
              type="button"
              onClick={resetForm}
              disabled={submitting}
              className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 disabled:bg-gray-200 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Volunteer Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {volunteers.length > 0 ? (
          volunteers.map((vol: Volunteer) => (
            <div
              key={vol.id}
              className="bg-white rounded-xl border p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-800 truncate">{vol.name}</h3>
                <span className="flex items-center gap-1 text-xs text-yellow-600 whitespace-nowrap">
                  <Star size={12} fill="currentColor" /> {(vol.reliability_score * 100).toFixed(0)}%
                </span>
              </div>

              <p className="text-xs text-gray-500 flex items-center gap-1 mb-2 truncate">
                <MapPin size={12} className="flex-shrink-0" /> {vol.location_name}
              </p>

              <div className="flex flex-wrap gap-1 mb-3">
                {(vol.skills || []).map((skill: string, i: number) => (
                  <span key={i} className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full truncate">
                    {skill}
                  </span>
                ))}
              </div>

              <div className="grid grid-cols-3 gap-2 text-xs text-gray-500">
                <div className="flex items-center gap-1">
                  <Clock size={12} className="flex-shrink-0" />
                  <span className="truncate">{vol.total_hours}h</span>
                </div>
                <div className="text-center truncate">{vol.tasks_completed} tasks</div>
                <div className={`text-right truncate ${vol.active_assignments > 0 ? 'text-blue-600' : 'text-green-600'}`}>
                  {vol.active_assignments > 0 ? `${vol.active_assignments} active` : 'Available'}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-12 text-gray-400">
            <p className="text-lg">No volunteers registered yet</p>
            <p className="text-sm">Click "Register Volunteer" to add the first one</p>
          </div>
        )}
      </div>
    </div>
  );
}