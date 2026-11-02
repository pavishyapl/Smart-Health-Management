import React, { useState } from 'react';
import { MapPin, Navigation, CheckCircle2, AlertCircle } from 'lucide-react';

export const LocationPicker = ({ latitude, longitude, address, onChange, required = true }) => {
  const [detecting, setDetecting] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);

  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      setStatusMsg({ type: 'error', text: 'Geolocation is not supported by your browser.' });
      return;
    }

    setDetecting(true);
    setStatusMsg({ type: 'info', text: 'Detecting GPS coordinates...' });

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = parseFloat(position.coords.latitude.toFixed(6));
        const lon = parseFloat(position.coords.longitude.toFixed(6));
        onChange({
          latitude: lat,
          longitude: lon,
          address: address || `GPS Location (${lat}, ${lon})`
        });
        setDetecting(false);
        setStatusMsg({ type: 'success', text: `Location auto-detected: ${lat}, ${lon}` });
      },
      (error) => {
        setDetecting(false);
        let errorText = 'Unable to retrieve your location.';
        if (error.code === error.PERMISSION_DENIED) {
          errorText = 'Location permission denied. Please enter coordinates manually.';
        } else if (error.code === error.POSITION_UNAVAILABLE) {
          errorText = 'Location information is unavailable. Please enter coordinates manually.';
        } else if (error.code === error.TIMEOUT) {
          errorText = 'Location request timed out. Please enter coordinates manually.';
        }
        setStatusMsg({ type: 'error', text: errorText });
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  return (
    <div className="space-y-3 bg-slate-50/80 p-4 rounded-xl border border-slate-200">
      <div className="flex items-center justify-between">
        <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
          <MapPin className="w-4 h-4 text-teal-600" />
          Geographic Location & Coordinates {required && <span className="text-rose-500">*</span>}
        </label>
        <button
          type="button"
          onClick={handleUseCurrentLocation}
          disabled={detecting}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-teal-600 hover:bg-teal-700 text-white shadow-xs transition-colors disabled:opacity-50 cursor-pointer"
        >
          <Navigation className={`w-3.5 h-3.5 ${detecting ? 'animate-spin' : ''}`} />
          {detecting ? 'Detecting...' : 'Use Current Location'}
        </button>
      </div>

      {statusMsg && (
        <div className={`p-2.5 rounded-lg text-xs flex items-center gap-2 ${
          statusMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' :
          statusMsg.type === 'error' ? 'bg-rose-50 text-rose-800 border border-rose-200' :
          'bg-teal-50 text-teal-800 border border-teal-200'
        }`}>
          {statusMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" /> : <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />}
          <span>{statusMsg.text}</span>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">
            Latitude <span className="text-slate-400 font-normal">(-90 to 90)</span>
          </label>
          <input
            type="number"
            step="0.000001"
            required={required}
            value={latitude !== undefined ? latitude : ''}
            onChange={(e) => onChange({ latitude: parseFloat(e.target.value) || 0, longitude, address })}
            placeholder="e.g. 28.613900"
            className="w-full px-3 py-2 text-sm bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">
            Longitude <span className="text-slate-400 font-normal">(-180 to 180)</span>
          </label>
          <input
            type="number"
            step="0.000001"
            required={required}
            value={longitude !== undefined ? longitude : ''}
            onChange={(e) => onChange({ latitude, longitude: parseFloat(e.target.value) || 0, address })}
            placeholder="e.g. 77.209000"
            className="w-full px-3 py-2 text-sm bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none"
          />
        </div>
      </div>
    </div>
  );
};

export default LocationPicker;
