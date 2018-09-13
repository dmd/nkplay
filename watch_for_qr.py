#!/usr/bin/env python3

from time import time, sleep
from PIL import Image
import zbar
import cv2
import musicpd

def main():
    music = musicpd.MPDClient()
    music.connect('localhost', 6600)
    music.update()

    lastdecoded = ""
    lastdecodedtime = 0
    capture = cv2.VideoCapture(0)
    scanner = zbar.Scanner()

    while True:
        sleep(0.1)  # we really don't need to do this more
        ret, frame = capture.read()
        # cv2.imshow('Current', frame)

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

        for decoded in scanner.scan(image):
            ddd = decoded.data.decode("utf-8")
            if ddd != lastdecoded or time() - lastdecodedtime > 30:
                lastdecoded = ddd
                lastdecodedtime = time()

                if ddd == 'STOP':
                    music.clear()
                    print('Stopped.')
                else:
                    try:
                        music.clear()
                        music.load(ddd + ".m3u")
                        music.play()
                        print('Now playing: ' + ddd)
                    except:
                        print('We should print the error here too.')
                        print('Failed to play ' + ddd)
                    

if __name__ == "__main__":
    main()
