import discord, aiohttp, re, statics, logging
from discord.ext import commands
from hp_cog import HPCog

from steam import *

logger = logging.getLogger(__name__)

# Extra cog that watches channels for steam profile vanity links and attempts to find the perma link for them
class VanityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.hp_cog: HPCog = bot.get_cog("HPCog")
        if self.hp_cog == None:
            raise RuntimeError("Couldn't get HPCog")
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        channel_id = message.channel.parent_id if isinstance(message.channel, discord.Thread) else message.channel.id
        if channel_id not in statics.VANITY_RESOLVER_CHANNELS:
            return

        matches = VANITY_LINK_PATTERN.findall(message.content)
        steamids = dict()
        unresolved_steamids = []

        for match in set(matches):
            res = await resolve_vanity_url(match[0])
            if res:
                steamids[match[1]] = str(res)
            else:
                unresolved_steamids.append(match[1])
                    
        matches = PERM_LINK_PATTERN.findall(message.content)
        reported_perms = dict()
        for sid in set(matches) | set(map(lambda s: s, steamids.values())):
            reports = self.hp_cog.reports.find_cheater(int(sid))
            if len(reports) > 0:
                verified = any(map(lambda r: r.verified, reports))
                if verified:
                    reported_perms[sid] = {"report": next(filter(lambda r: r.verified, reports)).thread_url, "verified": True}
                else:
                    reported_perms[sid] = {"report": reports[0].thread_url, "verified": False}

        # only reply if there were steamids found
        if len(steamids) > 0 or len(unresolved_steamids) > 0 or len(reported_perms) > 0:
            msg = ""
            if len(steamids) > 0:
                msg += "Permanent links:\n"
                msg += "\n".join(map(lambda sid: f'"{sid[0]}": {PERM_LINK_PREFIX+sid[1]}', steamids.items())) + "\n"
            if len(unresolved_steamids) > 0:
                msg += "Could not find profile for " + ",".join(map(lambda vid: f'"{vid}"', unresolved_steamids))
            if len(reported_perms) > 0:
                if msg != "":
                    msg += "\n"
                msg += "\n".join(map(lambda s: f"{s[0]} has already been reported: {s[1]['report']}{' (unverified)' if not s[1]['verified'] else ''}", reported_perms.items()))
            elif len(steamids) > 0:
                msg += "SteamIDs have not been reported"
            await message.reply(msg, mention_author=False)

    
async def setup(bot: commands.Bot):
    await bot.add_cog(VanityCog(bot))
