"""
HABSIM
=====

Exports classes Segment, Profile, ControlledProfile, Prediction, Trajectory, StaticTarget, and MovingTarget, and methods in util and ioutil.

A note about timestamps: this package manipulates UNIX timestamps extracted from user-supplied datetime objects. When you create a datetime object,
its timestamp() method returns as if the datetime is in the local time zone of your machine --- this package expects such behavior. You should not worry about
converting your datetime object to UTC time --- doing so may cause unexpected behavior.
"""

from . import util
from .classes import *
from . import ioutil