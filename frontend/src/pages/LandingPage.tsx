import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { publicScorecards, publicGallery, publicDirectory } from '../lib/api';
import { ShieldCheck, Users, Droplets, HeartHandshake } from 'lucide-react';

type Scorecards = {
  ngos_registered: number;
  tasks_completed: number;
  lives_impacted: number;
  needs_resolved: number;
  verified_stories: number;
};

export default function LandingPage() {
  const [cards, setCards] = useState<Scorecards | null>(null);
  const [stories, setStories] = useState<any[]>([]);
  const [ngos, setNgos] = useState<any[]>([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    publicScorecards().then((r) => setCards(r as Scorecards)).catch(() => {});
    publicGallery(12).then((r: any) => setStories(r.stories ?? [])).catch(() => {});
    publicDirectory().then((r: any) => setNgos(r.ngos ?? [])).catch(() => {});
  }, []);

  const filteredNgos = ngos.filter((n) =>
    !search || (n.name || '').toLowerCase().includes(search.toLowerCase()),
  );

  const stat = (label: string, value: number | undefined, Icon: any, color: string) => (
    <div className="bg-white rounded-2xl border border-gray-200 p-5 text-center shadow-sm">
      <Icon className={`mx-auto mb-2 ${color}`} size={26} />
      <div className="text-2xl font-bold text-gray-800">{(value ?? 0).toLocaleString()}</div>
      <div className="text-xs uppercase tracking-wide text-gray-500">{label}</div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <header className="flex items-center justify-between px-6 py-4">
        <div className="font-bold text-lg text-blue-700">Smart Resource Allocation</div>
        <Link to="/dashboard" className="text-sm bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700">
          Sign in
        </Link>
      </header>

      <section className="text-center px-6 py-12 max-w-3xl mx-auto">
        <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900">
          Transparent relief, delivered and verified.
        </h1>
        <p className="mt-3 text-gray-600">
          See exactly where resources go — every impact story below is backed by GPS-verified
          proof-of-work from the field.
        </p>
      </section>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4 px-6 max-w-5xl mx-auto">
        {stat('Lives impacted', cards?.lives_impacted, HeartHandshake, 'text-rose-500')}
        {stat('Needs resolved', cards?.needs_resolved, Droplets, 'text-blue-500')}
        {stat('Tasks completed', cards?.tasks_completed, ShieldCheck, 'text-green-500')}
        {stat('NGOs registered', cards?.ngos_registered, Users, 'text-purple-500')}
      </section>

      <section className="px-6 py-12 max-w-6xl mx-auto">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Impact Gallery</h2>
        {stories.length === 0 ? (
          <p className="text-sm text-gray-500">No verified stories yet — check back soon.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {stories.map((s) => (
              <article key={s.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
                <div className="grid grid-cols-2">
                  <img src={s.before_url || '/placeholder.png'} alt="before" className="h-32 w-full object-cover" />
                  <img src={s.after_url || '/placeholder.png'} alt="after" className="h-32 w-full object-cover" />
                </div>
                <div className="p-3">
                  <p className="text-sm text-gray-700 line-clamp-4">{s.narrative}</p>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="px-6 py-12 max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-800">NGO Directory</h2>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search NGOs..."
            className="border rounded-lg px-3 py-1.5 text-sm"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredNgos.map((n) => (
            <div key={n.id} className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-gray-800">{n.name}</span>
                {n.verified && <ShieldCheck size={16} className="text-green-500" />}
              </div>
              <div className="text-xs text-gray-500 mb-2">{n.sector}</div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>Reliability {n.reliability_score}</span>
                <span>{n.tasks_completed}/{n.tasks_total} tasks</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <footer className="text-center text-xs text-gray-400 py-8">
        Smart Resource Allocation — Google Solution Challenge
      </footer>
    </div>
  );
}