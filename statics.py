from discord import Object
from discord.app_commands import Choice

# Parameter file for all the things you might need to change

class Images:
    TOM_APPROVE = "https://cdn.discordapp.com/attachments/1121780046928023613/1306707037350006925/tomapp.gif"
    TOM_MAYBE_NEXT_TIME = "https://cdn.discordapp.com/attachments/1121780046928023613/1312484775889735680/tomnexttime.gif"

REPORT_CHANNEL_ID = 1313271773395161169 # report log channel id
CONFIRM_ROLE_WHITELIST = [
    1313270134852554852,  # testing role
    1272988674455375872, # HP Officer
    518203583825575964,  # Moderator
    425686371974512640   # Admin
]
TAGS = [
    Object(1313271607011311658), # needs more info
    Object(1313271630293631096), # already reported
    Object(1313271585502662709) # not a cheater
]
TAG_CHOICES = [ # Options for mark/unmark command autocomplete (value is index of tag in TAGS)
    Choice(name="Needs more info", value=0),
    Choice(name="Duplicate", value=1),
    Choice(name="Not cheating", value=2)
]
CONFIRMED_TAG = Object(1313271682059993239)
STEAMID_REGEX = "7656\\d{13}"
REPORTS_DATA_FILE = "reports.json"
    