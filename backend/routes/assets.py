"""
Asset Management Routes Module
================================
Handles all asset management API endpoints for Habitere platform.

This module provides:
- Asset registration and management (Real Estate, Equipment, Infrastructure, etc.)
- Maintenance task scheduling and tracking
- Expense logging and approval workflow
- Inventory management with low stock alerts
- Automated notifications and reminders

Features:
- Full CRUD for assets, maintenance tasks, and expenses
- Role-based access (Owner, Estate Manager, Technician, Viewer)
- Automated maintenance reminders
- Expense approval workflow
- Dashboard analytics

Authorization:
- Asset creation: property_owner, estate_manager, admin
- Maintenance tasks: estate_manager, technician, admin
- Expense approval: property_owner, admin
- View permissions: All authenticated users (filtered by ownership)

Dependencies:
- FastAPI for routing
- MongoDB for data storage
- Authentication middleware for protected endpoints

Author: Habitere Development Team
Last Modified: 2025-10-18
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
import uuid
import logging

# Import from parent modules
import sys
from pathlib import Path as FilePath
sys.path.append(str(FilePath(__file__).parent.parent))

from database import get_database
from utils import get_current_user, serialize_doc
from utils.notifications import create_in_app_notification

# Setup logging
logger = logging.getLogger(__name__)

# Create router for asset management endpoints
router = APIRouter(prefix="/assets", tags=["Asset Management"])


# ==================== PYDANTIC MODELS ====================

class AssetCreate(BaseModel):
    """Asset creation model."""
    name: str
    category: str  # Real Estate, Building Equipment, Infrastructure, Furniture, Vehicle, Tool
    property_id: str  # Link to existing property
    location: str
    status: str = "Active"  # Active, Under Maintenance, Decommissioned
    condition: str = "Good"  # Excellent, Good, Fair, Poor
    serial_number: Optional[str] = None
    acquisition_date: Optional[str] = None
    purchase_value: Optional[float] = None
    assigned_to: Optional[str] = None  # User ID
    documents: List[str] = []  # Document URLs
    last_maintenance_date: Optional[str] = None
    next_maintenance_date: Optional[str] = None
    depreciation_rate: Optional[float] = None
    notes: Optional[str] = None


class MaintenanceTaskCreate(BaseModel):
    """Maintenance task creation model."""
    asset_id: str
    task_title: str
    description: str
    assigned_to: Optional[str] = None  # User ID (technician)
    priority: str = "Medium"  # Low, Medium, High
    status: str = "Pending"  # Pending, In Progress, Completed
    scheduled_date: str
    attachments: List[str] = []
    estimated_cost: Optional[float] = None
    notes: Optional[str] = None


class ExpenseCreate(BaseModel):
    """Expense creation model."""
    asset_id: str
    expense_type: str  # Maintenance, Upgrade, Purchase, Repair
    amount: float
    description: str
    date: str
    approved_by: Optional[str] = None


class InventoryItemCreate(BaseModel):
    """Inventory item creation model."""
    name: str
    category: str  # Spare Parts, Tools, Consumables, Equipment, Safety Gear
    property_id: Optional[str] = None  # Link to property if specific
    quantity: int
    unit: str  # pcs, kg, liters, meters, etc.
    reorder_level: int  # Minimum quantity before reorder
    reorder_quantity: int  # Quantity to reorder
    unit_cost: Optional[float] = None
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None
    location: Optional[str] = None  # Storage location
    notes: Optional[str] = None


class InventoryItemUpdate(BaseModel):
    """Inventory item update model."""
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    reorder_level: Optional[int] = None
    reorder_quantity: Optional[int] = None
    unit_cost: Optional[float] = None
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class AssetUpdate(BaseModel):
    """Asset update model."""
    name: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    condition: Optional[str] = None
    serial_number: Optional[str] = None
    assigned_to: Optional[str] = None
    last_maintenance_date: Optional[str] = None
    next_maintenance_date: Optional[str] = None
    notes: Optional[str] = None


# ==================== ASSETS CRUD ====================

@router.post("/", response_model=Dict[str, Any])
async def create_asset(
    asset_data: AssetCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new asset.
    
    Only property owners, estate managers, and admins can create assets.
    
    Args:
        asset_data: Asset details
        current_user: Authenticated user
        
    Returns:
        Created asset with ID
        
    Raises:
        HTTPException: 403 if not authorized
    """
    db = get_database()
    
    # Check authorization
    allowed_roles = ["property_owner", "estate_manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only property owners, estate managers, and admins can create assets"
        )
    
    # Verify property exists
    property_doc = await db.properties.find_one({"id": asset_data.property_id})
    if not property_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Create asset
    asset = {
        "id": str(uuid.uuid4()),
        "owner_id": current_user["id"],
        **asset_data.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.assets.insert_one(asset)
    
    logger.info(f"Asset created: {asset['id']} by {current_user['email']}")
    
    # Send notification to assigned user if any
    if asset_data.assigned_to:
        try:
            await create_in_app_notification(
                user_id=asset_data.assigned_to,
                title="Asset Assigned",
                message=f"You have been assigned asset: {asset_data.name}",
                type="info",
                link=f"/assets/{asset['id']}"
            )
        except Exception as e:
            logger.error(f"Error sending assignment notification: {str(e)}")
    
    return serialize_doc(asset)


@router.get("/", response_model=List[Dict[str, Any]])
async def get_assets(
    property_id: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    condition: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Get assets with optional filtering.
    
    Users see only assets they own or are assigned to.
    Estate managers and admins see all assets.
    
    Args:
        property_id: Filter by property
        category: Filter by category
        status: Filter by status
        condition: Filter by condition
        skip: Pagination skip
        limit: Pagination limit
        current_user: Authenticated user
        
    Returns:
        List of assets
    """
    db = get_database()
    
    # Build filters
    filters = {}
    
    # Role-based filtering
    if current_user.get("role") not in ["estate_manager", "admin"]:
        # Users see only their assets or assets assigned to them
        filters["$or"] = [
            {"owner_id": current_user["id"]},
            {"assigned_to": current_user["id"]}
        ]
    
    if property_id:
        filters["property_id"] = property_id
    if category:
        filters["category"] = category
    if status:
        filters["status"] = status
    if condition:
        filters["condition"] = condition
    
    assets = await db.assets.find(filters).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return [serialize_doc(asset) for asset in assets]



@router.get("/{asset_id}", response_model=Dict[str, Any])
async def get_asset(
    asset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get single asset by ID.
    
    Args:
        asset_id: Asset ID
        current_user: Authenticated user
        
    Returns:
        Asset details
        
    Raises:
        HTTPException: 404 if asset not found or 403 if unauthorized
    """
    db = get_database()
    
    asset = await db.assets.find_one({"id": asset_id})
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Check authorization
    if current_user.get("role") not in ["estate_manager", "admin"]:
        if asset.get("owner_id") != current_user["id"] and asset.get("assigned_to") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this asset"
            )
    
    return serialize_doc(asset)


@router.put("/{asset_id}", response_model=Dict[str, Any])
async def update_asset(
    asset_id: str,
    asset_update: AssetCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update asset.
    
    Only owner, estate managers, and admins can update assets.
    
    Args:
        asset_id: Asset ID
        asset_update: Updated asset data
        current_user: Authenticated user
        
    Returns:
        Updated asset
        
    Raises:
        HTTPException: 404 if asset not found or 403 if unauthorized
    """
    db = get_database()
    
    # Check if asset exists
    asset = await db.assets.find_one({"id": asset_id})
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Check authorization
    if current_user.get("role") not in ["estate_manager", "admin"]:
        if asset.get("owner_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this asset"
            )
    
    # Update asset
    update_data = asset_update.dict()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.assets.update_one(
        {"id": asset_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update asset"
        )
    
    # Get updated asset
    updated_asset = await db.assets.find_one({"id": asset_id})
    
    logger.info(f"Asset updated: {asset_id} by user {current_user['id']}")
    
    return serialize_doc(updated_asset)


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete asset.
    
    Only owner, estate managers, and admins can delete assets.
    Also deletes all associated maintenance tasks and expenses.
    
    Args:
        asset_id: Asset ID
        current_user: Authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if asset not found or 403 if unauthorized
    """
    db = get_database()
    
    # Check if asset exists
    asset = await db.assets.find_one({"id": asset_id})
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Check authorization
    if current_user.get("role") not in ["estate_manager", "admin"]:
        if asset.get("owner_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this asset"
            )
    
    # Delete associated maintenance tasks
    await db.maintenance_tasks.delete_many({"asset_id": asset_id})
    
    # Delete associated expenses
    await db.expenses.delete_many({"asset_id": asset_id})
    
    # Delete asset
    result = await db.assets.delete_one({"id": asset_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete asset"
        )
    
    logger.info(f"Asset deleted: {asset_id} by user {current_user['id']}")
    
    return {"message": "Asset and associated data deleted successfully"}



# ==================== MAINTENANCE TASKS ====================

@router.post("/maintenance", response_model=Dict[str, Any])
async def create_maintenance_task(
    task_data: MaintenanceTaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a maintenance task.
    
    Estate managers, property owners, and admins can create tasks.
    
    Args:
        task_data: Task details
        current_user: Authenticated user
        
    Returns:
        Created task with ID
    """
    db = get_database()
    
    # Check authorization
    allowed_roles = ["property_owner", "estate_manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only estate managers, property owners, and admins can create maintenance tasks"
        )
    
    # Verify asset exists
    asset = await db.assets.find_one({"id": task_data.asset_id})
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Create task
    task = {
        "id": str(uuid.uuid4()),
        "created_by": current_user["id"],
        "asset_name": asset.get("name"),
        **task_data.dict(),
        "completion_date": None,
        "actual_cost": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.maintenance_tasks.insert_one(task)
    
    logger.info(f"Maintenance task created: {task['id']} for asset {task_data.asset_id}")
    
    # Send notification to assigned technician
    if task_data.assigned_to:
        try:
            await create_in_app_notification(
                user_id=task_data.assigned_to,
                title="New Maintenance Task",
                message=f"You've been assigned: {task_data.task_title}",
                type="info",
                link=f"/assets/maintenance/{task['id']}"
            )
        except Exception as e:
            logger.error(f"Error sending task notification: {str(e)}")
    
    return serialize_doc(task)


@router.get("/maintenance", response_model=List[Dict[str, Any]])
async def get_maintenance_tasks(
    asset_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get maintenance tasks with filtering."""
    db = get_database()
    
    filters = {}
    
    # Role-based filtering
    if current_user.get("role") == "technician":
        # Technicians see only their assigned tasks
        filters["assigned_to"] = current_user["id"]
    elif current_user.get("role") not in ["estate_manager", "admin"]:
        # Property owners see tasks for their assets
        filters["created_by"] = current_user["id"]
    
    if asset_id:
        filters["asset_id"] = asset_id
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority
    if assigned_to:
        filters["assigned_to"] = assigned_to
    
    tasks = await db.maintenance_tasks.find(filters).sort("scheduled_date", 1).skip(skip).limit(limit).to_list(limit)
    
    return [serialize_doc(task) for task in tasks]


@router.get("/maintenance/{task_id}", response_model=Dict[str, Any])
async def get_maintenance_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get maintenance task details."""
    db = get_database()
    
    task = await db.maintenance_tasks.find_one({"id": task_id})
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance task not found"
        )
    
    # Check authorization
    allowed_roles = ["estate_manager", "admin"]
    is_creator = task.get("created_by") == current_user["id"]
    is_assigned = task.get("assigned_to") == current_user["id"]
    has_role = current_user.get("role") in allowed_roles
    
    if not (is_creator or is_assigned or has_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this task"
        )
    
    return serialize_doc(task)


@router.put("/maintenance/{task_id}/status")
async def update_task_status(
    task_id: str,
    status_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Update maintenance task status.
    
    Technicians can update status to 'In Progress' or 'Completed'.
    Estate managers can approve or reject completion.
    
    Args:
        task_id: Task ID
        status_data: New status and optional completion details
        current_user: Authenticated user
        
    Returns:
        Updated task
    """
    db = get_database()
    
    task = await db.maintenance_tasks.find_one({"id": task_id})
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    new_status = status_data.get("status")
    
    # Authorization check
    is_assigned = task.get("assigned_to") == current_user["id"]
    is_manager = current_user.get("role") in ["estate_manager", "admin"]
    
    if not (is_assigned or is_manager):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    # Update task
    update_data = {
        "status": new_status,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if new_status == "Completed":
        update_data["completion_date"] = datetime.now(timezone.utc).isoformat()
        update_data["actual_cost"] = status_data.get("actual_cost")
    
    await db.maintenance_tasks.update_one(
        {"id": task_id},
        {"$set": update_data}
    )
    
    logger.info(f"Task {task_id} status updated to {new_status} by {current_user['email']}")
    
    # Send notification when completed
    if new_status == "Completed" and task.get("created_by"):
        try:
            await create_in_app_notification(
                user_id=task["created_by"],
                title="Task Completed",
                message=f"Maintenance task '{task['task_title']}' has been completed",
                type="success",
                link=f"/assets/maintenance/{task_id}"
            )
        except Exception as e:
            logger.error(f"Error sending completion notification: {str(e)}")
    
    # Get updated task
    updated_task = await db.maintenance_tasks.find_one({"id": task_id})
    
    return serialize_doc(updated_task)


# ==================== EXPENSES ====================

@router.post("/expenses", response_model=Dict[str, Any])
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Log an expense for an asset.
    
    Estate managers and admins can log expenses.
    Expenses above threshold require owner approval.
    
    Args:
        expense_data: Expense details
        current_user: Authenticated user
        
    Returns:
        Created expense with ID
    """
    db = get_database()
    
    # Check authorization
    allowed_roles = ["estate_manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only estate managers and admins can log expenses"
        )
    
    # Verify asset exists
    asset = await db.assets.find_one({"id": expense_data.asset_id})
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Determine approval status
    APPROVAL_THRESHOLD = 500000  # XAF
    requires_approval = expense_data.amount > APPROVAL_THRESHOLD
    
    # Create expense
    expense = {
        "id": str(uuid.uuid4()),
        "logged_by": current_user["id"],
        "asset_name": asset.get("name"),
        **expense_data.dict(),
        "approval_status": "pending" if requires_approval else "approved",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.expenses.insert_one(expense)
    
    logger.info(f"Expense created: {expense['id']} for asset {expense_data.asset_id}")
    
    # Send approval request if needed
    if requires_approval and asset.get("owner_id"):
        try:
            await create_in_app_notification(
                user_id=asset["owner_id"],
                title="Expense Approval Required",
                message=f"Expense of {expense_data.amount:,.0f} XAF for {asset.get('name')} requires your approval",
                type="warning",
                link=f"/assets/expenses/{expense['id']}"
            )
        except Exception as e:
            logger.error(f"Error sending approval notification: {str(e)}")
    
    return serialize_doc(expense)


@router.get("/expenses", response_model=List[Dict[str, Any]])
async def get_expenses(
    asset_id: Optional[str] = None,
    expense_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get expenses with filtering."""
    db = get_database()
    
    filters = {}
    
    if asset_id:
        filters["asset_id"] = asset_id
    if expense_type:
        filters["expense_type"] = expense_type
    
    expenses = await db.expenses.find(filters).sort("date", -1).skip(skip).limit(limit).to_list(limit)
    
    return [serialize_doc(expense) for expense in expenses]


# ==================== DASHBOARD STATS ====================

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get asset management dashboard statistics.
    
    Returns:
        Dashboard metrics and summaries
    """
    db = get_database()
    
    # Build filters based on role
    asset_filters = {}
    if current_user.get("role") not in ["estate_manager", "admin"]:
        asset_filters["$or"] = [
            {"owner_id": current_user["id"]},
            {"assigned_to": current_user["id"]}
        ]
    
    # Get counts
    total_assets = await db.assets.count_documents(asset_filters)
    active_tasks = await db.maintenance_tasks.count_documents({
        "status": {"$ne": "Completed"}
    })
    
    # Upcoming maintenance (next 7 days)
    seven_days_from_now = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    upcoming_maintenance = await db.assets.count_documents({
        **asset_filters,
        "next_maintenance_date": {
            "$lte": seven_days_from_now,
            "$gte": datetime.now(timezone.utc).isoformat()
        }
    })
    
    # Total expenses
    expenses_pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    expense_result = await db.expenses.aggregate(expenses_pipeline).to_list(1)
    total_expenses = expense_result[0]["total"] if expense_result else 0
    
    # Assets by category
    category_pipeline = [
        {"$match": asset_filters},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]
    categories = await db.assets.aggregate(category_pipeline).to_list(10)
    
    return {
        "total_assets": total_assets,
        "active_maintenance_tasks": active_tasks,
        "upcoming_maintenance": upcoming_maintenance,
        "total_expenses": total_expenses,
        "assets_by_category": [{"category": c["_id"], "count": c["count"]} for c in categories]
    }


# ==================== EXPENSE APPROVAL ====================

@router.put("/expenses/{expense_id}/approve")
async def approve_expense(
    expense_id: str,
    approval_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Approve or reject an expense.
    
    Only property owners and admins can approve expenses.
    
    Args:
        expense_id: Expense ID
        approval_data: {"approved": true/false, "notes": "optional"}
        current_user: Authenticated user
        
    Returns:
        Updated expense
    """
    db = get_database()
    
    expense = await db.expenses.find_one({"id": expense_id})
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Get asset to check ownership
    asset = await db.assets.find_one({"id": expense["asset_id"]})
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated asset not found"
        )
    
    # Check authorization
    is_owner = asset.get("owner_id") == current_user["id"]
    is_admin = current_user.get("role") == "admin"
    
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only asset owners and admins can approve expenses"
        )
    
    # Update expense
    approved = approval_data.get("approved", False)
    new_status = "approved" if approved else "rejected"
    
    update_data = {
        "approval_status": new_status,
        "approved_by": current_user["id"],
        "approval_date": datetime.now(timezone.utc).isoformat()
    }
    
    if approval_data.get("notes"):
        update_data["approval_notes"] = approval_data["notes"]
    
    await db.expenses.update_one(
        {"id": expense_id},
        {"$set": update_data}
    )
    
    logger.info(f"Expense {expense_id} {new_status} by {current_user['email']}")
    
    # Send notification to the person who logged the expense
    if expense.get("logged_by"):
        try:
            await create_in_app_notification(
                user_id=expense["logged_by"],
                title=f"Expense {new_status.title()}",
                message=f"Your expense of {expense['amount']:,.0f} XAF has been {new_status}",
                type="success" if approved else "error",
                link=f"/assets/expenses/{expense_id}"
            )
        except Exception as e:
            logger.error(f"Error sending approval notification: {str(e)}")
    
    # Get updated expense
    updated_expense = await db.expenses.find_one({"id": expense_id})
    
    return serialize_doc(updated_expense)



# ==================== INVENTORY MANAGEMENT ====================

@router.post("/inventory", response_model=Dict[str, Any])
async def create_inventory_item(
    item_data: InventoryItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new inventory item.
    
    Only estate managers and admins can create inventory items.
    
    Args:
        item_data: Inventory item details
        current_user: Authenticated user
        
    Returns:
        Created inventory item
    """
    db = get_database()
    
    # Check authorization
    allowed_roles = ["estate_manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only estate managers and admins can create inventory items"
        )
    
    # Create inventory item
    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        "name": item_data.name,
        "category": item_data.category,
        "property_id": item_data.property_id,
        "quantity": item_data.quantity,
        "unit": item_data.unit,
        "reorder_level": item_data.reorder_level,
        "reorder_quantity": item_data.reorder_quantity,
        "unit_cost": item_data.unit_cost,
        "supplier_name": item_data.supplier_name,
        "supplier_contact": item_data.supplier_contact,
        "location": item_data.location,
        "notes": item_data.notes,
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.inventory.insert_one(item)
    
    logger.info(f"Inventory item created: {item_id} by {current_user['email']}")
    
    # Check if below reorder level and send alert
    if item_data.quantity <= item_data.reorder_level:
        try:
            await create_in_app_notification(
                user_id=current_user["id"],
                title="Low Stock Alert",
                message=f"{item_data.name} is at or below reorder level ({item_data.quantity} {item_data.unit})",
                type="warning",
                link=f"/assets/inventory/{item_id}"
            )
        except Exception as e:
            logger.error(f"Error sending low stock notification: {str(e)}")
    
    return serialize_doc(item)


@router.get("/inventory", response_model=List[Dict[str, Any]])
async def list_inventory_items(
    category: Optional[str] = None,
    property_id: Optional[str] = None,
    low_stock: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    List all inventory items with optional filters.
    
    Args:
        category: Filter by category
        property_id: Filter by property
        low_stock: Show only low stock items
        current_user: Authenticated user
        
    Returns:
        List of inventory items
    """
    db = get_database()
    
    # Build filter
    filter_query = {}
    
    if category:
        filter_query["category"] = category
    
    if property_id:
        filter_query["property_id"] = property_id
    
    # Get items
    items = await db.inventory.find(filter_query).to_list(None)
    
    # Filter low stock if requested
    if low_stock:
        items = [item for item in items if item.get("quantity", 0) <= item.get("reorder_level", 0)]
    
    logger.info(f"Retrieved {len(items)} inventory items")
    
    return [serialize_doc(item) for item in items]


@router.get("/inventory/{item_id}", response_model=Dict[str, Any])
async def get_inventory_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific inventory item by ID.
    
    Args:
        item_id: Inventory item ID
        current_user: Authenticated user
        
    Returns:
        Inventory item details
    """
    db = get_database()
    
    item = await db.inventory.find_one({"id": item_id})
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    return serialize_doc(item)


@router.put("/inventory/{item_id}", response_model=Dict[str, Any])
async def update_inventory_item(
    item_id: str,
    item_data: InventoryItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an inventory item.
    
    Only estate managers and admins can update inventory items.
    
    Args:
        item_id: Inventory item ID
        item_data: Updated inventory item data
        current_user: Authenticated user
        
    Returns:
        Updated inventory item
    """
    db = get_database()
    
    # Check authorization
    allowed_roles = ["estate_manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only estate managers and admins can update inventory items"
        )
    
    item = await db.inventory.find_one({"id": item_id})
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    # Update fields
    update_data = {k: v for k, v in item_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.inventory.update_one(
        {"id": item_id},
        {"$set": update_data}
    )
    
    # Get updated item
    updated_item = await db.inventory.find_one({"id": item_id})
    
    logger.info(f"Inventory item updated: {item_id} by {current_user['email']}")
    
    # Check if now below reorder level
    if updated_item.get("quantity", 0) <= updated_item.get("reorder_level", 0):
        try:
            await create_in_app_notification(
                user_id=current_user["id"],
                title="Low Stock Alert",
                message=f"{updated_item['name']} is at or below reorder level ({updated_item['quantity']} {updated_item['unit']})",
                type="warning",
                link=f"/assets/inventory/{item_id}"
            )
        except Exception as e:
            logger.error(f"Error sending low stock notification: {str(e)}")
    
    return serialize_doc(updated_item)


@router.delete("/inventory/{item_id}")
async def delete_inventory_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an inventory item.
    
    Only admins can delete inventory items.
    
    Args:
        item_id: Inventory item ID
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    db = get_database()
    
    # Check authorization
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete inventory items"
        )
    
    item = await db.inventory.find_one({"id": item_id})
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    await db.inventory.delete_one({"id": item_id})
    
    logger.info(f"Inventory item deleted: {item_id} by {current_user['email']}")
    
    return {"message": "Inventory item deleted successfully"}


@router.post("/inventory/{item_id}/adjust-stock")
async def adjust_inventory_stock(
    item_id: str,
    adjustment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Adjust inventory stock quantity (add or subtract).
    
    Args:
        item_id: Inventory item ID
        adjustment_data: {"quantity": int, "reason": str, "type": "add" or "subtract"}
        current_user: Authenticated user
        
    Returns:
        Updated inventory item
    """
    db = get_database()
    
    # Check authorization
    allowed_roles = ["estate_manager", "technician", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to adjust stock"
        )
    
    item = await db.inventory.find_one({"id": item_id})
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    quantity = adjustment_data.get("quantity", 0)
    adjustment_type = adjustment_data.get("type", "add")
    reason = adjustment_data.get("reason", "Manual adjustment")
    
    # Calculate new quantity
    current_quantity = item.get("quantity", 0)
    if adjustment_type == "subtract":
        new_quantity = max(0, current_quantity - quantity)
    else:
        new_quantity = current_quantity + quantity
    
    # Update quantity
    await db.inventory.update_one(
        {"id": item_id},
        {
            "$set": {
                "quantity": new_quantity,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log the adjustment
    adjustment_log = {
        "id": str(uuid.uuid4()),
        "item_id": item_id,
        "item_name": item["name"],
        "type": adjustment_type,
        "quantity": quantity,
        "previous_quantity": current_quantity,
        "new_quantity": new_quantity,
        "reason": reason,
        "adjusted_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.inventory_adjustments.insert_one(adjustment_log)
    
    logger.info(f"Inventory adjusted: {item_id} ({adjustment_type} {quantity}) by {current_user['email']}")
    
    # Check if below reorder level
    if new_quantity <= item.get("reorder_level", 0):
        try:
            await create_in_app_notification(
                user_id=current_user["id"],
                title="Low Stock Alert",
                message=f"{item['name']} is at or below reorder level ({new_quantity} {item['unit']})",
                type="warning",
                link=f"/assets/inventory/{item_id}"
            )
        except Exception as e:
            logger.error(f"Error sending low stock notification: {str(e)}")
    
    # Get updated item
    updated_item = await db.inventory.find_one({"id": item_id})
    
    return serialize_doc(updated_item)


# ==================== AUTOMATION TRIGGER ====================

@router.post("/automation/run")
async def trigger_automation(
    current_user: dict = Depends(get_current_user)
):
    """
    Manually trigger automation tasks.
    
    Only admins and estate managers can trigger automations.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Automation results
    """
    # Check authorization
    allowed_roles = ["estate_manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only estate managers and admins can trigger automations"
        )
    
    try:
        from utils.automation import run_daily_automations
        
        logger.info(f"Manual automation triggered by {current_user['email']}")
        results = await run_daily_automations()
        
        return {
            "message": "Automation tasks completed successfully",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error running automations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run automations: {str(e)}"
        )
