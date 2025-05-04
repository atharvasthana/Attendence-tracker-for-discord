import csv
import os
import discord
from discord.ext import commands
import json
from datetime import datetime
from flask import Flask
from threading import Thread

# Flask server to keep bot alive (only needed on Replit, not Railway)
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# Discord bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    uid = str(member.id)
    now = datetime.utcnow()
    now_str = now.isoformat()

    joined_channel = before.channel is None and after.channel is not None
    left_channel = before.channel is not None and after.channel is None

    if not joined_channel and not left_channel:
        return  # Skip moves within same channel

    channel = after.channel.name if joined_channel else before.channel.name
    action = "Joined" if joined_channel else "Left"

    # Log to console
    print(f"{member.name} {action} {channel} at {now_str}")

    # Save to CSV (weekly file)
    year, week_num, _ = now.isocalendar()
    csv_filename = f"attendance_{year}-W{week_num:02d}.csv"
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["User ID", "Username", "Action", "Channel", "Timestamp"])
        writer.writerow([uid, member.name, action, channel, now_str])

    # Save to JSON
    try:
        with open("attendance.json", "r+") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

            data.setdefault(uid, {"username": member.name, "sessions": []})

            if joined_channel:
                data[uid]["sessions"].append({
                    "in": now_str,
                    "channel": channel
                })
            elif left_channel and data[uid]["sessions"]:
                data[uid]["sessions"][-1]["out"] = now_str
                data[uid]["sessions"][-1]["left_channel"] = channel

            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

    except Exception as e:
        print("Error updating attendance:", e)

# Start Flask server (optional on Railway, required on Replit)
# Comment out the line below if using Railway
# keep_alive()

# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))
