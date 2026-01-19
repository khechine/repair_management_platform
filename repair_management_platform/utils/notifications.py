import frappe
from frappe import _
from frappe.utils import get_url_to_form

def send_status_notification(doc, method=None):
    """Send email notification when repair order status changes"""

    if not doc.customer:
        return

    # Check if status has changed
    if doc.has_value_changed("status"):
        old_status = doc.get_doc_before_save().status if doc.get_doc_before_save() else None
        new_status = doc.status

        # Get customer email
        customer_doc = frappe.get_doc("Customer", doc.customer)
        if not customer_doc.email_id:
            return

        # Prepare email content based on status
        email_subject = get_email_subject(doc, new_status)
        email_message = get_email_message(doc, old_status, new_status)

        # Send email
        frappe.sendmail(
            recipients=[customer_doc.email_id],
            subject=email_subject,
            message=email_message,
            reference_doctype="Repair Order",
            reference_name=doc.name
        )

def get_email_subject(doc, status):
    """Get email subject based on status"""
    subject_map = {
        "Diagnostic Pending": _("Your Repair Order {0} - Diagnostic in Progress"),
        "Diagnostic Completed": _("Your Repair Order {0} - Diagnostic Complete"),
        "Quoted": _("Your Repair Order {0} - Quote Ready"),
        "Repair in Progress": _("Your Repair Order {0} - Repair Started"),
        "Ready for Collection": _("Your Repair Order {0} - Ready for Pickup!"),
        "Completed": _("Your Repair Order {0} - Completed"),
        "Cancelled": _("Your Repair Order {0} - Cancelled")
    }

    return subject_map.get(status, _("Your Repair Order {0} - Status Update")).format(doc.name)

def get_email_message(doc, old_status, new_status):
    """Get email message content based on status"""

    tracking_url = get_url_to_form("Repair Order", doc.name)
    portal_url = frappe.utils.get_url("/track")

    message_map = {
        "Diagnostic Pending": """
            <p>Dear Customer,</p>
            <p>Your device has been received and our technician will begin diagnostics shortly.</p>
            <p><strong>Order Details:</strong></p>
            <ul>
                <li>Order Number: {order_number}</li>
                <li>Device: {device}</li>
                <li>Technician: {technician}</li>
            </ul>
            <p>We will notify you once the diagnostic is complete.</p>
        """,
        "Diagnostic Completed": """
            <p>Dear Customer,</p>
            <p>The diagnostic for your device has been completed.</p>
            <p><strong>Order Details:</strong></p>
            <ul>
                <li>Order Number: {order_number}</li>
                <li>Device: {device}</li>
            </ul>
            <p>Our team will contact you shortly with the findings and quote.</p>
        """,
        "Quoted": """
            <p>Dear Customer,</p>
            <p>Your repair quote is ready!</p>
            <p><strong>Order Details:</strong></p>
            <ul>
                <li>Order Number: {order_number}</li>
                <li>Device: {device}</li>
                <li>Estimated Amount: {amount}</li>
                <li>Estimated Completion: {estimated_date}</li>
            </ul>
            <p>Please contact us to approve the quote and proceed with the repair.</p>
        """,
        "Repair in Progress": """
            <p>Dear Customer,</p>
            <p>Great news! Your repair has been approved and is now in progress.</p>
            <p><strong>Order Details:</strong></p>
            <ul>
                <li>Order Number: {order_number}</li>
                <li>Device: {device}</li>
                <li>Technician: {technician}</li>
                <li>Estimated Completion: {estimated_date}</li>
            </ul>
            <p>We will keep you updated on the progress.</p>
        """,
        "Ready for Collection": """
            <p>Dear Customer,</p>
            <p><strong>Your device is ready for pickup!</strong></p>
            <p><strong>Order Details:</strong></p>
            <ul>
                <li>Order Number: {order_number}</li>
                <li>Device: {device}</li>
                <li>Total Amount: {amount}</li>
            </ul>
            <p>Please visit our location to collect your device at your earliest convenience.</p>
        """,
        "Completed": """
            <p>Dear Customer,</p>
            <p>Thank you for choosing our service!</p>
            <p><strong>Order Details:</strong></p>
            <ul>
                <li>Order Number: {order_number}</li>
                <li>Device: {device}</li>
            </ul>
            <p>Your repair has been completed. We hope you're satisfied with our service.</p>
            <p>Please consider leaving us feedback about your experience!</p>
        """,
        "Cancelled": """
            <p>Dear Customer,</p>
            <p>Your repair order has been cancelled.</p>
            <p><strong>Order Details:</strong></p>
            <ul>
                <li>Order Number: {order_number}</li>
                <li>Device: {device}</li>
            </ul>
            <p>If you have any questions, please contact us.</p>
        """
    }

    template = message_map.get(new_status, """
        <p>Dear Customer,</p>
        <p>There has been an update to your repair order.</p>
        <p><strong>Order Number:</strong> {order_number}</p>
        <p><strong>New Status:</strong> {status}</p>
    """)

    # Get device name
    device_name = "N/A"
    if doc.device:
        device_doc = frappe.get_doc("Repair Device", doc.device)
        device_name = f"{device_doc.device_name} ({device_doc.model})"

    message = template.format(
        order_number=doc.name,
        device=device_name,
        technician=doc.technician or "To be assigned",
        amount=frappe.utils.fmt_money(doc.total_amount or 0, currency=frappe.defaults.get_defaults().currency),
        estimated_date=frappe.utils.formatdate(doc.estimated_completion_date) if doc.estimated_completion_date else "To be determined",
        status=new_status
    )

    message += f"""
        <p>Track your order status here: <a href="{portal_url}">Customer Portal</a></p>
        <p>Best regards,<br>Repair Management Team</p>
    """

    return message
