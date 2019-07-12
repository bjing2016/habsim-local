# habsim_client
Objected oriented interface and accession utilities to HABSIM

# Planned structure

class Prediction

class Trajectory

class Profile

class Params

profile.load()




pred = hs.predict(profile, model=1, interval=60)
pred.path()
pred.paths()

pred.run()


Prediction
    Path
        List of time, lat, lon, alt
    Winds
        List of winds
    Profile
    Interval
    Model run
    Model number

    .path() returns path
    .paths() returns pathlist by profile


Class trajectory. Methods to add segments, modify segments, set launch time.

Main predict method, passing in trajectory.

io methods for saving trajectories, viewing trajectories, outputting them as htmls
