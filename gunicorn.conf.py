bind = "0.0.0.0:8000"

workers = 4        # for 2 CPU
threads = 2
worker_class = "gthread"

timeout = 120
keepalive = 5

max_requests = 1000
max_requests_jitter = 100

preload_app = True
