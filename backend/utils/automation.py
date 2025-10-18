"""
Asset Management Automation Engine
===================================
Handles automated tasks for asset management:
- Scheduled maintenance reminders
- Expense alerts
- Task assignments
- Low stock inventory alerts

Author: Habitere Development Team
Last Modified: 2025-10-18
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from database import get_database
from utils.notifications import create_in_app_notification, send_email_notification

logger = logging.getLogger(__name__)


async def check_upcoming_maintenance():
    """
    Check for assets with upcoming maintenance and send reminders.
    Runs daily to check for maintenance due in the next 7 days.
    """
    try:
        db = get_database()
        
        # Get current date and 7 days from now
        now = datetime.now(timezone.utc).isoformat()
        seven_days_from_now = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        
        # Find assets with maintenance due in next 7 days
        assets_due = await db.assets.find({
            "next_maintenance_date": {
                "$gte": now,
                "$lte": seven_days_from_now
            },
            "status": {"$ne": "Decommissioned"}
        }).to_list(None)
        
        logger.info(f"Found {len(assets_due)} assets with upcoming maintenance")
        
        for asset in assets_due:
            # Notify owner
            if asset.get("owner_id"):
                try:
                    maintenance_date = datetime.fromisoformat(asset["next_maintenance_date"])
                    days_until = (maintenance_date.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).days
                    
                    await create_in_app_notification(
                        user_id=asset["owner_id"],
                        title=f"Maintenance Due: {asset['name']}",
                        message=f"Maintenance is due in {days_until} days for {asset['name']}. Please schedule a maintenance task.",
                        type="warning",
                        link=f"/assets/{asset['id']}"
                    )
                    
                    logger.info(f"Sent maintenance reminder for asset {asset['id']}")
                except Exception as e:
                    logger.error(f"Error sending maintenance reminder: {str(e)}")
            
            # Notify assigned technician if any
            if asset.get("assigned_to"):
                try:
                    await create_in_app_notification(
                        user_id=asset["assigned_to"],
                        title=f"Maintenance Due: {asset['name']}",
                        message=f"Asset {asset['name']} requires maintenance soon.",
                        type="info",
                        link=f"/assets/{asset['id']}"
                    )
                except Exception as e:
                    logger.error(f"Error sending technician notification: {str(e)}")
        
        return len(assets_due)
    except Exception as e:
        logger.error(f"Error in check_upcoming_maintenance: {str(e)}")
        return 0


async def check_overdue_maintenance():
    """
    Check for assets with overdue maintenance and send alerts.
    """
    try:
        db = get_database()
        
        # Get current date
        now = datetime.now(timezone.utc).isoformat()
        
        # Find assets with overdue maintenance
        assets_overdue = await db.assets.find({
            "next_maintenance_date": {"$lt": now},
            "status": "Active"  # Only alert for active assets
        }).to_list(None)
        
        logger.info(f"Found {len(assets_overdue)} assets with overdue maintenance")
        
        for asset in assets_overdue:
            # Auto-update status to "Under Maintenance"
            await db.assets.update_one(
                {"id": asset["id"]},
                {"$set": {"status": "Under Maintenance"}}
            )
            
            # Notify owner
            if asset.get("owner_id"):
                try:
                    await create_in_app_notification(
                        user_id=asset["owner_id"],
                        title=f"Maintenance Overdue: {asset['name']}",
                        message=f"Maintenance for {asset['name']} is overdue. Asset status updated to 'Under Maintenance'.",
                        type="error",
                        link=f"/assets/{asset['id']}"
                    )
                except Exception as e:
                    logger.error(f"Error sending overdue notification: {str(e)}")
        
        return len(assets_overdue)
    except Exception as e:
        logger.error(f"Error in check_overdue_maintenance: {str(e)}")
        return 0


async def check_pending_task_reminders():
    """
    Send reminders for maintenance tasks scheduled for tomorrow.
    """
    try:
        db = get_database()
        
        # Get tomorrow's date range
        tomorrow_start = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()
        tomorrow_end = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        ).isoformat()
        
        # Find tasks scheduled for tomorrow
        tasks_tomorrow = await db.maintenance_tasks.find({
            "scheduled_date": {
                "$gte": tomorrow_start,
                "$lte": tomorrow_end
            },
            "status": {"$in": ["Pending", "In Progress"]}
        }).to_list(None)
        
        logger.info(f"Found {len(tasks_tomorrow)} tasks scheduled for tomorrow")
        
        for task in tasks_tomorrow:
            # Notify assigned technician
            if task.get("assigned_to"):
                try:
                    await create_in_app_notification(
                        user_id=task["assigned_to"],
                        title=f"Task Tomorrow: {task['task_title']}",
                        message=f"Maintenance task '{task['task_title']}' is scheduled for tomorrow.",
                        type="info",
                        link=f"/assets/maintenance/{task['id']}"
                    )
                except Exception as e:
                    logger.error(f"Error sending task reminder: {str(e)}")
            
            # Notify task creator
            if task.get("created_by"):
                try:
                    await create_in_app_notification(
                        user_id=task["created_by"],
                        title=f"Task Scheduled Tomorrow: {task['task_title']}",
                        message=f"Maintenance task '{task['task_title']}' is scheduled for tomorrow.",
                        type="info",
                        link=f"/assets/maintenance/{task['id']}"
                    )
                except Exception as e:
                    logger.error(f"Error sending creator notification: {str(e)}")
        
        return len(tasks_tomorrow)
    except Exception as e:
        logger.error(f"Error in check_pending_task_reminders: {str(e)}")
        return 0


async def check_high_expense_approvals():
    """
    Send reminders for pending high-value expense approvals.
    """
    try:
        db = get_database()
        
        # Find pending expenses that have been waiting for more than 2 days
        two_days_ago = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        
        pending_expenses = await db.expenses.find({
            "approval_status": "pending",
            "created_at": {"$lt": two_days_ago}
        }).to_list(None)
        
        logger.info(f"Found {len(pending_expenses)} pending expense approvals")
        
        for expense in pending_expenses:
            # Get the asset to find the owner
            asset = await db.assets.find_one({"id": expense["asset_id"]})
            
            if asset and asset.get("owner_id"):
                try:
                    await create_in_app_notification(
                        user_id=asset["owner_id"],
                        title="Expense Approval Pending",
                        message=f"Expense of {expense['amount']:,.0f} XAF for {asset.get('name', 'asset')} is awaiting your approval.",
                        type="warning",
                        link=f"/assets/expenses/{expense['id']}"
                    )
                except Exception as e:
                    logger.error(f"Error sending expense reminder: {str(e)}")
        
        return len(pending_expenses)
    except Exception as e:
        logger.error(f"Error in check_high_expense_approvals: {str(e)}")
        return 0


async def run_daily_automations():


async def check_low_stock_inventory():
    """
    Check for inventory items at or below reorder level and send alerts.
    """
    try:
        db = get_database()
        
        # Find all inventory items
        all_items = await db.inventory.find({}).to_list(None)
        
        # Filter items at or below reorder level
        low_stock_items = [
            item for item in all_items 
            if item.get("quantity", 0) <= item.get("reorder_level", 0)
        ]
        
        logger.info(f"Found {len(low_stock_items)} low stock items")
        
        # Get estate managers to notify
        estate_managers = await db.users.find({"role": "estate_manager"}).to_list(None)
        admins = await db.users.find({"role": "admin"}).to_list(None)
        
        managers_to_notify = estate_managers + admins
        
        for item in low_stock_items:
            for manager in managers_to_notify:
                try:
                    reorder_needed = item.get("reorder_quantity", 0)
                    current_qty = item.get("quantity", 0)
                    
                    await create_in_app_notification(
                        user_id=manager["id"],
                        title=f"Low Stock Alert: {item['name']}",
                        message=f"Stock level is low ({current_qty} {item['unit']}). Reorder quantity: {reorder_needed} {item['unit']}. Supplier: {item.get('supplier_name', 'N/A')}",
                        type="warning",
                        link=f"/assets/inventory/{item['id']}"
                    )
                except Exception as e:
                    logger.error(f"Error sending low stock notification: {str(e)}")
        
        return len(low_stock_items)
    except Exception as e:
        logger.error(f"Error in check_low_stock_inventory: {str(e)}")
        return 0

    """
    Run all daily automation tasks.
    This should be called by a scheduler (cron job or similar).
    """
    logger.info("Starting daily asset management automations...")
    
    results = {
        "upcoming_maintenance": 0,
        "overdue_maintenance": 0,
        "task_reminders": 0,
        "expense_reminders": 0
    }
    
    try:
        results["upcoming_maintenance"] = await check_upcoming_maintenance()
        results["overdue_maintenance"] = await check_overdue_maintenance()
        results["task_reminders"] = await check_pending_task_reminders()
        results["expense_reminders"] = await check_high_expense_approvals()
        
        logger.info(f"Daily automations completed: {results}")
        return results
    except Exception as e:
        logger.error(f"Error running daily automations: {str(e)}")
        return results


# Background task runner
async def automation_scheduler():
    """
    Background task scheduler that runs automation tasks periodically.
    In production, this should be replaced with a proper task queue (Celery, etc.)
    """
    logger.info("Asset Management Automation Scheduler started")
    
    while True:
        try:
            # Run at midnight every day
            now = datetime.now(timezone.utc)
            next_run = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            wait_seconds = (next_run - now).total_seconds()
            
            logger.info(f"Next automation run in {wait_seconds / 3600:.2f} hours")
            await asyncio.sleep(wait_seconds)
            
            # Run all automations
            await run_daily_automations()
            
        except asyncio.CancelledError:
            logger.info("Automation scheduler cancelled")
            break
        except Exception as e:
            logger.error(f"Error in automation scheduler: {str(e)}")
            # Wait 1 hour before retrying
            await asyncio.sleep(3600)
