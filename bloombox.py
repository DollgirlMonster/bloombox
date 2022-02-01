import pygame
import requests

import time
import io

from PIL import Image, ImageFilter, ImageStat

pygame.init()

DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480

gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN)

COLOR_BLACK = (0,0,0)
COLOR_WHITE = (255,255,255)

ALBUM_ART_SIZE = (240, 240)

running = True

class Song:
    def __init__(self, title, artist, album, artwork):
        self.title = title
        self.artist = artist
        self.album = album
        self.artwork = artwork
current_song = Song("", "", "", "")

while running:
    if pygame.event.get(pygame.QUIT):
        running = False
    
    gameDisplay.fill(COLOR_WHITE)

    # Get the current information
    payload = {'id': 'now_playing'}
    try: 
        r = requests.get('http://owntone.local/api/queue', params=payload)
        r = r.json()
    except Exception as e:
        print(e)
        print("Sleeping 5s...")
        time.sleep(5)
        print("Retrying...")
        pass

    if len(r['items']) > 0: # if there are items in the queue
        title = r['items'][0]['title']
        artist = r['items'][0]['artist']
        album = r['items'][0]['album']
        artwork = 'http://owntone.local/%s' % r['items'][0]['artwork_url'].lstrip('/.')

        # If the song is new, download the artwork
        if [current_song.title, current_song.artist, current_song.album] != [title, artist, album]:
            artwork = requests.get(artwork)
        else:
            # If the song is the same, just use the old artwork
            artwork = current_song.artwork

        current_song = Song(title, artist, album, artwork)

        # Determine colors for the text based on the background
        if ImageStat.Stat(Image.open(io.BytesIO(artwork.content))).mean[0] < 128:
            is_light = False
        else:
            is_light = True

        # Blur the image for the background
        background = Image.open(io.BytesIO(artwork.content))
        if background.mode != 'RGB': background = background.convert('RGB')
        background = background.filter(ImageFilter.GaussianBlur(radius=50))
        background_surface = pygame.image.frombuffer(background.tobytes(), background.size, background.mode)
        background_surface = pygame.transform.scale(background_surface, (750, 750))
        gameDisplay.blit(background_surface, (0 - (480 / 2), 0 - (234 / 2)))
        
        # Draw the shadow
        # shadow = pygame.Surface(ALBUM_ART_SIZE)
        # shadow.set_alpha(80)
        # shadow.fill(COLOR_BLACK)
        # gameDisplay.blit(shadow, (50, 20))

        # Draw the album art
        artwork = pygame.image.load(io.BytesIO(artwork.content))
        artwork = pygame.transform.scale(artwork, ALBUM_ART_SIZE)   # scale the image
        gameDisplay.blit(artwork, (65, 23))     # blit the image

        # Get ready to display the information
        font = pygame.font.SysFont('Square One', 25, bold=True) # set the font

        # Determine colors for the text based on the background
        if is_light: color = ImageStat.Stat(background).mean[0] - 140
        else: color = ImageStat.Stat(background).mean[0] + 140
        color = (color, color, color)

        # Draw the info
        if len(title) > 13: title = title[:13] + '...'
        title = font.render(title, True, color)
        title = pygame.transform.rotozoom(title, 90, 1)
        gameDisplay.blit(title, (ALBUM_ART_SIZE[0] + 70, 23))

        font = pygame.font.SysFont('Square One', 20, bold=False)

        if len(artist) > 18: artist = artist[:18] + '...'
        artist = font.render(artist, True, color)
        artist = pygame.transform.rotozoom(artist, 90, 1)
        gameDisplay.blit(artist, (ALBUM_ART_SIZE[0] + 95, 23))

        if len(album) > 18: album = album[:18] + '...'
        album = font.render(album, True, color)
        album = pygame.transform.rotozoom(album, 90, 1)
        gameDisplay.blit(album, (ALBUM_ART_SIZE[0] + 115, 23))
        
    else:
        print("No song playing")

    pygame.display.update()
    pygame.mouse.set_visible(False)
    time.sleep(5)

pygame.quit()
quit(1)
