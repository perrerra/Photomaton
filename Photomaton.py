import sys
import pygame
import picamera
import RPi.GPIO as GPIO
from time import sleep, strftime, gmtime
#import os

def outputToggle(pin, status, time=False):

    GPIO.output(pin, status)
    if time:
        sleep(time)
    return status

def photoButtonPress(event):
    sleep(0.005)
    if GPIO.input(photobuttonPin) != GPIO.LOW:
        print("fake button press")
        return
    camera.start_preview()
    sleep(3)
    print("trying to take picture")
    time_stamp = strftime("%Y_%m_%dT%H_%M_%S", gmtime())
    path = "/home/pi/Desktop/photobooth_photos/%s.jpg" % time_stamp
    # camera.hflip = False
    
    outputToggle(ledPin, True, time=1)
    for j in range(4):
        outputToggle(ledPin, False, time=0.125)
        outputToggle(ledPin, True, time=0.125)
    
    camera.capture(path)
    outputToggle(ledPin, False)
    # shutter_sound.play()
    # camera.hflip = True
    
    camera.stop_preview()
    print("picture taken")

def safeClose():
    """
    Cleanly exits the program by turning off the lights, stopping
    the camera, and cleaning up the resources.

    Parameters:
    -----------
    None

    Returns:
    --------
    None
    """
    # outputToggle(ledPin, False)
    # outputToggle(auxlightPin, False)
    camera.stop_preview()
    camera.close()
    GPIO.cleanup()

pygame.init()
pygame.mixer.init()
# shutter_sound = pygame.mixer.Sound("/home/pi/Desktop/GIT/Photomaton/shutter.wav")

size = width, height = 800, 600
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
# Pin configuration
ledPin = 17  # GPIO of the indicator LED
#auxlightPin = 20  # GPIO of the AUX lighting output
photobuttonPin = 18  # GPIO of the photo push button
#shutdownbuttonPin = 17  # GPIO of the shutdown push button

# Setup camera
camera = picamera.PiCamera()
camera.resolution = (1280,720)  # 1280,720 also works for some setups 2592, 1944
camera.framerate = 8  # slower is necessary for high-resolution
camera.brightness = 57

camera.hflip = False
camera.vflip = True


# Turn off mouse
pygame.mouse.set_visible(False)

# Setup and tie GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(photobuttonPin, GPIO.IN, GPIO.PUD_UP)  # Take photo button
GPIO.add_event_detect(photobuttonPin, GPIO.FALLING,
                      callback=photoButtonPress, bouncetime=1000)

GPIO.setup(ledPin, GPIO.OUT)  # Front LED
outputToggle(ledPin, False)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print "QUIT event detected"
            safeClose()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            # Quit the program on escape
            if event.key == pygame.K_ESCAPE:
                safeClose()
                sys.exit()           

        else:
            pass