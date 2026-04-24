import os
from typing import Dict, Any

INTERCOM_URL = "https://app.intercom.com/a/inbox/tftcemdb/inbox/new-conversation"
EMAIL_SUBJECT = "Action Required - Laundroworks Payment Processing - Fortis"
FEES_IMAGE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "Fortis Fees.png")


def _build_body(customer_name: str) -> str:
    return (
        f"Hi {customer_name},\n\n"
        "Your system will arrive with a Fortis payment terminal, enabling you to accept "
        "credit, debit, and EBT transactions.\n\n"
        "To keep everything on track and avoid any delays in approval, please complete the "
        "Fortis Merchant Account Application and ensure all information is entered accurately.\n\n"
        "A few quick notes while completing the application:\n"
        "If you do not plan to accept EBT, enter 0000000 in the EBT field\n"
        "If you're unsure of your average transaction value, you may enter $15\n"
        "Monthly fees begin upon account creation and are outlined at the end of the application\n\n"
        "If you have any questions along the way, our team is here to help:\n"
        "Onboarding: mark@trycents.com\n"
        "Order Support: orders@laundroworks.com\n"
        "Account or Cents Questions: matt.duncan@trycents.com\n"
        "Technical Support: support@laundroworks.com"
    )


def run_intercom(page, order: Dict[str, Any]) -> None:
    print("\n[Workflow] Intercom Email Draft (New Tab)")

    email = order.get("email", "")
    customer_name = order.get("customer_name", "")

    context = page.context
    ic_page = context.new_page()
    print("[Intercom] Navigating...")
    ic_page.goto(INTERCOM_URL, wait_until="domcontentloaded")
    ic_page.wait_for_selector('input.form__input', timeout=10000)
    print("[Intercom] Compose opened")

    # Clear any leftover draft content before filling
    # Remove existing recipient chips by pressing Backspace repeatedly
    ic_page.locator('.data-recipient-selector').click()
    for _ in range(10):
        ic_page.keyboard.press("Backspace")

    # Clear Subject
    ic_page.get_by_role("textbox", name="Subject").click(click_count=3)
    ic_page.keyboard.press("Backspace")

    # Clear body
    body_el = ic_page.locator('div[contenteditable="true"][role="textbox"]').first
    body_el.click()
    ic_page.keyboard.press("Control+a")
    ic_page.keyboard.press("Delete")

    # Remove any existing attachments
    try:
        for btn in ic_page.locator('[class*="attachment"] button').all():
            btn.click()
    except Exception:
        pass

    # Fill To — type email, click autocomplete if contact exists (no wait to avoid double-add)
    ic_page.locator('.data-recipient-selector').click()
    ic_page.keyboard.type(email)
    try:
        ic_page.locator('[role="option"]').first.click(timeout=3000)
    except Exception:
        ic_page.keyboard.press("Enter")

    # Fill Subject
    ic_page.get_by_role("textbox", name="Subject").fill(EMAIL_SUBJECT)

    # Fill body — ProseMirror contenteditable editor
    body_el = ic_page.locator('div[contenteditable="true"][role="textbox"]').first
    body_el.click()
    ic_page.keyboard.press("Control+a")
    ic_page.keyboard.press("Delete")
    ic_page.keyboard.type(_build_body(customer_name))

    # Attach fee details image if file exists
    if os.path.exists(FEES_IMAGE):
        try:
            with ic_page.expect_file_chooser() as fc_info:
                ic_page.keyboard.press("Control+Shift+A")
            fc_info.value.set_files(FEES_IMAGE)
            print("[Intercom] Fee details image attached.")
        except Exception as e:
            print(f"[Intercom] Could not attach image: {e}")
    else:
        print(f"[Intercom] Fee image not found at {FEES_IMAGE} — skipping attachment.")

    print("[Intercom] Draft ready — review and send manually.")
