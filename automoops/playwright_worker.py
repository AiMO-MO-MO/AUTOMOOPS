"""
Playwright must run in the main thread (greenlet restriction).
Flask runs in a background thread and submits tasks here via a queue.
The main thread processes tasks one at a time and returns results.
"""
import queue

_task_queue = queue.Queue()
_running = True


def submit_task(fn, *args, **kwargs):
    """Called from Flask thread. Blocks until the main thread finishes the task."""
    result_queue = queue.Queue()
    _task_queue.put((fn, args, kwargs, result_queue))
    result = result_queue.get()
    if isinstance(result, Exception):
        raise result
    return result


def run_worker():
    """Runs in the main thread. Processes Playwright tasks indefinitely."""
    while _running:
        try:
            fn, args, kwargs, result_queue = _task_queue.get(timeout=0.1)
            try:
                result_queue.put(fn(*args, **kwargs))
            except Exception as e:
                result_queue.put(e)
        except queue.Empty:
            pass


def stop_worker():
    global _running
    _running = False
