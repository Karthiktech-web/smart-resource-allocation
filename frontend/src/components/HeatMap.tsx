import { GoogleMap, useLoadScript, HeatmapLayer, Marker, InfoWindow } from '@react-google-maps/api';
import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const libraries: ("visualization")[] = ['visualization'];

interface HeatMapPoint {
  lat: number;
  lng: number;
  weight: number;
  name?: string;
  id?: string;
  area_priority?: string;
  compound_score?: number;
}

const CATEGORY_COLORS: Record<string, string> = {
  all: '#4285f4',
  water: '#1a73e8',
  health: '#ea4335',
  food: '#fbbc05',
  education: '#34a853',
  shelter: '#ff6d01',
  infrastructure: '#46bdc6',
};

export default function HeatMap({ data, areas }: { data: HeatMapPoint[]; areas?: any[] }) {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedArea, setSelectedArea] = useState<any>(null);
  
  const { isLoaded } = useLoadScript({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '',
    libraries,
  });

  const filteredData = useMemo(() => {
    if (selectedCategory === 'all') return data;
    return data.filter((p: any) => p.category === selectedCategory);
  }, [data, selectedCategory]);

  const heatmapData = useMemo(() => {
    if (!isLoaded || !window.google) return [];
    return filteredData.map((point) => ({
      location: new google.maps.LatLng(point.lat, point.lng),
      weight: point.weight || 1,
    }));
  }, [filteredData, isLoaded]);

  if (!isLoaded) {
    return <div className="h-[500px] bg-gray-100 rounded-lg flex items-center justify-center">Loading map...</div>;
  }

  return (
    <div>
      {/* Category Filter Buttons */}
      <div className="flex flex-wrap gap-2 mb-4">
        {Object.keys(CATEGORY_COLORS).map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              selectedCategory === cat
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      <GoogleMap
        center={{ lat: 15.5, lng: 78.5 }}
        zoom={7}
        mapContainerStyle={{ width: '100%', height: '500px', borderRadius: '12px' }}
      >
        {heatmapData.length > 0 && (
          <HeatmapLayer
            data={heatmapData}
            options={{
              radius: 60,
              opacity: 0.7,
              gradient: [
                'rgba(0, 255, 0, 0)',
                'rgba(0, 255, 0, 1)',
                'rgba(255, 255, 0, 1)',
                'rgba(255, 165, 0, 1)',
                'rgba(255, 0, 0, 1)',
              ],
            }}
          />
        )}

        {/* Clickable area markers */}
        {(areas || []).map((area: any) => (
          <Marker
            key={area.id}
            position={{ lat: area.lat, lng: area.lng }}
            onClick={() => setSelectedArea(area)}
            label={{
              text: String(area.compound_score || 0),
              color: 'white',
              fontSize: '11px',
              fontWeight: 'bold',
            }}
          />
        ))}

        {selectedArea && (
          <InfoWindow
            position={{ lat: selectedArea.lat, lng: selectedArea.lng }}
            onCloseClick={() => setSelectedArea(null)}
          >
            <div className="p-2 max-w-[200px]">
              <h3 className="font-bold text-sm">{selectedArea.name}</h3>
              <p className="text-xs text-gray-500">{selectedArea.district}</p>
              <p className="text-xs mt-1">
                Score: <strong>{selectedArea.compound_score}/10</strong> |
                Needs: <strong>{selectedArea.open_needs}</strong>
              </p>
              <button
                onClick={() => navigate(`/areas/${selectedArea.id}`)}
                className="mt-2 text-xs bg-blue-600 text-white px-3 py-1 rounded-full hover:bg-blue-700"
              >
                View Details
              </button>
            </div>
          </InfoWindow>
        )}
      </GoogleMap>
    </div>
  );
}