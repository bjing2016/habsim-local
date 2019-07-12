import sys
sys.path.append("/mnt/e/git")

import habsim_client as hs


hs.util.checkServer()
asc = hs.Segment(5, stopalt=29000)
equil = hs.Segment(0, dur=3)
desc = hs.Segment(-2, stopalt=0)
floating = hs.Segment(0, dur=30, coeff=0.5)

profile = hs.Profile([asc, equil, desc, floating])

pred = hs.Prediction(profile=profile)
hollister = hs.LaunchSite((36.8492, -121.432))

pred.run(launchsite=hollister, model=1, step=60)
print(pred.profile)
print(pred.profile.waypoints())
print(pred.profile.segmentList())
print(pred.trajectory.duration())