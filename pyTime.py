# Python prototype algorithms for computing current time/date
# based on a set time/date and elapsed time.
# Used for unit-testing of algorithms for: 
#     https://github.com/bsiever/microbit-pxt-softclock


# Device:  Use C code based on us_ticker_read()/1000 (and handle roll overs)
#    Note:   us_ticker_read() had a atomicity error/race condition.

# Stored:
#   Start time reference (for delta)
#      Actual time and CPU time since start of CPU
#      (I.e., CPU time and the actual real time at that moment)
#   Year at start 

from math import floor   # For weekday computation

# Cumulative days of year at the start of each month (non-leap years)
# (a prefix sum)
# Padded for 1-based indices (month 1=Jan)
cdoy = [0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]

def isLeapYear(y):
    return (y%400==0 or (y%100!=0 and y%4==0))

def dateToDayOfYear(m, d, y):
    # Assumes a valid date 
    dayOfYear = cdoy[m] + d  
    # Handle after Feb in leap years:
    if m>2 and isLeapYear(y):
        dayOfYear += 1
    return dayOfYear

def dayOfYearToMonthAndDay(d, y):
    # If it's after Feb in a leap year, adjust
    if isLeapYear(y):
        if d==60:
            return (2, 29)
        elif d>60:   # Adjust for leap day
            d -= 1
    for i in range(1,len(cdoy)):  # Adjust for 1-based index
        # If the day lands in (not through) this month, return it
        if d<=cdoy[i+1]:
            return (i, d-cdoy[i])
    return (-1,-1)

def secondsSoFarForYear(d,m,y, hh, mm, ss):
    # ((((Complete Days * 24hrs/day)+complete hours)*60min/hr)+complete minutes)* 60s/min + complete seconds
    # Yay Horner's Rule!:
    return (((dateToDayOfYear(m,d,y)-1)*24 + hh)*60+mm)*60+ss

# Start Point has
year = 0
timeToSetpoint = 0
cpuTimeAtSetpoint = 0

#
#  Year Start          Time Date/Time set        CurrentCPUTime
#  |                   | (in s)                  | (in s)
#  V                   V                         V
#  |-------------------+-------------------------|
#                      ^
#                      | 
#                      Known dd/mm/yy hh:mm,.s
#                      AND cpuTimeAtSetpoint (in s)
#   |------------------|-------------------------|
#      timeToSetpoint          deltaTime
#      (in s)                  ( in s)


# Find the date+time (24 hr format) given a cpu time
def timeFor(cpuTime):
    deltaTime = cpuTime - cpuTimeAtSetpoint
    sSinceStartOfYear = timeToSetpoint + deltaTime
    # Find elapsed years by counting up from start year and subtracting off complete years
    y = year
    leap = isLeapYear(y)
    while (not leap and sSinceStartOfYear>365*24*60*60) or (sSinceStartOfYear>366*24*60*60):
        if leap:
            sSinceStartOfYear -= 366*24*60*60 
        else:
            sSinceStartOfYear -= 365*24*60*60 
        y += 1
        leap = isLeapYear(y)

    # sSinceStartOfYear and leap are now for "y", not "year"

    # Find elapsed days
    daysFromStartOfYear = sSinceStartOfYear//(24*60*60)+1  # Offset for 1/1 being day 1
    secondsSinceStartOfDay = sSinceStartOfYear%(24*60*60)

    # Find elapsed hours
    hoursFromStartOfDay = secondsSinceStartOfDay//(60*60)
    secondsSinceStartOfHour = secondsSinceStartOfDay%(60*60)

    # Find elapsed minutes
    minutesFromStartOfHour = secondsSinceStartOfHour//(60)
    # Find elapsed seconds
    secondsSinceStartOfMinute = secondsSinceStartOfHour%(60)

    # Convert days to dd/mm
    (mm, dd) = dayOfYearToMonthAndDay(daysFromStartOfYear, y) # current year, y, not start year
    # TODO: Make this a date/time object
    return (mm, dd, y, hoursFromStartOfDay, minutesFromStartOfHour, secondsSinceStartOfMinute, daysFromStartOfYear)


# Set date at given cpuTime
def setDate(mm,dd, yy, cpuTime):
    (_, _, _, h, m, s, _) = timeFor(cpuTime)    
    global year, cpuTimeAtSetpoint, timeToSetpoint
    year = yy
    cpuTimeAtSetpoint = cpuTime
    timeToSetpoint = secondsSoFarForYear(dd, mm, yy, h, m, s)

# Set time at given cpuTime
def setTime(h,m, s, cpuTime):
    (mm, dd, yy, _, _, _, _) = timeFor(cpuTime)    
    global year, cpuTimeAtSetpoint, timeToSetpoint
    cpuTimeAtSetpoint = cpuTime
    timeToSetpoint = secondsSoFarForYear(dd, mm, yy, h, m, s)

def dayOfWeek(doy, y):
    # Gauss's Algorithm for Jan 1: https://en.wikipedia.org/wiki/Determination_of_the_day_of_the_week
    # R(1+5R(A-1,4)+4R(A-1,100)+6R(A-1,400),7)    
    jan1 = ((1+5*( (y-1) % 4)+4*( (y-1) % 100)+6* ( (y-1) % 400)) % 7) 
    jan1 += 6  # Shift range:  Gauss used 0=Sunday, we'll use 0=Monday
    dow = ( (doy-1) + jan1 ) % 7
    return dow

def advanceTime(amount, unit):
    units = [1, 60*1, 60*60*1, 24*60*60*1]
    global year, cpuTimeAtSetpoint, timeToSetpoint
    cpuTimeAtSetpoint -= amount*units[unit]


