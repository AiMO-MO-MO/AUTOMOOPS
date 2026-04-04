from automoops.workflows.itf import run_itf

# Add new workflows here: "display name" -> function
WORKFLOWS = {
    "1": ("ITF Form", run_itf),
}


def route(order, page):
    print("\nAvailable workflows:")
    for key, (name, _) in WORKFLOWS.items():
        print(f"  {key}. {name}")

    choice = input("\nSelect workflow (or Enter to skip): ").strip()

    if choice not in WORKFLOWS:
        print("Skipped.\n")
        return

    name, fn = WORKFLOWS[choice]
    print(f"\n[Running] {name}\n")
    fn(page, order)
