#!/usr/bin/env python2

import zbar
from PIL import Image
import cv2
from time import time

def main():

    lastdecoded = ""
    capture = cv2.VideoCapture(0)
    scanner = zbar.ImageScanner()

    while True:
        ret, frame = capture.read()
        # cv2.imshow('Current', frame)

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        width, height = image.size
        zbar_image = zbar.Image(width, height, 'Y800', image.tobytes())
        scanner.scan(zbar_image)

        for decoded in zbar_image:
            if decoded.data != lastdecoded: # or more than x secs passed?
                lastdecoded = decoded.data
                print(str(time()) + " " + decoded.data)


if __name__ == "__main__":
    main()
