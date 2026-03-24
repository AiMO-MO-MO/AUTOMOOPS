from typing import Dict, Any, List
from automoops.config import SELECTORS
from automoops.extraction.parse_mitech_notes import parse_internal_mitech_notes


def _parse_shipping_to_block(text: str) -> Dict[str, Any]:
    lines: List[str] = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]

    out: Dict[str, Any] = {
        "shipping_location": "",
        "shipping_street": "",
        "shipping_city": "",
        "shipping_state": "",
        "shipping_zip": "",
        "shipping_country": "",
        "shipping_contact": "",
        "shipping_first_name": "",
        "shipping_last_name": "",
        "shipping_phone": "",
        "shipping_to_raw": text or "",
    }

    if not lines:
        return out

    if len(lines) >= 1:
        out["shipping_location"] = lines[0]
    if len(lines) >= 2:
        out["shipping_street"] = lines[1]

    if len(lines) >= 3:
        parts = [p.strip() for p in lines[2].split(",") if p.strip()]
        if len(parts) >= 1:
            out["shipping_city"] = parts[0]
        if len(parts) >= 2:
            out["shipping_state"] = parts[1]
        if len(parts) >= 3:
            out["shipping_zip"] = parts[2]
        if len(parts) >= 4:
            out["shipping_country"] = parts[3]

    if len(lines) >= 4 and lines[3].upper().startswith("ATTN:"):
        rest = lines[3].split(":", 1)[1].strip()

        name = rest
        phone = ""
        if "," in rest:
            name, phone = rest.split(",", 1)
            name = name.strip()
            phone = phone.strip()

        out["shipping_contact"] = name
        out["shipping_phone"] = phone

        name_parts = name.split()
        if len(name_parts) >= 1:
            out["shipping_first_name"] = name_parts[0]
        if len(name_parts) >= 2:
            out["shipping_last_name"] = " ".join(name_parts[1:])

    return out


def extract_order(page) -> Dict[str, Any]:
    # Internal Mitech Notes
    notes_raw = page.locator(SELECTORS["internal_mitech_notes"]).input_value()
    parsed_notes = parse_internal_mitech_notes(notes_raw)

    # Shipping To textarea
    shipping_raw = page.locator(SELECTORS["shipping_to"]).input_value()
    shipping = _parse_shipping_to_block(shipping_raw)

    return {
        "so_url": page.url,

        # From notes
        "customer_name": parsed_notes.get("location_name", ""),
        "contact_name": parsed_notes.get("new_contact_name", ""),
        "email": parsed_notes.get("new_contact_email", ""),
        "phone": parsed_notes.get("new_contact_phone", ""),
        "location_address": parsed_notes.get("location_address", ""),
        "raw_notes": notes_raw,

        # Shipping (structured)
        "shipping": shipping,
    }
