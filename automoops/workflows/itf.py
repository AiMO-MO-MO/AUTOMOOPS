from typing import Dict, Any

ITF_URL = "https://cents.atlassian.net/servicedesk/customer/portal/1/group/3/create/171"


def run_itf(page, order: Dict[str, Any]) -> None:
    """
    Opens ITF form in a NEW TAB so Moops stays open.
    Fills Jira fields from extracted order dict.
    """

    print("\n[Workflow] ITF Form Entry (New Tab)")

    # ✅ Create a new tab in the same browser context
    context = page.context
    itf_page = context.new_page()

    print("Opening ITF form in new tab...")
    itf_page.goto(ITF_URL)


    # --- Fill core fields ---
    itf_page.get_by_label("Admin Portal Name").fill(order.get("customer_name", ""))
    itf_page.get_by_label("Contact Name").fill(order.get("contact_name", ""))
    itf_page.get_by_label("Contact Email").fill(order.get("email", ""))
    itf_page.get_by_label("Contact Number").fill(order.get("phone", ""))
    itf_page.get_by_label("Address").fill(order.get("location_address", ""))

    # --- Extra fields ---
    # SO URL
    try:
        itf_page.get_by_label("SO url").fill(order.get("so_url", ""))
    except Exception:
        itf_page.get_by_label("SO URL").fill(order.get("so_url", ""))

    # VAC licenses (default 2)
    try:
        itf_page.get_by_label("Number of VAC licences").fill("2")
    except Exception:
        itf_page.get_by_label("Number of VAC licenses").fill("2")

    # Laundry Operation Type dropdown
    try:
        itf_page.get_by_label("Laundry Operation Type").select_option(label="Laundromat")
    except Exception:
        lot = itf_page.get_by_label("Laundry Operation Type")
        lot.click()
        itf_page.get_by_role("option", name="Laundromat", exact=True).click()

    print("[Workflow] ITF form filled — review and submit in the browser tab.")
