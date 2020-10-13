import pafy
import datetime
import urllib.request
import json

import fHDHR.tools


class fHDHRservice():
    def __init__(self, settings):
        self.config = settings

        self.web = fHDHR.tools.WebReq()

        self.video_records = {}

    def login(self):
        return True

    def check_service_dict(self, videoid):
        if videoid not in list(self.video_records.keys()):

            video_api_url = ('https://www.googleapis.com/youtube/v3/videos?id=%s&part=snippet,contentDetails&key=%s' %
                             (videoid, str(self.config.dict["origin"]["api_key"])))
            video_response = urllib.request.urlopen(video_api_url)
            video_data = json.load(video_response)

            self.video_records[videoid] = {
                                            "stream": None,
                                            "title": video_data["items"][0]["snippet"]["title"],
                                            "description": video_data["items"][0]["snippet"]["description"],
                                            "channel_id": video_data["items"][0]["snippet"]["channelId"],
                                            "channel_name": video_data["items"][0]["snippet"]["channelTitle"],
                                            }
            channel_api_url = ('https://www.googleapis.com/youtube/v3/channels?id=%s&part=snippet,contentDetails&key=%s' %
                               (self.video_records[videoid]["channel_id"], str(self.config.dict["origin"]["api_key"])))
            channel_response = urllib.request.urlopen(channel_api_url)
            channel_data = json.load(channel_response)

            self.video_records[videoid]["channel_thumbnail"] = channel_data["items"][0]["snippet"]["thumbnails"]["high"]["url"]

        return self.video_records[videoid]

    def stations_from_config(self):
        channel_list = self.config.dict['origin']["streams"]
        if isinstance(channel_list, str):
            channel_list = [channel_list]
        station_list = []
        for station in channel_list:
            station_item = {}
            if station in list(self.config.dict.keys()):
                for channel_key in ["number", "name", "videoid"]:
                    if channel_key in list(self.config.dict[station]):
                        station_item[channel_key] = str(self.config.dict[station][channel_key])
            if "number" in list(station_item.keys()) and "name" in list(station_item.keys()) and "videoid" in list(station_item.keys()):
                self.check_service_dict(station_item["videoid"])
                clean_station_item = {
                                     "name": station_item["name"],
                                     "callsign": self.video_records[station_item["videoid"]]["channel_name"],
                                     "number": station_item["number"],
                                     "id": self.video_records[station_item["videoid"]]["channel_id"],
                                     }
                station_list.append(clean_station_item)
        return station_list

    def get_channels(self):
        channel_list = self.config.dict['origin']["streams"]
        if isinstance(channel_list, str):
            channel_list = [channel_list]
        station_list = []
        for station in channel_list:
            station_item = {}
            if station in list(self.config.dict.keys()):
                for channel_key in ["number", "name", "videoid"]:
                    if channel_key in list(self.config.dict[station]):
                        station_item[channel_key] = str(self.config.dict[station][channel_key])
            if "number" in list(station_item.keys()) and "name" in list(station_item.keys()) and "videoid" in list(station_item.keys()):
                self.check_service_dict(station_item["videoid"])
                clean_station_item = {
                                     "name": station_item["name"],
                                     "callsign": self.video_records[station_item["videoid"]]["channel_name"],
                                     "number": station_item["number"],
                                     "id": station_item["videoid"],
                                     }
                station_list.append(clean_station_item)
        return station_list

    def get_channel_stream(self, chandict, allchandict):
        caching = True
        streamlist = []
        streamdict = {}
        pafyobj = pafy.new(chandict["id"])
        streamdict = {"number": chandict["number"], "stream_url": str(pafyobj.getbest().url)}
        streamlist.append(streamdict)
        return streamlist, caching

    def get_channel_thumbnail(self, content_id):
        for c in self.get_channels():
            if c["id"] == content_id:
                self.check_service_dict(c["id"])
                return self.video_records[content_id]["channel_thumbnail"]

    def get_content_thumbnail(self, content_id):
        return ("https://i.ytimg.com/vi/%s/maxresdefault.jpg" % (str(content_id)))

    def update_epg(self):

        programguide = {}

        timestamps = []
        todaydate = datetime.date.today()
        for x in range(0, 6):
            xdate = todaydate + datetime.timedelta(days=x)
            xtdate = xdate + datetime.timedelta(days=1)

            for hour in range(0, 24):
                time_start = datetime.datetime.combine(xdate, datetime.time(hour, 0))
                if hour + 1 < 24:
                    time_end = datetime.datetime.combine(xdate, datetime.time(hour + 1, 0))
                else:
                    time_end = datetime.datetime.combine(xtdate, datetime.time(0, 0))
                timestampdict = {
                                "time_start": str(time_start.strftime('%Y%m%d%H%M%S')) + " +0000",
                                "time_end": str(time_end.strftime('%Y%m%d%H%M%S')) + " +0000",
                                }
                timestamps.append(timestampdict)

        for c in self.get_channels():

            self.check_service_dict(c["id"])

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
                                    "title": self.video_records[c["id"]]["title"],
                                    "sub-title": "Unavailable",
                                    "description": self.video_records[c["id"]]["description"],
                                    "rating": "N/A",
                                    "episodetitle": None,
                                    "releaseyear": None,
                                    "genres": [],
                                    "seasonnumber": None,
                                    "episodenumber": None,
                                    "isnew": False,
                                    "id": timestamp['time_start'],
                                    }

                programguide[str(c["number"])]["listing"].append(clean_prog_dict)

        return programguide
