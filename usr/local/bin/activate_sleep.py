#!/usr/bin/env python3
import sys
from socketIO_client import SocketIO
from time import sleep

# Change this to somewhere you can easily access
SLEEP_TIME_FILE="/home/volumio/mpd_sleep_time.txt"


def setSleep(state):
    if not "enabled" in state:
        raise Exception("enabled not found in initial sleep state check")
    else:
        enabled = state.get("enabled")

        if not enabled:
            print("Enabling sleep")
            socketIO = SocketIO('localhost', 3000)
            socketIO.emit('setSleep', {"enabled":True, "time":SLEEP_TIME})
            socketIO.wait(seconds=1)
            checkSleep()
        else:
            print("Sleep is already enabled")
            print(state)
            global okay
            okay = True


def checkSleepStatus(state):
    if not "enabled" in state:
        raise Exception("enabled not found in check sleep state")

    enabled = state.get("enabled")
    if enabled:
        print("Sleep successfully enabled")
        print(state)
        global okay
        okay = True
    else:
        raise Exception("Error sleep was not enabled")


def checkSleep():
    socketIO = SocketIO('localhost', 3000)
    socketIO.on('pushSleep', checkSleepStatus)
    socketIO.emit('getSleep', '')
    socketIO.wait(seconds=1)


# Main


try:
    file = open(SLEEP_TIME_FILE, "r")
    result = int(file.readline().strip())
    file.close()
except:
    print("Error reading file:", SLEEP_TIME_FILE, "- setting sleep action cancelled") 
    result = 0


if result != 0:
    hours = result // 60
    minutes = result % 60
    SLEEP_TIME = '{:02d}:{:02d}:'.format(hours, minutes)
    # Use the format "HH:MM:"
    # For example "02:00:"
    print("Using a sleep time of", SLEEP_TIME, "for volumio")

    okay = False
    count = 0
    while okay == False and count < 5:
        try:
            socketIO = SocketIO('localhost', 3000)
            socketIO.on('pushSleep', setSleep)
            socketIO.emit('getSleep', '')
            socketIO.wait(seconds=1)
        except Exception as e:
            print("Error setting sleep")
            print(e)
            sleep(1)
        count = count + 1

    if not okay:
        print("Gave up trying to enable sleep")
