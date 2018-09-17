#!/usr/bin/env python3

from time import time, sleep
from PIL import Image
import zbar
import cv2
import musicpd
import picamera
import picamera.array

def main():
    music = musicpd.MPDClient()
    music.connect('localhost', 6600)
    music.update()

    lastdecoded = ""
    lastdecodedtime = 0
    camera = picamera.PiCamera()
    camera.resolution = (640, 480)
    scanner = zbar.Scanner()

    while True:
        sleep(0.1)  # we really don't need to do this more
        with picamera.array.PiRGBArray(camera) as stream:
            camera.capture(stream, format='bgr', use_video_port=True)
            frame = stream.array

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

        print(". ", end=" ", flush=True)
        ddd = scanner.scan(image)[0].data.decode("utf-8")

        if ddd != lastdecoded:
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
