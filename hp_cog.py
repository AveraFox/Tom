import discord, typing, logging, re, traceback
from io import StringIO
from discord.ext import commands, tasks
from discord import app_commands

import statics
from reports import Reports
import steam

logger = logging.getLogger(__name__)

class NotInThreadError(app_commands.AppCommandError): # custom error that is thrown when a thread-only command isn't called in a thread
    pass

def check_in_thread(interaction: discord.Interaction): # function to check if a command was called in a thread
    if not isinstance(interaction.channel, discord.Thread):
        raise NotInThreadError()
    return True

async def get_steamid(id: str) -> int: # resolve steam profile links and vanity urls
    if re.fullmatch(steam.STEAMID_REGEX, id) is not None:
        return int(id)
    
    m = re.match(steam.PERM_LINK_PATTERN, id)
    if m:
        return int(m.group(1))
    
    m = re.match(steam.VANITY_LINK_PATTERN, id)
    if m:
        return await steam.resolve_vanity_url(m.group(0))
    
    return None

def has_any_role(member: discord.Member, roles: typing.List[int]) -> bool: # check if a user has any of the roles passed
    if(any(role.id in roles for role in member.roles)):
        return True
    return False

class HPCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.reports: Reports = None
        self.bot: commands.Bot = bot
        self.toplist_needs_rebuild: bool = True
        self.toplist: typing.Optional[str] = None

    #### EVENT HANDLERS ####
    async def cog_load(self):
        self.reports = await Reports.load()
        logger.info("reports loaded")
        self.log_channel = await self.bot.fetch_channel(statics.REPORT_CHANNEL_ID)
        self.error_channel = await self.bot.fetch_channel(statics.ERROR_CHANNEL_ID)
        self.update_toplist.start() # start loop task to update the toplist regularly

    async def interaction_check(self, interaction: discord.Interaction): 
        # usually used to check some condition for all app_commands in this Cog, but just log user and the command that was run
        options = []
        if "options" in interaction.data:
            for option in interaction.data["options"]:
                options.append(f"{option['name']}:'{option['value']}'")
        logger.info(f"{interaction.user.name} executed command: {interaction.command.name} {' '.join(options)}")
        return True

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # error handler for all the checks in this cog
        if isinstance(error, app_commands.errors.MissingAnyRole):
            await interaction.response.send_message("You are not allowed to use this command", ephemeral=True)
        elif isinstance(error, NotInThreadError):
            await interaction.response.send_message("Cannot use this command outside of a thread", ephemeral=True)
        elif isinstance(error, app_commands.errors.CommandOnCooldown):
            await interaction.response.send_message("Issuing commands too quickly!", ephemeral=True)
        else:
            msg = "".join(traceback.format_exception(error))
            sio = StringIO(msg)
            await self.error_channel.send(file=discord.File(sio, filename="error.txt"))
            logger.error(msg)

    @tasks.loop(minutes=1.0) # runs this function every minute
    async def update_toplist(self):
        # only run if necessary
        if not self.toplist_needs_rebuild:
            return
        logger.info("Toplist outdated, rebuilding")
        self.toplist_needs_rebuild = False

        top_reporters = self.reports.get_top_n(20)
        msg = ""
        for reporter in top_reporters:
            try:
                user = await self.bot.fetch_user(reporter.userid)
            except discord.NotFound: # Handle deleted user accounts
                class Mockuser:
                    def __init__(self, id):
                        self.global_name = id
                user =  Mockuser(reporter.userid) # dummy class object, so the user id is used instead of the name

            msg += f"{reporter.points()}: {user.mention} ({user.global_name})\n"

        self.toplist = msg # Store toplist for later use
        logger.info("Toplist rebuilt")
        
    #### REGULAR USER COMMANDS ####
    @app_commands.command(
        name="points",
        description="Get a users (or your own) report point count"
    )
    @app_commands.describe(user="User to lookup points for, leave blank to get your own count")
    @app_commands.checks.cooldown(1, 5.0) # only allow one call every 5 seconds
    async def get_report_point_count(self, interaction: discord.Interaction, user: typing.Optional[discord.User] = None):
        if not user: # if no user was passed, look up points for the user calling the command
            user = interaction.user

        reporter = self.reports.get(user.id)
        if not reporter: # user does not have a reporter entry
            await interaction.response.send_message("This user does not have any reports recorded", ephemeral=True)
            return

        embed = discord.Embed()
        embed.set_author(name=user.global_name, icon_url=user.display_avatar.url)
        embed.add_field(name="Report count", value=reporter.points(), inline=False)

        # detailed information that is only shown to officers
        if(has_any_role(interaction.user, statics.CONFIRM_ROLE_WHITELIST)):
            steamprofile = f"https://steamcommunity.com/profiles/{reporter.profile_id}" if reporter.profile_id else "not on record"
            embed.add_field(name="Steam profile", value=steamprofile, inline=False)
            
            recentreports = "\n".join(map(lambda r: r.message, reversed(reporter.reports[max(0,len(reporter.reports)-5):])))
            embed.add_field(name="Recent reports", value=recentreports, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True) # ephemeral means that the message only shows up for the user using the command
        
    @app_commands.command(
        name="toplist",
        description="List the top 20 people based on report count"
    )
    @app_commands.checks.cooldown(1, 5.0)
    async def get_top_reporters(self, interaction: discord.Interaction):
        # sends back the toplist, if it was created already
        if not self.toplist:
            await interaction.response.send_message("Please wait, the toplist is being built", ephemeral=True)
            return
        await interaction.response.send_message(embed=discord.Embed(title="Top Reporters", description=self.toplist), ephemeral=True)

    @app_commands.command(
        name="lookup",
        description="Look up previous reports of a SteamID"
    )
    async def lookup(self, interaction: discord.Interaction, steamid: str):
        await interaction.response.defer(ephemeral=True)
        steamid = await get_steamid(steamid.strip())
        if not steamid:
            await interaction.followup.send("Invalid SteamID", ephemeral=True)
            return
        
        reports = self.reports.find_cheater(int(steamid))
        
        if len(reports) == 0:
            await interaction.followup.send(f"No reports found for {steamid}", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Reports for {steamid}",
            description='\n'.join(map(lambda r: r.message + (' -- (unverified)' if not r.verified else ''), reports))
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    #### OFFICER COMMANDS ####
    @app_commands.command(
        name="mark",
        description="Mark the current thread"
    )
    @app_commands.checks.has_any_role(*statics.CONFIRM_ROLE_WHITELIST)
    @app_commands.choices(tag=statics.TAG_CHOICES) # defines options for this parameter that show up in discord
    @app_commands.check(check_in_thread)
    async def mark(self, interaction: discord.Interaction, tag: app_commands.Choice[int]):
        # just adds the selected tag to the thread the command is called in
        thread: discord.Thread = interaction.channel
        await thread.add_tags(statics.TAGS[tag.value])
        await interaction.response.send_message(f"Added tag {tag.name}", ephemeral=True)

    @app_commands.command(
        name="unmark",
        description="Unmark the current thread"
    )
    @app_commands.checks.has_any_role(*statics.CONFIRM_ROLE_WHITELIST)
    @app_commands.choices(tag=statics.TAG_CHOICES)
    @app_commands.check(check_in_thread)
    async def unmark(self, interaction: discord.Interaction, tag: app_commands.Choice[int]):
        # removes the selected tag from the thread this command was called in
        thread: discord.Thread = interaction.channel
        await thread.remove_tags(statics.TAGS[tag.value])
        await interaction.response.send_message(f"Removed tag {tag.name}", ephemeral=True)
        
    @app_commands.command(
        name="approve",
        description="Approve the cheater report"
    )
    @app_commands.describe(
        points="Amount of points this report gives (default 1)", 
        steamids="Comma seperated list of reported steamids, ex. \"76561199796492647,76561199532619504\"",
        verified="If the steamids can be verified to be in the report",
        allow_duplicate="Skip checking if the user was already reported",
        reporter_steamid="SteamID of the person reporting, required if none has been logged yet",
        skip_reporter_steamid_check="Allow confirming even though the reporter has not provided a profile SteamID"
    )
    @app_commands.checks.has_any_role(*statics.CONFIRM_ROLE_WHITELIST)
    @app_commands.check(check_in_thread)
    @app_commands.rename(steamids="cheater_steamids")
    async def approve(self, 
        interaction: discord.Interaction, 
        steamids: str, 
        verified: bool,
        points: int = 1, 
        reporter_steamid: typing.Optional[str] = None,
        allow_duplicate: bool = False,
        skip_reporter_steamid_check: bool = False
    ):            
        # Approves the report the command is executed in
        thread: discord.Thread = interaction.channel
        owner = await self.bot.fetch_user(thread.owner_id)
        reporter = self.reports.get_or_create(thread.owner_id)
        
        if reporter.find_report(thread.jump_url): # look up if report was already approved
            await interaction.response.send_message("Report was already approved", ephemeral=True)
            return

        if not reporter.profile_id and not reporter_steamid and not skip_reporter_steamid_check: # check if reporter has a steamid on record
            await interaction.response.send_message("Reporter does not have a steam profile ID associated", ephemeral=True)
            return
        elif reporter_steamid: # new steamid was passed to the command
            if not validate_steamid(reporter_steamid):
                await interaction.response.send_message(f"Reporter SteamID \"{reporter_steamid}\" is not valid", ephemeral=True)
                return

        steamids_str = steamids.split(",") # get steamids from the command argument
        steamids_list = []
        for steamid in steamids_str: # verify each steamid and convert to number
            steamid = steamid.strip()
            if not validate_steamid(steamid):
                await interaction.response.send_message(f"Cheater SteamID \"{steamid}\" is not valid", ephemeral=True)
                return
            steamids_list.append(int(steamid))
        
        if len(steamids_list) == 0:
            await interaction.response.send_message("At least one cheater SteamID is required, or \"none\"")
            return
        
        if not allow_duplicate:
            for steamid in steamids_list: # check steamids if they were reported before
                reports = self.reports.find_cheater(steamid)
                if len(reports) > 0 and (not verified or any(map(lambda r: r.verified, reports))):
                    await interaction.response.send_message(f"Cheater {steamid} was already reported:\n{chr(10).join(map(lambda r: r.message + (' -- (unverified)' if not r.verified else ''), reports))}", ephemeral=True)
                    return

        if reporter_steamid: # if a steamid for the reporter was passed, add it to the record and log it in the log channel
            reporter.profile_id = int(reporter_steamid)
            await self.log_channel.send(f"Associated SteamID {reporter_steamid} with user {owner.mention}", silent=True)

        # log channel message
        msg = f"{thread.jump_url} {owner.mention} ({owner.global_name}) cheater exposed (+{points} points, {reporter.points()+points} total)"
        # add report to internal record
        reporter.add_report(msg, points, steamids_list, verified)
        # save data to json
        await self.reports.save()
        # mark toplist for rebuild
        self.toplist_needs_rebuild = True
        # send confirmation message in log channel
        await self.log_channel.send(msg, silent=True)

        await thread.remove_tags(*statics.TAGS) # remove "Needs info", "Not a cheater" and "Already reported" tags
        await thread.add_tags(statics.CONFIRMED_TAG) # add "Confirmed" tag

        if verified:
            await interaction.response.send_message(statics.Images.TOM_APPROVE) # send tom approved gif :D
        else:
            await interaction.response.send_message(f"-# unverified report[.]({statics.Images.TOM_APPROVE})")

    @app_commands.command(
        name="unapprove",
        description="Unapprove a report"
    )
    @app_commands.check(check_in_thread)
    @app_commands.checks.has_any_role(*statics.CONFIRM_ROLE_WHITELIST)
    async def unapprove(self, interaction: discord.Interaction):
        # removes a report for the current thread
        thread = interaction.channel
            
        reporter = self.reports.get(thread.owner_id)
        if not reporter:
            await interaction.response.send_message("User does not have any reports", ephemeral=True)
            return
        
        if not reporter.remove_report(thread.jump_url): # try to remove report from user, returns False if no matching reports were found
            await interaction.response.send_message("This thread has not been confirmed", ephemeral=True)
            return
        
        # save report record to disk
        await self.reports.save()
        # mark toplist for rebuild
        self.toplist_needs_rebuild = True
        # remove the "Confirmed" tag
        await thread.remove_tags(statics.CONFIRMED_TAG)
        # log unapproval in log channel
        await self.log_channel.send(f"{thread.jump_url} <@{thread.owner_id}> unapproved ({reporter.points()} points)", silent=True)
        # send a message that it was unapproved
        await interaction.response.send_message("Report unapproved")

async def setup(bot: commands.Bot):
    # create new HPCog (just a self-contained module that provides commands) and add it to the bot
    # this function gets called by the bot.load_extension call in bot.py
    await bot.add_cog(HPCog(bot))
