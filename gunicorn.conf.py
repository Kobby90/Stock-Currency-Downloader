# Gunicorn configuration file

# Define the Gunicorn server configuration
bind = '127.0.0.1:8080'  # Bind to all addresses on port 8080
workers = 4  # Number of worker processes
timeout = 30  # Timeout for worker processes in seconds

# Logging configuration
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'  # Log level: debug, info, warning, error, critical
