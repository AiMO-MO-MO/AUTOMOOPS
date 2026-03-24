# AUTOMOOPS

A first attempt at automating order processing through [Playwright](https://playwright.dev/python/).

## What It Does

AUTOMOOPS uses Playwright to drive a persistent Chromium browser session, allowing a user to navigate to an order in the Moops web interface and extract the order data with a single keypress. It then routes the order through the appropriate automated workflow.

The flow:
1. Launch a persistent browser (preserves login session)
2. User navigates to an order page in Moops
3. Press Enter — AUTOMOOPS extracts the order data from the page
4. Confirm to run the automated workflow for that order
5. Repeat for the next order

## Project Structure

```
AUTOMOOPS/
├── run.py                  # Entry point
├── requirements.txt
├── chrome_profile/         # Persistent browser profile (preserves login)
└── automoops/
    ├── config.py
    ├── extraction/         # Page scraping logic
    ├── routing/            # Order routing logic
    └── workflows/          # Automated workflow steps
```

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

```bash
python run.py
```

Then navigate to an order in the browser window that opens and press Enter to process it.

## Notes

This was the initial proof-of-concept for browser automation against Moops. The approach uses a persistent Chrome profile so credentials are preserved between runs.
