"""
Notification Utilities
=======================
Email and in-app notification system for Homeland Security module.

Handles:
- Email notifications via SendGrid
- In-app notification creation
- Notification templates
"""

import logging
import os
from datetime import datetime, timezone
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from database import get_database

logger = logging.getLogger(__name__)

# SendGrid configuration
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@habitere.com")
SENDGRID_FROM_NAME = os.environ.get("SENDGRID_FROM_NAME", "Homeland Security - Habitere")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")


async def create_in_app_notification(user_id: str, title: str, message: str, type: str = "info", link: str = None):
    """
    Create an in-app notification for a user.
    
    Args:
        user_id: User ID to notify
        title: Notification title
        message: Notification message
        type: Notification type (info, success, warning, error)
        link: Optional link for the notification
    """
    db = get_database()
    
    notification = {
        "id": str(__import__('uuid').uuid4()),
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": type,
        "link": link,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.notifications.insert_one(notification)
    logger.info(f"In-app notification created for user {user_id}: {title}")
    
    return notification


async def send_booking_confirmation_email(booking: dict, user_email: str, user_name: str):
    """Send email confirmation for a new booking."""
    if not SENDGRID_API_KEY:
        logger.warning("SendGrid API key not configured - skipping email")
        return False
    
    message = Mail(
        from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
        to_emails=user_email,
        subject='Security Booking Confirmation - Homeland Security',
        html_content=f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🛡️ Booking Confirmed!</h1>
            </div>
            
            <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                    Hello {user_name},
                </p>
                
                <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                    Your security service booking has been submitted successfully!
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #10B981;">
                    <h3 style="margin-top: 0; color: #10B981;">Booking Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #6B7280;">Service:</td>
                            <td style="padding: 8px 0; font-weight: bold;">{booking.get('service_title', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #6B7280;">Start Date:</td>
                            <td style="padding: 8px 0; font-weight: bold;">{booking.get('start_date', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #6B7280;">Duration:</td>
                            <td style="padding: 8px 0; font-weight: bold;">{booking.get('duration', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #6B7280;">Location:</td>
                            <td style="padding: 8px 0; font-weight: bold;">{booking.get('location', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #6B7280;">Guards:</td>
                            <td style="padding: 8px 0; font-weight: bold;">{booking.get('num_guards', 1)}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #6B7280;">Status:</td>
                            <td style="padding: 8px 0;"><span style="background: #FEF3C7; color: #92400E; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 12px;">PENDING</span></td>
                        </tr>
                    </table>
                </div>
                
                <p style="font-size: 14px; color: #6B7280; margin-bottom: 20px;">
                    The security provider will review your booking and contact you shortly to confirm the details.
                </p>
                
                <a href="{FRONTEND_URL}/security/bookings" style="display: inline-block; background: #10B981; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-bottom: 20px;">
                    View My Bookings
                </a>
                
                <p style="font-size: 12px; color: #9CA3AF; margin-top: 30px; padding-top: 20px; border-top: 1px solid #E5E7EB;">
                    Questions? Contact us at support@habitere.com<br>
                    Homeland Security by Habitere - Protecting What Matters Most
                </p>
            </div>
        </div>
        '''
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Booking confirmation email sent to {user_email}, status: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Error sending booking confirmation email: {str(e)}")
        return False


async def send_application_status_email(application: dict, user_email: str, status: str):
    """Send email notification about guard application status."""
    if not SENDGRID_API_KEY:
        logger.warning("SendGrid API key not configured - skipping email")
        return False
    
    if status == "approved":
        subject = "Congratulations! Your Guard Application is Approved"
        status_color = "#10B981"
        status_bg = "#D1FAE5"
        message_text = f'''
            <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                Congratulations! Your application to become a security guard with Homeland Security has been approved.
            </p>
            <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                You can now start accepting security assignments through our platform.
            </p>
        '''
        cta_text = "View My Guard Profile"
        cta_link = f"{FRONTEND_URL}/dashboard"
    else:
        subject = "Application Status Update - Homeland Security"
        status_color = "#EF4444"
        status_bg = "#FEE2E2"
        message_text = f'''
            <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                Thank you for your interest in joining Homeland Security. After careful review, we are unable to approve your application at this time.
            </p>
            <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                You may reapply in the future once you meet our requirements.
            </p>
        '''
        cta_text = "Browse Security Services"
        cta_link = f"{FRONTEND_URL}/security"
    
    message = Mail(
        from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
        to_emails=user_email,
        subject=subject,
        html_content=f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: {status_color}; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Application Update</h1>
            </div>
            
            <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px;">
                <div style="background: {status_bg}; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                    <p style="color: {status_color}; font-weight: bold; font-size: 18px; margin: 0;">
                        Application {status.upper()}
                    </p>
                </div>
                
                <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                    Hello {application.get('full_name', 'Applicant')},
                </p>
                
                {message_text}
                
                <a href="{cta_link}" style="display: inline-block; background: {status_color}; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0;">
                    {cta_text}
                </a>
                
                <p style="font-size: 12px; color: #9CA3AF; margin-top: 30px; padding-top: 20px; border-top: 1px solid #E5E7EB;">
                    Homeland Security by Habitere<br>
                    For questions, contact us at support@habitere.com
                </p>
            </div>
        </div>
        '''
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Application status email sent to {user_email}, status: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Error sending application status email: {str(e)}")
        return False


async def send_booking_confirmed_email(booking: dict, user_email: str, user_name: str):
    """Send email when provider confirms a booking."""
    if not SENDGRID_API_KEY:
        logger.warning("SendGrid API key not configured - skipping email")
        return False
    
    message = Mail(
        from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
        to_emails=user_email,
        subject='Booking Confirmed by Provider - Homeland Security',
        html_content=f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">✅ Booking Confirmed!</h1>
            </div>
            
            <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                    Great news, {user_name}!
                </p>
                
                <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                    Your security service booking for <strong>{booking.get('service_title')}</strong> has been confirmed by the provider.
                </p>
                
                <div style="background: #D1FAE5; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10B981;">
                    <p style="color: #065F46; font-weight: bold; margin: 0;">
                        📅 Start Date: {booking.get('start_date')}<br>
                        📍 Location: {booking.get('location')}<br>
                        🛡️ Guards: {booking.get('num_guards')}
                    </p>
                </div>
                
                <p style="font-size: 14px; color: #6B7280; margin-bottom: 20px;">
                    The provider will contact you shortly with final details.
                </p>
                
                <a href="{FRONTEND_URL}/security/bookings" style="display: inline-block; background: #10B981; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    View Booking Details
                </a>
                
                <p style="font-size: 12px; color: #9CA3AF; margin-top: 30px; padding-top: 20px; border-top: 1px solid #E5E7EB;">
                    Homeland Security by Habitere - Your Safety is Our Priority
                </p>
            </div>
        </div>
        '''
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Booking confirmed email sent to {user_email}, status: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Error sending booking confirmed email: {str(e)}")
        return False
