# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 14:49:40 2018

@author: Joe
"""

from traincatcher import *

tc = TrainCatcher(walkTime = 6)
tc.setSchedule(0, HOLIDAYS_SCHED)
tc.setSchedule([1,2,3,4,5], WEEKDAYS_SCHED)
tc.setSchedule(6, SATURDAYS_SCHED)
tc.setGoodDests(['浦', '川', '宮', '赤', '池'])

print(tc.getNextGood())
input()