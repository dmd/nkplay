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
            # successfully acquired a QR code!
            lastdecodedtime = time()
            ddd = decoded.data.decode("utf-8")

            # we should take action on the QR code if any of:
            #   - it is different from the last one we TOOK ACTION on
            #   - we are not currently PLAYing
            #   - it has been more than 15 seconds since the last time we saw a QR code
            #     (this means it should be OK to LEAVE a code in view, as lastdecodedtime gets updated
            #      even if no ACTION gets taken on it)

            if ddd != lastdecoded or music.status()['state'] != 'play' or time() - lastdecodedtime > 15
                lastdecoded = ddd

                if ddd == 'STOP':
                    music.clear()
                    print('Stopped.')
                else:
                    try:
                        music.clear()
                        music.load(ddd + ".m3u")
                        music.consume(1)
                        music.play()
                        print('Now playing: ' + ddd)
                    except:
                        print('We should print the error here too.')
                        print('Failed to play ' + ddd)


if __name__ == "__main__":
    main()
