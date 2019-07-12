import datetime
import util


'''
A single instance of a profile and its associated trajectory.

Users may create Prediction objects by passing it a profile
and then run the prediction, which calls the HABSIM server.
'''
class Prediction:
    '''
    Prediction objects keep track of their associated profile,
    the model number (1-20) they are based on,
    a launchtime, a launchsite, and a simulation step size in seconds.
    '''
    def __init__(self, profile=None, model=None, launchtime=None, launchsite=None, step=240):
        self.trajectory = Trajectory()
        self.model = model
        self.profile = profile
        self.launchtime = datetime.datetime.now() if not launchtime else launchtime
        self.launchsite = launchsite
        self.step = step

    '''
    Set new launch sites using this method, not by modifying the field.
    This is because the profile needs to be updated with new elevation information.
    '''
    def setLaunchSite(self, launchsite):
        self.launchsite = launchsite
        if self.profile is not None:
            self.profile.setLaunchAlt(launchsite.elev)

    '''
    If no parameters are passed in, looks in instance fields.
    '''
    def run(self, model=None, launchtime=None, launchsite=None, step=None):
        if step != None:
            self.step = step
        if launchtime != None:
            self.launchtime = launchtime
        if launchsite != None:
            self.launchsite = launchsite
        if model != None:
            self.model = model
        if self.profile == None:
            raise Exception("Profile not specified.")
        if self.launchsite == None:
            raise Exception("Launchsite not specified.")
        if self.model < 1 or self.model > 20:
            raise Exception("Model not specified or invalid.")
        self.profile.setLaunchAlt(self.launchsite.elev)


        time = self.launchtime.timestamp()
        lat, lon = self.launchsite.coords
        rates, durs, coeffs = self.profile.segmentList()
        __, alts = self.profile.waypoints()
        
        for i in range(len(rates)):
            self.trajectory.append(util.predict(time, lat, lon, alts[i], coeffs[i], self.model, rates[i], durs[i], self.step))
            time, lat, lon, __, __, __ = self.trajectory.endpoint()
            

            # Warning: controlled profile interval is not multiple of simulation time step
'''
A LaunchSite keeps track of its coordinates and elevation.
The elevation is ground elevation by default,
but may be specified to be higher.
'''
class LaunchSite:
    def __init__(self, coords, elev=None, name=None):
        self.name = name
        self.coords = coords
        self.elev = elev
        if self.elev == None:
            self.elev = util.getElev(self.coords)
        elif not util.checkElev(self):
            raise Exception("Launch site cannot be underground.")


class Trajectory:
    def __init__(self):
        self.data = list()

    def append(self, new):
        self.data = self.data[:-1] + new

    def endpoint(self):
        return self.data[-1]

    def startpoint(self):
        return self.data[0]

    def duration(self):
        return (self.endpoint()[0] - self.startpoint()[0]) / 3600

class ControlledProfile:
    def __init__(self, dur=None, interval=None, target=None, launchsite=None):
        pass
    
    def waypoints(self):
        pass
    
    def setTarget(self, target):
        pass

    
    


'''
A Profile object keeps track of a full flight profile for prediction.
It is not meant to be optimized --- use ControlledProfile instead.

A Profile consists of segments of a flight, which can be ascent, descent,
equilibration, or floating (marine anchor).
'''
class Profile:
    def __init__(self, segments=None, name=None, launchalt=None):
        self.segments = list()
        if segments != None:
            for i in range(len(segments)):
                self.append(segments[i])
        self.name = name
        self.launchalt = launchalt
        if self.launchalt != None:
            self.setLaunchAlt(launchalt)

    '''
    When you set the launch altitude, the information is used to populate
    altitude waypoints for each segment, propogating forward in time.
    '''
    def setLaunchAlt(self, alt):
        self.launchalt = alt
        curralt = alt
        for i in range(len(self)):
            if self[i].type == "alt":
                self[i].dur = (self[i].stopalt - curralt)/self[i].rate/3600
                if self[i].dur < 0:
                    raise Exception("Profile inconsistency: altitude changes in opposite direction of movement.")
                return
            else:
                self[i].stopalt = curralt + self[i].dur * 3600 * self[i].rate
                curralt = self[i].stopalt    


    '''
    Runs a few checks are run to make sure the profile remains self-consistent.
    '''
    def append(self, segment):
        if len(self) > 0 and self[-1].stopalt != None:
                lastalt = self[-1].stopalt
                if segment.type == "alt":
                    if segment.stopalt != lastalt and segment.rate == 0:
                        raise Exception("Profile inconsistency: nonzero altitude change while equilibrated.")
                    segment.dur = (segment.stopalt - lastalt) / segment.rate / 3600
                    if segment.dur < 0:
                        raise Exception("Profile inconsistency: altitude changes in opposite direction of movement.")
                if segment.type == "dur":
                    segment.stopalt = lastalt + (segment.dur * 3600 * segment.rate)
                
        if segment.stopalt != None:
            if segment.stopalt < 0:
                raise Exception("Profile inconsistency: altitude is negative.")
            if segment.stopalt > 32000:
                print("Warning: model inaccurate above 32km.")

        self.segments.append(segment)


    '''
    A pair of lists [hours, altitudes] specifying the profile.
    '''
    def waypoints(self):
        if self.launchalt == None:
            raise Exception("Full altitude profile not specified.")
        hours = [0]
        for i in range(len(self)):
            hours.append(hours[-1] + self[i].dur)
        altitudes = [self.launchalt] + [self[i].stopalt for i in range(len(self))]
        return hours, altitudes

    def segmentList(self):
        if self.launchalt == None:
            raise Exception("Full altitude profile not specified.")
        return [self[i].rate for i in range(len(self))], [self[i].dur for i in range(len(self))], [self[i].coeff for i in range(len(self))]
        

    def __len__(self):
        return len(self.segments)

    def __getitem__(self, key):
        return self.segments[key]

    def __str__(self):
        res = "Launch alt:{}\n".format(self.launchalt)
        for i in range(len(self)):
            res += str(self[i]) + "\n"
        return res[:-1]

'''
A single part of a profile with a constant ascent/descent rate.
Segments may be of type "dur" (specified duration) or type "alt" (specified stopping altitude).

Segments default to motion coefficient 1, which can be modified in the case of
marine anchor segments.
'''
class Segment:
    def __init__(self, rate, dur=None, stopalt=None, name=None, coeff=1):
        if stopalt == None and dur == None:
            raise Exception("A duration or a stopping altitude must be specified.")
        if stopalt != None and dur != None:
            raise Exception("Duration and stopping altitude both specified.")
        if dur != None and dur < 0:
            raise Exception("Segment cannot have negative duration.")
        self.rate = rate
        self.type = "dur" if dur else "alt"
        self.dur = dur
        self.stopalt = stopalt
        self.name = name
        self.coeff = coeff
    def __str__(self):
        if self.type == "alt":
            return '{}, Rate:{}, Type:alt, Stopalt:{}, Coeff:{} (Dur:{})'.format(self.name, self.rate, self.stopalt, self.coeff, self.dur)
        else:
            return '{}, Rate:{}, Type:dur, Dur:{}, Coeff:{} (Stopalt:{})'.format(self.name, self.rate, self.dur, self.coeff, self.stopalt)