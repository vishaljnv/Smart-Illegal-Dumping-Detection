import requests
import json
import base64
from utils import *

class HttpClient:

    def __init__(self, server_ip):
        self.headers = {'Content-type': 'application/json'}
        self.base_url = "http://" + server_ip
        self.station_id = None

    def is_server_up(self):
        url = self.base_url + "/test"
        data = {"data":"test request"}
        r = requests.post(url, data=json.dumps(data), headers=self.headers)
        if r.status_code != requests.status_codes.ok:
            return False

        return True

    def register_with_server(self):
        url = self.base_url + "/register"
        data = { "station_type": MY_STATION_TYPE,
                 "cameras": get_configured_camera_list(),
                 "registered_time": time_stamp(),
                 "description": "Hi there!" }

        r = requests.post(url, data=json.dumps(data), headers=self.headers)
        if r.status_code != requests.status_codes.ok:
            return False

        self.station_id = json.loads(r.content)["station_id"]
        return True

    def connect_to_server(self, location):
        url = self.base_url + "/connect"
        data = { "station_id": self.station_id,
                 "connection_time" : time_stamp(),
                 "location": location}

        r = requests.post(url, data=json.dumps(data), headers=self.headers)
        if r.status_code != requests.status_codes.ok:
            return False

        return True

    def send_detection_results(self, images, classifiers, location):
        url = self.base_url + "/alerting"
        data = { "station_id": self.station_id, "alerting_type":"IllegalDumpingAlert",
                 "classifier": classifiers,"alerting_time" : time_stamp() ,
                 "location": location,"description":"This is an alert from a truck at San Jose",
                 "images":[]}

        for image in images:
            with open(image,"rb") as image_file:
                encoded_string = "data:image/jpeg;base64," + base64.b64encode(image_file.read())
                data["images"].append(encoded_string)

        r = requests.post(url, data=json.dumps(data), headers=self.headers)
        if r.status_code != requests.status_codes.ok:
            return False

        return True
