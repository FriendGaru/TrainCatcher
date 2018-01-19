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

tc = TrainCatcher(walkTime = 6)
tc.setSchedule(0, HOLIDAYS_SCHED)
tc.setSchedule([1,2,3,4,5], WEEKDAYS_SCHED)
tc.setSchedule(6, SATURDAYS_SCHED)
tc.setGoodDests(['浦', '川', '宮', '赤', '池'])

print(tc.getNextGood())
input()
