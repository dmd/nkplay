#!/usr/bin/env python3

import zbar
from PIL import Image
import cv2
from time import time
import musicpd

def main():
    music = musicpd.MPDClient()
    music.connect('localhost', 6600)
    music.update()

    lastdecoded = ""
    capture = cv2.VideoCapture(0)
    scanner = zbar.Scanner()

    while True:
        ret, frame = capture.read()
#        cv2.imshow('Current', frame)

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

        for decoded in scanner.scan(image):
            if decoded.data != lastdecoded: # or more than x secs passed?
                lastdecoded = decoded.data
                print(decoded.data.decode("utf-8"))
                music.clear()
                music.load(decoded.data.decode("utf-8") + ".m3u")
                music.play()


if __name__ == "__main__":
    main()
