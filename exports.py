import statics, json, datetime, aiofiles

async def simple_export(reports):
    steamids = []
    for reporter in reports._reporters.values():
        for report in reporter.reports:
            steamids += report.steamids
    steamids = set(map(lambda i: str(i), steamids))
    async with aiofiles.open(statics.ID_LIST_FILE, "w") as f:
        await f.write("\n".join(sorted(steamids)))

def steamid64_to_32(id: int) -> str:
    return f"[U:1:{id-statics.STEAMID64_OFFSET}]"

async def tfbd_export(reports):
    steamids = {}
    for reporter in reports._reporters.values():
        for report in reporter.reports:
            for sid in report.steamids:
                sid = steamid64_to_32(sid)
                if sid not in steamids:
                    steamids[sid] = []
                steamids[sid] += [report.message]

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    contents = {
         "$schema": "https://raw.githubusercontent.com/PazerOP/tf2_bot_detector/master/schemas/v3/playerlist.schema.json",
        "file_info": {
            "authors": [ "All contributors in the hackerpolice channel" ],
            "description": f"List of cheaters reported in the hackerpolice channel on the Vorobey discord server, last updated {now}",
            "title": f"vorobey-hackerpolice - {now}",
            "update_url": f"https://raw.githubusercontent.com/AveraFox/Tom/refs/heads/main/{statics.TFBD_LIST_NAME}"
        },
        "players": list(map(lambda s: {
            "attributes": ["cheater"],
            "steamid": s[0],
        }, steamids.items()))
    }

    async with aiofiles.open(statics.TFBD_LIST_NAME, "w") as f:
        await f.write(json.dumps(contents, indent=4))

async def export(reports):
    await simple_export(reports)
    await tfbd_export(reports)
