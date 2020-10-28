import json
import urllib.request
import urllib.parse
import pafy

import fHDHR.tools


class OriginService():

    def __init__(self, settings):
        self.config = settings

        self.web = fHDHR.tools.WebReq()

        self.video_reference = {}

    def get_status_dict(self):
        ret_status_dict = {}
        return ret_status_dict

    def get_channels(self):

        conf_channel_list = self.config.dict['origin']["streams"]
        if isinstance(conf_channel_list, str):
            conf_channel_list = [conf_channel_list]

        channel_list = []
        for station in conf_channel_list:

            station_item = {}
            if station in list(self.config.dict.keys()):
                for channel_key in ["number", "name", "videoid"]:
                    if channel_key in list(self.config.dict[station]):
                        station_item[channel_key] = str(self.config.dict[station][channel_key])

            if station_item["videoid"] not in list(self.video_reference.keys()):
                self.video_reference[station_item["videoid"]] = {}

            video_api_url = ('https://www.googleapis.com/youtube/v3/videos?id=%s&part=snippet,contentDetails&key=%s' %
                             (station_item["videoid"], str(self.config.dict["origin"]["api_key"])))
            video_response = urllib.request.urlopen(video_api_url)
            video_data = json.load(video_response)

            self.video_reference[station_item["videoid"]]["title"] = video_data["items"][0]["snippet"]["title"]
            self.video_reference[station_item["videoid"]]["description"] = video_data["items"][0]["snippet"]["description"]
            self.video_reference[station_item["videoid"]]["channel_id"] = video_data["items"][0]["snippet"]["channelId"]
            self.video_reference[station_item["videoid"]]["channel_name"] = video_data["items"][0]["snippet"]["channelTitle"]

            clean_station_item = {
                                    "name": station_item["name"],
                                    "callsign": self.video_reference[station_item["videoid"]]["channel_name"],
                                    "id": station_item["videoid"],
                                    }
            if "number" in list(station_item.keys()):
                clean_station_item["number"] = float(station_item["number"])

            channel_list.append(clean_station_item)

        return channel_list

    def get_channel_stream(self, chandict, allchandict):
        caching = True
        streamlist = []
        streamdict = {}
        pafyobj = pafy.new(chandict["id"])
        streamdict = {"number": chandict["number"], "stream_url": str(pafyobj.getbest().url)}
        streamlist.append(streamdict)
        return streamlist, caching
