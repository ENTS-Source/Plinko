# ENTS Plinko Raspberry Pi
# ------------------------------------------------------------------------------
# Competition display for ENTS Plinko
import RPi.GPIO as GPIO
import subprocess

from config import Configuration
config = Configuration()

print("Game fullscreen = " + str(config.game.fullscreen))
print("Left device = " + config.devices.left)
print("Right device = " + config.devices.right)

print("Setting up buttons")
GPIO.setmode(GPIO.BOARD)
GPIO.setup(config.buttons.btn1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(config.buttons.btn2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Preparing game...")
import pygame
import os
import sys
from time import time, sleep


# Set up engine
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
pygame.init()
displayInfo = pygame.display.Info()
offset = 0
# Just so that the bottom of the screen can be screen
if not config.game.fullscreen:
    offset = 100
screenSize = sWidth, sHeight = displayInfo.current_w, displayInfo.current_h - offset

# Create screen
print("Setting up graphical interface")
screen = pygame.display.set_mode(screenSize, pygame.DOUBLEBUF, 32)
screen.set_alpha(None)
pygame.display.set_caption("ENTS Plinko")
if config.game.fullscreen:
    pygame.display.toggle_fullscreen()

# Start the game communications
print("Starting communications")
from communication.device import PlinkoBoard
leftBoard = PlinkoBoard(config.devices.left)
rightBoard = PlinkoBoard(config.devices.right)
#rightBoard = leftBoard # TODO: Remove debugging

# Start the score tracker
print("Starting score tracker")
from scoretracker import ScoreTracker
scoreTracker = ScoreTracker()

# Start the screen manager
print("Preparing screen")
from screen import Screen
gameScreen = Screen(screen, scoreTracker)

# Prepare for the game loop
gameRunning = True
def closeAll():
    print("Close requested")
    gameRunning = False
    print("Shutting down display...")
    pygame.display.quit()
    print("Shutting down engine...")
    pygame.quit()
    print("Shutting down devices...")
    leftBoard.close()
    rightBoard.close()
    print("Shutting down score tracker...")
    scoreTracker.close()
    print("Exiting...")
    if forceExit:
        print("Force exit set, running shutdown command")
        subprocess.Popen('shutdown -h 1', shell=True) # 1 minute shutdown
    sys.exit()
def millis():
    return int(round(time() * 1000))
maxRenderTime = 0
timesOver1s = 0
forceExit = False
lastTick = millis()

print("Starting game loop...")
while gameRunning:
    start = millis()
    if forceExit:
        gameRunning = False
        closeAll()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            gameRunning = False
            closeAll()
    rStart = millis()
    hasUpdate = False
    if leftBoard.newScore or leftBoard.scoreUpdated:
        if leftBoard.newScore:
            scoreTracker.recordScore(0, leftBoard.score) # player 0
        leftBoard.newScore = False
        leftBoard.scoreUpdated = False
        hasUpdate = True
    if rightBoard.newScore or rightBoard.scoreUpdated:
        if rightBoard.newScore:
            scoreTracker.recordScore(1, rightBoard.score) # player 1
        rightBoard.newScore = False
        rightBoard.scoreUpdated = False
        hasUpdate = True
    if hasUpdate:
        gameScreen.render(leftBoard.score, rightBoard.score)
    end = millis()
    rTime = end - rStart
    if rTime > maxRenderTime:
        if rTime > 1000:
            timesOver1s += 1
        else:
            maxRenderTime = rTime
        print("!! NEW MAXIMUM RENDER TIME: " + str(maxRenderTime) + "ms (" + str(timesOver1s) + " times over 1s)")
    sleep(0.1) # for catchup

    # check for shutdown buttons
    if(GPIO.input(config.buttons.btn1_pin) == 0):
        print("Shutdown button pressed, forcing exit on next loop")
        forceExit = True
    if(GPIO.input(config.buttons.btn2_pin) == 0):
        print("Clearing visible scores")
        leftBoard.score = 0
        leftBoard.scoreUpdated = True
        rightBoard.score = 0
        rightBoard.scoreUpdated = True
