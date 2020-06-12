


# Simulator input.runningTime() == Time in ms
# Device:  Use C code based on us_ticker_read()/1000 (and handle roll overs)

# Functions for testing time computations

# Stored:
#   Start time reference (for delta)
#   HH:MM.s at start 
#   Day of Year at start 
#   Year at start 


# Alternate:
#   Store year, time since beginning, and timestamp

#   currentTimeFromBeginingOfStartYear = (now-timestamp) + timeSinceBeginning
#  Reduces storage a tiny bit I guess (and cal?)



# Cummulative days of year at the start of each month (non-leap years)
#  (Prefix sum)
# Padded for 1-based indices
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
            print("Advancing Leap Year")
            sSinceStartOfYear -= 366*24*60*60 
        else:
            print("Advancing NORMAL Year")
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

def dayOfWeek(m, d, y):
    # f = k + [(13*m-1)/5] + D + [D/4] + [C/4] - 2*C.
    # Zeller's Rule from http://mathforum.org/dr.math/faq/faq.calendar.html
    D = y%100
    C = y//100 
    # Use integer division
    return d + (13*m-1)//5 + D + D//4 + C//4 - 2*C


def advanceTime(amount, unit):
    units = [1, 60*1, 60*60*1, 24*60*60*1]
    global year, cpuTimeAtSetpoint, timeToSetpoint
    cpuTimeAtSetpoint -= amount*units[unit]



# def cpuTimeToDate(cpuTime):
#     totalTimeFromYear = timeToSetpoint + (cpuTime - cpuSetpoint)
#     y = year
#     years = True
#     while years:
#         leap = isLeapYear(y)
#         if (not leap and totalTimeFromYear>364*24*60*60) or (totalTimeFromYear>365*24*60*60):
#             totalTimeFromYear -= 364*24*60*60 if not leap else 365*24*60*60
#             y += 1
#         else: 
#             years = False
#     dayOfYear = totalTimeFromYear//(24*60*60)
#     timeOfDay = totalTimeFromYear%(24*60*60)
#     (m,d) = dayOfYearToMonthAndDay(dayOfYear, year)
#     hh = timeOfDay//(60*60)
#     timeOfDay = timeOfDay%(60*60)
#     mm = timeOfDay//(60)
#     ss = timeOfDay % 60
#     return (y,m,d, dayOfYear, hh, mm, ss)

# def timeAndDate(cpuTime):
#     nowFromStartOfYear = timeToSetpoint + (cpuTime - cpuSetpoint)
#     ss = nowFromStartOfYear%60
#     nowFromStartOfYear /= 60
#     mm = nowFromStartOfYear%60
#     nowFromStartOfYear /= 60
#     hh = nowFromStartOfYear%24
#     yd = nowFromStartOfYear / 24

#     # Count years until less than 1
#     ty = year 
#     while isLeapYear(ty) and yd>365 or yd>364:
#         yd -= 365 if isLeapYear(ty) else 364 
#         ty += 1


#     pass 




# def timeFromStartYear(now):
#     nowFromStartOfYear = timeToSetpoint + (now-cpuSetpoint)
#     ss = nowFromStartOfYear%60
#     nowFromStartOfYear /= 60
#     mm = nowFromStartOfYear%60
#     nowFromStartOfYear /= 60
#     hh = nowFromStartOfYear%24
#     d = nowFromStartOfYear / 24
#     return (d, hh, mm, ss)

# def setDate(y,m,d):
#     currentCPUTime = now()
#     # Get current time of day and recompute 
#     (d, hh, mm, ss) = timeFromStartYear(currentCPUTime)
#     # Update all state variables using this time
#     year = y
#     timeToSetpoint =  secondsSoFarForYear(d,m,y, hh, mm, ss)
#     cpuSetpoint = currentCPUTime

# def setTime(hh,mm,ss):
#     currentCPUTime = now()
#     # Get current day since running and recompute
#     (d, _, _, _) = timeFromStartYear(currentCPUTime)
#     # Find month and day of month
#     (m, d) = dayOfYearToMonthAndDay(d, year)
#     # Update all state variables using this time
#     timeToSetpoint =  secondsSoFarForYear(d,m,year, hh, mm, ss)
#     cpuSetpoint = currentCPUTime


# # Store:
# #    Year 
# #    time in seconds from beginning of year to time setpoint cpu time
# #    setpoint cpu time

# # Current time from start of year = timeAtSetpoint + (now-setpoint)   
# #     Remove seconds, minutes, hours, days, years 




# # All time tracked in ms count

# # State Variables
# #
# #    StartTimeMark
# #    Beginning year
# #    
# # 
# #
# #


# def newTime(d,m, y, h, min, s, ds):
#     # Take an original m/d/y hh:mm:ss and add on a ds to compute a new 
#     # d/m/y hh:mm:ss
#     sTot = s+ds
#     newSS = sTot%60
#     om = sTot//60   # Overflow into minutes

#     mTot = min+om
#     newMM = mTot%60
#     oh = mTot//60   # Overflow into hours 

#     hTot = h+oh 
#     newH = hTot%24 
#     od = hTot//24

#     # Days to start date from Jan 1 of start year
#     dFsY = dateToDayOfYear(m, d, y) 
#     tD = dFsY+od  # Total elapsed days 

#     # Advance years / decrease days (Clunky, but probably only a few years...)
#     newYear = y 
#     while tD > 365 if isLeapYear(newYear) else 364:
#         td -= 365 if isLeapYear(newYear) else 364
#         newYear += 1
#     (newM, newD) = dayOfYearToMonthAndDay(tD, newYear)

#     return (newM, newD, newYear, newH, newMM, newSS)


# def dayOfWeek(m, d, y):
#     # f = k + [(13*m-1)/5] + D + [D/4] + [C/4] - 2*C.
#     # Zeller's Rule from http://mathforum.org/dr.math/faq/faq.calendar.html
#     D = y%100
#     C = y/100 
#     # Use integer division
#     return d + (13*m-1)//5 + D + D//4 + C//4 - 2*C

#     # How....
# # Compute new time via overflows of sec, min, hr
# # Use # of days to add to initial period
# # Remove years....somehow....loop???


