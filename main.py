import os
import asyncio
import random
import discord
from discord.ext import commands, tasks
from aiohttp import web

# Environment variables se token aur target channel id uthayenge
TOKEN = os.getenv("DISCORD_TOKEN")
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "0"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Yahan aap jitne chahein utne messages ya links add kar sakte hain (4 se 6 ya zyada)
LINKS_TO_SHARE = [
    "Want to earn free gift cards and cash in your spare time? 💸 Join Swagbucks and get paid for taking surveys, watching videos, and shopping online! Sign up using my link and start earning today: https://www.swagbucks.com/refer/Irshad01",
    "https://youtube.com/@mishorts1818?si=_KHPvSshfC16VcBM",
    "https://discord.gg/H6KqzMCDP",
    # Aap aur bhi links yahan double quotes mein comma laga kar jod sakte hain
]

# Index track karne ke liye variable taaki ek-ek karke link jaye
current_link_index = 0


@bot.event
async def on_ready():
  print(f"✅ LOGGED IN AS {bot.user}")
  if not auto_post_loop.is_running():
    auto_post_loop.start()


# Har 1 ghante (hours=1) mein chalne wala background task
@tasks.loop(hours=1.0)
async def auto_post_loop():
  global current_link_index
  await bot.wait_until_ready()
  try:
    target_channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not target_channel:
      target_channel = await bot.fetch_channel(TARGET_CHANNEL_ID)

    if target_channel and LINKS_TO_SHARE:
      # List se current link uthana
      link_to_send = LINKS_TO_SHARE[current_link_index]

      # Bina kisi extra prefix ke seedha link bhejna
      await target_channel.send(link_to_send)
      print(f"✅ Auto-posted successfully: {link_to_send}")

      # Agli baar agli link bhejne ke liye index ko aage badhana (loop around)
      current_link_index = (current_link_index + 1) % len(LINKS_TO_SHARE)

  except Exception as e:
    print(f"❌ Auto-post error: {str(e)}")


@bot.command(name="postmsg")
async def postmsg(ctx, message_link: str):
  try:
    parts = message_link.split("/")
    if len(parts) < 7:
      await ctx.send("❌ Invalid message link format!")
      return

    source_channel_id = int(parts[5])
    message_id = int(parts[6])

    source_channel = bot.get_channel(source_channel_id)
    if not source_channel:
      source_channel = await bot.fetch_channel(source_channel_id)

    msg = await source_channel.fetch_message(message_id)

    target_channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not target_channel:
      target_channel = await bot.fetch_channel(TARGET_CHANNEL_ID)

    content_to_send = f"**Forwarded from {msg.author.mention}:**\n{msg.content}"

    files = []
    for attachment in msg.attachments:
      file = await attachment.to_file()
      files.append(file)

    await target_channel.send(content=content_to_send, files=files)
    await ctx.send("✅ Message successfully posted to the target channel!")

  except Exception as e:
    await ctx.send(f"❌ Error: {str(e)}")


# Render ke liye web server
async def handle(request):
  return web.Response(text="Bot is running!")


async def run_web():
  app = web.Application()
  app.router.add_get("/", handle)
  runner = web.AppRunner(app)
  await runner.setup()
  port = int(os.getenv("PORT", 10000))
  site = web.TCPSite(runner, "0.0.0.0", port)
  await site.start()


async def main():
  await run_web()
  await bot.start(TOKEN)


if __name__ == "__main__":
  asyncio.run(main())
