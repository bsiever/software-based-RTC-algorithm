from pyTime import *

from datetime import datetime
from datetime import timedelta
from random import randint


def resetGlobalState():
    global year 
    year = 0
    global timeToSetpoint
    timeToSetpoint = 0
    global cpuTimeAtSetpoint
    cpuTimeAtSetpoint = 0    

def test_time():
    resetGlobalState()
    setTime(1,5,5, 0)
    (mm, dd, yy, h, m, s, doy) = timeFor(0)

    assert 1 == mm
    assert 1 == dd
    assert 0 == yy 
    assert 1 == h
    assert 5 == m
    assert 5 == s
    assert 1 == doy


def test_time_p5s():
    resetGlobalState()
    setTime(1,5,5, 0)
    (mm, dd, yy, h, m, s, doy) = timeFor(5)
    assert 1 == mm
    assert 1 == dd
    assert 0 == yy 
    assert 1 == h
    assert 5 == m
    assert 10 == s
    assert 1 == doy


def test_time_p55s():
    resetGlobalState()
    setTime(1,5,5, 0)
    (mm, dd, yy, h, m, s, doy) = timeFor(55)
    assert 1 == mm
    assert 1 == dd
    assert 0 == yy 
    assert 1 == h
    assert 6 == m
    assert 0 == s
    assert 1 == doy

def test_time_p1h():
    resetGlobalState()
    setTime(1,5,5, 0)
    (mm, dd, yy, h, m, s, doy) = timeFor(60*60)
    assert 1 == mm
    assert 1 == dd
    assert 0 == yy 
    assert 2 == h
    assert 5 == m
    assert 5 == s
    assert 1 == doy

def test_time_p1d():
    resetGlobalState()
    setTime(1,5,5, 0)
    (mm, dd, yy, h, m, s, doy) = timeFor(24*60*60)
    assert 1 == mm
    assert 2 == dd
    assert 0 == yy 
    assert 1 == h
    assert 5 == m
    assert 5 == s
    assert 2 == doy


def test_time_sdst1():
    resetGlobalState()
    setTime(1,5,5, 0)
    setDate(3,1,2020,0 )
    (mm, dd, yy, h, m, s, doy) = timeFor(0)
    assert 3 == mm
    assert 1 == dd
    assert 2020 == yy 
    assert 1 == h
    assert 5 == m
    assert 5 == s
    assert 61 == doy

def test_time_adv5s():
    resetGlobalState()
    setTime(1,5,5, 0)
    setDate(1,1,0,0 )

    advanceTime(5,0)
    (mm, dd, yy, h, m, s, doy) = timeFor(0)
    assert 1 == mm
    assert 1 == dd
    assert 0 == yy 
    assert 1 == h
    assert 5 == m
    assert 10 == s
    assert 1 == doy


def test_LeapProb():
    # 2/28/2050 4:45.37;  214
    # 2/28/2097 20:34.34;  230
    # 2/28/2031 11:44.15;  383
        smm = 2
        sdd = 28
        syy = 2050
        sh = 4
        sm = 45
        ss = 37
        scpu = 214

        print(f"{smm}/{sdd}/{syy} {sh}:{sm}.{ss};  {scpu}")
        setDate(smm,sdd,syy, scpu )
        setTime(sh,sm,ss, scpu)

        (mm, dd, yy, h, m, s, doy) = timeFor(scpu)
        assert smm == mm
        assert sdd == dd
        assert syy == yy 
        assert sh == h
        assert sm == m
        assert ss == s


def test_randomSetSetting():
    # 2/28/2050 4:45.37;  214
    # 2/28/2097 20:34.34;  230
    # 2/28/2031 11:44.15;  383

    for i in range(100):
        resetGlobalState()
        smm = randint(1,12)
        sdd = randint(1,28)
        syy = randint(2020, 2100)
        sh = randint(0,23)
        sm = randint(0,59)
        ss = randint(0,59)
        scpu = randint(0,600)

        print(f"{smm}/{sdd}/{syy} {sh}:{sm}.{ss};  {scpu}")
        setTime(sh,sm,ss, scpu)
        setDate(smm,sdd,syy, scpu )

        (mm, dd, yy, h, m, s, doy) = timeFor(scpu)
        assert smm == mm
        assert sdd == dd
        assert syy == yy 
        assert sh == h
        assert sm == m
        assert ss == s



def test_randomSetLaters():
    for i in range(400):
        resetGlobalState()
        smm = randint(1,12)
        sdd = randint(1,28)
        syy = randint(2020, 2100)
        sh = randint(0,23)
        sm = randint(0,59)
        ss = randint(0,59)
        scpu = randint(0,600)
        later = randint(1, 25*365*24*60*60)

        print(f"Start: {smm}/{sdd}/{syy} {sh}:{sm}.{ss};  {scpu} {later}")
        setTime(sh,sm,ss, scpu)
        setDate(smm,sdd,syy, scpu )

        # Date Object using values
        d = datetime(year=syy, month=smm, day=sdd, hour=sh, minute=sm, second=ss)
        delta = timedelta(seconds=later)
        n = d+delta
        (mm, dd, yy, h, m, s, doy) = timeFor(scpu+later)
        print(f"End: {mm}/{dd}/{yy} {h}:{m}.{s}  doy: {doy}")
        print(f"Expected: {n.month}/{n.day}/{n.year} {n.hour}:{n.minute}.{n.second}")
        assert n.month == mm
        assert n.day == dd
        assert n.year == yy 
        assert n.hour == h
        assert n.minute == m
        assert n.second == s



