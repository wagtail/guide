import gunicorn

# Tell gunicorn to run our app
wsgi_app = "apps.guide.wsgi:application"

# Replace gunicorn's 'Server' HTTP header to avoid leaking info to attackers
gunicorn.SERVER = ""

# Serve requests with threads within one worker process, rather than
# dedicating a process to each concurrent request: requests spend most of
# their time waiting on I/O (database, Redis, S3, AI providers), during which
# threads release the GIL and run in parallel. This keeps memory use low
# while still allowing many concurrent requests.
worker_class = "gthread"
threads = 8

# Restart gunicorn worker processes every 1200-1250 requests
max_requests = 1200
max_requests_jitter = 50

# Log to stdout
accesslog = "-"

# Time out after 25 seconds (notably shorter than Heroku's). Note this is a
# worker liveness check rather than a per-request deadline: gthread workers
# keep heartbeating while their request threads run, so a hung request (e.g.
# an AI provider call) occupies one of the threads until it returns, rather
# than being aborted. Outbound calls should enforce their own timeouts.
timeout = 25

# Load app pre-fork to save memory and worker startup time
preload_app = True
