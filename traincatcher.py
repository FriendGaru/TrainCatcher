# -*- coding: utf-8 -*-
"""
Train Catcher

A simple script that if provided with a proper set of schedules, can be used to figure out the 
next train you can catch.
"""

import datetime

SCHEDULE_TYPES = ["weekday", "saturday", "holiday"]
DAY_INT = {6: "Sunday", 0: "Monday", 1: "Tuesday", 2: "Wednesday", 
           3: "Thursday", 4: "Friday", 5: "Saturday"}




def simplifyTime(time):
    """
    This takes either a tuple of (hour,minute) or an int of minutes after midnight
    Returns an int of minutes after midnight
    """
    if type(time) == tuple:
        time = 60 * time[0] + time[1]
    assert type(time) == int
    return time

def timeToString(timeTup):
    """
    Takes a tuple of (minutesFromMidnight, dayOfTheWeek) and returns a nice string like "Monday 12:05"
    """
    hour = timeTup[0] // 60
    if hour < 10:
        hour = "0" + str(hour)
    else:
        hour = str(hour)
        
    minute = timeTup[0] % 60
    if minute < 10:
        minute = "0" + str(minute)
    else:
        minute = str(minute)
        
    weekday = DAY_INT[timeTup[1]]
        
    out = "%s %s:%s" % (weekday, hour, minute)
    return out


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
        if self.hour < 10:
            hour = '0' + str(self.hour)
        else:
            hour = str(self.hour)
            
        if self.minute < 10:
            minute = '0' + str(self.minute)
        else:
            minute = str(self.minute)
            
        return ("%s:%s %s" % (hour, minute, self.dest))
    
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
        
        """
        #Old method using filtered schedule
        time = simplifyTime(time)
        
        if dests:
            return self.filteredSched(dests).nextDep(time)
        else:

            for departure in self.departures:
                if departure.minFromMidnight() > time:
                    return departure
            return None
        """
        
        time = simplifyTime(time)
        if dests == None:
            dests = self.getDests()
            
        for departure in self.departures:
            if departure.minFromMidnight() > time and departure.getDest() in dests:
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
    !!Wiggle hasn't been implemented yet, for now this simply will tell tghe user the next catchable train
    
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
        
    def getNextTrain(self, time, day, dests = None):
        """
        Returns the next catchable departure given a specified time
        
        Time can be given as either a tuple(hour,minute) or an int for minutes from midnight

        """
        activeSched = self.schedules[day]

        return activeSched.nextDep(time, dests)
    
    def setGoodDests(self, goodDests):
        """
        Not all departures are necessarily good trains to catch
        This sets which destinations constitute good trains
        Setting to None will mean all trains are good
        """
        self.goodDests = goodDests
    
    def getNextGood(self, time = None, day = None, walkTime = None, goodDests = None):
        """
        This returns the next good, catchable train
        """
        nowTup = None
        if time == None or day == None:
            nowTup = TrainCatcher.getNowTime() # Should only call datetime if needed
        
        if time == None:
            time = nowTup[0]
        else:
            time = simplifyTime(time)
            
        if day == None:
            day = nowTup[1]
        
        if walkTime == None:
            walkTime = self.walkTime
            
        if goodDests == None:
            goodDests = self.goodDests
            
        if walkTime:
            time += walkTime
        
        return self.getNextTrain(time = time, day = day, dests = goodDests)
    
    def checkDeparture(self, dep, time):
        """
        Takes a departure obj and checks it against the TC obj's walktime and wiggle
        Returns one of the following:
            'gone' - already left
            'uncatchable' - hasn't departed yet, but not catchable within walk time
            'maybe' - within walk time, but not wiggle
            'good' - within both walk and wiggle time
        """
        depTime = dep.minFromMidnight()
        
        if time > depTime:
            return 'gone'
        elif time + self.walkTime + self.wiggle < depTime:
            return 'good'
        elif time + self.walkTime < depTime:
            return 'maybe'
        else:
            return 'uncatchable'
    
    def getLookup(self, time = None, day = None):
        """
        Takes a time and returns a LookupResults obj which contains all needed info.
        Uses only good destinations and the TrainCatcher obj's walkTime and wiggle
        """
        if time == None or day == None:
            nowTup = TrainCatcher.getNowTime()
        
        if time:
            time = simplifyTime(time)
        else:
            time = nowTup[0]
            
        if day == None:
            day = nowTup[1]
            
        uncatchableTrains = []
        maybeTrains = []
        goodTrains = []
        
        activeSched = self.schedules[day]
        
        for dep in activeSched.departures:
            depClass = self.checkDeparture(dep, time)
            if depClass == 'good':
                goodTrains.append(dep)
            elif depClass == 'maybe':
                maybeTrains.append(dep)
            elif depClass == 'uncatchable':
                uncatchableTrains.append(dep)
                
            if len(goodTrains) >= 2:
                break
        
        lookup = LookupResults( lookupTime = (time,day), goodTrains = goodTrains, uncatchableTrains = uncatchableTrains, maybeTrains = maybeTrains )
        
        return lookup
            

    
class LookupResults():
    """
    This class encapsulates all of the potentially important output data from one lookup
    
    lookupTime - When the lookup was run, (hours-from-midnight, day-of-the-week)
    uncatchableTrains - Trains that would be good, but are departing too soon to catch
    maybeTrains - Trains that are catchable, but only if you leave very soon
    goodTrains - The next certain good departure, and the following one for reference
    """
    def __init__(self, lookupTime, uncatchableTrains = None, maybeTrains = None, goodTrains = None):
        self.lookupTime = lookupTime
        self.uncatchableTrains = uncatchableTrains
        self.maybeTrains = maybeTrains
        self.goodTrains = goodTrains
        
    def __str__(self):
        out = "Lookup Time: " + timeToString(self.lookupTime)
        if self.uncatchableTrains:
            out += "\nBad: "
            for train in self.uncatchableTrains:
                out += str(train) + " "
        if self.maybeTrains:
            out += "\nMaybe: "
            for train in self.maybeTrains:
                out += str(train) + " "
        if self.goodTrains:
            out += "\nGood: "
            for train in self.goodTrains:
                out += str(train) + " "
        return out
        
        
        
        
