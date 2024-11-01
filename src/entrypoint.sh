#!/bin/bash

# Set up cron schedule using the CRON_SCHEDULE environment variable
echo "Setting up cron job with schedule: $CRON_SCHEDULE"
echo "$CRON_SCHEDULE /app/run.sh >> /proc/1/fd/1 2>&1" > /etc/cron.d/mitos

# Apply the cron job
crontab /etc/cron.d/mitos

# Start cron in the foreground
cron -f