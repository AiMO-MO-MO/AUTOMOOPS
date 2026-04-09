from typing import Dict, Any
from automoops.config import STATE_ABBREVIATIONS

EFS_URL = "https://fcp.efulfillmentservice.com/index.php?fuseaction=order.newOrder&clientID=4612"


def _state_abbr(state: str) -> str:
    s = state.strip()
    if len(s) == 2:
        return s.upper()
    return STATE_ABBREVIATIONS.get(s.lower(), s)


def _fill_products(efs_page, products: Dict[str, Any]) -> None:
    """
    Scans all product rows on the EFS form, builds a map of item_code -> qty input,
    then fills quantities for any codes that match the MOOPS order.
    """
    # Gather all items from MOOPS: cards + other (reader kits / VACs don't appear on EFS)
    moops_items: Dict[str, int] = {}
    for item in products.get("cards", []):
        moops_items[item["code"].upper()] = item["qty"]
    for item in products.get("other", []):
        moops_items[item["code"].upper()] = item["qty"]

    if not moops_items:
        return

    # Single JS call: scan all rows and fill matching qty inputs in one shot
    filled_codes = efs_page.evaluate("""
        (moopsItems) => {
            const filled = [];
            for (const row of document.querySelectorAll('tr')) {
                const tds = row.querySelectorAll('td');
                if (tds.length < 2) continue;
                const code = tds[0].textContent.trim().toUpperCase();
                if (!(code in moopsItems)) continue;
                const input = row.querySelector('input[type="text"]');
                if (input) {
                    input.value = String(moopsItems[code]);
                    filled.push(code);
                }
            }
            return filled;
        }
    """, moops_items)

    for code in filled_codes:
        print(f"[EFS] Filled {code} = {moops_items[code]}")
    print(f"[EFS] Filled {len(filled_codes)}/{len(moops_items)} products.")


def run_efs(page, order: Dict[str, Any]) -> None:
    print("\n[Workflow] EFS New Order (New Tab)")

    shipping = order.get("shipping", {})

    context = page.context
    efs_page = context.new_page()
    print("[EFS] Navigating...")
    efs_page.goto(EFS_URL, wait_until="domcontentloaded")
    print("[EFS] domcontentloaded")
    efs_page.wait_for_selector('input[name="custBillFName"]', timeout=15000)
    print("[EFS] Form ready")

    # Fill all billing fields in one JS call
    state_abbr = _state_abbr(shipping.get("shipping_state", ""))
    efs_page.evaluate("""
        (d) => {
            const f = (name, val) => { const el = document.querySelector('input[name="' + name + '"]'); if (el) el.value = val; };
            f('custEmail',        d.email);
            f('custPhone',        d.phone);
            f('custBillFName',    d.firstName);
            f('custBillLName',    d.lastName);
            f('custBillCompany',  d.company);
            f('custBillAddress1', d.address);
            f('custBillCity',     d.city);
            f('custBillZip',      d.zip);
            const sel = document.querySelector('select[name="custBillState"]');
            if (sel && d.state) sel.value = d.state;
        }
    """, {
        "email":     order.get("email", ""),
        "phone":     shipping.get("shipping_phone", ""),
        "firstName": shipping.get("shipping_first_name", ""),
        "lastName":  shipping.get("shipping_last_name", ""),
        "company":   shipping.get("shipping_location", ""),
        "address":   shipping.get("shipping_street", ""),
        "city":      shipping.get("shipping_city", ""),
        "zip":       shipping.get("shipping_zip", ""),
        "state":     state_abbr,
    })

    print("[EFS] Billing filled")
    # Product quantities
    products = order.get("products", {})
    if products:
        print("[EFS] Filling products...")
        _fill_products(efs_page, products)

    print("[Workflow] EFS form filled.")
