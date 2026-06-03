"""
Gunicorn configuration for Toonify on Render.
Using server hooks to safely start the keep-alive thread AFTER forking,
which avoids the 'threads don't survive fork()' problem.
"""
import os
import time
import threading
import urllib.request

# ── Gunicorn settings ─────────────────────────────────────────────────────────
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = 1
timeout = 120
keepalive = 65
preload_app = True   # Import app once in master, then fork — faster startup


# ── Keep-alive hook (runs in each worker AFTER fork) ─────────────────────────
def post_fork(server, worker):
    """Start the keep-alive ping thread inside the worker process after fork."""
    port = os.environ.get('PORT', '5000')
    url = f"http://localhost:{port}/ping"

    def _keep_alive_loop():
        # Wait 60s before first ping so the worker is fully ready
        time.sleep(60)
        while True:
            try:
                urllib.request.urlopen(url, timeout=10)
                server.log.info("[KEEP-ALIVE] Self-ping OK — service stays warm")
            except Exception as exc:
                server.log.warning(f"[KEEP-ALIVE] Ping failed (non-critical): {exc}")
            time.sleep(600)  # Ping every 10 minutes

    t = threading.Thread(target=_keep_alive_loop, daemon=True, name="keep-alive")
    t.start()
    server.log.info("[KEEP-ALIVE] Background ping thread started in worker")
