from discord import Object
from discord.app_commands import Choice

class Images:
    TOM_APPROVE = "https://cdn.discordapp.com/attachments/1121780046928023613/1306707037350006925/tomapp.gif"
    TOM_MAYBE_NEXT_TIME = "https://cdn.discordapp.com/attachments/1121780046928023613/1312484775889735680/tomnexttime.gif"

REPORT_CHANNEL_ID = 1312815909697622106
CONFIRM_ROLE_WHITELIST = [
    739206335949701241,  # testing role
    1272988674455375872, # HP Officer
    518203583825575964,  # Moderator
    425686371974512640   # Admin
]
TAGS = [
    Object(1312935821577289758), # needs more info
    Object(1312935861784150056), # already reported
    Object(1312951292146221056) # not a cheater
]
TAG_CHOICES = [
    Choice(name="Needs more info", value=0),
    Choice(name="Duplicate", value=1),
    Choice(name="Not cheating", value=2)
]
CONFIRMED_TAG = Object(1312935772155805807)
STEAMID_REGEX = "7656\\d{13}"
REPORTS_DATA_FILE = "reports.json"
    