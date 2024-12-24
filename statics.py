from discord import Object
from discord.app_commands import Choice

# Parameter file for all the things you might need to change

class Images:
    TOM_APPROVE = "https://cdn.discordapp.com/attachments/1121780046928023613/1306707037350006925/tomapp.gif"
    TOM_MAYBE_NEXT_TIME = "https://cdn.discordapp.com/attachments/1121780046928023613/1312484775889735680/tomnexttime.gif"

REPORT_CHANNEL_ID = 1221426805689417808 # report log channel id
CONFIRM_ROLE_WHITELIST = [
    1272988674455375872, # HP Officer
    518203583825575964,  # Moderator
    425686371974512640   # Admin
]
TAGS = [
    Object(1309945406385426432), # not enough info
    Object(1311759650261172334), # already reported
    Object(1309945373971709952) # not a cheater
]
TAG_CHOICES = [ # Options for mark/unmark command autocomplete (value is index of tag in TAGS)
    Choice(name="Not enough info", value=0),
    Choice(name="Duplicate", value=1),
    Choice(name="Not cheating", value=2)
]
CONFIRMED_TAG = Object(1309945340073349130)
STEAMID_REGEX = "7656\\d{13}"
REPORTS_DATA_FILE = "reports.json"
ID_LIST_FILE="reported_ids.txt"
TFBD_LIST_NAME="playerlist.vorobey-hackerpolice.json"
STEAMID64_OFFSET = 76561197960265728
