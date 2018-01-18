# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 09:58:14 2018

@author: Joe
"""

import datetime

DAY_TYPES = ["weekday", "saturday", "holiday"]
DAY_INT = {0:'holiday', 1: "weekday", 2: "weekday", 3: "weekday", 
           4: "weekday", 5: "weekday", 6: "saturday"}

WEEKDAYS_SCHED = "weekdays.txt"
SATURDAYS_SCHED = "saturdays.txt"
HOLIDAYS_SCHED = "holidays.txt"

ALL_SCHED = [WEEKDAYS_SCHED, SATURDAYS_SCHED, HOLIDAYS_SCHED]

def simplifyTime(time):
    """
    This takes either a tuple of (hour,minute) or an int of minutes after midnight
    Returns an int of minutes after midnight
    """
    if type(time) == tuple:
        time = 60 * time[0] + time[1]
    assert type(time) == int
    return time

class Departure():
    def __init__(self, hour, minute, dest):
        self.hour = hour
        self.minute = minute
        self.dest = dest
        
    def minFromMidnight(self):
        """
        Returns the total minutes from midnight
        """
        return (self.hour * 60 + self.minute)
    
    def getHour(self):
        return self.hour
    
    def getMinute(self):
        return self.minute

    def getDest(self):
        return self.dest
    
    def __str__(self):
        return ("%d:%d %s" % (self.hour, self.minute, self.dest))
    
class Schedule():
    def __init__(self, departures = [], title = 'Schedule'):
        assert type(departures) is list
        self.departures = departures
        self.sortDep()
        self.title = title
        
    def addDep(self, dep):
        self.departures.append(dep)
        self.sortDep()
    
    def sortDep(self):
        self.departures.sort(key=Departure.minFromMidnight)
        
    def getTitle(self):
        return self.title
    
    def getDests(self):
        """
        Returns a list of unique destinations used by departures
        """
        out = []
        for departure in self.departures:
            if departure.getDest() not in out:
                out.append(departure.getDest())
        return out
    
    def __str__(self):
        out = self.title + "\n"
        for departure in self.departures:
            out += str(departure) + "  "
        return out
    
    def filteredSched(self, dests = []):
        """
        Returns a new Schedule of departures containing only the given destinations
        """
        if type(dests) is not list:
            dests = [dests,]
        out = []
        for departure in self.departures:
            if departure.getDest() in dests:
                out.append(departure)
        return Schedule(out, self.title)
    
    def nextDep(self, time, dests = None):
        """
        Returns the next departure after a given time
        
        Time can be either a tuple of (hour, minute) OR an int of minutes from midnight
        
        Using a linear search right now, 'should' be a bisection search
        """
        time = simplifyTime(time)
        
        if dests:
            return self.filteredSched(dests).nextDep(time)
        else:

            for departure in self.departures:
                if departure.minFromMidnight() > time:
                    return departure
            return None
    
    def niceSchedule(self):
        """
        Returns a nice looking string for schedule with just one line for all departures in an hour
        """
        out = ""
        currentHour = -1
        currentLine = self.title
        for dep in self.departures:
            if not dep.getHour() == currentHour:
                currentHour = dep.getHour()
                out += currentLine + "\n"
                currentLine = "%d: " % dep.getHour()
            currentLine += "%d %s   " % (dep.getMinute(), dep.getDest())
        out += currentLine
        return out
    
    
    def loadSched(fileLoc):
        """
        Takes the location of a text file and returns a new schedule object from its contents
        Returns None if there is a problem
        """
        
        try:
            file = open (fileLoc, "r", encoding = "utf8")
        except:
            print("Failed to open file")
        
        fileLines = []
        for line in file:
            fileLines.append(line[:-1].strip()) #Get rid of the \n and whitespace
        fileLines = [l for l in fileLines if l != ''] #Get rid of those '' lines
        title = fileLines[0]
        fileLines = fileLines[1:] #First line is the title
        
        currentHour = -1
        linesIter = iter(fileLines)
        departures = []
        for line in linesIter:
            if line.isdigit():
                currentHour = int(line)
                #print(currentHour)
            else:
                departures.append(Departure(currentHour,int(next(linesIter)), line[-1]))
        
        newSched = Schedule(departures, title)    
        return newSched
        

class TrainCatcher():
    """
    walkTime is the amount of time needed to get to the trainstation
    wiggle is the amount of extra time needed for catching the train to be safe
    
    if the diff between the current time and the next train is > walkTime + wiggle, just return the next train
    if the diff is > walkTime, but < walkTime + wiggle, give an alert to leave immediately, plus list the next safe train
    if the diff is < walkTime, give the following train instead
    """
    def __init__(self, walkTime = 0, defaultSchedule = None, wiggle = 0, goodDests = None):
        self.walkTime = walkTime
        self.schedules = {}
        self.wiggle = wiggle
        for dayInt in DAY_INT:
            self.schedules[dayInt] = defaultSchedule
        self.goodDests = goodDests
    
    def setSchedule(self, dayTypes, schedule):
        """
        dayType should be an int or list of ints for the day of the week
        
        schedule may be either a Schedule object, or a str for a text file to build a new sched from
        """
        if type(schedule) == str:
            schedule = Schedule.loadSched(schedule)
        assert type(schedule) == Schedule
        
        if type(dayTypes) is not list:
            dayTypes = [dayTypes,]
        for dayType in dayTypes:
            self.schedules[dayType] = schedule
            
    def getNowTime():
        """
        Returns a tuple of (minutes-from-midnight, weekday)
        """
        nowDT = datetime.datetime.now()
        return (60 * nowDT.hour + nowDT.minute, nowDT.weekday() )
    
    """
    def getDayType():
        dayInt = datetime.datetime.today().weekday()
        if dayInt == 0:
            return "holiday"
        elif dayInt == 6:
            return "saturday"
        else:
            return "weekday"
    """
        
    def getNextTrain(self, time = None, walkTime = 0, day = None, dests = None):
        """
        Returns the next catchable departure
        
        Time can be given as either a tuple(hour,minute) or an int for minutes from midnight
        If no time is specified, will use 
        """
        nowTup = None
        if time == None or day == None:
            nowTup = TrainCatcher.getNowTime() # Should only call datetime if needed
        
        if time == None:
            time = nowTup[0]
        else:
            time = simplifyTime(time)
            
        time += walkTime 
            
        if day == None:
            day = nowTup[1]
        
        
        todaySchedule = self.schedules[day]

        return todaySchedule.nextDep(time, dests)
    
    def setGoodDests(self, goodDests):
        """
        Not all departures are necessarily good trains to catch
        This sets which destinations constitute good trains
        Setting to None will mean all trains are good
        """
        self.goodDests = goodDests
    
    def getNextGood(self):
        """
        This returns the next good, catchable train
        """
        return self.getNextTrain(walkTime = self.walkTime, dests = self.goodDests)

    
    
        
        
        
        
