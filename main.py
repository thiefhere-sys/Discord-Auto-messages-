import os
import aiohttp
import discord
from discord.ext import commands

# Environment variables se token aur target channel id uthayenge
TOKEN = os.getenv("DISCORD_TOKEN")
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "0"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"✅ LOGGED IN AS {bot.user}")


@bot.command(name="postmsg")
async def postmsg(ctx, message_link: str):
  try:
    # Discord link format: https://discord.com/channels/guild_id/channel_id/message_id
    parts = message_link.split("/")
    if len(parts) < 7:
      await ctx.send("❌ Invalid message link format!")
      return

    source_channel_id = int(parts[5])
    message_id = int(parts[6])

    # Source channel se message fetch karna
    source_channel = bot.get_channel(source_channel_id)
    if not source_channel:
      source_channel = await bot.fetch_channel(source_channel_id)

    msg = await source_channel.fetch_message(message_id)

    # Target channel find karna
    target_channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not target_channel:
      target_channel = await bot.fetch_channel(TARGET_CHANNEL_ID)

    # Content aur attachments prepare karna
    content_to_send = f"**Forwarded from {msg.author.mention}:**\n{msg.content}"

    # Agar koi image/attachment hai toh unhe collect karna
    files = []
    for attachment in msg.attachments:
      file = await attachment.to_file()
      files.append(file)

    # Target channel par bhej dena
    await target_channel.send(content=content_to_send, files=files)
    await ctx.send("✅ Message successfully posted to the target channel!")

  except Exception as e:
    await ctx.send(f"❌ Error: {str(e)}")


# Render / UptimeRobot ke liye aiohttp web server (optional par safe hai)
async def handle(request):
  return aiohttp.web.Response(text="Bot is running!")


async def run_web():
  app = aiohttp.web.Application()
  app.router.add_get("/", handle)
  runner = aiohttp.web.AppRunner(app)
  await runner.setup()
  port = int(os.getenv("PORT", 10000))
  site = aiohttp.web.TCPSite(runner, "0.0.0.0", port)
  await site.start()


import asyncio


async def main():
  await run_web()
  await bot.start(TOKEN)


if __name__ == "__main__":
  asyncio.run(main())
