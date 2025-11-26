import React, { useState } from 'react';
import { RotateCw, ZoomIn, ZoomOut, Maximize2, Grid3x3, Eye } from 'lucide-react';

const FloorPlan3DViewer = ({ floors }) => {
  const [selectedFloor, setSelectedFloor] = useState(0);
  const [viewMode, setViewMode] = useState('2D'); // '2D' or '3D'
  const [rotation, setRotation] = useState(45);
  const [zoom, setZoom] = useState(1);

  if (!floors || floors.length === 0) {
    return (
      <div className="bg-gray-100 rounded-lg p-8 text-center">
        <p className="text-gray-600">No floor plans available</p>
      </div>
    );
  }

  const currentFloor = floors[selectedFloor];
  
  // Calculate total dimensions for scaling
  const getTotalDimensions = () => {
    if (!currentFloor.rooms || currentFloor.rooms.length === 0) {
      return { width: 0, height: 0 };
    }
    
    const maxLength = Math.max(...currentFloor.rooms.map(r => r.length || 4));
    const maxWidth = Math.max(...currentFloor.rooms.map(r => r.width || 3));
    
    return { width: maxLength * 50, height: maxWidth * 50 };
  };

  const { width: totalWidth, height: totalHeight } = getTotalDimensions();

  // Room color mapping
  const getRoomColor = (type) => {
    const colors = {
      'living_room': { primary: '#10b981', secondary: '#059669', light: '#d1fae5' },
      'bedroom': { primary: '#3b82f6', secondary: '#2563eb', light: '#dbeafe' },
      'kitchen': { primary: '#f59e0b', secondary: '#d97706', light: '#fef3c7' },
      'bathroom': { primary: '#8b5cf6', secondary: '#7c3aed', light: '#ede9fe' },
      'dining_room': { primary: '#06b6d4', secondary: '#0891b2', light: '#cffafe' },
      'office': { primary: '#84cc16', secondary: '#65a30d', light: '#ecfccb' },
      'store': { primary: '#64748b', secondary: '#475569', light: '#e2e8f0' },
      'balcony': { primary: '#ec4899', secondary: '#db2777', light: '#fce7f3' },
    };
    return colors[type] || { primary: '#6b7280', secondary: '#4b5563', light: '#f3f4f6' };
  };

  const renderRoom3D = (room, index) => {
    const roomLength = room.length || 4;
    const roomWidth = room.width || 3;
    const roomHeight = room.height || 3;
    
    // Scale for visualization
    const scale = 40;
    const width = roomLength * scale;
    const depth = roomWidth * scale;
    const height = roomHeight * scale * 0.5; // Half scale for height
    
    const colors = getRoomColor(room.type);
    
    // Calculate position (simple grid layout)
    const cols = 3;
    const row = Math.floor(index / cols);
    const col = index % cols;
    const x = col * (width + 40) + 50;
    const y = row * (depth + 40) + 50;
    
    if (viewMode === '2D') {
      // 2D Top-down view
      return (
        <div
          key={index}
          className="absolute transition-all duration-300 hover:z-10"
          style={{
            left: `${x}px`,
            top: `${y}px`,
            width: `${width}px`,
            height: `${depth}px`,
          }}
        >
          <div
            className="w-full h-full rounded-lg border-4 shadow-lg flex flex-col items-center justify-center relative overflow-hidden"
            style={{
              backgroundColor: colors.light,
              borderColor: colors.primary,
            }}
          >
            {/* Room info */}
            <div className="text-center z-10 relative">
              <div className="font-bold text-gray-900 text-sm">{room.name}</div>
              <div className="text-xs text-gray-600">{room.type.replace('_', ' ')}</div>
              <div className="text-xs font-semibold text-gray-700 mt-1">
                {roomLength}m × {roomWidth}m
              </div>
              <div 
                className="inline-block px-2 py-1 rounded text-white text-xs font-bold mt-1"
                style={{ backgroundColor: colors.primary }}
              >
                {(roomLength * roomWidth).toFixed(1)} m²
              </div>
            </div>
            
            {/* Grid pattern */}
            <div className="absolute inset-0 opacity-10">
              {Array.from({ length: 5 }).map((_, i) => (
                <div
                  key={`h-${i}`}
                  className="absolute w-full border-t"
                  style={{
                    top: `${(i + 1) * 20}%`,
                    borderColor: colors.secondary,
                  }}
                />
              ))}
              {Array.from({ length: 5 }).map((_, i) => (
                <div
                  key={`v-${i}`}
                  className="absolute h-full border-l"
                  style={{
                    left: `${(i + 1) * 20}%`,
                    borderColor: colors.secondary,
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      );
    } else {
      // 3D Isometric view
      return (
        <div
          key={index}
          className="absolute transition-all duration-300 hover:z-10"
          style={{
            left: `${x}px`,
            top: `${y}px`,
            transform: `rotateX(60deg) rotateZ(${rotation}deg) scale(${zoom})`,
            transformStyle: 'preserve-3d',
          }}
        >
          {/* Floor */}
          <div
            className="absolute rounded shadow-2xl"
            style={{
              width: `${width}px`,
              height: `${depth}px`,
              backgroundColor: colors.light,
              border: `3px solid ${colors.primary}`,
            }}
          />
          
          {/* Walls */}
          {/* Front wall */}
          <div
            className="absolute origin-bottom"
            style={{
              width: `${width}px`,
              height: `${height}px`,
              top: `-${height}px`,
              backgroundColor: colors.secondary,
              opacity: 0.8,
              transform: 'rotateX(90deg)',
              border: `2px solid ${colors.primary}`,
            }}
          />
          
          {/* Back wall */}
          <div
            className="absolute origin-bottom"
            style={{
              width: `${width}px`,
              height: `${height}px`,
              top: `-${height}px`,
              transform: `translateZ(${depth}px) rotateX(90deg)`,
              backgroundColor: colors.secondary,
              opacity: 0.6,
              border: `2px solid ${colors.primary}`,
            }}
          />
          
          {/* Left wall */}
          <div
            className="absolute origin-bottom"
            style={{
              width: `${depth}px`,
              height: `${height}px`,
              top: `-${height}px`,
              left: 0,
              backgroundColor: colors.secondary,
              opacity: 0.7,
              transform: 'rotateY(90deg) rotateX(90deg)',
              border: `2px solid ${colors.primary}`,
            }}
          />
          
          {/* Right wall */}
          <div
            className="absolute origin-bottom"
            style={{
              width: `${depth}px`,
              height: `${height}px`,
              top: `-${height}px`,
              left: `${width}px`,
              backgroundColor: colors.secondary,
              opacity: 0.7,
              transform: 'rotateY(90deg) rotateX(90deg)',
              border: `2px solid ${colors.primary}`,
            }}
          />
          
          {/* Room label */}
          <div
            className="absolute text-center z-20"
            style={{
              width: `${width}px`,
              top: `${depth / 2}px`,
              left: 0,
              transform: 'translateZ(5px)',
            }}
          >
            <div className="font-bold text-gray-900 text-xs" style={{ textShadow: '0 0 3px white' }}>
              {room.name}
            </div>
            <div className="text-xs text-gray-700" style={{ textShadow: '0 0 3px white' }}>
              {roomLength}m × {roomWidth}m × {roomHeight}m
            </div>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      {/* Controls */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <h3 className="text-xl font-bold text-gray-900">Floor Plan Viewer</h3>
          
          {/* View Mode Toggle */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('2D')}
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center ${
                viewMode === '2D'
                  ? 'bg-white text-green-600 shadow'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Grid3x3 className="w-4 h-4 mr-2" />
              2D View
            </button>
            <button
              onClick={() => setViewMode('3D')}
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center ${
                viewMode === '3D'
                  ? 'bg-white text-blue-600 shadow'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Eye className="w-4 h-4 mr-2" />
              3D View
            </button>
          </div>
        </div>
        
        {/* 3D Controls */}
        {viewMode === '3D' && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setRotation(r => r - 15)}
              className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              title="Rotate Left"
            >
              <RotateCw className="w-5 h-5 text-gray-700 transform -scale-x-100" />
            </button>
            <button
              onClick={() => setRotation(r => r + 15)}
              className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              title="Rotate Right"
            >
              <RotateCw className="w-5 h-5 text-gray-700" />
            </button>
            <div className="w-px h-6 bg-gray-300 mx-1" />
            <button
              onClick={() => setZoom(z => Math.min(z + 0.1, 2))}
              className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-5 h-5 text-gray-700" />
            </button>
            <button
              onClick={() => setZoom(z => Math.max(z - 0.1, 0.5))}
              className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-5 h-5 text-gray-700" />
            </button>
            <button
              onClick={() => { setRotation(45); setZoom(1); }}
              className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              title="Reset View"
            >
              <Maximize2 className="w-5 h-5 text-gray-700" />
            </button>
          </div>
        )}
      </div>
      
      {/* Floor Selector */}
      {floors.length > 1 && (
        <div className="mb-6 flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Floor:</span>
          <div className="flex gap-2">
            {floors.map((floor, index) => (
              <button
                key={index}
                onClick={() => setSelectedFloor(index)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  selectedFloor === index
                    ? 'bg-green-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {floor.floor_name}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Viewer */}
      <div 
        className="relative bg-gray-50 rounded-lg overflow-hidden border-2 border-gray-200"
        style={{ 
          minHeight: '600px',
          perspective: viewMode === '3D' ? '1000px' : 'none',
        }}
      >
        <div className="absolute inset-0" style={{ perspectiveOrigin: '50% 50%' }}>
          {currentFloor.rooms && currentFloor.rooms.map((room, index) => 
            renderRoom3D(room, index)
          )}
        </div>
        
        {/* Info Badge */}
        <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-4">
          <div className="text-sm font-medium text-gray-700">
            {currentFloor.floor_name}
          </div>
          <div className="text-xs text-gray-600 mt-1">
            {currentFloor.rooms ? currentFloor.rooms.length : 0} rooms
          </div>
          <div className="text-xs text-gray-600">
            {currentFloor.rooms
              ? (currentFloor.rooms.reduce((sum, r) => sum + (r.length * r.width), 0)).toFixed(1)
              : 0} m²
          </div>
        </div>
      </div>
      
      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-3">
        {['living_room', 'bedroom', 'kitchen', 'bathroom', 'dining_room'].map(type => {
          const colors = getRoomColor(type);
          return (
            <div key={type} className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded border-2"
                style={{
                  backgroundColor: colors.light,
                  borderColor: colors.primary,
                }}
              />
              <span className="text-xs text-gray-600">
                {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default FloorPlan3DViewer;
