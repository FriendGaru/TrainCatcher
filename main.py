# -*- coding: utf-8 -*-
"""
This script is for my use catching a train at Tennozu Asle
"""

from traincatcher import *
import os

SCHED_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/'

WEEKDAYS_SCHED = SCHED_FOLDER + "weekdays.txt"
SATURDAYS_SCHED = SCHED_FOLDER + "saturdays.txt"
HOLIDAYS_SCHED = SCHED_FOLDER + "holidays.txt"

tc = TrainCatcher(walkTime = 6, wiggle = 3)
tc.setSchedule(6, HOLIDAYS_SCHED)
tc.setSchedule([0,1,2,3,4], WEEKDAYS_SCHED)
tc.setSchedule(5, SATURDAYS_SCHED)
tc.setGoodDests(['浦', '川', '宮', '赤', '池'])

lookup = tc.getLookup()
print(lookup)
#input()
