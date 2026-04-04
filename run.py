from playwright.sync_api import sync_playwright
from automoops.extraction.moops_order import extract_order
from automoops.routing.router import route


def main():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="chrome_profile",
            headless=False
        )

        page = context.pages[0] if context.pages else context.new_page()


        print("\nAUTOMOOPS is running.")
        print("Open Moops and navigate to an order page.")
        print("Press Enter to extract each order.")
        print("Type 'q' + Enter to quit.\n")

        while True:
            cmd = input("Ready for next order? (Enter = extract, q = quit): ").strip().lower()

            if cmd == "q":
                print("Exiting AUTOMOOPS...")
                break

            # Extract order data
            order = extract_order(page)

            print("\n✅ EXTRACTED ORDER:\n")
            print(order)

            # Human confirmation before workflow
            confirm = input("\nRun workflow for this order? (y/n): ").strip().lower()
            if confirm != "y":
                print("Skipped workflow.\n")
                continue

            # Route + run workflow
            route(order, page)

            print("\n--- Done. Navigate to the next order. ---\n")

        context.close()


if __name__ == "__main__":
    main()
