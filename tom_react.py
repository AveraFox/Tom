from discord.ext import commands
import statics, time, discord, random

class ReactCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.cooldowns: dict[int, int] = dict()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.bot.user.mention in message.content:
            return

        curtime = time.time()
        cooldowns = {i: ts for i, ts in self.cooldowns.items() if ts > curtime}
        self.cooldowns = cooldowns
        
        if message.author.id in self.cooldowns:
            await message.add_reaction("\N{SLEEPING SYMBOL}")
            return

        self.cooldowns[message.author.id] = time.time() + statics.TOM_REACT_INTERVAL_SECONDS
        m = await message.channel.send(random.choice(statics.Images.TOM_REACTS))
        await m.add_reaction("\u2764")

async def setup(bot: commands.Bot):
    await bot.add_cog(ReactCog(bot))