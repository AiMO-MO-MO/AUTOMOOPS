from typing import Dict, Any

EFS_URL = "https://fcp.efulfillmentservice.com/index.php?fuseaction=order.newOrder&clientID=4612"

STATE_ABBREVIATIONS = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}


def _state_abbr(state: str) -> str:
    s = state.strip()
    if len(s) == 2:
        return s.upper()
    return STATE_ABBREVIATIONS.get(s.lower(), s)


def run_efs(page, order: Dict[str, Any]) -> None:
    print("\n[Workflow] EFS New Order (New Tab)")

    shipping = order.get("shipping", {})

    context = page.context
    efs_page = context.new_page()
    efs_page.goto(EFS_URL, wait_until="domcontentloaded")
    efs_page.wait_for_selector('input[name="custBillFName"]', timeout=15000)

    efs_page.locator('input[name="custEmail"]').fill(order.get("email", ""))
    efs_page.locator('input[name="custPhone"]').fill(shipping.get("shipping_phone", ""))
    efs_page.locator('input[name="custBillFName"]').fill(shipping.get("shipping_first_name", ""))
    efs_page.locator('input[name="custBillLName"]').fill(shipping.get("shipping_last_name", ""))
    efs_page.locator('input[name="custBillCompany"]').fill(shipping.get("shipping_location", ""))
    efs_page.locator('input[name="custBillAddress1"]').fill(shipping.get("shipping_street", ""))
    efs_page.locator('input[name="custBillCity"]').fill(shipping.get("shipping_city", ""))
    efs_page.locator('input[name="custBillZip"]').fill(shipping.get("shipping_zip", ""))

    state_abbr = _state_abbr(shipping.get("shipping_state", ""))
    try:
        efs_page.locator('select[name="custBillState"]').select_option(value=state_abbr)
    except Exception:
        pass

    print("[Workflow] EFS form filled.")
