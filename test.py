import sys
sys.path.append("/mnt/e/git")
from datetime import datetime
import habsim as hs

hs.util.checkServer()

asc = hs.Segment(5, stopalt=29000)
equil = hs.Segment(0, dur=3)
desc = hs.Segment(-10, stopalt=0)
floating = hs.Segment(0, dur=30, coeff=1)
hollister = hs.LaunchSite((36.8492, -121.432))

profile = hs.Profile([asc, equil, desc])
pred = hs.Prediction(profile=profile,launchsite=hollister, step=60, launchtime=datetime(2019,7,20))

plt = hs.ioutil.webplot()
plt.origin(*hollister.coords)
for i in range(1,5):
    plt.add(pred.run(model=i).split())
plt.save("test.html")
