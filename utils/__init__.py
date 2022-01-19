import requests
from os import environ
from time import sleep
import threading

def getnickstags(stats):
    stats = stats.json()["data"]

    if stats["dungeons"]:
        cata = int(stats["dungeons"]["types"]["catacombs"]["level"])
        cataclass = ((stats["dungeons"]["selected_class"])[0]).upper()
    else:
        # no doogan
        cata, cataclass = 0, "W"

    name = stats["username"]
    tag = stats["discord_tag"] if "discord_tag" in stats.keys(
    ) else "No discord tag"

    return [f"[{cata}] [{cataclass}] {name}", tag]



def get_nicks():
    key = "93328f1e-e618-4041-91a4-9477393b36d0"

    nicks = []

    guild = requests.get(
        "https://api.slothpixel.me/api/guilds/id/600b55008ea8c9e004b042cb")
    if guild.status_code == 200:
        guild = guild.json()["members"]
    else:
        print("status code error")

    for x in guild:
        uuid = x["uuid"]

        stats = requests.get(
            f"https://hypixel-skyblock-facade.kunaldandekar.repl.co/v1/profiles/{uuid}/cata?key={key}")

        if stats.status_code == 200:
            nicks.append(getnickstags(stats))
        elif stats.status_code == 429:
            print("Cooling down the quantum thermostatic generator")
            sleep(10)
            print("Cooldown ended (lol)")
            stats_retry = requests.get(
                f"https://hypixel-skyblock-facade.kunaldandekar.repl.co/v1/profiles/{uuid}/cata?key={key}")
            nicks.append(getnickstags(stats_retry))
        else:
            print("Status error with stats api", stats.status_code)

    print(len(nicks))
    return nicks


def t_get_nicks():
    x = threading.Thread(target=get_nicks)
    x.start()
    print(x.is_alive)