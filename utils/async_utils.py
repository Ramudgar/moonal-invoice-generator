import threading
import tkinter as tk

def run_async(widget, target, on_success=None, on_error=None, *args, **kwargs):
    """
    Run `target(*args, **kwargs)` in a separate thread.
    On completion, schedule `on_success(result)` or `on_error(exception)`
    to run on the main thread using `widget.after`.
    
    :param widget: A Tkinter widget (e.g., self, root) to schedule the callback.
    :param target: The function to run in the background thread.
    :param on_success: Callback function receiving the result on success.
    :param on_error: Callback function receiving the exception on error.
    """
    def thread_target():
        try:
            result = target(*args, **kwargs)
            if on_success:
                widget.after(0, lambda: on_success(result))
        except Exception as e:
            if on_error:
                widget.after(0, lambda: on_error(e))
    
    threading.Thread(target=thread_target, daemon=True).start()
