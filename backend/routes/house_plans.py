"""
House Plans Routes Module
==========================
Industry-standard house plan generation with material calculation and cost estimation.

Features:
- Template-based and custom house plans
- Full Bill of Quantities (BOQ) generation
- Material calculation per construction stage
- Regional cost estimation
- PDF export
- 3D/2D visualization data
- Integration with service providers
- Quote request system

Author: Habitere Development Team
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid
import logging
import math
import os
from io import BytesIO

# PDF Generation imports
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image, ImageDraw, ImageFont

# Import from parent modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_database
from utils import get_current_user, serialize_doc

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/house-plans", tags=["House Plans"])


# ==================== PYDANTIC MODELS ====================

class RoomSpec(BaseModel):
    """Room specification within a floor"""
    name: str
    type: str  # bedroom, bathroom, kitchen, living_room, etc.
    length: float  # in meters
    width: float  # in meters
    height: float = 3.0  # default ceiling height in meters

class FloorPlan(BaseModel):
    """Floor plan specification"""
    floor_number: int
    floor_name: str  # Ground Floor, First Floor, etc.
    rooms: List[RoomSpec]
    total_area: Optional[float] = None

class HousePlanCreate(BaseModel):
    """House plan creation model"""
    name: str
    description: Optional[str] = None
    house_type: str  # bungalow, duplex, multi_story, apartment
    location: str  # For regional pricing
    floors: List[FloorPlan]
    foundation_type: str = "strip"  # strip, raft, pile
    wall_type: str = "sandcrete"  # sandcrete, brick, concrete
    roofing_type: str = "aluminum"  # aluminum, tiles, concrete
    finishing_level: str = "standard"  # basic, standard, luxury
    template_id: Optional[str] = None

class MaterialItem(BaseModel):
    """Individual material item in BOQ"""
    category: str
    item_name: str
    unit: str
    quantity: float
    unit_price: float
    total_price: float
    specification: Optional[str] = None

class ConstructionStage(BaseModel):
    """Construction stage with materials"""
    stage_name: str
    stage_order: int
    materials: List[MaterialItem]
    total_cost: float
    duration_days: int

class HousePlanResponse(BaseModel):
    """Complete house plan with calculations"""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    house_type: str
    location: str
    floors: List[FloorPlan]
    total_floor_area: float
    total_built_area: float
    foundation_type: str
    wall_type: str
    roofing_type: str
    finishing_level: str
    construction_stages: List[ConstructionStage]
    total_materials_cost: float
    labor_cost: float
    total_project_cost: float
    estimated_duration_days: int
    created_at: str
    updated_at: str


# ==================== MATERIAL CALCULATION ENGINE ====================

class MaterialCalculator:
    """Advanced material calculation engine"""
    
    # Material prices per unit (XAF) - Base prices for Douala
    MATERIAL_PRICES = {
        # Cement & Aggregates
        "cement_50kg": 4500,
        "sand_tonne": 15000,
        "gravel_tonne": 18000,
        "laterite_tonne": 12000,
        
        # Blocks & Bricks
        "sandcrete_block_6inch": 250,
        "sandcrete_block_9inch": 350,
        "hollow_block_6inch": 275,
        "hollow_block_9inch": 375,
        
        # Steel & Reinforcement
        "steel_10mm_tonne": 650000,
        "steel_12mm_tonne": 650000,
        "steel_16mm_tonne": 650000,
        "steel_20mm_tonne": 650000,
        "binding_wire_kg": 500,
        
        # Roofing
        "aluminum_sheet": 4500,
        "roofing_tile": 2500,
        "ceiling_board": 3500,
        "timber_4x2": 2500,
        "timber_4x4": 4500,
        
        # Doors & Windows
        "door_standard": 35000,
        "door_luxury": 75000,
        "window_standard_sqm": 25000,
        "window_luxury_sqm": 45000,
        
        # Plumbing
        "pvc_pipe_half_inch": 850,
        "pvc_pipe_1inch": 1500,
        "pvc_pipe_2inch": 3500,
        "water_tank_500L": 35000,
        "water_tank_1000L": 65000,
        
        # Electrical
        "cable_2.5mm_meter": 450,
        "cable_4mm_meter": 750,
        "socket_standard": 850,
        "switch_standard": 650,
        "distribution_board": 25000,
        
        # Finishing
        "cement_plaster_sqm": 3500,
        "paint_emulsion_25L": 18000,
        "floor_tiles_sqm": 4500,
        "wall_tiles_sqm": 3500,
    }
    
    # Regional price multipliers
    REGIONAL_MULTIPLIERS = {
        "douala": 1.0,
        "yaounde": 1.05,
        "bafoussam": 0.95,
        "bamenda": 0.98,
        "garoua": 1.10,
        "maroua": 1.12,
        "ngaoundere": 1.08,
        "buea": 1.02,
        "limbe": 1.03,
        "kribi": 1.15,
    }
    
    @staticmethod
    def calculate_foundation_materials(total_area: float, foundation_type: str, location: str) -> List[Dict]:
        """Calculate foundation materials"""
        materials = []
        multiplier = MaterialCalculator.REGIONAL_MULTIPLIERS.get(location.lower(), 1.0)
        
        if foundation_type == "strip":
            # Strip foundation calculations
            cement_bags = math.ceil(total_area * 2.5)
            sand_tonnes = math.ceil(total_area * 0.8)
            gravel_tonnes = math.ceil(total_area * 1.2)
            steel_10mm = math.ceil(total_area * 15)  # kg
            steel_12mm = math.ceil(total_area * 20)  # kg
            
            materials.extend([
                {
                    "category": "Foundation",
                    "item_name": "Cement (50kg bags)",
                    "unit": "bag",
                    "quantity": cement_bags,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["cement_50kg"] * multiplier,
                    "specification": "Grade 32.5 Portland Cement"
                },
                {
                    "category": "Foundation",
                    "item_name": "Sharp Sand",
                    "unit": "tonne",
                    "quantity": sand_tonnes,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["sand_tonne"] * multiplier,
                    "specification": "River sand, washed"
                },
                {
                    "category": "Foundation",
                    "item_name": "Granite Gravel",
                    "unit": "tonne",
                    "quantity": gravel_tonnes,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["gravel_tonne"] * multiplier,
                    "specification": "20mm aggregate"
                },
                {
                    "category": "Foundation",
                    "item_name": "Steel Reinforcement 10mm",
                    "unit": "kg",
                    "quantity": steel_10mm,
                    "unit_price": (MaterialCalculator.MATERIAL_PRICES["steel_10mm_tonne"] / 1000) * multiplier,
                    "specification": "High tensile steel bars"
                },
                {
                    "category": "Foundation",
                    "item_name": "Steel Reinforcement 12mm",
                    "unit": "kg",
                    "quantity": steel_12mm,
                    "unit_price": (MaterialCalculator.MATERIAL_PRICES["steel_12mm_tonne"] / 1000) * multiplier,
                    "specification": "High tensile steel bars"
                },
            ])
        
        elif foundation_type == "raft":
            # Raft foundation (more expensive)
            cement_bags = math.ceil(total_area * 4.0)
            sand_tonnes = math.ceil(total_area * 1.5)
            gravel_tonnes = math.ceil(total_area * 2.0)
            steel_12mm = math.ceil(total_area * 35)
            steel_16mm = math.ceil(total_area * 25)
            
            materials.extend([
                {
                    "category": "Foundation",
                    "item_name": "Cement (50kg bags)",
                    "unit": "bag",
                    "quantity": cement_bags,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["cement_50kg"] * multiplier,
                    "specification": "Grade 42.5 Portland Cement"
                },
                {
                    "category": "Foundation",
                    "item_name": "Sharp Sand",
                    "unit": "tonne",
                    "quantity": sand_tonnes,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["sand_tonne"] * multiplier,
                    "specification": "River sand, washed"
                },
                {
                    "category": "Foundation",
                    "item_name": "Granite Gravel",
                    "unit": "tonne",
                    "quantity": gravel_tonnes,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["gravel_tonne"] * multiplier,
                    "specification": "20mm aggregate"
                },
                {
                    "category": "Foundation",
                    "item_name": "Steel Reinforcement 12mm",
                    "unit": "kg",
                    "quantity": steel_12mm,
                    "unit_price": (MaterialCalculator.MATERIAL_PRICES["steel_12mm_tonne"] / 1000) * multiplier,
                    "specification": "High tensile steel bars"
                },
                {
                    "category": "Foundation",
                    "item_name": "Steel Reinforcement 16mm",
                    "unit": "kg",
                    "quantity": steel_16mm,
                    "unit_price": (MaterialCalculator.MATERIAL_PRICES["steel_16mm_tonne"] / 1000) * multiplier,
                    "specification": "High tensile steel bars"
                },
            ])
        
        # Calculate total prices
        for material in materials:
            material["total_price"] = material["quantity"] * material["unit_price"]
        
        return materials
    
    @staticmethod
    def calculate_blockwork_materials(floors: List[FloorPlan], wall_type: str, location: str) -> List[Dict]:
        """Calculate blockwork/wall materials"""
        materials = []
        multiplier = MaterialCalculator.REGIONAL_MULTIPLIERS.get(location.lower(), 1.0)
        
        # Calculate total wall area (perimeter * height for each floor)
        total_wall_area = 0
        for floor in floors:
            for room in floor.rooms:
                perimeter = 2 * (room.length + room.width)
                wall_area = perimeter * room.height
                total_wall_area += wall_area
        
        # Sandcrete blocks calculation
        if wall_type == "sandcrete":
            blocks_per_sqm = 10  # Standard 6-inch blocks
            total_blocks = math.ceil(total_wall_area * blocks_per_sqm)
            cement_bags = math.ceil(total_blocks * 0.15)  # Mortar cement
            sand_tonnes = math.ceil(total_blocks * 0.025)  # Mortar sand
            
            materials.extend([
                {
                    "category": "Blockwork",
                    "item_name": "Sandcrete Blocks (6 inch)",
                    "unit": "piece",
                    "quantity": total_blocks,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["sandcrete_block_6inch"] * multiplier,
                    "specification": "450x225x150mm hollow blocks"
                },
                {
                    "category": "Blockwork",
                    "item_name": "Cement for Mortar",
                    "unit": "bag",
                    "quantity": cement_bags,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["cement_50kg"] * multiplier,
                    "specification": "Grade 32.5 Portland Cement"
                },
                {
                    "category": "Blockwork",
                    "item_name": "Building Sand",
                    "unit": "tonne",
                    "quantity": sand_tonnes,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["sand_tonne"] * multiplier,
                    "specification": "Fine building sand"
                },
            ])
        
        # Calculate total prices
        for material in materials:
            material["total_price"] = material["quantity"] * material["unit_price"]
        
        return materials
    
    @staticmethod
    def calculate_roofing_materials(total_area: float, roofing_type: str, location: str) -> List[Dict]:
        """Calculate roofing materials"""
        materials = []
        multiplier = MaterialCalculator.REGIONAL_MULTIPLIERS.get(location.lower(), 1.0)
        
        # Add 20% for roof overhang
        roof_area = total_area * 1.2
        
        if roofing_type == "aluminum":
            sheets_needed = math.ceil(roof_area / 1.8)  # 1.8 sqm per sheet
            timber_4x2 = math.ceil(roof_area * 2)  # meters
            timber_4x4 = math.ceil(roof_area * 0.5)  # meters
            nails_kg = math.ceil(roof_area * 0.3)
            
            materials.extend([
                {
                    "category": "Roofing",
                    "item_name": "Aluminum Roofing Sheets",
                    "unit": "sheet",
                    "quantity": sheets_needed,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["aluminum_sheet"] * multiplier,
                    "specification": "0.55mm gauge, corrugated"
                },
                {
                    "category": "Roofing",
                    "item_name": "Timber 4x2 (Battens)",
                    "unit": "meter",
                    "quantity": timber_4x2,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["timber_4x2"] * multiplier,
                    "specification": "Treated timber"
                },
                {
                    "category": "Roofing",
                    "item_name": "Timber 4x4 (Rafters)",
                    "unit": "meter",
                    "quantity": timber_4x4,
                    "unit_price": MaterialCalculator.MATERIAL_PRICES["timber_4x4"] * multiplier,
                    "specification": "Treated timber"
                },
            ])
        
        # Calculate total prices
        for material in materials:
            material["total_price"] = material["quantity"] * material["unit_price"]
        
        return materials
    
    @staticmethod
    def calculate_doors_windows(floors: List[FloorPlan], finishing_level: str, location: str) -> List[Dict]:
        """Calculate doors and windows"""
        materials = []
        multiplier = MaterialCalculator.REGIONAL_MULTIPLIERS.get(location.lower(), 1.0)
        
        # Count rooms to estimate doors
        total_rooms = sum(len(floor.rooms) for floor in floors)
        
        # Standard: 1 external door per floor, 1 internal door per room
        external_doors = len(floors)
        internal_doors = total_rooms - len(floors)
        
        # Windows: estimate based on total area
        total_area = sum(
            sum(room.length * room.width for room in floor.rooms)
            for floor in floors
        )
        window_area = total_area * 0.15  # 15% of floor area for windows
        
        door_price = MaterialCalculator.MATERIAL_PRICES["door_luxury" if finishing_level == "luxury" else "door_standard"]
        window_price = MaterialCalculator.MATERIAL_PRICES["window_luxury_sqm" if finishing_level == "luxury" else "window_standard_sqm"]
        
        materials.extend([
            {
                "category": "Doors & Windows",
                "item_name": "External Doors",
                "unit": "piece",
                "quantity": external_doors,
                "unit_price": door_price * multiplier * 1.5,  # External doors more expensive
                "specification": f"{finishing_level.capitalize()} grade, with frame and locks"
            },
            {
                "category": "Doors & Windows",
                "item_name": "Internal Doors",
                "unit": "piece",
                "quantity": internal_doors,
                "unit_price": door_price * multiplier,
                "specification": f"{finishing_level.capitalize()} grade, with frame"
            },
            {
                "category": "Doors & Windows",
                "item_name": "Windows",
                "unit": "sqm",
                "quantity": math.ceil(window_area),
                "unit_price": window_price * multiplier,
                "specification": f"{finishing_level.capitalize()} aluminum frames with glass"
            },
        ])
        
        # Calculate total prices
        for material in materials:
            material["total_price"] = material["quantity"] * material["unit_price"]
        
        return materials
    
    @staticmethod
    def calculate_plumbing_materials(floors: List[FloorPlan], location: str) -> List[Dict]:
        """Calculate plumbing materials"""
        materials = []
        multiplier = MaterialCalculator.REGIONAL_MULTIPLIERS.get(location.lower(), 1.0)
        
        # Count bathrooms and kitchens
        bathrooms = sum(
            sum(1 for room in floor.rooms if 'bath' in room.type.lower())
            for floor in floors
        )
        kitchens = sum(
            sum(1 for room in floor.rooms if 'kitchen' in room.type.lower())
            for floor in floors
        )
        
        # PVC pipes estimation
        pipe_half_inch = math.ceil((bathrooms + kitchens) * 25)  # meters
        pipe_1inch = math.ceil((bathrooms + kitchens) * 15)  # meters
        pipe_2inch = math.ceil((bathrooms + kitchens) * 10)  # meters
        
        materials.extend([
            {
                "category": "Plumbing",
                "item_name": "PVC Pipe 1/2 inch",
                "unit": "meter",
                "quantity": pipe_half_inch,
                "unit_price": MaterialCalculator.MATERIAL_PRICES["pvc_pipe_half_inch"] * multiplier,
                "specification": "Water supply pipes"
            },
            {
                "category": "Plumbing",
                "item_name": "PVC Pipe 1 inch",
                "unit": "meter",
                "quantity": pipe_1inch,
                "unit_price": MaterialCalculator.MATERIAL_PRICES["pvc_pipe_1inch"] * multiplier,
                "specification": "Main supply line"
            },
            {
                "category": "Plumbing",
                "item_name": "PVC Pipe 2 inch",
                "unit": "meter",
                "quantity": pipe_2inch,
                "unit_price": MaterialCalculator.MATERIAL_PRICES["pvc_pipe_2inch"] * multiplier,
                "specification": "Drainage pipes"
            },
            {
                "category": "Plumbing",
                "item_name": "Water Tank (1000L)",
                "unit": "piece",
                "quantity": 1 if len(floors) > 1 else 0,
                "unit_price": MaterialCalculator.MATERIAL_PRICES["water_tank_1000L"] * multiplier,
                "specification": "Overhead storage tank"
            },
        ])
        
        # Calculate total prices
        for material in materials:
            material["total_price"] = material["quantity"] * material["unit_price"]
        
        return materials
    
    @staticmethod
    def calculate_electrical_materials(floors: List[FloorPlan], location: str) -> List[Dict]:
        """Calculate electrical materials"""
        materials = []
        multiplier = MaterialCalculator.REGIONAL_MULTIPLIERS.get(location.lower(), 1.0)
        
        total_rooms = sum(len(floor.rooms) for floor in floors)
        
        # Estimate electrical points (2 sockets + 2 switches per room)
        sockets = total_rooms * 2
        switches = total_rooms * 2
        cable_2_5mm = math.ceil(total_rooms * 30)  # meters
        cable_4mm = math.ceil(total_rooms * 15)  # meters
        
        materials.extend([
            {
                "category": "Electrical",
                "item_name": "Electrical Cable 2.5mm",
                "unit": "meter",
                "quantity": cable_2_5mm,
                "unit_price": MaterialCalculator.MATERIAL_PRICES["cable_2.5mm_meter"] * multiplier,
                "specification": "PVC insulated copper wire"
            },
            {
                "category": "Electrical",
                "item_name": "Electrical Cable 4mm",
                "unit": "meter",
                "quantity": cable_4mm,
                "unit_price": MaterialCalculator.MATERIAL_PRICES["cable_4mm_meter"] * multiplier,
                "specification": "PVC insulated copper wire"
            },
            {
                "category": "Electrical",
                "item_name": "Power Sockets",
                "unit": "piece",
                "quantity": sockets,
                "unit_price": MaterialCalculator.MATERIAL_PRICES["socket_standard"] * multiplier,
                "specification": "13A standard sockets"
            },
            {
                "category": "Electrical",
                "item_name": "Light Switches",
                "unit": "piece",
                "quantity": switches,
                "unit_price": MaterialCalculator.MATERIAL_PRICES["switch_standard"] * multiplier,
                "specification": "Standard switches"
            },
            {
                "category": "Electrical",
                "item_name": "Distribution Board",
                "unit": "piece",
                "quantity": len(floors),
                "unit_price": MaterialCalculator.MATERIAL_PRICES["distribution_board"] * multiplier,
                "specification": "12-way consumer unit with MCBs"
            },
        ])
        
        # Calculate total prices
        for material in materials:
            material["total_price"] = material["quantity"] * material["unit_price"]
        
        return materials
    
    @staticmethod
    def calculate_finishing_materials(floors: List[FloorPlan], finishing_level: str, location: str) -> List[Dict]:
        """Calculate finishing materials"""
        materials = []
        multiplier = MaterialCalculator.REGIONAL_MULTIPLIERS.get(location.lower(), 1.0)
        
        # Calculate total floor and wall areas
        total_floor_area = sum(
            sum(room.length * room.width for room in floor.rooms)
            for floor in floors
        )
        
        total_wall_area = 0
        for floor in floors:
            for room in floor.rooms:
                perimeter = 2 * (room.length + room.width)
                wall_area = perimeter * room.height
                total_wall_area += wall_area
        
        # Plastering
        plaster_area = total_wall_area
        cement_for_plaster = math.ceil(plaster_area / 12)  # bags per sqm
        
        # Painting
        paint_buckets = math.ceil(total_wall_area / 40)  # 25L covers ~40 sqm
        
        # Floor tiles
        floor_tiles_area = total_floor_area
        
        materials.extend([
            {
                "category": "Finishing",
                "item_name": "Cement for Plastering",
                "unit": "bag",
                "quantity": cement_for_plaster,
                "unit_price": MaterialCalculator.MATERIAL_PRICES["cement_50kg"] * multiplier,
                "specification": "Grade 32.5 Portland Cement"
            },
            {
                "category": "Finishing",
                "item_name": "Plastering Sand",
                "unit": "tonne",
                "quantity": math.ceil(plaster_area / 20),
                "unit_price": MaterialCalculator.MATERIAL_PRICES["sand_tonne"] * multiplier,
                "specification": "Fine plastering sand"
            },
            {
                "category": "Finishing",
                "item_name": "Emulsion Paint (25L)",
                "unit": "bucket",
                "quantity": paint_buckets,
                "unit_price": MaterialCalculator.MATERIAL_PRICES["paint_emulsion_25L"] * multiplier,
                "specification": f"{finishing_level.capitalize()} grade interior paint"
            },
            {
                "category": "Finishing",
                "item_name": "Floor Tiles",
                "unit": "sqm",
                "quantity": math.ceil(floor_tiles_area),
                "unit_price": MaterialCalculator.MATERIAL_PRICES["floor_tiles_sqm"] * multiplier * (1.5 if finishing_level == "luxury" else 1.0),
                "specification": f"{finishing_level.capitalize()} grade ceramic tiles"
            },
        ])
        
        # Calculate total prices
        for material in materials:
            material["total_price"] = material["quantity"] * material["unit_price"]
        
        return materials


# ==================== API ENDPOINTS ====================

@router.post("/create", response_model=Dict[str, Any])
async def create_house_plan(
    plan_data: HousePlanCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new house plan with full material and cost calculation.
    
    Calculates:
    - Material quantities for all construction stages
    - Cost estimation with regional pricing
    - Labor costs
    - Project duration
    - Full Bill of Quantities (BOQ)
    """
    db = get_database()
    
    try:
        # Calculate total floor area
        total_floor_area = sum(
            sum(room.length * room.width for room in floor.rooms)
            for floor in plan_data.floors
        )
        
        # Calculate total built area (including walls)
        total_built_area = total_floor_area * 1.15  # Add 15% for walls
        
        # Calculate materials for each construction stage
        construction_stages = []
        
        # Stage 1: Foundation
        foundation_materials = MaterialCalculator.calculate_foundation_materials(
            total_built_area, 
            plan_data.foundation_type, 
            plan_data.location
        )
        foundation_cost = sum(m["total_price"] for m in foundation_materials)
        construction_stages.append({
            "stage_name": "Foundation & Groundwork",
            "stage_order": 1,
            "materials": foundation_materials,
            "total_cost": foundation_cost,
            "duration_days": 14
        })
        
        # Stage 2: Blockwork
        blockwork_materials = MaterialCalculator.calculate_blockwork_materials(
            plan_data.floors,
            plan_data.wall_type,
            plan_data.location
        )
        blockwork_cost = sum(m["total_price"] for m in blockwork_materials)
        construction_stages.append({
            "stage_name": "Blockwork & Walls",
            "stage_order": 2,
            "materials": blockwork_materials,
            "total_cost": blockwork_cost,
            "duration_days": 21
        })
        
        # Stage 3: Roofing
        roofing_materials = MaterialCalculator.calculate_roofing_materials(
            total_built_area,
            plan_data.roofing_type,
            plan_data.location
        )
        roofing_cost = sum(m["total_price"] for m in roofing_materials)
        construction_stages.append({
            "stage_name": "Roofing & Ceiling",
            "stage_order": 3,
            "materials": roofing_materials,
            "total_cost": roofing_cost,
            "duration_days": 10
        })
        
        # Stage 4: Doors & Windows
        doors_windows_materials = MaterialCalculator.calculate_doors_windows(
            plan_data.floors,
            plan_data.finishing_level,
            plan_data.location
        )
        doors_windows_cost = sum(m["total_price"] for m in doors_windows_materials)
        construction_stages.append({
            "stage_name": "Doors & Windows",
            "stage_order": 4,
            "materials": doors_windows_materials,
            "total_cost": doors_windows_cost,
            "duration_days": 7
        })
        
        # Stage 5: Plumbing
        plumbing_materials = MaterialCalculator.calculate_plumbing_materials(
            plan_data.floors,
            plan_data.location
        )
        plumbing_cost = sum(m["total_price"] for m in plumbing_materials)
        construction_stages.append({
            "stage_name": "Plumbing Installation",
            "stage_order": 5,
            "materials": plumbing_materials,
            "total_cost": plumbing_cost,
            "duration_days": 10
        })
        
        # Stage 6: Electrical
        electrical_materials = MaterialCalculator.calculate_electrical_materials(
            plan_data.floors,
            plan_data.location
        )
        electrical_cost = sum(m["total_price"] for m in electrical_materials)
        construction_stages.append({
            "stage_name": "Electrical Installation",
            "stage_order": 6,
            "materials": electrical_materials,
            "total_cost": electrical_cost,
            "duration_days": 10
        })
        
        # Stage 7: Finishing
        finishing_materials = MaterialCalculator.calculate_finishing_materials(
            plan_data.floors,
            plan_data.finishing_level,
            plan_data.location
        )
        finishing_cost = sum(m["total_price"] for m in finishing_materials)
        construction_stages.append({
            "stage_name": "Finishing & Painting",
            "stage_order": 7,
            "materials": finishing_materials,
            "total_cost": finishing_cost,
            "duration_days": 21
        })
        
        # Calculate totals
        total_materials_cost = sum(stage["total_cost"] for stage in construction_stages)
        labor_cost = total_materials_cost * 0.45  # Labor is typically 45% of materials
        total_project_cost = total_materials_cost + labor_cost
        estimated_duration = sum(stage["duration_days"] for stage in construction_stages)
        
        # Create house plan document
        house_plan = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.get("id"),
            "name": plan_data.name,
            "description": plan_data.description,
            "house_type": plan_data.house_type,
            "location": plan_data.location,
            "floors": [floor.dict() for floor in plan_data.floors],
            "total_floor_area": round(total_floor_area, 2),
            "total_built_area": round(total_built_area, 2),
            "foundation_type": plan_data.foundation_type,
            "wall_type": plan_data.wall_type,
            "roofing_type": plan_data.roofing_type,
            "finishing_level": plan_data.finishing_level,
            "construction_stages": construction_stages,
            "total_materials_cost": round(total_materials_cost, 2),
            "labor_cost": round(labor_cost, 2),
            "total_project_cost": round(total_project_cost, 2),
            "estimated_duration_days": estimated_duration,
            "template_id": plan_data.template_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Save to database
        await db.house_plans.insert_one(house_plan)
        
        logger.info(f"House plan created: {house_plan['id']} by {current_user.get('email')}")
        
        return {
            "success": True,
            "message": "House plan created successfully",
            "plan": serialize_doc(house_plan)
        }
        
    except Exception as e:
        logger.error(f"Error creating house plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create house plan"
        )


@router.get("/my-plans", response_model=Dict[str, Any])
async def get_my_house_plans(
    current_user: dict = Depends(get_current_user)
):
    """Get all house plans created by current user"""
    db = get_database()
    
    try:
        plans = await db.house_plans.find({"user_id": current_user.get("id")}).to_list(length=None)
        
        return {
            "success": True,
            "plans": [serialize_doc(plan) for plan in plans]
        }
        
    except Exception as e:
        logger.error(f"Error fetching house plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch house plans"
        )


@router.get("/{plan_id}", response_model=Dict[str, Any])
async def get_house_plan(
    plan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific house plan by ID"""
    db = get_database()
    
    try:
        plan = await db.house_plans.find_one({"id": plan_id})
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="House plan not found"
            )
        
        # Check ownership
        if plan["user_id"] != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this plan"
            )
        
        return {
            "success": True,
            "plan": serialize_doc(plan)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching house plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch house plan"
        )


@router.delete("/{plan_id}", response_model=Dict[str, Any])
async def delete_house_plan(
    plan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a house plan"""
    db = get_database()
    
    try:
        plan = await db.house_plans.find_one({"id": plan_id})
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="House plan not found"
            )
        
        # Check ownership
        if plan["user_id"] != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this plan"
            )
        
        await db.house_plans.delete_one({"id": plan_id})
        
        logger.info(f"House plan deleted: {plan_id}")
        
        return {
            "success": True,
            "message": "House plan deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting house plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete house plan"
        )
