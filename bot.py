import discord, logging
import discord.ext.commands

intents = discord.Intents.default()
intents.message_content = True
bot = discord.ext.commands.Bot(command_prefix='&', intents=intents, help_command=None)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format="{levelname:8s} | {asctime} | {name:15s} | {message}", style="{")

@bot.event
async def on_ready():
    await bot.load_extension("hp_cog")
    await bot.tree.sync()
    logger.info(f"{bot.user} is up and running meow")

@bot.tree.command() # REMOVE THIS BEFORE DEPLOYING, letting random people reload the module is bound to break something
async def reload(interaction: discord.Interaction):
    await bot.reload_extension("hp_cog")
    await bot.tree.sync()
    await interaction.response.send_message("Reloaded!", ephemeral=True)

if __name__ == "__main__":
    token = open("token.txt").read().strip()
    bot.run(token, log_handler=None)

