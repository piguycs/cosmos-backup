import requests
import discord
from discord_slash import SlashCommand
from discord_slash.context import ComponentContext
from discord.utils import get
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType

from os import environ
from dotenv import load_dotenv

# this is shit to make shit work ok
#from os import system
#system("python3 uptime.py >> flasklogs &")


load_dotenv()

status = "over the guild"
#status = "over my maintenance"
activity = discord.Activity(
    type=discord.ActivityType.watching, name=status)

client = discord.Client(intents=discord.Intents.all(),
                        activity=activity, status=discord.Status.idle)
# Declares slash commands through the client.
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    print("Ready!")


# index 0 = test server, index 1 = cosmic exiles
guild_ids = [901009690929012766, 802308200506458132]


def is_me(m):
    return m.author == client.user

async def getuuid(ign):
    uuidreq = requests.get(
        f"https://api.mojang.com/users/profiles/minecraft/{ign}")

    if uuidreq.status_code != 200:
        return None

    uuid = uuidreq.json()["id"]
    
    return uuid

async def getprofiles(uuid):
    api = f'https://api.slothpixel.me/api/skyblock/profiles/{uuid}'
    data = requests.get(api).json()

    if data:
        temp = 0
        lastprofile = "ERROR-NO-PROFILE"
        profiles = []

        for x in data:
            login = data[x]["members"][uuid]["last_save"]
            name = data[x]["cute_name"]
            profiles.append([login, name])

        profiles = sorted(profiles,key=lambda l:l[0], reverse=True)

        currprofile = profiles[0][1]

        return currprofile

    else:
        return None

def verifyUser(dungeons):
    isEligible = dungeons["catacombs"]["level"]["level"] and dungeons["secrets_found"] >= 2000

    return isEligible


async def getCata(ign, currprofile, checkeligibility=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion'
    }

    url = f"https://sky.shiiyu.moe/api/v2/dungeons/{ign}/{currprofile}"
    cata = requests.get(url, headers=headers).json()

    if checkeligibility:
        return verifyUser(cata["dungeons"])
    else:
        if "dungeons" in cata:
            if cata["dungeons"]["catacombs"]["visited"]:
                return cata["dungeons"]["catacombs"]["level"]["level"], cata["dungeons"]["selected_class"], \
                     cata["dungeons"]["secrets_found"]
        else:
            return 0, "000000", \
                   0000
            #return "Never visited dungeons", "ERR", "ERR"


async def getDiscord(ign):
    uuid = requests.get(
        f"https://api.mojang.com/users/profiles/minecraft/{ign}")

    key = environ.get("KEY")

    if uuid.status_code == 200:
        uuid = uuid.json()
        uuid = uuid["id"]
    else:
        return None, "This minecraft account does not exist"  # ERROR

    playerAPI = requests.get(
        f"https://api.hypixel.net/player?uuid={uuid}&key={key}")

    if playerAPI.status_code == 200:
        player = playerAPI.json()

        if player["player"] == None:
            return None, "this player never joined hypixel"  # ERROR
        else:
            playerdiscord = player["player"]
            if "socialMedia" in playerdiscord.keys():
                playerdiscord = player["player"]["socialMedia"]["links"]
                if "DISCORD" in playerdiscord.keys():
                    return playerdiscord["DISCORD"], None  # NOT ERROR
                else:
                    return None, "the player does not have discord connected"  # ERROR
            else:
                return None, "the player does not have discord connected"  # ERROR
    else:
        return None, "the api is not responding, pls try again later"  # ERROR


async def userinceguild(ign):
    key = environ.get("KEY")

    uuid = requests.get(
        f"https://api.mojang.com/users/profiles/minecraft/{ign}")

    if uuid.status_code == 200:
        uuid = uuid.json()["id"]
        api = requests.get(
            f"https://api.hypixel.net/guild?key={key}&player={uuid}")

        if api.status_code == 200:
            guild = api.json()["guild"]
            if guild:
                guild = guild["_id"]
                if guild == "600b55008ea8c9e004b042cb":
                    return True
                else:
                    return False

    return None  # API DOWN ERROR


async def getRoles(catalvl, catasecrets, ign):
    roles = []

    useringuild = await userinceguild(ign)

    if useringuild:
        if catalvl >= 24 and catasecrets >= 2000:
            roles.append("Livid")
        if catalvl >= 27 and catasecrets >= 4000:
            roles.append("Sadan")
        if catalvl >= 30 and catasecrets >= 10000:
            roles.append("Necron")
        if catalvl >= 38 and catasecrets >= 20000:
            roles.append("Kyrios Champ")
    elif useringuild == None:
        return None
    else:
        return []

    # if user in guild
    return roles


roleids = {
    "livid": 804114416898801735,
    "sadan": 804114554602520586,
    "necron": 804114592774881330,
    "kchamp": 841048108993740820,
    "verified": 803747071484100658
}

# TEST SERVER
# roleids = {
#     "livid": 901010817611350026,
#     "sadan": 901767834437296128,
#     "necron": 901796653575585822,
#     "kchamp": 901796600458924064,
#     "verified": 901797028038836304
# }

## -----------------------------------------------------
##                     COMMANDS
## -----------------------------------------------------

verifyargs = [
    {
        # IGN - Example "thepiguy_"
        "name": "ign",
        "description": "In Game Name (Username)",
        "type": 3,
        "required": True
    },
    {
        # Profile - Example "Orange"
        "name": "profile",
        "description": "Your skyblock profile",
        "type": 3,
        "required": False
    }
]


@slash.slash(name="verify", guild_ids=guild_ids, description="Link your skyblock profile with your discord account",
             options=verifyargs)
async def _verify(ctx: ComponentContext, ign, profile=None):
    # returns latest profile of the user...
    # if never joined skyblock or hypixel returns None

    print(f'\033[0;36mSTARTED VERIFY FOR {ign} {profile}\033[0m')

    await ctx.defer(hidden=True)

    uuid = await getuuid(ign)

    if uuid == None:
        await ctx.send("The minecraft account does not exist, perhaps try checking if it is spelled correctly?")

    if profile:
        currprofile = profile
    else:
        currprofile = await getprofiles(uuid)
        print(f'\033[0;36mPROFILE FOR ABOVE ACCOUNT IS {currprofile}\033[0m')


    requireddisc, discerror = await getDiscord(ign)
    currdisc = ctx.author

    if requireddisc:
        # The user has discord connected
        if str(requireddisc) == str(currdisc):
            # the user owns the account
            if currprofile:
                catalvl, cataclass, catasecrets = await getCata(ign, currprofile)

            if currprofile == None:
                catalvl = "User does not exist on skyblock"

            if catalvl in ["Never visited dungeons", "does not meet requirements",
                           "Not your account... maybe try updating discord link in your social settings",
                           "User does not exist on skyblock"]:
                await ctx.send(str(catalvl), hidden=True)  # ERROR
            else:
                cataclass = cataclass[0].upper()

                # Change Nickname
                await ctx.author.edit(nick=str(f"[{catalvl}] [{cataclass}] {ign}"))
                await ctx.author.add_roles(get(ctx.guild.roles, id=roleids["verified"]))

                roles = await getRoles(catalvl, catasecrets, ign)

                if roles == None:
                    await ctx.send("API is down so cannot update roles, please try again later", hidden=True)
                else:
                    for x in roles:
                        if x == "Livid":
                            livid = get(ctx.guild.roles, id=roleids["livid"])
                            await ctx.author.add_roles(livid)
                        elif x == "Sadan":
                            sadan = get(ctx.guild.roles, id=roleids["sadan"])
                            await ctx.author.add_roles(sadan)
                        elif x == "Necron":
                            necron = get(ctx.guild.roles, id=roleids["necron"])
                            await ctx.author.add_roles(necron)
                        elif x == "Kyrios Champ":
                            kyrios_champ = get(ctx.guild.roles, id=roleids["kchamp"])
                            await ctx.author.add_roles(kyrios_champ)

                await ctx.send("DONE", hidden=True)
        else:
            await ctx.send("This minecraft is not connected to your current discord profile, make sure it is updated",
                           hidden=True)
    else:
        await ctx.send(discerror, hidden=True)


perms = {
    802308200506458132: [
        create_permission(901798424129716244, SlashCommandPermissionType.ROLE, True),
        create_permission(802313686554247229, SlashCommandPermissionType.ROLE, True)
    ]
}


@client.event
async def on_component(ctx: ComponentContext):
    # you may want to filter or change behaviour based on custom_id or message
    await ctx.channel.send("You pressed a button!")


client.run(environ.get("TOKEN"))
