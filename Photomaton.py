import sys
import pygame
import picamera
import random
import RPi.GPIO as GPIO
from time import sleep, strftime, gmtime
import os


# Setup Parameters
# Only change things here unless you want to dig into the program
play_shutter_sound = False  # Turn on/off shutter sound effects
photo_path = '/home/pi/Desktop/photos'  # Where photos will be stored

# Pin configuration
#ledPin = 19  # GPIO of the indicator LED
#auxlightPin = 20  # GPIO of the AUX lighting output
photobuttonPin = 18  # GPIO of the photo push button
#shutdownbuttonPin = 17  # GPIO of the shutdown push button

# Camera Settings
previewBrightness = 60  # Lighter than normal to offset the alpha distortion
photoBrightness = 57  # Darker than preview since there is no alpha
photoContrast = 0  # Default


def loadpic(imageName): # affiche imagename
    print("loading image: " + imageName)      
    background = pygame.image.load(imageName);
    sleep(3)
    background.convert_alpha()
    background = pygame.transform.scale(background,(width,height))
    screen.blit(background,(0,0),(0,0,width,height))
    pygame.display.flip()    
    


def minuterie():
  print("starting countdown")
  camera.preview_alpha = 210  # Set transparency so we can see the countdown
  drawText(bigfont, "3")
  sleep(0.3)
  drawText(bigfont, "2")
  sleep(0.3)
  drawText(bigfont, "1")
  sleep(0.3)
  drawText(smfont, "souriez")
  camera.preview_alpha = 254  # Set transparency so we can see the countdown

  

def drawText(font, textstr, clear_screen=True, color=(250, 10, 10)):
    """
    Draws the given string onto the pygame screen.

    Parameters:
    -----------
    font : object
        pygame font object
    textstr: string
        text to be written to the screen
    clean_screan : boolean
        determines if previously shown text should be cleared
    color : tuple
        RGB tuple of font color

    Returns:
    --------
    None
    """
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

    stopPreview()
    # Unflip the photo so it is correct when taken
    #camera.hflip = False
    takepic(path)
    # Take the photo
    #camera.capture(path)    

    return path

def outputToggle(pin, status, time=False):
    """
    Changes the state of an ouput GPIO pin with optional time delay.

    Parameters:
    -----------
    pin : int
        Pin number to manipulate
    status : boolean
        Status to be assigned to the pin
    time : int, float
        Time to wait before returning (optional)
    """
    GPIO.output(pin, status)
    if time:
        sleep(time)
    return status

def startPreview():    

    camera = picamera.PiCamera()
    camera.resolution = (1280,720)  # 1280,720 also works for some setups 2592, 1944
    camera.framerate = 8  # slower is necessary for high-resolution
    camera.brightness = previewBrightness  # Turned up so the black isn't too dark
    camera.hflip = True
    camera.vflip = True
    camera.start_preview()
    screen.fill(black)
    camera.preview_alpha = 254

def stopPreview():    
    print("trying to stop preview")
    camera.stop_preview()
    print("trying to stop camera")
    camera.close()
    print("camera stopped")

def photoButtonPress(event):
    print("button pressed")
    # Wait for 0.1 sec to be sure it's a person pressing the
    # button, not noise.
    sleep(0.05)
    if GPIO.input(photobuttonPin) != GPIO.LOW:
        return

    minuterie()
    fname = takePhoto()
    loadpic(fname)
    startPreview()





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

    stopPreview()
    GPIO.cleanup()

pygame.init()
# screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
# width, height = screen.get_size()

# pygame Settings
size = width, height = 800, 600
black = 0, 0, 0
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
bigfont = pygame.font.Font(None, 800)
smfont = pygame.font.Font(None, 600)
tinyfont = pygame.font.Font(None, 300)

# Setup camera


startPreview()


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

# Initial Setup
if not os.path.exists(photo_path):
    os.makedirs(photo_path)


# Main loop. Waits for keypress events. Everything else is
# an interrupt. Most of the time this just loops doing nothing.
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

            # Adjust brightness with the up and down arrows
            if event.key == pygame.K_UP:
                photoBrightness += 1
                previewBrightness += 1
                camera.brightness = previewBrightness
                print "New brightness (preview/photo): %d/%d" % (
                        photoBrightness, previewBrightness)

            if event.key == pygame.K_DOWN:
                photoBrightness -= 1
                previewBrightness -= 1
                camera.brightness = previewBrightness
                print "New brightness (preview/photo): %d/%d" % (
                        photoBrightness, previewBrightness)

            # Adjust contrast with the right and left arrows
            if event.key == pygame.K_RIGHT:
                photoContrast += 1
                camera.contrast = photoContrast
                print "New contrast: %d" % (photoContrast)

            if event.key == pygame.K_LEFT:
                photoContrast -= 1
                camera.contrast = photoContrast
                print "New contrast: %d" % (photoContrast)

        else:
            pass
