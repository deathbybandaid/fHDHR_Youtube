import os
import json
import datetime
import urllib.request


class proxyserviceFetcher():

    def __init__(self, config):

        self.config = config.config

        self.servicename = "fHDHR-Youtube"

        self.urls = {}
        self.url_assembler()

        self.video_records = {}

        self.epg_cache = None
        self.epg_cache_file = config.config["youtube"]["epg_cache"]
        self.epg_cache = self.epg_cache_open()

    def epg_cache_open(self):
        epg_cache = None
        if os.path.isfile(self.epg_cache_file):
            with open(self.epg_cache_file, 'r') as epgfile:
                epg_cache = json.load(epgfile)
        return epg_cache

    def check_youtube_dict(self, videoid):
        if videoid not in list(self.video_records.keys()):

            video_api_url = ('https://www.googleapis.com/youtube/v3/videos?id=%s&part=snippet,contentDetails&key=%s' %
                             (videoid, str(self.config["youtube"]["api_key"])))
            video_response = urllib.request.urlopen(video_api_url)
            video_data = json.load(video_response)

            self.video_records[videoid] = {
                                            "stream": "https://www.youtube.com/watch?v=" + videoid,
                                            "title": video_data["items"][0]["snippet"]["title"],
                                            "description": video_data["items"][0]["snippet"]["description"],
                                            "channel_id": video_data["items"][0]["snippet"]["channelId"],
                                            }
            channel_api_url = ('https://www.googleapis.com/youtube/v3/channels?id=%s&part=snippet,contentDetails&key=%s' %
                               (self.video_records[videoid]["channel_id"], str(self.config["youtube"]["api_key"])))
            channel_response = urllib.request.urlopen(channel_api_url)
            channel_data = json.load(channel_response)

            self.video_records[videoid]["channel_thumbnail"] = channel_data["items"][0]["snippet"]["thumbnails"]["high"]["url"]

        return self.video_records[videoid]

    def url_assembler(self):
        pass

    def get_channels(self):
        channel_list = self.config['youtube']["streams"].split(",")
        station_list = []
        for station in channel_list:
            station_item = {}
            if station in list(self.config.keys()):
                for channel_key in ["number", "name", "videoid"]:
                    if channel_key in list(self.config[station]):
                        station_item[channel_key] = str(self.config[station][channel_key])
            if "number" in list(station_item.keys()) and "name" in list(station_item.keys()) and "videoid" in list(station_item.keys()):
                station_list.append(station_item)
        return station_list

    def get_station_list(self, base_url):
        station_list = []

        for c in self.get_channels():
            if self.config["fakehdhr"]["stream_type"] == "ffmpeg":
                watchtype = "ffmpeg"
            else:
                watchtype = "direct"
            url = ('%s%s/watch?method=%s&channel=%s' %
                   ("http://",
                    base_url,
                    watchtype,
                    c['number']
                    ))
            station_list.append(
                                {
                                 'GuideNumber': str(c['number']),
                                 'GuideName': c['name'],
                                 'URL': url
                                })
        return station_list

    def get_station_total(self):
        total_channels = 1
        return total_channels

    def get_channel_streams(self):
        streamdict = {}
        for c in self.get_channels():
            self.check_youtube_dict(c["videoid"])
            streamdict[str(c["number"])] = self.video_records[c["videoid"]]["stream"]
        return streamdict

    def get_channel_thumbnail(self, content_id):
        for c in self.get_channels():
            if c["videoid"] == content_id:
                self.check_youtube_dict(c["videoid"])
                return self.video_records[content_id]["channel_thumbnail"]

    def get_content_thumbnail(self, content_id):
        return ("https://i.ytimg.com/vi/%s/maxresdefault.jpg" % (str(content_id)))

    def update_epg(self):
        print('Updating Youtube EPG cache file.')

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

            self.check_youtube_dict(c["videoid"])

            if str(c["number"]) not in list(programguide.keys()):
                programguide[str(c["number"])] = {}

            channel_thumb_path = self.get_channel_thumbnail(c["videoid"])
            programguide[str(c["number"])]["thumbnail"] = channel_thumb_path

            if "name" not in list(programguide[str(c["number"])].keys()):
                programguide[str(c["number"])]["name"] = c["name"]

            if "callsign" not in list(programguide[str(c["number"])].keys()):
                programguide[str(c["number"])]["callsign"] = c["name"]

            if "id" not in list(programguide[str(c["number"])].keys()):
                programguide[str(c["number"])]["id"] = c["videoid"]

            if "number" not in list(programguide[str(c["number"])].keys()):
                programguide[str(c["number"])]["number"] = c["number"]

            if "listing" not in list(programguide[str(c["number"])].keys()):
                programguide[str(c["number"])]["listing"] = []

            for timestamp in timestamps:
                clean_prog_dict = {}

                clean_prog_dict["time_start"] = timestamp['time_start']
                clean_prog_dict["time_end"] = timestamp['time_end']
                clean_prog_dict["duration_minutes"] = 60.0

                content_thumb = self.get_content_thumbnail(c["videoid"])
                clean_prog_dict["thumbnail"] = content_thumb

                clean_prog_dict["title"] = self.video_records[c["videoid"]]["title"]

                clean_prog_dict["genres"] = []

                clean_prog_dict["sub-title"] = "Unavailable"

                clean_prog_dict['releaseyear'] = ""
                clean_prog_dict["episodetitle"] = "Unavailable"

                clean_prog_dict["description"] = self.video_records[c["videoid"]]["description"]

                clean_prog_dict['rating'] = "N/A"

                programguide[str(c["number"])]["listing"].append(clean_prog_dict)

        self.epg_cache = programguide
        with open(self.epg_cache_file, 'w') as epgfile:
            epgfile.write(json.dumps(programguide, indent=4))
        print('Wrote updated Youtube EPG cache file.')
        return programguide
