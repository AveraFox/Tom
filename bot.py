import discord, logging, os
import discord.ext.commands

intents = discord.Intents.default()
intents.message_content = True
bot = discord.ext.commands.Bot(command_prefix='idkhowtodisablethissoilljustputsomethingunlikelyhere', intents=intents, help_command=None)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format="{levelname:8s} | {asctime} | {name:15s} | {message}", style="{")

@bot.event
async def on_ready():
    await bot.load_extension("hp_cog") # load hp_cog.py into the bot
    await bot.load_extension("vanity_resolver_cog")
    await bot.tree.sync() # upload command tree to discord, so you can see all available commands in the client
    await bot.change_presence(activity=discord.CustomActivity("🫡"))
    logger.info(f"{bot.user} is up and running meow")

if os.environ.get("DEBUG") == "1": # only enable command if debug is set in environment
    @bot.tree.command()
    async def reload(interaction: discord.Interaction):
        await bot.reload_extension("hp_cog")
        await bot.reload_extension("vanity_resolver_cog")
        await bot.tree.sync()
        await interaction.response.send_message("Reloaded!", ephemeral=True)

if __name__ == "__main__":
    token = open("token.txt").read().strip()
    bot.run(token, log_handler=None)

