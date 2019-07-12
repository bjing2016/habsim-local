import requests
import json
import math
import urllib

URL = "http://predict.stanfordssi.org"
EARTH_RADIUS = 6371.0

def checkElev(launchsite):
    return launchsite.elev > getElev(launchsite.coords)

def getElev(coords):
    lat, lon = coords
    elev = requests.get(URL + "/elev?lat={}&lon={}".format(lat, lon)).text
    return float(elev)

def whichgefs():
    return requests.get(url=URL+"/which").text
    
def checkServer():
    which = whichgefs()
    if which == "Unavailable":        
        print("Server live. Wind data temporarily unavailable.")
    else:
        print("Server live with GEFS run " + which)
        status = requests.get(URL+"/status").text
        if status != "Ready":
            print(status)

def predict(timestamp, lat, lon, alt, drift_coeff, model, rate, dur, step):
    URL = 'https://predict.stanfordssi.org/singlepredict?&timestamp={}&lat={}&lon={}&alt={}&coeff={}&dur={}&step={}&model={}&rate={}'\
        .format(timestamp, lat, lon, alt, drift_coeff, dur, step, model, rate)
    return json.load(urllib.request.urlopen(URL))

def windprofile(datetime, lat, lon):
    pass


def angular_to_lin_distance(lat1, lat2, lon1, lon2): 
    v = math.radians(lat2 - lat1) * EARTH_RADIUS
    u = math.radians(lon2 - lon1) * EARTH_RADIUS * math.cos(math.radians(lat1))
    return u, v
