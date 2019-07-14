import sys
sys.path.append("/mnt/e/git")
from datetime import datetime
import habsim as hs

hs.util.checkServer()
'''
asc = hs.Segment(5, stopalt=29000)
equil = hs.Segment(0, dur=3)
desc = hs.Segment(-10, stopalt=0)
floating = hs.Segment(0, dur=30, coeff=1)
'''
hollister = hs.LaunchSite((36.8492, -121.432))

profile = hs.ControlledProfile(100, 5)
profile.initialize(2000, 5000, 30000, seed=[79.0, 12245.206040319974])


pred = hs.Prediction(profile=profile,launchsite=hollister, step=240)

for i in range(10):
    pred.run(model=1)
    closest = hs.util.optimize_step(pred, hs.StaticTarget(30.7, -92.7), 50)
    print(profile)
    print(closest)

plt = hs.ioutil.webplot()
plt.origin(*hollister.coords)
plt.add(pred.split(), hs.ioutil.RandomColorGenerator())
plt.marker(30.7, -92.7)
plt.save("test.html") 

print(pred.trajectory.startpoint())
print(pred.trajectory.endpoint())