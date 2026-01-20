#!/bin/bash

# ANDI IoT System Startup Script
# Starts both the Telegram bot and the main system

echo "Starting ANDI IoT System..."
echo "=============================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with your API keys"
    exit 1
fi

echo ""
echo "Starting Telegram bot in background..."
python bot.py &
BOT_PID=$!
echo "✓ Bot started (PID: $BOT_PID)"

# Give bot time to initialize
sleep 2

echo ""
echo "Starting main system..."
python main.py

# When main.py exits, kill the bot
echo ""
echo "Shutting down..."
kill $BOT_PID 2>/dev/null
echo "✓ System stopped"
