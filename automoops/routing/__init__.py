from automoops.workflows.itf import run_itf


def route(order, page):
    """
    Minimal router: always runs ITF workflow.
    Later you can add system vs parts logic.
    """
    print("\nRouting order to ITF workflow...\n")
    run_itf(page, order)
