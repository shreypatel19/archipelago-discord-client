import os
from typing import Optional
import discord
from discord.ext import commands
from CommonClient import CommonContext, server_loop
import asyncio
import copy
from NetUtils import JSONtoTextParser, color_codes
import ModuleUpdate
ModuleUpdate.update(yes=True)  # Automatically update dependencies without user interaction

from dotenv import load_dotenv
load_dotenv()

def discord_color_code(*args):
  return '\u001b[0;' + ';'.join([str(color_codes[arg]) for arg in args]) + 'm'

class DiscordJSONtoTextParser(JSONtoTextParser):
  def _handle_color(self, node):
    codes = node["color"].split(";")
    buffer = "".join(discord_color_code(code) for code in codes if code in color_codes)
    return buffer + self._handle_text(node) + discord_color_code("reset")

class DiscordContext(CommonContext):
  tags = CommonContext.tags | {"TextOnly"}
  game = ""
  items_handling = 0b111
  want_slot_data = False

  def __init__(self, address: str, password: Optional[str], discord_client: discord.Client, channel_id: int):
    super().__init__(address, password)
    self.discord_client = discord_client
    self.channel_id = channel_id
    self.json_parser = DiscordJSONtoTextParser(self)
  
    print(f"Initialized DiscordContext with address: {address}, channel_id: {channel_id}")

  async def server_auth(self, password_requested = False):
    if password_requested and not self.password:
      await super().server_auth(password_requested)
    await self.get_username()
    await self.send_connect(game="")
    print(f"Connected to server with username: {self.username}")

  
  def on_package(self, cmd, args):
    if cmd == "Connected":
      self.game = self.slot_info[self.slot].game
    print(f"Received package: {cmd} with args: {args}")
  
  async def disconnect(self, allow_autoreconnect = False):
    self.game = ""
    print(f"Disconnected from server")
    return await super().disconnect(allow_autoreconnect)
  
  def on_print_json(self, args):
    channel = self.discord_client.get_channel(self.channel_id)
    data = copy.deepcopy(args["data"])
    output = f'```ansi\n{self.json_parser(data)}\n```'
    if channel:
      asyncio.run_coroutine_threadsafe(channel.send(output), self.discord_client.loop)
      print(f"Sent message to Discord channel {self.channel_id}: {output}")
    else:
      print(f"Failed to send message to Discord channel {self.channel_id}: Channel not found")
  
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.command(name="connect")
async def _connect(ctx, address: str, name: str):
  if not isinstance(ctx.channel, discord.TextChannel):
    await ctx.send("This command can only be used in a text channel.")
    return
  if hasattr(bot, "ap_client") and bot.ap_client.game:
    await ctx.send("Already connected to a game.")
    return
  bot.ap_client = DiscordContext(address, None, bot, ctx.channel.id)
  bot.ap_client.auth = name
  bot.ap_client.server_task = asyncio.create_task(server_loop(bot.ap_client))
  await ctx.send(f"Connecting to {address}...")

@bot.command(name="disconnect")
async def _disconnect(ctx):
  if not isinstance(ctx.channel, discord.TextChannel):
    await ctx.send("This command can only be used in a text channel.")
    return
  if not hasattr(bot, "ap_client") or not bot.ap_client.game:
    await ctx.send("Not currently connected to a game.")
    return
  await bot.ap_client.disconnect()
  await ctx.send("Disconnected from the game.")

@bot.command(name="ping")
async def _ping(ctx):
  await ctx.send("Pong!")

@bot.event
async def on_ready():
  await bot.tree.sync()
  print(f'{bot.user} has logged in!')
  
bot.run(os.getenv("DISCORD_TOKEN"))