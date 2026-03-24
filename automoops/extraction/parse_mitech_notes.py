from typing import Dict, Any, List

# Full US state name -> USPS abbreviation
STATE_ABBREV = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
}


def abbreviate_states(text: str) -> str:
    """
    Replace full US state names inside an address string with USPS abbreviations.
    Example: 'Fairfield, California, 94533' -> 'Fairfield, CA, 94533'
    """
    if not text:
        return ""

    # Lightweight casing attempts (no regex)
    for full, abbr in STATE_ABBREV.items():
        text = text.replace(full.title(), abbr)
        text = text.replace(full.upper(), abbr)
        text = text.replace(full.capitalize(), abbr)

    return text


def parse_internal_mitech_notes(notes: str) -> Dict[str, Any]:
    """
    Takes the raw textarea blob and extracts structured fields.

    Handles:
    - Location Name
    - Location Address (multi-line OR single-line mashed "name + street + city/state/zip")
    - New Contact Name / Email / Phone
    - Normalizes US state names to abbreviations inside the extracted address
    """

    lines = [ln.strip() for ln in (notes or "").splitlines() if ln.strip()]
    lines = [ln for ln in lines if not ln.startswith("---")]

    out: Dict[str, Any] = {}
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("Location Name:"):
            out["location_name"] = line.split(":", 1)[1].strip()

        elif line.startswith("Location Address:"):
            address_lines: List[str] = []

            # ✅ Capture anything after the colon on the SAME line
            inline = line.split(":", 1)[1].strip()
            if inline:
                address_lines.append(inline)

            i += 1

            # Collect subsequent lines until next "Key:"
            while i < len(lines) and ":" not in lines[i]:
                address_lines.append(lines[i])
                i += 1

            # Fix 1: Single-line mashed address (remove everything before first digit)
            if len(address_lines) == 1:
                s = address_lines[0]
                for idx, ch in enumerate(s):
                    if ch.isdigit():
                        address_lines[0] = s[idx:].strip()
                        break

            # Fix 2: Multi-line case where first line is "name + street" mashed
            if len(address_lines) >= 2:
                first = address_lines[0].strip()
                has_number = any(ch.isdigit() for ch in first)
                starts_with_number = first[:1].isdigit()
                if has_number and not starts_with_number:
                    address_lines = address_lines[1:]

            address_text = "\n".join(address_lines).strip()
            address_text = abbreviate_states(address_text)

            out["location_address"] = address_text
            continue

        elif line.startswith("New Contact Name:"):
            out["new_contact_name"] = line.split(":", 1)[1].strip()

        elif line.startswith("New Contact Email:"):
            out["new_contact_email"] = line.split(":", 1)[1].strip()

        elif line.startswith("New Contact Phone:"):
            out["new_contact_phone"] = line.split(":", 1)[1].strip()

        i += 1

    return out
