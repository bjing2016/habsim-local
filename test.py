import sys
sys.path.append("/mnt/e/git")

import habsim as hs

hs.util.checkServer()
asc = hs.Segment(5, stopalt=29000)
equil = hs.Segment(0, dur=3)
desc = hs.Segment(-0.5, stopalt=0)
floating = hs.Segment(0, dur=30, coeff=1)
hollister = hs.LaunchSite((36.8492, -121.432))
profile = hs.Profile([asc, equil, desc])
pred = hs.Prediction(profile=profile,launchsite=hollister, step=60)

plt = hs.ioutil.webplot()
plt.origin(*hollister.coords)
for i in range(1,5):
    plt.add(pred.run(model=i).split())
plt.save("test.html")