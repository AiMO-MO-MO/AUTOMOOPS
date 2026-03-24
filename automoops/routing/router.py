from automoops.workflows.itf import run_itf

def route(order, page):
    print("\nRouting order to ITF workflow...\n")
    run_itf(page, order)
