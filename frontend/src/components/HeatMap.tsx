import { GoogleMap, useLoadScript, Marker, InfoWindow } from '@react-google-maps/api';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Fixed: Define libraries outside the component to prevent constant re-renders
const libraries: ("visualization")[] = [];

type HeatMapPoint = {
  lat: number;
  lng: number;
  weight?: number;
};

type HeatMapArea = {
  id: string;
  lat: number;
  lng: number;
  name?: string;
  compound_score?: number;
  area_priority?: string;
  needs_by_category?: Record<string, number>;
};

interface HeatMapProps {
  data: HeatMapPoint[];  // Points with weights for the glow effect
  areas: HeatMapArea[]; // Full area data for the clickable pins
}

// Helper function to get marker color based on intensity score
function getMarkerColor(score: number) {
  if (score >= 8) return '#FF0000';      // Red - Critical
  if (score >= 6) return '#FF8800';      // Orange - High
  if (score >= 4) return '#FFFF00';      // Yellow - Medium
  return '#00CC00';                      // Green - Low
}

export default function HeatMap({ data, areas }: HeatMapProps) {
  const navigate = useNavigate();
  const [selectedArea, setSelectedArea] = useState<HeatMapArea | null>(null);
  const [filter, setFilter] = useState('all');
  
  const { isLoaded } = useLoadScript({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '',
    libraries,
  });

  // LOG: Verify data arrives in browser console (F12)
  console.log(`Rendering Map: ${data?.length} points, ${areas?.length} interactive markers.`);

  if (!isLoaded) {
    return (
      <div className="h-[550px] bg-slate-50 rounded-3xl flex flex-col items-center justify-center border-2 border-dashed border-slate-200">
        <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
        <p className="text-slate-500 font-medium">Mounting Intelligence Layer...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 1. Category Filter Controls */}
      <div className="flex flex-wrap gap-2 p-2 bg-slate-50 rounded-2xl border border-slate-100">
        {['All', 'Water', 'Health', 'Food', 'Education', 'Shelter', 'Infrastructure'].map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat.toLowerCase())}
            className={`px-5 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all duration-200 ${
              filter === cat.toLowerCase() 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-200 scale-105' 
                : 'bg-white text-slate-500 border border-slate-200 hover:border-blue-400 hover:text-blue-600'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* 2. Map Interface */}
      <GoogleMap
        center={{ lat: 15.5, lng: 79.5 }}
        zoom={7}
        mapContainerStyle={{ width: '100%', height: '550px', borderRadius: '24px' }}
        options={{
          styles: [{ featureType: "poi", stylers: [{ visibility: "off" }] }],
          disableDefaultUI: true,
          zoomControl: true,
          gestureHandling: "greedy"
        }}
      >
        {/* 3. Intensity Visualization with Colored Markers */}
        {/* HeatmapLayer is deprecated in Google Maps API v3.65+ */}

        {/* 4. The Clickable Pins (Markers) with Color Coding */}
        {(areas || []).map((area) => (
          <Marker
            key={area.id}
            position={{ lat: area.lat, lng: area.lng }}
            onClick={() => setSelectedArea(area)}
            zIndex={1000}
            icon={{
              path: window.google?.maps?.SymbolPath?.CIRCLE || 0,
              scale: 12,
              fillColor: getMarkerColor(area.compound_score || 0),
              fillOpacity: 0.8,
              strokeColor: '#FFF',
              strokeWeight: 2,
            }}
            label={{
              text: area.compound_score?.toString() || "!",
              color: "white",
              fontSize: "12px",
              fontWeight: "900"
            }}
            opacity={
              filter === 'all' ||
              ((area.needs_by_category?.[filter.charAt(0).toUpperCase() + filter.slice(1)] ?? 0) > 0) ||
              ((area.needs_by_category?.[filter] ?? 0) > 0)
                ? 1
                : 0.4
            }
          />
        ))}

        {/* 5. Interactive InfoWindow */}
        {selectedArea && (
          <InfoWindow
            position={{ lat: selectedArea.lat, lng: selectedArea.lng }}
            onCloseClick={() => setSelectedArea(null)}
          >
            <div className="p-3 max-w-[200px] text-center">
              <h4 className="font-bold text-slate-800 text-sm mb-1 uppercase">{selectedArea.name}</h4>
              <div className="h-px bg-slate-100 my-2"></div>
              <p className="text-xs text-slate-500 mb-3">
                Priority: <span className="font-black text-red-600">{selectedArea.compound_score}/10</span>
              </p>
              <button
                onClick={() => navigate(`/areas/${selectedArea.id}`)}
                className="w-full bg-blue-600 text-white text-[10px] font-black py-2 rounded-lg hover:bg-blue-700 transition-colors uppercase tracking-tighter"
              >
                Inspect Intelligence
              </button>
            </div>
          </InfoWindow>
        )}
      </GoogleMap>
    </div>
  );
}