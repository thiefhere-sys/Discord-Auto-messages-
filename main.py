import os
import asyncio
import discord
from discord.ext import commands, tasks
from aiohttp import web

# Environment variables se token aur target channel id uthayenge
TOKEN = os.getenv("DISCORD_TOKEN")
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "0"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Jo link aap har 1 ghante mein bhejna chahte hain
LINK_TO_SHARE = "https://youtube.com/@mishorts1818?si=_KHPvSshfC16VcBM"


@bot.event
async def on_ready():
  print(f"✅ LOGGED IN AS {bot.user}")
  # Background task ko start karna jab bot online ho jaye
  if not auto_post_loop.is_running():
    auto_post_loop.start()


# Har 1 ghante (hours=1) mein chalne wala background task
@tasks.loop(hours=1.0)
async def auto_post_loop():
  await bot.wait_until_ready()
  try:
    target_channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not target_channel:
      target_channel = await bot.fetch_channel(TARGET_CHANNEL_ID)

    if target_channel:
      await target_channel.send(
          f"📢 **Automatic Share:** {LINK_TO_SHARE}"
      )
      print("✅ Auto-posted link successfully!")
  except Exception as e:
    print(f"❌ Auto-post error: {str(e)}")


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


# Render / UptimeRobot ke liye web server
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
