import aiohttp, re

STEAMID_XML_PATTERN = re.compile("<steamID64>(\\d+)</steamID64>")
VANITY_LINK_PATTERN = re.compile("(https://steamcommunity.com/id/([\\w-]+))")
PERM_LINK_PATTERN = re.compile("https://(?:steamcommunity.com/profiles|steamhistory.net/id|shadefall.net/daemon)/(\\d+)")
PERM_LINK_PREFIX = "https://steamcommunity.com/profiles/"
STEAMID_REGEX = "7656\\d{13}"

async def resolve_vanity_url(url: str) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.get(url + "?xml=1") as resp:
            steamid = STEAMID_XML_PATTERN.search(await resp.text())
            if not steamid:
                return None
            return int(steamid.group(1))