import { GoogleMap, useLoadScript, HeatmapLayer } from '@react-google-maps/api';
import { useMemo } from 'react';

const libraries: ("visualization")[] = ['visualization'];

interface HeatMapPoint {
  lat: number;
  lng: number;
  weight: number;
  name?: string;
  priority?: string;
  needs_count?: number;
}

interface HeatMapProps {
  data: HeatMapPoint[];
  onAreaClick?: (point: HeatMapPoint) => void;
}

export default function HeatMap({ data, onAreaClick }: HeatMapProps) {
  const { isLoaded } = useLoadScript({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '',
    libraries,
  });

  const heatmapData = useMemo(() => {
    if (!isLoaded || !window.google) return [];
    return data.map((point) => ({
      location: new google.maps.LatLng(point.lat, point.lng),
      weight: point.weight || 1,
    }));
  }, [data, isLoaded]);

  if (!isLoaded) {
    return (
      <div className="h-[500px] bg-gray-100 rounded-xl flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2" />
          <p className="text-gray-500 text-sm">Loading map...</p>
        </div>
      </div>
    );
  }

  return (
    <GoogleMap
      center={{ lat: 15.5, lng: 78.5 }} // Center of Andhra Pradesh
      zoom={7}
      mapContainerStyle={{ width: '100%', height: '500px', borderRadius: '12px' }}
      options={{
        styles: [{ featureType: 'poi', stylers: [{ visibility: 'off' }] }],
        mapTypeControl: false,
        streetViewControl: false,
      }}
    >
      {heatmapData.length > 0 && (
        <HeatmapLayer
          data={heatmapData}
          options={{
            radius: 60,
            opacity: 0.7,
            gradient: [
              'rgba(0, 255, 0, 0)',       // Transparent
              'rgba(0, 255, 0, 1)',       // Green (low severity)
              'rgba(255, 255, 0, 1)',     // Yellow (medium)
              'rgba(255, 165, 0, 1)',     // Orange (high)
              'rgba(255, 0, 0, 1)',       // Red (critical)
            ],
          }}
        />
      )}
    </GoogleMap>
  );
}