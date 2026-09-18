import gunicorn

# Tell gunicorn to run Django's ASGI application with the uvicorn worker.
# Gunicorn remains the process manager, providing worker recycling, timeouts,
# and pre-fork memory sharing.
# https://www.uvicorn.org/deployment/#gunicorn
wsgi_app = "apps.guide.asgi:application"

# Replace gunicorn's 'Server' HTTP header to avoid leaking info to attackers
gunicorn.SERVER = ""

# Each worker runs one asyncio event loop. Django adapts the app's
# (synchronous) middleware and views to run in a single thread per worker, so
# concurrent requests scale with the number of worker processes
# (WEB_CONCURRENCY), rather than with threads as in the previous gthread
# setup.
worker_class = "uvicorn_worker.UvicornWorker"

# Restart gunicorn worker processes every 1200-1250 requests. The uvicorn
# worker implements this via uvicorn's limit_max_requests, after which
# gunicorn respawns the worker.
max_requests = 1200
max_requests_jitter = 50

# Log to stdout
accesslog = "-"

# Time out after 25 seconds (notably shorter than Heroku's). Note this is a
# worker liveness check rather than a per-request deadline: the worker's event
# loop keeps heartbeating while its request thread is stuck, so a hung request
# (e.g. an AI provider call) blocks all other requests in that worker until it
# returns, rather than being aborted. Outbound calls should enforce their own
# timeouts, and enough worker processes should be available to absorb hung
# requests.
timeout = 25

# Load app pre-fork to save memory and worker startup time
preload_app = True
