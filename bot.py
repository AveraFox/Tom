
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
from discord import Message

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='&', intents=intents)

hp_academy_modding_but_its_not = 1312054856164573204
tom = os.getenv('TOM')

@bot.event
async def on_ready():
    print(f"{bot.user} is up and running meow")


@bot.command(name='confirm')
async def confirm(ctx):
    '''
    sends report info in hp modding(but actually not because i havent added him to the server yet)
    '''
    if await is_whitelisted(ctx):
        if isinstance(ctx.channel, discord.Thread):
            logging_channel = bot.get_channel(hp_academy_modding_but_its_not)
            user_tag = await bot.fetch_user(ctx.channel.owner_id)
            starter_message = await ctx.channel.fetch_message(ctx.channel.id)
            msg_link = starter_message.jump_url
            confirmation_msg = f"{msg_link} {user_tag} ({ctx.channel.owner_id}) cheater exposed"
            try:
                await logging_channel.send(confirmation_msg)
            except Exception as e:
                await ctx.send(f"Something went wrong: {e}")
            else:
                await ctx.send(tom)
        else:
            await ctx.send("Use the command in the forum thread, dumb ass")
    else:
        await ctx.send("You don't have the role to use this shit")

@bot.command(name="count")
async def report_count(ctx, userid: str):
    """
    &count <userid> - sends how many reports this user has
    """
    if await is_whitelisted(ctx):
        username = await bot.fetch_user(int(userid))
        with open("reports.json", "r") as reports:
            data = json.load(reports)
            for user, count in data.items():
                if user == userid:
                    found = True
                    await ctx.send(f"{username} ({user}) has {count} reports")
                    break
            if not found:
                await ctx.send(f"I couldn't find the user")
    else:
        await ctx.send("You don't have the role to use this shit")

async def is_whitelisted(ctx):
    hp_role_id = 1312766723857846325
    userid = ctx.author.id
    userroles = ctx.author.roles
    if any(hp_role_id == role.id for role in userroles):
        return True
    else:
        return False

    





if __name__ == "__main__":
    bot.run(TOKEN)

