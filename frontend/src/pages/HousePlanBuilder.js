import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import {
  Home, Plus, Minus, Save, Calculator, FileText, Download,
  Building, Layers, Drill, Zap, Droplet, Paintbrush, DollarSign,
  Clock, CheckCircle, AlertCircle, ArrowRight, ArrowLeft, Trash2, Users
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const HousePlanBuilder = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [calculatedPlan, setCalculatedPlan] = useState(null);
  
  // Plan basic info
  const [planName, setPlanName] = useState('');
  const [description, setDescription] = useState('');
  const [houseType, setHouseType] = useState('bungalow');
  const [location, setLocation] = useState('douala');
  const [foundationType, setFoundationType] = useState('strip');
  const [wallType, setWallType] = useState('sandcrete');
  const [roofingType, setRoofingType] = useState('aluminum');
  const [finishingLevel, setFinishingLevel] = useState('standard');
  
  // Floors and rooms
  const [floors, setFloors] = useState([
    {
      floor_number: 0,
      floor_name: 'Ground Floor',
      rooms: [
        { name: 'Living Room', type: 'living_room', length: 5, width: 4, height: 3 },
        { name: 'Bedroom 1', type: 'bedroom', length: 4, width: 3.5, height: 3 },
        { name: 'Bedroom 2', type: 'bedroom', length: 4, width: 3.5, height: 3 },
        { name: 'Kitchen', type: 'kitchen', length: 4, width: 3, height: 3 },
        { name: 'Bathroom', type: 'bathroom', length: 2.5, width: 2, height: 3 },
      ]
    }
  ]);

  const addFloor = () => {
    const newFloorNumber = floors.length;
    setFloors([...floors, {
      floor_number: newFloorNumber,
      floor_name: `Floor ${newFloorNumber + 1}`,
      rooms: [
        { name: 'Bedroom', type: 'bedroom', length: 4, width: 3.5, height: 3 },
      ]
    }]);
  };

  const removeFloor = (floorIndex) => {
    if (floors.length > 1) {
      setFloors(floors.filter((_, i) => i !== floorIndex));
    }
  };

  const addRoom = (floorIndex) => {
    const newFloors = [...floors];
    newFloors[floorIndex].rooms.push({
      name: 'New Room',
      type: 'bedroom',
      length: 4,
      width: 3,
      height: 3
    });
    setFloors(newFloors);
  };

  const removeRoom = (floorIndex, roomIndex) => {
    const newFloors = [...floors];
    if (newFloors[floorIndex].rooms.length > 1) {
      newFloors[floorIndex].rooms.splice(roomIndex, 1);
      setFloors(newFloors);
    }
  };

  const updateRoom = (floorIndex, roomIndex, field, value) => {
    const newFloors = [...floors];
    newFloors[floorIndex].rooms[roomIndex][field] = value;
    setFloors(newFloors);
  };

  const calculatePlan = async () => {
    if (!user) {
      alert('Please login to create house plans');
      navigate('/auth/login');
      return;
    }

    if (!planName) {
      alert('Please enter a plan name');
      return;
    }

    setLoading(true);
    
    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/house-plans/create`,
        {
          name: planName,
          description,
          house_type: houseType,
          location,
          floors,
          foundation_type: foundationType,
          wall_type: wallType,
          roofing_type: roofingType,
          finishing_level: finishingLevel
        },
        { withCredentials: true }
      );
      
      setCalculatedPlan(response.data.plan);
      setStep(4); // Move to results step
      alert('House plan created successfully!');
      
    } catch (error) {
      console.error('Error creating plan:', error);
      alert(error.response?.data?.detail || 'Failed to create house plan');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CM', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0
    }).format(amount);
  };

  // Step 1: Basic Information
  const renderStep1 = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 flex items-center">
        <FileText className="w-6 h-6 mr-2 text-green-600" />
        Basic Information
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Plan Name *
          </label>
          <input
            type="text"
            value={planName}
            onChange={(e) => setPlanName(e.target.value)}
            placeholder="e.g., My Dream Home"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            House Type *
          </label>
          <select
            value={houseType}
            onChange={(e) => setHouseType(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="bungalow">Bungalow (1 Floor)</option>
            <option value="duplex">Duplex (2 Floors)</option>
            <option value="multi_story">Multi-Story (3+ Floors)</option>
            <option value="apartment">Apartment/Flat</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location *
          </label>
          <select
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="douala">Douala</option>
            <option value="yaounde">Yaoundé</option>
            <option value="bafoussam">Bafoussam</option>
            <option value="bamenda">Bamenda</option>
            <option value="garoua">Garoua</option>
            <option value="maroua">Maroua</option>
            <option value="ngaoundere">Ngaoundéré</option>
            <option value="buea">Buea</option>
            <option value="limbe">Limbe</option>
            <option value="kribi">Kribi</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Foundation Type
          </label>
          <select
            value={foundationType}
            onChange={(e) => setFoundationType(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="strip">Strip Foundation (Standard)</option>
            <option value="raft">Raft Foundation (Premium)</option>
            <option value="pile">Pile Foundation (Special)</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Wall Type
          </label>
          <select
            value={wallType}
            onChange={(e) => setWallType(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="sandcrete">Sandcrete Blocks</option>
            <option value="brick">Brick Walls</option>
            <option value="concrete">Concrete Walls</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Roofing Type
          </label>
          <select
            value={roofingType}
            onChange={(e) => setRoofingType(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="aluminum">Aluminum Sheets</option>
            <option value="tiles">Roofing Tiles</option>
            <option value="concrete">Concrete Slab</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Finishing Level
          </label>
          <select
            value={finishingLevel}
            onChange={(e) => setFinishingLevel(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="basic">Basic Finishing</option>
            <option value="standard">Standard Finishing</option>
            <option value="luxury">Luxury Finishing</option>
          </select>
        </div>
        
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description (Optional)
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe your dream house..."
            rows="3"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>
      </div>
      
      <div className="flex justify-end">
        <button
          onClick={() => setStep(2)}
          className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-medium flex items-center"
        >
          Next: Design Rooms
          <ArrowRight className="w-5 h-5 ml-2" />
        </button>
      </div>
    </div>
  );

  // Step 2: Room Design
  const renderStep2 = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 flex items-center">
        <Building className="w-6 h-6 mr-2 text-green-600" />
        Design Rooms & Floors
      </h2>
      
      {floors.map((floor, floorIndex) => (
        <div key={floorIndex} className="bg-gray-50 p-6 rounded-lg border-2 border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">
              {floor.floor_name}
            </h3>
            {floors.length > 1 && (
              <button
                onClick={() => removeFloor(floorIndex)}
                className="text-red-600 hover:text-red-700 flex items-center text-sm"
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Remove Floor
              </button>
            )}
          </div>
          
          <div className="space-y-4">
            {floor.rooms.map((room, roomIndex) => (
              <div key={roomIndex} className="bg-white p-4 rounded-lg border border-gray-300">
                <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Room Name</label>
                    <input
                      type="text"
                      value={room.name}
                      onChange={(e) => updateRoom(floorIndex, roomIndex, 'name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Type</label>
                    <select
                      value={room.type}
                      onChange={(e) => updateRoom(floorIndex, roomIndex, 'type', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    >
                      <option value="bedroom">Bedroom</option>
                      <option value="living_room">Living Room</option>
                      <option value="kitchen">Kitchen</option>
                      <option value="bathroom">Bathroom</option>
                      <option value="dining_room">Dining Room</option>
                      <option value="office">Office</option>
                      <option value="store">Store</option>
                      <option value="balcony">Balcony</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Length (m)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={room.length}
                      onChange={(e) => updateRoom(floorIndex, roomIndex, 'length', parseFloat(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Width (m)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={room.width}
                      onChange={(e) => updateRoom(floorIndex, roomIndex, 'width', parseFloat(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                  <div className="flex items-end">
                    <button
                      onClick={() => removeRoom(floorIndex, roomIndex)}
                      className="w-full px-3 py-2 bg-red-50 text-red-600 hover:bg-red-100 rounded text-sm flex items-center justify-center"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="mt-2 text-xs text-gray-600">
                  Area: {(room.length * room.width).toFixed(2)} m²
                </div>
              </div>
            ))}
            
            <button
              onClick={() => addRoom(floorIndex)}
              className="w-full py-3 border-2 border-dashed border-gray-300 hover:border-green-500 rounded-lg text-gray-600 hover:text-green-600 font-medium flex items-center justify-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              Add Room to {floor.floor_name}
            </button>
          </div>
        </div>
      ))}
      
      <button
        onClick={addFloor}
        className="w-full py-4 border-2 border-dashed border-green-500 hover:bg-green-50 rounded-lg text-green-600 font-bold flex items-center justify-center"
      >
        <Layers className="w-5 h-5 mr-2" />
        Add New Floor
      </button>
      
      <div className="flex justify-between">
        <button
          onClick={() => setStep(1)}
          className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-8 py-3 rounded-lg font-medium flex items-center"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back
        </button>
        <button
          onClick={() => setStep(3)}
          className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-medium flex items-center"
        >
          Next: Review & Calculate
          <ArrowRight className="w-5 h-5 ml-2" />
        </button>
      </div>
    </div>
  );

  // Step 3: Review & Calculate
  const renderStep3 = () => {
    const totalFloorArea = floors.reduce((sum, floor) =>
      sum + floor.rooms.reduce((roomSum, room) => roomSum + (room.length * room.width), 0), 0
    );
    
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Calculator className="w-6 h-6 mr-2 text-green-600" />
          Review & Calculate
        </h2>
        
        <div className="bg-gradient-to-br from-green-50 to-blue-50 p-6 rounded-xl border-2 border-green-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Plan Summary</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-600">Plan Name</div>
              <div className="font-bold text-gray-900">{planName}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-600">House Type</div>
              <div className="font-bold text-gray-900 capitalize">{houseType}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-600">Total Floors</div>
              <div className="font-bold text-gray-900">{floors.length}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-600">Total Area</div>
              <div className="font-bold text-gray-900">{totalFloorArea.toFixed(2)} m²</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-600">Location</div>
              <div className="font-bold text-gray-900 capitalize">{location}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-600">Foundation</div>
              <div className="font-bold text-gray-900 capitalize">{foundationType}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-600">Finishing</div>
              <div className="font-bold text-gray-900 capitalize">{finishingLevel}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-600">Total Rooms</div>
              <div className="font-bold text-gray-900">
                {floors.reduce((sum, floor) => sum + floor.rooms.length, 0)}
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
          <div className="flex items-start">
            <AlertCircle className="w-6 h-6 text-blue-600 mr-3 mt-1 flex-shrink-0" />
            <div>
              <h4 className="font-bold text-gray-900 mb-2">What happens next?</h4>
              <ul className="text-sm text-gray-700 space-y-2">
                <li className="flex items-center">
                  <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                  We'll calculate all required building materials
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                  Generate a detailed Bill of Quantities (BOQ)
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                  Estimate total project cost including materials and labor
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                  Calculate estimated construction duration
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="flex justify-between">
          <button
            onClick={() => setStep(2)}
            className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-8 py-3 rounded-lg font-medium flex items-center"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back
          </button>
          <button
            onClick={calculatePlan}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-bold flex items-center disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Calculating...
              </>
            ) : (
              <>
                <Calculator className="w-5 h-5 mr-2" />
                Calculate Materials & Cost
              </>
            )}
          </button>
        </div>
      </div>
    );
  };

  // Step 4: Results
  const renderStep4 = () => {
    if (!calculatedPlan) return null;
    
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white p-8 rounded-xl">
          <h2 className="text-3xl font-black mb-2">Plan Created Successfully! 🎉</h2>
          <p className="text-green-50">Your house plan with detailed materials and cost estimation is ready.</p>
        </div>
        
        {/* Cost Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-xl shadow-lg border-2 border-green-200">
            <DollarSign className="w-10 h-10 text-green-600 mb-3" />
            <div className="text-sm text-gray-600">Total Materials</div>
            <div className="text-2xl font-black text-gray-900">
              {formatCurrency(calculatedPlan.total_materials_cost)}
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg border-2 border-blue-200">
            <Users className="w-10 h-10 text-blue-600 mb-3" />
            <div className="text-sm text-gray-600">Labor Cost</div>
            <div className="text-2xl font-black text-gray-900">
              {formatCurrency(calculatedPlan.labor_cost)}
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg border-2 border-purple-200">
            <Calculator className="w-10 h-10 text-purple-600 mb-3" />
            <div className="text-sm text-gray-600">Total Project Cost</div>
            <div className="text-2xl font-black text-purple-900">
              {formatCurrency(calculatedPlan.total_project_cost)}
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg border-2 border-orange-200">
            <Clock className="w-10 h-10 text-orange-600 mb-3" />
            <div className="text-sm text-gray-600">Est. Duration</div>
            <div className="text-2xl font-black text-gray-900">
              {calculatedPlan.estimated_duration_days} days
            </div>
          </div>
        </div>
        
        {/* Construction Stages */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Construction Stages & Materials</h3>
          
          <div className="space-y-4">
            {calculatedPlan.construction_stages.map((stage, index) => (
              <div key={index} className="border-2 border-gray-200 rounded-lg p-4 hover:border-green-300 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
                      {stage.stage_order}
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900">{stage.stage_name}</h4>
                      <p className="text-sm text-gray-600">{stage.duration_days} days</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-green-600">{formatCurrency(stage.total_cost)}</div>
                    <div className="text-xs text-gray-500">{stage.materials.length} items</div>
                  </div>
                </div>
                
                <details className="cursor-pointer">
                  <summary className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                    View {stage.materials.length} materials
                  </summary>
                  <div className="mt-3 space-y-2">
                    {stage.materials.slice(0, 5).map((material, mIndex) => (
                      <div key={mIndex} className="text-sm bg-gray-50 p-2 rounded flex justify-between">
                        <div>
                          <span className="font-medium">{material.item_name}</span>
                          <span className="text-gray-600"> - {material.quantity} {material.unit}</span>
                        </div>
                        <span className="font-semibold">{formatCurrency(material.total_price)}</span>
                      </div>
                    ))}
                    {stage.materials.length > 5 && (
                      <div className="text-xs text-gray-500 text-center">
                        +{stage.materials.length - 5} more items...
                      </div>
                    )}
                  </div>
                </details>
              </div>
            ))}
          </div>
        </div>
        
        {/* Floor Plan Preview */}
        <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <Building className="w-6 h-6 mr-2 text-green-600" />
            Floor Plan Layouts
          </h3>
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-blue-800">
              <CheckCircle className="w-5 h-5 inline mr-2" />
              2D floor plans have been generated and are included in your PDF download. 
              View the complete floor layouts in "View My Plans" or download the PDF.
            </p>
          </div>
          
          {calculatedPlan.floors.map((floor, idx) => (
            <div key={idx} className="mb-4 last:mb-0">
              <h4 className="font-bold text-gray-900 mb-2">{floor.floor_name}</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <img 
                  src={`${BACKEND_URL}/api/house-plans/${calculatedPlan.id}/floor-plan/${idx}`}
                  alt={`${floor.floor_name} Layout`}
                  className="w-full h-auto rounded-lg border-2 border-green-300"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              </div>
            </div>
          ))}
        </div>
        
        {/* Actions */}
        <div className="flex flex-wrap gap-4">
          <button
            onClick={() => navigate('/house-plans/my-plans')}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white px-6 py-4 rounded-lg font-bold flex items-center justify-center"
          >
            <Save className="w-5 h-5 mr-2" />
            View My Plans
          </button>
          <button
            onClick={() => window.location.reload()}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-4 rounded-lg font-bold flex items-center justify-center"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create New Plan
          </button>
          <button
            onClick={() => {
              window.open(`${BACKEND_URL}/api/house-plans/${calculatedPlan.id}/download-pdf`, '_blank');
            }}
            className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-6 py-4 rounded-lg font-bold flex items-center justify-center"
          >
            <Download className="w-5 h-5 mr-2" />
            Download PDF
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h1 className="text-3xl font-black text-gray-900 flex items-center">
            <Home className="w-8 h-8 mr-3 text-green-600" />
            House Plan Builder
          </h1>
          <p className="text-gray-600 mt-2">Create detailed house plans with accurate material and cost estimates</p>
          
          {/* Progress Steps */}
          <div className="flex items-center justify-between mt-6">
            {[
              { num: 1, label: 'Basic Info' },
              { num: 2, label: 'Design Rooms' },
              { num: 3, label: 'Calculate' },
              { num: 4, label: 'Results' }
            ].map((s, i) => (
              <React.Fragment key={s.num}>
                <div className="flex items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                    step >= s.num ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-600'
                  }`}>
                    {s.num}
                  </div>
                  <span className={`ml-2 text-sm font-medium ${
                    step >= s.num ? 'text-green-600' : 'text-gray-500'
                  }`}>
                    {s.label}
                  </span>
                </div>
                {i < 3 && (
                  <div className={`flex-1 h-1 mx-4 ${
                    step > s.num ? 'bg-green-600' : 'bg-gray-200'
                  }`}></div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
        
        {/* Main Content */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
          {step === 4 && renderStep4()}
        </div>
      </div>
    </div>
  );
};

export default HousePlanBuilder;
