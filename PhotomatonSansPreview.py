import sys
import pygame
import picamera
import random
import RPi.GPIO as GPIO
from time import sleep, strftime, gmtime
import os


# Setup Parameters
# Only change things here unless you want to dig into the program
play_shutter_sound = True  # Turn on/off shutter sound effects
photo_path = '/home/pi/Desktop/photos'  # Where photos will be stored
gallery_path = '/home/pi/Desktop/photos/gallery.txt'
# Pin configuration
#ledPin = 19  # GPIO of the indicator LED
#auxlightPin = 20  # GPIO of the AUX lighting output
photobuttonPin = 18  # GPIO of the photo push button
#shutdownbuttonPin = 17  # GPIO of the shutdown push button

diaporama = True
photo_cursor = -1
photo_count = 0

gallery = []
gallery_file = open(gallery_path, 'r') 

picture_path = gallery_file.readline()
while picture_path <> '':
    gallery.append(picture_path)
    picture_path = gallery_file.readline()
    pass

photo_count = len(gallery)

def loadpic(imageName): # affiche imagename
    print("loading image: " + imageName)      
    background = pygame.image.load(imageName);
#    sleep(3)
    background = pygame.transform.scale(background,(width,height))
    background.convert_alpha()
    screen.blit(background,(0,0),(0,0,width,height))
    pygame.display.flip()    
    
def display_gallery():
    global photo_cursor
    photo_cursor = photo_cursor + 1
    print("displaying photo")
    if photo_cursor >= photo_count:
        photo_cursor = 0
    loadpic(gallery[photo_cursor])
    sleep(5)

def countdown():
  drawText(bigfont, "3")
  sleep(1)
  drawText(bigfont, "2")
  sleep(2)
  drawText(bigfont, "1")
  sleep(3)
  drawText(tinyfont, "souriez !")  

def drawText(font, textstr, clear_screen=True, color=(255, 255, 255)):
    if clear_screen:
        screen.fill(black)  # black screen

    # Render font
    pltText = font.render(textstr, 1, color)

    # Center text
    textpos = pltText.get_rect()
    textpos.centerx = screen.get_rect().centerx
    textpos.centery = screen.get_rect().centery

    # Blit onto screen
    screen.blit(pltText, textpos)

    # Update
    pygame.display.update()


def clearScreen():
    screen.fill(black)
    pygame.display.update()


if (os.path.isdir(photo_path) == False): # si le dossier pour stocker les photos n'existe pas       
   os.mkdir(photo_path)                  # alors on cree le dossier (sur le bureau)
   os.chmod(photo_path,0o777)            # et on change les droits pour pouvoir effacer des photos


def takepic(imageName):
    # command = "sudo raspistill -t 1000 -w 960 -h 720 -o "+ imageName +" -q 80" 
    # comman!d = "sudo raspistill -t 1000 -w 960 -h 720 -o "+ imageName +" -rot 90 -q 80" 
    command = "sudo raspistill -t 1000 -w 960 -h 720 -o "+ imageName +" -rot 180 -q 80" 
    # command = "sudo raspistill -t 1000 -w 960 -h 720 -o "+ imageName +" -rot 270 -q 80" S
    os.system(command)

def takePhoto():


    # Grab the capture
    time_stamp = strftime("%Y_%m_%dT%H_%M_%S", gmtime())
    path = "/home/pi/Desktop/photos/%s.jpg" % time_stamp
    if play_shutter_sound:
        shutter_sound.play()
    takepic(path)

        # Take the photo
    #camera.capture(path)    

    return path

def outputToggle(pin, status, time=False):
    GPIO.output(pin, status)
    if time:
        sleep(time)
    
	
def photoButtonPress(event):
    diaporama = False
    # Wait for 0.1 sec to be sure it's a person pressing the
    # button, not noise.
    sleep(0.05)
    if GPIO.input(photobuttonPin) != GPIO.LOW:
        return

    countdown()
    picture_path = takePhoto()
    screen.fill(black)
    loadpic(picture_path)
    sleep(3)
    gallery.append(picture_path) 
    with open(gallery_path, 'a') as gallery_file_w:
        gallery_file_w.write(picture_path)
        gallery_file_w.write('\n')
    global photo_count
    photo_count= photo_count + 1 
    diaporama = True

def safeClose():

    GPIO.cleanup()

pygame.init()
pygame.mixer.init()
shutter_sound = pygame.mixer.Sound("/home/pi/Desktop/GIT/Photomaton/shutter.wav")
# screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
# width, height = screen.get_size()

# pygame Settings
size = width, height = 800, 600
black = 0, 0, 0
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
bigfont = pygame.font.Font(None, 800)
smfont = pygame.font.Font(None, 600)
tinyfont = pygame.font.Font(None, 150)

# Setup camera
#camera = picamera.PiCamera()
#camera.resolution = (1280,720)  # 1280,720 also works for some setups 2592, 1944
#camera.framerate = 8  # slower is necessary for high-resolution
#camera.brightness = previewBrightness  # Turned up so the black isn't too dark

# Turn off mouse
pygame.mouse.set_visible(False)

# GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Setup and tie GPIO pins 
GPIO.setmode(GPIO.BCM)
GPIO.setup(photobuttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Take photo button
# GPIO.setup(shutdownbuttonPin, GPIO.IN, GPIO.PUD_UP)  # Shutdown button
# GPIO.setup(ledPin, GPIO.OUT)  # Front LED
# GPIO.setup(auxlightPin, GPIO.OUT)  # Aux Lights
GPIO.add_event_detect(photobuttonPin, GPIO.FALLING,
                      callback=photoButtonPress, bouncetime=500)
# GPIO.add_event_detect(shutdownbuttonPin, GPIO.FALLING,
#                       callback=shutdownButtonPress, bouncetime=1000)

# outputToggle(ledPin, True)  # Turn on the camera "power" LED




while 1:
    if diaporama:
        display_gallery()

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
