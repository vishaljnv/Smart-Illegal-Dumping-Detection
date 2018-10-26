import datetime

def get_configured_camera_list():
    return [{"model":"Geo Vision GV-EDR4700-0F",
             "type":"Action camera - 1440p",
             "image_format":"JPEG",
             "installation_position":"front-left"}]

def time_stamp():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def get_my_current_location():
    return "here, there"
