import discord, logging, os, statics, sys
import discord.ext.commands
from io import StringIO
import traceback

intents = discord.Intents.default()
intents.message_content = True
bot = discord.ext.commands.Bot(command_prefix='idkhowtodisablethissoilljustputsomethingunlikelyhere', intents=intents, help_command=None)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format="{levelname:8s} | {asctime} | {name:15s} | {message}", style="{")

error_channel = None

@bot.event
async def on_ready():
    global error_channel
    error_channel = await bot.fetch_channel(statics.ERROR_CHANNEL_ID)
    await bot.load_extension("hp_cog") # load hp_cog.py into the bot
    await bot.load_extension("vanity_resolver_cog")
    await bot.load_extension("tom_react")
    await bot.tree.sync() # upload command tree to discord, so you can see all available commands in the client
    logger.info(f"{bot.user} is up and running meow")

@bot.event
async def on_error(event, *args, **kwargs):
    error = sys.exception()
    msg = "".join(traceback.format_exception(error))
    sio = StringIO(msg)
    await error_channel.send(file=discord.File(sio, filename="error.txt"))
    logger.error(msg)

if os.environ.get("DEBUG") == "1": # only enable command if debug is set in environment
    @bot.tree.command()
    async def reload(interaction: discord.Interaction):
        await bot.reload_extension("hp_cog")
        await bot.reload_extension("vanity_resolver_cog")
        await bot.reload_extension("tom_react")
        await bot.tree.sync()
        await interaction.response.send_message("Reloaded!", ephemeral=True)

if __name__ == "__main__":
    token = open("token.txt").read().strip()
    bot.run(token, log_handler=None)

