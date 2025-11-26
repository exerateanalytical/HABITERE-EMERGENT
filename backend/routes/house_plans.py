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


# ==================== HOUSE PLAN TEMPLATES ====================

HOUSE_PLAN_TEMPLATES = {
    "cameroon_3bed_bungalow": {
        "name": "Standard 3-Bedroom Bungalow",
        "description": "Popular Cameroonian 3-bedroom design with living room, kitchen, and bathroom",
        "house_type": "bungalow",
        "floors": [
            {
                "floor_number": 0,
                "floor_name": "Ground Floor",
                "rooms": [
                    {"name": "Living Room", "type": "living_room", "length": 6, "width": 5, "height": 3},
                    {"name": "Master Bedroom", "type": "bedroom", "length": 4.5, "width": 4, "height": 3},
                    {"name": "Bedroom 2", "type": "bedroom", "length": 4, "width": 3.5, "height": 3},
                    {"name": "Bedroom 3", "type": "bedroom", "length": 3.5, "width": 3, "height": 3},
                    {"name": "Kitchen", "type": "kitchen", "length": 4, "width": 3.5, "height": 3},
                    {"name": "Bathroom", "type": "bathroom", "length": 3, "width": 2.5, "height": 3},
                    {"name": "Toilet", "type": "bathroom", "length": 2, "width": 1.5, "height": 3},
                ]
            }
        ]
    },
    "modern_2bed_apartment": {
        "name": "Modern 2-Bedroom Apartment",
        "description": "Contemporary apartment design perfect for urban living",
        "house_type": "apartment",
        "floors": [
            {
                "floor_number": 0,
                "floor_name": "Main Floor",
                "rooms": [
                    {"name": "Open Living/Dining", "type": "living_room", "length": 7, "width": 4, "height": 2.8},
                    {"name": "Master Bedroom", "type": "bedroom", "length": 4, "width": 3.5, "height": 2.8},
                    {"name": "Bedroom 2", "type": "bedroom", "length": 3.5, "width": 3, "height": 2.8},
                    {"name": "Kitchen", "type": "kitchen", "length": 3.5, "width": 3, "height": 2.8},
                    {"name": "Bathroom", "type": "bathroom", "length": 2.5, "width": 2, "height": 2.8},
                    {"name": "Balcony", "type": "balcony", "length": 4, "width": 1.5, "height": 2.8},
                ]
            }
        ]
    },
    "luxury_4bed_duplex": {
        "name": "Luxury 4-Bedroom Duplex",
        "description": "Spacious two-story design with en-suite bedrooms and modern amenities",
        "house_type": "duplex",
        "floors": [
            {
                "floor_number": 0,
                "floor_name": "Ground Floor",
                "rooms": [
                    {"name": "Living Room", "type": "living_room", "length": 7, "width": 6, "height": 3.5},
                    {"name": "Dining Room", "type": "dining_room", "length": 5, "width": 4, "height": 3.5},
                    {"name": "Kitchen", "type": "kitchen", "length": 5, "width": 4, "height": 3.5},
                    {"name": "Guest Bedroom", "type": "bedroom", "length": 4, "width": 3.5, "height": 3.5},
                    {"name": "Guest Bathroom", "type": "bathroom", "length": 2.5, "width": 2, "height": 3.5},
                    {"name": "Storage", "type": "store", "length": 3, "width": 2, "height": 3.5},
                ]
            },
            {
                "floor_number": 1,
                "floor_name": "First Floor",
                "rooms": [
                    {"name": "Master Suite", "type": "bedroom", "length": 6, "width": 5, "height": 3},
                    {"name": "Master Bathroom", "type": "bathroom", "length": 3.5, "width": 3, "height": 3},
                    {"name": "Bedroom 2", "type": "bedroom", "length": 4.5, "width": 4, "height": 3},
                    {"name": "Bedroom 3", "type": "bedroom", "length": 4, "width": 3.5, "height": 3},
                    {"name": "Shared Bathroom", "type": "bathroom", "length": 3, "width": 2.5, "height": 3},
                    {"name": "Family Room", "type": "living_room", "length": 5, "width": 4, "height": 3},
                ]
            }
        ]
    },
    "compact_studio": {
        "name": "Compact Studio Apartment",
        "description": "Efficient single-room living space with bathroom and kitchenette",
        "house_type": "apartment",
        "floors": [
            {
                "floor_number": 0,
                "floor_name": "Main Floor",
                "rooms": [
                    {"name": "Living/Sleeping Area", "type": "living_room", "length": 5, "width": 4, "height": 2.8},
                    {"name": "Kitchenette", "type": "kitchen", "length": 3, "width": 2, "height": 2.8},
                    {"name": "Bathroom", "type": "bathroom", "length": 2.5, "width": 2, "height": 2.8},
                ]
            }
        ]
    },
    "family_5bed_house": {
        "name": "Large 5-Bedroom Family House",
        "description": "Spacious single-story house perfect for large families",
        "house_type": "bungalow",
        "floors": [
            {
                "floor_number": 0,
                "floor_name": "Ground Floor",
                "rooms": [
                    {"name": "Living Room", "type": "living_room", "length": 8, "width": 6, "height": 3.5},
                    {"name": "Dining Room", "type": "dining_room", "length": 5, "width": 4.5, "height": 3.5},
                    {"name": "Master Bedroom", "type": "bedroom", "length": 5, "width": 4.5, "height": 3.5},
                    {"name": "Master Bathroom", "type": "bathroom", "length": 3.5, "width": 3, "height": 3.5},
                    {"name": "Bedroom 2", "type": "bedroom", "length": 4, "width": 3.5, "height": 3.5},
                    {"name": "Bedroom 3", "type": "bedroom", "length": 4, "width": 3.5, "height": 3.5},
                    {"name": "Bedroom 4", "type": "bedroom", "length": 3.5, "width": 3, "height": 3.5},
                    {"name": "Bedroom 5", "type": "bedroom", "length": 3.5, "width": 3, "height": 3.5},
                    {"name": "Kitchen", "type": "kitchen", "length": 5, "width": 4, "height": 3.5},
                    {"name": "Main Bathroom", "type": "bathroom", "length": 3, "width": 2.5, "height": 3.5},
                    {"name": "Guest Toilet", "type": "bathroom", "length": 2, "width": 1.5, "height": 3.5},
                    {"name": "Store Room", "type": "store", "length": 3, "width": 2.5, "height": 3.5},
                ]
            }
        ]
    }
}


@router.get("/templates", response_model=Dict[str, Any])
async def get_house_plan_templates():
    """
    Get all available house plan templates.
    Public endpoint - no authentication required.
    """
    try:
        templates_list = []
        
        for template_id, template in HOUSE_PLAN_TEMPLATES.items():
            total_area = sum(
                sum(room['length'] * room['width'] for room in floor['rooms'])
                for floor in template['floors']
            )
            
            templates_list.append({
                "id": template_id,
                "name": template['name'],
                "description": template['description'],
                "house_type": template['house_type'],
                "floors_count": len(template['floors']),
                "total_area": round(total_area, 2),
                "total_rooms": sum(len(floor['rooms']) for floor in template['floors'])
            })
        
        return {
            "success": True,
            "templates": templates_list
        }
        
    except Exception as e:
        logger.error(f"Error fetching templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch templates"
        )


@router.get("/templates/{template_id}", response_model=Dict[str, Any])
async def get_house_plan_template_detail(template_id: str):
    """
    Get detailed information about a specific template.
    Public endpoint - no authentication required.
    """
    try:
        if template_id not in HOUSE_PLAN_TEMPLATES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        template = HOUSE_PLAN_TEMPLATES[template_id]
        
        total_area = sum(
            sum(room['length'] * room['width'] for room in floor['rooms'])
            for floor in template['floors']
        )
        
        return {
            "success": True,
            "template": {
                "id": template_id,
                **template,
                "total_area": round(total_area, 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch template"
        )

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



# ==================== FLOOR PLAN GENERATION ====================

class FloorPlanGenerator:
    """Generate professional 2D floor plan images with realistic layouts"""
    
    @staticmethod
    def arrange_rooms_smart(rooms, total_width=1000, total_height=700):
        """
        Intelligently arrange rooms in a realistic floor plan layout.
        Uses a grid-based approach to place rooms side-by-side.
        """
        if not rooms:
            return []
        
        # Sort rooms by area (largest first)
        sorted_rooms = sorted(rooms, key=lambda r: r.get('length', 4) * r.get('width', 3), reverse=True)
        
        # Calculate scale factor
        max_dim = max(max(r.get('length', 4), r.get('width', 3)) for r in rooms)
        scale = min(total_width / (max_dim * 3), total_height / (max_dim * 2.5))
        
        placed_rooms = []
        current_x = 50
        current_y = 50
        row_height = 0
        
        for room in sorted_rooms:
            room_length = room.get('length', 4)
            room_width = room.get('width', 3)
            
            # Convert to pixels
            room_px_width = int(room_length * scale)
            room_px_height = int(room_width * scale)
            
            # Check if room fits in current row
            if current_x + room_px_width > total_width - 50:
                # Move to next row
                current_x = 50
                current_y += row_height + 20
                row_height = 0
            
            # Place room
            placed_rooms.append({
                'room': room,
                'x': current_x,
                'y': current_y,
                'width': room_px_width,
                'height': room_px_height
            })
            
            current_x += room_px_width + 20
            row_height = max(row_height, room_px_height)
        
        return placed_rooms, scale
    
    @staticmethod
    def draw_wall(draw, x1, y1, x2, y2, thickness=6):
        """Draw a wall line with proper thickness"""
        draw.rectangle(
            [(x1 - thickness//2, y1 - thickness//2), 
             (x2 + thickness//2, y2 + thickness//2)],
            fill='#2c3e50'
        )
    
    @staticmethod
    def draw_door(draw, x, y, width, orientation='horizontal'):
        """Draw a door symbol"""
        door_color = '#8B4513'
        if orientation == 'horizontal':
            draw.rectangle([(x, y-2), (x+width, y+2)], fill=door_color)
            draw.arc([(x, y-width), (x+width, y+width)], 0, 90, fill='#D2691E', width=2)
        else:
            draw.rectangle([(x-2, y), (x+2, y+width)], fill=door_color)
            draw.arc([(x-width, y), (x+width, y+width)], 0, 90, fill='#D2691E', width=2)
    
    @staticmethod
    def draw_window(draw, x, y, size, orientation='horizontal'):
        """Draw a window symbol"""
        window_color = '#4A90E2'
        if orientation == 'horizontal':
            draw.rectangle([(x, y-3), (x+size, y+3)], fill='white', outline=window_color, width=2)
            draw.line([(x, y), (x+size, y)], fill=window_color, width=1)
        else:
            draw.rectangle([(x-3, y), (x+3, y+size)], fill='white', outline=window_color, width=2)
            draw.line([(x, y), (x, y+size)], fill=window_color, width=1)
    
    @staticmethod
    def draw_furniture_bedroom(draw, x, y, width, height):
        """Draw bedroom furniture (bed, nightstands)"""
        # Bed (centered)
        bed_width = min(width * 0.4, 80)
        bed_height = min(height * 0.5, 100)
        bed_x = x + (width - bed_width) / 2
        bed_y = y + height * 0.3
        
        # Bed frame
        draw.rectangle([(bed_x, bed_y), (bed_x + bed_width, bed_y + bed_height)], 
                      fill='#8B7355', outline='#654321', width=2)
        # Pillow
        pillow_height = bed_height * 0.2
        draw.rectangle([(bed_x + 5, bed_y + 5), (bed_x + bed_width - 5, bed_y + pillow_height)],
                      fill='#FFF8DC', outline='#DEB887', width=1)
        
        # Nightstands
        nightstand_size = min(width * 0.12, 25)
        if width > 150:  # Only draw if room is large enough
            # Left nightstand
            draw.rectangle([(bed_x - nightstand_size - 10, bed_y + bed_height/2 - nightstand_size/2),
                          (bed_x - 10, bed_y + bed_height/2 + nightstand_size/2)],
                         fill='#A0826D', outline='#654321', width=1)
            # Right nightstand
            draw.rectangle([(bed_x + bed_width + 10, bed_y + bed_height/2 - nightstand_size/2),
                          (bed_x + bed_width + 10 + nightstand_size, bed_y + bed_height/2 + nightstand_size/2)],
                         fill='#A0826D', outline='#654321', width=1)
    
    @staticmethod
    def draw_furniture_living_room(draw, x, y, width, height):
        """Draw living room furniture (sofa, coffee table, TV)"""
        # Sofa (L-shaped or straight)
        sofa_width = min(width * 0.6, 120)
        sofa_depth = min(height * 0.25, 50)
        sofa_x = x + (width - sofa_width) / 2
        sofa_y = y + height * 0.6
        
        draw.rectangle([(sofa_x, sofa_y), (sofa_x + sofa_width, sofa_y + sofa_depth)],
                      fill='#4A90E2', outline='#2E5C8A', width=2)
        # Sofa cushions
        cushion_width = sofa_width / 3
        for i in range(3):
            draw.rectangle([(sofa_x + i * cushion_width + 5, sofa_y + 5),
                          (sofa_x + (i + 1) * cushion_width - 5, sofa_y + sofa_depth - 5)],
                         outline='#1E3A5F', width=1)
        
        # Coffee table
        table_width = min(sofa_width * 0.6, 70)
        table_height = min(sofa_depth * 0.8, 35)
        table_x = x + (width - table_width) / 2
        table_y = sofa_y - table_height - 20
        
        draw.rectangle([(table_x, table_y), (table_x + table_width, table_y + table_height)],
                      fill='#8B4513', outline='#654321', width=2)
        
        # TV stand (on opposite wall)
        if height > 100:
            tv_width = min(width * 0.4, 80)
            tv_height = 10
            tv_x = x + (width - tv_width) / 2
            tv_y = y + 20
            draw.rectangle([(tv_x, tv_y), (tv_x + tv_width, tv_y + tv_height)],
                          fill='#2c3e50', outline='#1a1a1a', width=2)
    
    @staticmethod
    def draw_furniture_kitchen(draw, x, y, width, height):
        """Draw kitchen fixtures (counters, sink, stove)"""
        # Counter along one wall
        counter_width = min(width * 0.8, width - 30)
        counter_depth = 25
        counter_x = x + 15
        counter_y = y + 15
        
        # Main counter
        draw.rectangle([(counter_x, counter_y), (counter_x + counter_width, counter_y + counter_depth)],
                      fill='#D2B48C', outline='#8B7355', width=2)
        
        # Sink (in counter)
        sink_width = 30
        sink_x = counter_x + counter_width * 0.3
        draw.ellipse([(sink_x, counter_y + 5), (sink_x + sink_width, counter_y + counter_depth - 5)],
                    fill='#C0C0C0', outline='#808080', width=2)
        
        # Stove/Cooktop
        stove_width = 35
        stove_x = counter_x + counter_width * 0.65
        draw.rectangle([(stove_x, counter_y + 5), (stove_x + stove_width, counter_y + counter_depth - 5)],
                      fill='#2c3e50', outline='#1a1a1a', width=2)
        # Burners
        for i in range(2):
            for j in range(2):
                draw.ellipse([(stove_x + 5 + i * 15, counter_y + 8 + j * 10),
                            (stove_x + 15 + i * 15, counter_y + 18 + j * 10)],
                           outline='#555', width=1)
        
        # Refrigerator (corner)
        if width > 100 and height > 100:
            fridge_width = 30
            fridge_height = 35
            fridge_x = x + width - fridge_width - 15
            fridge_y = y + 15
            draw.rectangle([(fridge_x, fridge_y), (fridge_x + fridge_width, fridge_y + fridge_height)],
                          fill='#E8E8E8', outline='#A9A9A9', width=2)
            # Fridge handles
            draw.line([(fridge_x + 5, fridge_y + 10), (fridge_x + 5, fridge_y + 25)],
                     fill='#696969', width=2)
    
    @staticmethod
    def draw_furniture_bathroom(draw, x, y, width, height):
        """Draw bathroom fixtures (toilet, sink, shower/tub)"""
        # Toilet
        toilet_size = min(width * 0.25, 30)
        toilet_x = x + width - toilet_size - 15
        toilet_y = y + 15
        
        # Toilet bowl
        draw.ellipse([(toilet_x, toilet_y), (toilet_x + toilet_size, toilet_y + toilet_size)],
                    fill='white', outline='#D3D3D3', width=2)
        # Toilet tank
        draw.rectangle([(toilet_x + 5, toilet_y - 10), (toilet_x + toilet_size - 5, toilet_y)],
                      fill='white', outline='#D3D3D3', width=2)
        
        # Sink
        sink_width = min(width * 0.3, 35)
        sink_x = x + 15
        sink_y = y + 15
        
        draw.ellipse([(sink_x, sink_y), (sink_x + sink_width, sink_y + sink_width * 0.7)],
                    fill='white', outline='#C0C0C0', width=2)
        # Faucet
        draw.line([(sink_x + sink_width/2, sink_y - 5), (sink_x + sink_width/2, sink_y)],
                 fill='#C0C0C0', width=3)
        
        # Shower/Bathtub
        if height > 80:
            tub_width = min(width * 0.5, 50)
            tub_height = min(height * 0.4, 70)
            tub_x = x + 15
            tub_y = y + height - tub_height - 15
            
            draw.rectangle([(tub_x, tub_y), (tub_x + tub_width, tub_y + tub_height)],
                          fill='#F0F8FF', outline='#B0C4DE', width=2)
            # Shower head
            draw.ellipse([(tub_x + 5, tub_y + 5), (tub_x + 15, tub_y + 15)],
                        fill='#C0C0C0', outline='#808080', width=1)
    
    @staticmethod
    def draw_furniture_dining_room(draw, x, y, width, height):
        """Draw dining room furniture (table, chairs)"""
        # Dining table (centered)
        table_width = min(width * 0.6, 100)
        table_height = min(height * 0.5, 80)
        table_x = x + (width - table_width) / 2
        table_y = y + (height - table_height) / 2
        
        draw.rectangle([(table_x, table_y), (table_x + table_width, table_y + table_height)],
                      fill='#8B4513', outline='#654321', width=2)
        
        # Chairs around table
        chair_size = 15
        # Top chairs
        for i in range(2):
            chair_x = table_x + table_width * 0.25 * (i + 1)
            draw.rectangle([(chair_x - chair_size/2, table_y - chair_size - 5),
                          (chair_x + chair_size/2, table_y - 5)],
                         fill='#654321', outline='#4A3728', width=1)
        # Bottom chairs
        for i in range(2):
            chair_x = table_x + table_width * 0.25 * (i + 1)
            draw.rectangle([(chair_x - chair_size/2, table_y + table_height + 5),
                          (chair_x + chair_size/2, table_y + table_height + chair_size + 5)],
                         fill='#654321', outline='#4A3728', width=1)
        # Side chairs if room is wide enough
        if width > 150:
            # Left chair
            draw.rectangle([(table_x - chair_size - 5, table_y + table_height/2 - chair_size/2),
                          (table_x - 5, table_y + table_height/2 + chair_size/2)],
                         fill='#654321', outline='#4A3728', width=1)
            # Right chair
            draw.rectangle([(table_x + table_width + 5, table_y + table_height/2 - chair_size/2),
                          (table_x + table_width + chair_size + 5, table_y + table_height/2 + chair_size/2)],
                         fill='#654321', outline='#4A3728', width=1)
    
    @staticmethod
    def draw_room_furniture(draw, room_type, x, y, width, height):
        """Draw appropriate furniture based on room type"""
        if width < 60 or height < 60:  # Room too small for furniture
            return
        
        if room_type == 'bedroom':
            FloorPlanGenerator.draw_furniture_bedroom(draw, x, y, width, height)
        elif room_type == 'living_room':
            FloorPlanGenerator.draw_furniture_living_room(draw, x, y, width, height)
        elif room_type == 'kitchen':
            FloorPlanGenerator.draw_furniture_kitchen(draw, x, y, width, height)
        elif room_type == 'bathroom':
            FloorPlanGenerator.draw_furniture_bathroom(draw, x, y, width, height)
        elif room_type == 'dining_room':
            FloorPlanGenerator.draw_furniture_dining_room(draw, x, y, width, height)
    
    @staticmethod
    def generate_proper_floor_plan(floor: Dict, floor_number: int) -> str:
        """
        Generate a PROPER architectural floor plan with connected rooms,
        hallways, and following architectural standards
        """
        try:
            # Image settings
            scale = 60  # pixels per meter - increased for better detail
            margin = 150
            
            # Get all rooms
            rooms = floor.get('rooms', [])
            if not rooms:
                return None
            
            # Step 1: Analyze room requirements and calculate building footprint
            total_area = sum(r.get('length', 4) * r.get('width', 3) for r in rooms)
            
            # Calculate optimal building dimensions (rectangular footprint)
            # Aim for roughly 1.5:1 aspect ratio for a typical bungalow
            building_width = (total_area * 1.5) ** 0.5
            building_length = total_area / building_width
            
            # Add hallway space (15% of total area)
            building_width *= 1.15
            building_length *= 1.15
            
            # Round to nearest 0.5m
            building_width = round(building_width * 2) / 2
            building_length = round(building_length * 2) / 2
            
            # Image dimensions
            img_width = int(building_length * scale + 2 * margin)
            img_height = int(building_width * scale + 2 * margin)
            
            # Create image
            img = Image.new('RGB', (img_width, img_height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Load fonts
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                font_room = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
                font_dim = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
            except:
                font_title = ImageFont.load_default()
                font_room = ImageFont.load_default()
                font_dim = ImageFont.load_default()
            
            # Step 2: Layout rooms using proper architectural algorithm
            # Create building perimeter
            building_x = margin
            building_y = margin + 60  # Space for title
            building_w = int(building_length * scale)
            building_h = int(building_width * scale)
            
            # Draw title
            floor_name = floor.get('floor_name', f'Floor {floor_number}')
            draw.text((margin, 20), f"{floor_name.upper()} - FLOOR PLAN", fill='#1a1a1a', font=font_title)
            
            # Draw building perimeter (external walls) - THICK BLACK LINES
            wall_thickness = 8
            draw.rectangle(
                [(building_x, building_y), (building_x + building_w, building_y + building_h)],
                outline='#000000',
                width=wall_thickness
            )
            
            # Step 3: Arrange rooms in a connected layout
            # Categorize rooms
            living_rooms = [r for r in rooms if r.get('type') in ['living_room', 'dining_room']]
            bedrooms = [r for r in rooms if r.get('type') == 'bedroom']
            service_rooms = [r for r in rooms if r.get('type') in ['kitchen', 'bathroom', 'store']]
            other_rooms = [r for r in rooms if r not in living_rooms + bedrooms + service_rooms]
            
            # Layout strategy: 
            # - Living spaces at the front/entrance
            # - Central hallway (10% of width)
            # - Bedrooms on one side
            # - Service rooms distributed logically
            
            hallway_width_m = building_length * 0.1  # 10% for hallway
            hallway_width_px = int(hallway_width_m * scale)
            
            # Calculate usable space
            left_zone_w = int((building_w - hallway_width_px) * 0.5)
            right_zone_w = building_w - hallway_width_px - left_zone_w
            
            # Place rooms in zones
            room_placements = []
            current_y_left = building_y + wall_thickness
            current_y_right = building_y + wall_thickness
            
            # Zone 1 (Left): Living spaces
            for room in living_rooms:
                room_w = int(room.get('length', 4) * scale)
                room_h = int(room.get('width', 3) * scale)
                # Fit to zone
                room_w = min(room_w, left_zone_w - 20)
                room_placements.append({
                    'room': room,
                    'x': building_x + wall_thickness,
                    'y': current_y_left,
                    'w': room_w,
                    'h': room_h
                })
                current_y_left += room_h
            
            # Zone 2 (Right): Bedrooms
            for room in bedrooms:
                room_w = int(room.get('length', 4) * scale)
                room_h = int(room.get('width', 3) * scale)
                room_w = min(room_w, right_zone_w - 20)
                room_placements.append({
                    'room': room,
                    'x': building_x + left_zone_w + hallway_width_px,
                    'y': current_y_right,
                    'w': room_w,
                    'h': room_h
                })
                current_y_right += room_h
            
            # Zone 3: Service rooms (distribute)
            for idx, room in enumerate(service_rooms):
                room_w = int(room.get('length', 4) * scale)
                room_h = int(room.get('width', 3) * scale)
                if idx % 2 == 0:
                    # Left zone
                    room_w = min(room_w, left_zone_w - 20)
                    room_placements.append({
                        'room': room,
                        'x': building_x + wall_thickness,
                        'y': current_y_left,
                        'w': room_w,
                        'h': room_h
                    })
                    current_y_left += room_h
                else:
                    # Right zone
                    room_w = min(room_w, right_zone_w - 20)
                    room_placements.append({
                        'room': room,
                        'x': building_x + left_zone_w + hallway_width_px,
                        'y': current_y_right,
                        'w': room_w,
                        'h': room_h
                    })
                    current_y_right += room_h
            
            # Room type colors (more professional palette)
            room_colors = {
                'living_room': '#E8F5E9',
                'bedroom': '#E3F2FD',
                'kitchen': '#FFF3E0',
                'bathroom': '#F3E5F5',
                'dining_room': '#E0F2F1',
                'office': '#FFF9C4',
                'store': '#FFE0B2',
                'balcony': '#F8BBD0',
                'garage': '#CFD8DC',
                'hallway': '#F5F5F5'
            }
            
            # Draw rooms with walls, doors, and windows
            for idx, room_data in enumerate(placed_rooms):
                room = room_data['room']
                x = room_data['x'] + padding
                y = room_data['y'] + padding + 70
                width = room_data['width']
                height = room_data['height']
                
                room_type = room.get('type', 'bedroom')
                room_color = room_colors.get(room_type, '#E8EAF6')
                
                # Draw room floor
                draw.rectangle(
                    [(x, y), (x + width, y + height)],
                    fill=room_color,
                    outline='#2c3e50',
                    width=6
                )
                
                # Add texture/pattern for different room types
                if room_type == 'bathroom':
                    # Tiles pattern
                    for i in range(x + 10, x + width - 10, 20):
                        for j in range(y + 10, y + height - 10, 20):
                            draw.rectangle([(i, j), (i+15, j+15)], outline='#9E9E9E', width=1)
                
                # Draw furniture and fixtures for this room
                FloorPlanGenerator.draw_room_furniture(draw, room_type, x, y, width, height)
                
                # Draw door (on one side)
                door_width = min(40, width // 3)
                door_x = x + width // 2 - door_width // 2
                FloorPlanGenerator.draw_door(draw, door_x, y, door_width, 'horizontal')
                
                # Draw windows (if room is not bathroom/store)
                if room_type not in ['bathroom', 'store']:
                    window_size = min(50, width // 4)
                    # Top wall window
                    if height > 80:
                        FloorPlanGenerator.draw_window(
                            draw, x + width // 2 - window_size // 2, 
                            y + height, window_size, 'horizontal'
                        )
                
                # Draw dimension labels on walls
                room_length = room.get('length', 4)
                room_width = room.get('width', 3)
                try:
                    # Top wall dimension (length)
                    dim_text = f"{room_length}m"
                    draw.text((x + width/2, y - 15), dim_text, fill='#059669', 
                             font=font_small, anchor='mm')
                    # Side wall dimension (width)
                    dim_text = f"{room_width}m"
                    draw.text((x - 20, y + height/2), dim_text, fill='#059669',
                             font=font_small, anchor='mm')
                except:
                    pass  # Skip if font not available
                
                # Room label (centered)
                room_name = room.get('name', f'Room {idx+1}')
                room_type_label = room_type.replace('_', ' ').title()
                dimensions = f"{room.get('length', 4)}m × {room.get('width', 3)}m"
                area = f"{room.get('length', 4) * room.get('width', 3):.1f} m²"
                
                # Center of room
                center_x = x + width // 2
                center_y = y + height // 2
                
                # Draw text with background
                draw.text((center_x, center_y - 25), room_name, 
                         fill='#2c3e50', font=font_label, anchor='mm')
                draw.text((center_x, center_y), room_type_label, 
                         fill='#555', font=font_info, anchor='mm')
                draw.text((center_x, center_y + 20), dimensions, 
                         fill='#777', font=font_small, anchor='mm')
                
                # Area badge
                area_bbox = draw.textbbox((center_x, center_y + 40), area, font=font_info, anchor='mm')
                draw.rectangle(
                    [(area_bbox[0]-5, area_bbox[1]-3), (area_bbox[2]+5, area_bbox[3]+3)],
                    fill='#10b981',
                    outline='#059669',
                    width=2
                )
                draw.text((center_x, center_y + 40), area, 
                         fill='white', font=font_info, anchor='mm')
            
            # Legend and info box
            legend_y = img_height - 60
            draw.rectangle([(padding, legend_y), (img_width - padding, img_height - 20)], 
                          fill='#f8f9fa', outline='#dee2e6', width=2)
            
            # Total area
            total_area = sum(r.get('length', 4) * r.get('width', 3) for r in rooms)
            draw.text((padding + 20, legend_y + 15), 
                     f"Total Floor Area: {total_area:.2f} m²  |  Rooms: {len(rooms)}  |  Scale: ~1:{int(100/scale)}",
                     fill='#2c3e50', font=font_info)
            
            # Draw symbols legend
            legend_x = img_width - padding - 300
            draw.text((legend_x, legend_y + 5), "Symbols:", fill='#2c3e50', font=font_small)
            # Door symbol
            FloorPlanGenerator.draw_door(draw, legend_x + 70, legend_y + 12, 20, 'horizontal')
            draw.text((legend_x + 100, legend_y + 12), "Door", fill='#555', font=font_small)
            # Window symbol
            FloorPlanGenerator.draw_window(draw, legend_x + 160, legend_y + 12, 20, 'horizontal')
            draw.text((legend_x + 190, legend_y + 12), "Window", fill='#555', font=font_small)
            
            # North arrow
            arrow_x = img_width - 100
            arrow_y = padding + 120
            draw.text((arrow_x, arrow_y), "N", fill='#2c3e50', font=font_title)
            draw.polygon([(arrow_x, arrow_y-30), (arrow_x-15, arrow_y-10), (arrow_x+15, arrow_y-10)], 
                        fill='#10b981', outline='#059669')
            
            # Save image
            output_dir = "/app/backend/uploads/floor_plans"
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"floor_{floor_number}_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(output_dir, filename)
            img.save(filepath, quality=95)
            
            logger.info(f"Advanced floor plan generated: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating floor plan: {e}")
            import traceback
            traceback.print_exc()
            return None


# ==================== PDF GENERATION ====================

class HousePlanPDFGenerator:
    """Generate professional PDF house plans"""
    
    @staticmethod
    def generate_pdf(plan: Dict) -> str:
        """
        Generate a comprehensive PDF house plan document.
        Returns the file path of the generated PDF.
        """
        try:
            # Create output directory
            output_dir = "/app/backend/uploads/pdf_plans"
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"house_plan_{plan['id'][:8]}.pdf"
            filepath = os.path.join(output_dir, filename)
            
            # Create PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4,
                                   rightMargin=1*cm, leftMargin=1*cm,
                                   topMargin=1*cm, bottomMargin=1*cm)
            
            # Container for PDF elements
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#10b981'),
                spaceAfter=12,
                alignment=TA_CENTER
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#059669'),
                spaceAfter=10,
                spaceBefore=10
            )
            
            # Title Page
            elements.append(Paragraph("HOUSE PLAN & COST ESTIMATE", title_style))
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph(f"<b>Project Name:</b> {plan['name']}", styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
            
            if plan.get('description'):
                elements.append(Paragraph(f"<b>Description:</b> {plan['description']}", styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
            
            # Project Summary Table
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("PROJECT SUMMARY", heading_style))
            
            summary_data = [
                ['Item', 'Value'],
                ['House Type', plan['house_type'].replace('_', ' ').title()],
                ['Location', plan['location'].title()],
                ['Total Floor Area', f"{plan['total_floor_area']:.2f} m²"],
                ['Total Built Area', f"{plan['total_built_area']:.2f} m²"],
                ['Number of Floors', str(len(plan['floors']))],
                ['Foundation Type', plan['foundation_type'].title()],
                ['Wall Type', plan['wall_type'].title()],
                ['Roofing Type', plan['roofing_type'].title()],
                ['Finishing Level', plan['finishing_level'].title()],
                ['Estimated Duration', f"{plan['estimated_duration_days']} days"],
            ]
            
            summary_table = Table(summary_data, colWidths=[3.5*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ]))
            elements.append(summary_table)
            
            # Cost Summary
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("COST SUMMARY", heading_style))
            
            cost_data = [
                ['Description', 'Amount (XAF)'],
                ['Materials Cost', f"{plan['total_materials_cost']:,.0f}"],
                ['Labor Cost', f"{plan['labor_cost']:,.0f}"],
                ['TOTAL PROJECT COST', f"{plan['total_project_cost']:,.0f}"],
            ]
            
            cost_table = Table(cost_data, colWidths=[3.5*inch, 3*inch])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 14),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(cost_table)
            
            elements.append(PageBreak())
            
            # Floor Plans
            elements.append(Paragraph("FLOOR PLANS", heading_style))
            
            for idx, floor in enumerate(plan['floors']):
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(f"<b>{floor['floor_name']}</b>", styles['Heading3']))
                
                # Generate floor plan image
                floor_image_path = FloorPlanGenerator.generate_floor_plan_image(floor, idx)
                
                if floor_image_path and os.path.exists(floor_image_path):
                    # Add image to PDF
                    img = RLImage(floor_image_path, width=6*inch, height=4.5*inch)
                    elements.append(img)
                
                # Room details table
                elements.append(Spacer(1, 0.2*inch))
                room_data = [['Room Name', 'Type', 'Dimensions', 'Area (m²)']]
                
                for room in floor.get('rooms', []):
                    room_data.append([
                        room['name'],
                        room['type'].replace('_', ' ').title(),
                        f"{room['length']}m × {room['width']}m",
                        f"{room['length'] * room['width']:.2f}"
                    ])
                
                floor_area = sum(r['length'] * r['width'] for r in floor.get('rooms', []))
                room_data.append(['TOTAL FLOOR AREA', '', '', f"{floor_area:.2f}"])
                
                room_table = Table(room_data, colWidths=[2*inch, 1.8*inch, 1.5*inch, 1.2*inch])
                room_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.lightgrey),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#059669')),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(room_table)
                
                if idx < len(plan['floors']) - 1:
                    elements.append(PageBreak())
            
            elements.append(PageBreak())
            
            # Bill of Quantities
            elements.append(Paragraph("BILL OF QUANTITIES (BOQ)", heading_style))
            
            for stage in plan['construction_stages']:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(
                    f"<b>Stage {stage['stage_order']}: {stage['stage_name']}</b> - {stage['duration_days']} days",
                    styles['Heading3']
                ))
                
                # Materials table
                boq_data = [['Item', 'Unit', 'Quantity', 'Unit Price', 'Total Price']]
                
                for material in stage['materials']:
                    boq_data.append([
                        material['item_name'],
                        material['unit'],
                        f"{material['quantity']:.2f}",
                        f"{material['unit_price']:,.0f}",
                        f"{material['total_price']:,.0f}"
                    ])
                
                boq_data.append(['STAGE TOTAL', '', '', '', f"{stage['total_cost']:,.0f}"])
                
                boq_table = Table(boq_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.2*inch])
                boq_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.lightgrey),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#059669')),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ]))
                elements.append(boq_table)
            
            # Footer
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph(
                f"Generated by Habitere.com on {datetime.now(timezone.utc).strftime('%B %d, %Y')}",
                ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
            ))
            elements.append(Paragraph(
                "This estimate is based on current market prices and may vary.",
                ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
            ))
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"PDF generated: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise


@router.get("/{plan_id}/download-pdf")
async def download_house_plan_pdf(
    plan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate and download house plan as PDF with floor plans and BOQ.
    """
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
        
        # Generate PDF
        pdf_path = HousePlanPDFGenerator.generate_pdf(plan)
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF"
            )
        
        # Return PDF file
        return FileResponse(
            path=pdf_path,
            filename=f"{plan['name'].replace(' ', '_')}_House_Plan.pdf",
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={plan['name'].replace(' ', '_')}_House_Plan.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download PDF"
        )


@router.get("/{plan_id}/floor-plan/{floor_number}")
async def get_floor_plan_image(
    plan_id: str,
    floor_number: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get floor plan image for a specific floor.
    Generates the image if it doesn't exist.
    """
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
        
        # Get the specific floor
        if floor_number >= len(plan['floors']):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Floor not found"
            )
        
        floor = plan['floors'][floor_number]
        
        # Generate floor plan image
        floor_image_path = FloorPlanGenerator.generate_floor_plan_image(floor, floor_number)
        
        if not floor_image_path or not os.path.exists(floor_image_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate floor plan image"
            )
        
        # Return image file
        return FileResponse(
            path=floor_image_path,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting floor plan image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get floor plan image"
        )
