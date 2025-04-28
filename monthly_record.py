import csv
import os
import discord
from discord.ext import commands
import json
from datetime import datetime
from flask import Flask
from threading import Thread

# Flask server to keep Replit bot alive
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# Enable privileged intents
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

    # Get ISO week format
    year, week_num, _ = now.isocalendar()
    csv_filename = f"attendance_{year}-W{week_num:02d}.csv"

    joined_channel = before.channel is None and after.channel is not None
    left_channel = before.channel is not None and after.channel is None

    if joined_channel or left_channel:
        action = "Joined" if joined_channel else "Left"
        channel = after.channel.name if joined_channel else before.channel.name

        # Log to console
        print(f"{member.name} {action} {channel} at {now_str}")

        # Append to weekly CSV
        file_exists = os.path.isfile(csv_filename)
        with open(csv_filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["User ID", "Username", "Action", "Channel", "Timestamp"])
            writer.writerow([uid, member.name, action, channel, now_str])


@bot.event

async def on_voice_state_update(member, before, after):
    uid = str(member.id)
    now = datetime.utcnow().isoformat()

    try:
        with open("attendance.json", "r+") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

            data.setdefault(uid, {"username": member.name, "sessions": []})

            if before.channel is None and after.channel is not None:
                # Joined a voice channel
                channel_name = after.channel.name if after.channel else "Unknown"
                data[uid]["sessions"].append({
                    "in": now,
                    "channel": channel_name
                })
                print(f"{member.name} joined {channel_name}")

            elif before.channel is not None and after.channel is None:
                # Left a voice channel
                channel_name = before.channel.name if before.channel else "Unknown"
                if data[uid]["sessions"]:
                    data[uid]["sessions"][-1]["out"] = now
                    data[uid]["sessions"][-1]["left_channel"] = channel_name
                print(f"{member.name} left {channel_name}")

            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

    except Exception as e:
        print("Error updating attendance:", e)


# Start the Flask ping server
keep_alive()

# Your actual bot token here (KEEP PRIVATE!)
bot.run("MTM2NDI4MjA5NTMwMzY1NTQ3NA.GA6mGI.UV-L5CdmGMQQ9CIvuIbWvVGHzYt6O7FqtE_2BE")
