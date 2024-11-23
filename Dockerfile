FROM python:3.9-slim

# Install git and cron
RUN apt-get update && apt-get install -y git cron && rm -rf /var/lib/apt/lists/*

# Copy the script and entrypoint
COPY update_repos.py /usr/local/bin/update_repos.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /usr/local/bin/update_repos.py /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
