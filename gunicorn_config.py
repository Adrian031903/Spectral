"""Gunicorn configuration.

- Binds to Render/Heroku style $PORT when provided.
- Keeps concurrency modest by default to avoid exhausting DB connections.
"""

import os

# The socket to bind.
# "0.0.0.0" to bind to all interfaces.
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# The number of worker processes for handling requests.
# Render free instances are small; default to 2 unless configured.
workers = int(os.environ.get('WEB_CONCURRENCY', '2'))

# Use the default synchronous worker.
worker_class = 'sync'

# Log level
loglevel = 'info'

# Where to log to
accesslog = '-'  # '-' means log to stdout
errorlog = '-'  # '-' means log to stderr