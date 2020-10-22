import datetime
import json
import urllib.request

import fHDHR.tools


class originEPG():

    def __init__(self, settings, channels):
        self.config = settings
        self.channels = channels

        self.web = fHDHR.tools.WebReq()

        self.base_api_url = 'https://api.pluto.tv'
        self.web_cache_dir = self.config.dict["filedir"]["epg_cache"]["origin"]["web_cache"]

    def xmltimestamp_pluto(self, inputtime):
        xmltime = inputtime.replace('Z', '+00:00')
        xmltime = datetime.datetime.fromisoformat(xmltime)
        xmltime = xmltime.strftime('%Y%m%d%H%M%S %z')
        return xmltime

    def duration_pluto_minutes(self, induration):
        return ((int(induration))/1000/60)

    def get_channel_thumbnail(self, videoid):
        if "channel_thumbnail" not in list(self.channels.origin.video_reference[videoid].keys()):

            channel_id = self.channels.origin.video_reference[videoid]["channel_id"]
            channel_api_url = ('https://www.googleapis.com/youtube/v3/channels?id=%s&part=snippet,contentDetails&key=%s' %
                               (channel_id, str(self.config.dict["origin"]["api_key"])))
            channel_response = urllib.request.urlopen(channel_api_url)
            channel_data = json.load(channel_response)

            self.channels.origin.video_reference[videoid]["channel_thumbnail"] = channel_data["items"][0]["snippet"]["thumbnails"]["high"]["url"]

        return self.channels.origin.video_reference[videoid]["channel_thumbnail"]

    def get_content_thumbnail(self, content_id):
        return ("https://i.ytimg.com/vi/%s/maxresdefault.jpg" % (str(content_id)))

    def update_epg(self):
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

        for c in self.channels.get_channels():

            if str(c["number"]) not in list(programguide.keys()):
                programguide[str(c["number"])] = {
                                                    "callsign": c["callsign"] or c["name"],
                                                    "name": c["name"],
                                                    "number": c["number"],
                                                    "id": c["id"],
                                                    "thumbnail": self.get_channel_thumbnail(c["id"]),
                                                    "listing": [],
                                                    }

            for timestamp in timestamps:
                clean_prog_dict = {
                                    "time_start": timestamp['time_start'],
                                    "time_end": timestamp['time_end'],
                                    "duration_minutes": 60,
                                    "thumbnail": self.get_content_thumbnail(c["id"]),
                                    "title": self.channels.origin.video_reference[c["id"]]["title"],
                                    "sub-title": "Unavailable",
                                    "description": self.channels.origin.video_reference[c["id"]]["description"],
                                    "rating": "N/A",
                                    "episodetitle": None,
                                    "releaseyear": None,
                                    "genres": [],
                                    "seasonnumber": None,
                                    "episodenumber": None,
                                    "isnew": False,
                                    "id": str(c["id"]) + "_" + str(timestamp['time_start']).split(" ")[0],
                                    }

                programguide[str(c["number"])]["listing"].append(clean_prog_dict)

        return programguide
