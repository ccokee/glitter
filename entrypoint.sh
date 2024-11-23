#!/bin/bash

# Write environment variables to a file so cron can access them
printenv | grep -v "no_proxy" >> /etc/environment

# Set up the cron schedule
CRON_SCHEDULE="${CRON_SCHEDULE:-0 * * * *}"  # Default to every hour if not set

echo "Setting up cron job with schedule: $CRON_SCHEDULE"

# Write out the cron job
echo "$CRON_SCHEDULE /usr/bin/python /usr/local/bin/update_repos.py >> /var/log/cron.log 2>&1" > /etc/cron.d/update_repos_cron

# Give execution rights on the cron job file
chmod 0644 /etc/cron.d/update_repos_cron

# Apply the cron job
crontab /etc/cron.d/update_repos_cron

# Create the log file to be able to run tail
touch /var/log/cron.log

# Start cron and tail the log file
echo "Starting cron..."

cron && tail -f /var/log/cron.log
