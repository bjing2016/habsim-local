import requests
import json
import math
import urllib
import os

URL = "http://predict.stanfordssi.org"
EARTH_RADIUS = 6371.0

def checkElev(launchsite):
    return launchsite.elev > getElev(launchsite.coords)

def getElev(coords):
    lat, lon = coords
    elev = requests.get(URL + f"/elev?lat={lat}&lon={lon}").text
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

def angular_to_lin_distance(lat1, lat2, lon1, lon2): 
    v = math.radians(lat2 - lat1) * EARTH_RADIUS
    u = math.radians(lon2 - lon1) * EARTH_RADIUS * math.cos(math.radians(lat1))
    return u, v

'''
Implements a modified binary search algorithm to find the closest point between a trajectory
and a target. First, points are taken from the trajectory at a user-defined interval. Then the search range
is [start, end]. If start is closer, the new range is [start, start + division * (end-start)], and vice versa.
The search continues until a single point is reached.

Returns the point, distance, and bearing
'''
def closestPoint(traj, target, interval=1, division=0.75):
    traj = traj[::interval]
    if len(traj) == 1:
        return traj[0], haversine(*traj[0][1:3], *target.location(traj[0][0])), bearing(*traj[0][1:3], *target.location(traj[0][0]))
    slat, slon = traj[0][1:3]
    elat, elon = traj[-1][1:3]
    stlat, stlon = target.location(traj[0][0])
    etlat, etlon = target.location(traj[-1][0])

    start_dist = haversine(slat, slon, stlat, stlon)
    end_dist = haversine(elat, elon, etlat, etlon)

    if start_dist < end_dist:
        end = math.floor(len(traj) * division)
        return closestPoint(traj[:end], target, division=division)
    else:
        start = math.ceil(len(traj) * (1-division))
        return closestPoint(traj[start:], target, division=division)

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2-lat1
    dlon = lon2-lon1

    a = math.sin(dlat/2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return EARTH_RADIUS * c
    '''
    var φ1 = lat1.toRadians();
    var φ2 = lat2.toRadians(); 
    var Δφ = (lat2-lat1).toRadians();
    var Δλ = (lon2-lon1).toRadians();

    var a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
        Math.cos(φ1) * Math.cos(φ2) *
        Math.sin(Δλ/2) * Math.sin(Δλ/2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    var d = R * c;
    https://www.movable-type.co.uk/scripts/latlong.html
    '''

def bearing(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2-lon1

    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    return math.degrees(math.atan2(y, x))

    '''
    var y = Math.sin(λ2-λ1) * Math.cos(φ2);
    var x = Math.cos(φ1)*Math.sin(φ2) -
        Math.sin(φ1)*Math.cos(φ2)*Math.cos(λ2-λ1);
    var brng = Math.atan2(y, x).toDegrees();
    '''

def optimize_step(pred, target, alpha, decreasing_weights=False):
    closest, distance, bearing = closestPoint(pred.trajectory, target)
    vectoru = distance * math.sin(math.radians(bearing))
    vectorv = distance * math.cos(math.radians(bearing))

    prof = pred.profile
    steps_per_interval = int(prof.interval * 3600 / pred.step)
    for i in range(1, len(prof)):
        du, dv = pred.trajectory[i * steps_per_interval][-2:]
        prof[i] += alpha * (vectoru * du + vectorv * dv) * ((len(prof) - i) if decreasing_weights else 1)
    
    return closest, distance, bearing


    