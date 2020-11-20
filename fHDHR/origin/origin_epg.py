import datetime
import json
import urllib.request


class OriginEPG():

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def get_channel_thumbnail(self, videoid, fhdhr_channels):
        if "channel_thumbnail" not in list(fhdhr_channels.origin.video_reference[videoid].keys()):

            channel_id = fhdhr_channels.origin.video_reference[videoid]["channel_id"]
            channel_api_url = ('https://www.googleapis.com/youtube/v3/channels?id=%s&part=snippet,contentDetails&key=%s' %
                               (channel_id, str(self.config.dict["origin"]["api_key"])))
            channel_response = urllib.request.urlopen(channel_api_url)
            channel_data = json.load(channel_response)

            fhdhr_channels.origin.video_reference[videoid]["channel_thumbnail"] = channel_data["items"][0]["snippet"]["thumbnails"]["high"]["url"]

        return fhdhr_channels.origin.video_reference[videoid]["channel_thumbnail"]

    def get_content_thumbnail(self, content_id):
        return ("https://i.ytimg.com/vi/%s/maxresdefault.jpg" % (str(content_id)))

    def update_epg(self, fhdhr_channels):
        programguide = {}

        timestamps = []
        xtimestart = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        xtimeend = xtimestart + datetime.timedelta(days=6)
        xtime = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        while xtime <= xtimeend:
            timestampdict = {
                            "time_start": str(xtime.strftime('%Y%m%d%H%M%S')) + " +0000",
                            "time_end": str((xtime + datetime.timedelta(hours=1)).strftime('%Y%m%d%H%M%S')) + " +0000",
                            }
            xtime = xtime + datetime.timedelta(hours=1)
            timestamps.append(timestampdict)

        for c in fhdhr_channels.get_channels():

            if str(c["number"]) not in list(programguide.keys()):
                programguide[str(c["number"])] = {
                                                    "callsign": c["callsign"] or c["name"],
                                                    "name": c["name"],
                                                    "number": c["number"],
                                                    "id": c["origin_id"],
                                                    "thumbnail": self.get_channel_thumbnail(c["origin_id"], fhdhr_channels),
                                                    "listing": [],
                                                    }

            for timestamp in timestamps:
                clean_prog_dict = {
                                    "time_start": timestamp['time_start'],
                                    "time_end": timestamp['time_end'],
                                    "duration_minutes": 60,
                                    "thumbnail": self.get_content_thumbnail(c["origin_id"]),
                                    "title": fhdhr_channels.origin.video_reference[c["origin_id"]]["title"],
                                    "sub-title": "Unavailable",
                                    "description": fhdhr_channels.origin.video_reference[c["origin_id"]]["description"],
                                    "rating": "N/A",
                                    "episodetitle": None,
                                    "releaseyear": None,
                                    "genres": [],
                                    "seasonnumber": None,
                                    "episodenumber": None,
                                    "isnew": False,
                                    "id": str(c["origin_id"]) + "_" + str(timestamp['time_start']).split(" ")[0],
                                    }

                programguide[str(c["number"])]["listing"].append(clean_prog_dict)

        return programguide
