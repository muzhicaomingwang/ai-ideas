#!/bin/bash

# Daily Podcast Automated Execution Script
# This script runs at 9:00 AM daily via launchd
# Created: 2026-01-13

# Exit on any error
set -e

# Set working directory
WORK_DIR="/Users/qitmac001395/workspace/QAL/ideas/apps/daily-podcast-ai"
cd "$WORK_DIR"

# Create logs directory if it doesn't exist
mkdir -p "$WORK_DIR/logs"

# Log file for this run
LOG_FILE="$WORK_DIR/logs/daily_run.log"
ERROR_LOG="$WORK_DIR/logs/daily_error.log"

# Get today's date
TODAY=$(date +%Y-%m-%d)
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Log start
echo "[$TIMESTAMP] ========================================" >> "$LOG_FILE"
echo "[$TIMESTAMP] Starting daily podcast generation for $TODAY" >> "$LOG_FILE"

# Load environment variables from .env file if it exists
if [ -f "$WORK_DIR/.env" ]; then
    export $(grep -v '^#' "$WORK_DIR/.env" | xargs)
    echo "[$TIMESTAMP] Loaded environment variables from .env" >> "$LOG_FILE"
fi

# Verify required API keys are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "[$TIMESTAMP] ERROR: OPENAI_API_KEY is not set" >> "$ERROR_LOG"
    exit 1
fi

if [ -z "$ELEVENLABS_API_KEY" ]; then
    echo "[$TIMESTAMP] ERROR: ELEVENLABS_API_KEY is not set" >> "$ERROR_LOG"
    exit 1
fi

# Check RSS.com credentials (optional - publishing will be skipped if not set)
if [ -z "$RSS_COM_API_KEY" ] || [ -z "$RSS_COM_PODCAST_ID" ]; then
    echo "[$TIMESTAMP] ⚠️  WARNING: RSS.com credentials not set - publishing will be skipped" >> "$LOG_FILE"
    echo "[$TIMESTAMP]   Set RSS_COM_API_KEY and RSS_COM_PODCAST_ID in .env to enable publishing" >> "$LOG_FILE"
fi

echo "[$TIMESTAMP] Environment variables verified" >> "$LOG_FILE"

# Check if output for today already exists
OUTPUT_DIR="$WORK_DIR/output/$TODAY/dailyReport"
if [ -d "$OUTPUT_DIR" ] && [ -f "$OUTPUT_DIR/podcast-$TODAY.mp3" ]; then
    echo "[$TIMESTAMP] Podcast for $TODAY already exists, skipping generation" >> "$LOG_FILE"
    exit 0
fi

# Run the podcast generation
echo "[$TIMESTAMP] Executing: python scripts/daily_generate.py --date $TODAY --classic --output output" >> "$LOG_FILE"

if python scripts/daily_generate.py --date "$TODAY" --classic --output output >> "$LOG_FILE" 2>> "$ERROR_LOG"; then
    END_TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$END_TIMESTAMP] ✅ Podcast generation completed successfully for $TODAY" >> "$LOG_FILE"

    # Verify output files exist
    if [ -f "$OUTPUT_DIR/podcast-$TODAY.mp3" ]; then
        FILE_SIZE=$(du -h "$OUTPUT_DIR/podcast-$TODAY.mp3" | cut -f1)
        echo "[$END_TIMESTAMP] Generated podcast size: $FILE_SIZE" >> "$LOG_FILE"
    fi

    if [ -f "$OUTPUT_DIR/cover-$TODAY.png" ]; then
        echo "[$END_TIMESTAMP] Cover image generated successfully" >> "$LOG_FILE"
    fi

    if [ -f "$OUTPUT_DIR/script-$TODAY.md" ]; then
        echo "[$END_TIMESTAMP] Script file generated successfully" >> "$LOG_FILE"
    fi

    # Publish to RSS.com (optional step - failures won't break podcast generation)
    echo "[$END_TIMESTAMP] Publishing to RSS.com..." >> "$LOG_FILE"
    if python scripts/publish_to_rss.py --date "$TODAY" >> "$LOG_FILE" 2>> "$ERROR_LOG"; then
        echo "[$END_TIMESTAMP] ✅ Published to RSS.com successfully" >> "$LOG_FILE"
    else
        echo "[$END_TIMESTAMP] ⚠️  WARNING: RSS.com publishing failed (check $ERROR_LOG)" >> "$LOG_FILE"
        # Note: Using warning instead of exit 1 to not break daily podcast generation
    fi

    echo "[$END_TIMESTAMP] ========================================" >> "$LOG_FILE"
    exit 0
else
    END_TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$END_TIMESTAMP] ❌ ERROR: Podcast generation failed for $TODAY" >> "$ERROR_LOG"
    echo "[$END_TIMESTAMP] Check $ERROR_LOG for details" >> "$LOG_FILE"
    echo "[$END_TIMESTAMP] ========================================" >> "$LOG_FILE"
    exit 1
fi
