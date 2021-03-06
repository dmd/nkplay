#!/usr/bin/env python3

from time import time
from getch import getche
from subprocess import call
import signal
import musicpd


MAXPLAYTIME = 3600

def sleep_handler(signum, frame):
    music = musicpd.MPDClient()
    music.connect('localhost', 6600)
    music.clear()
    print('going to sleep')
    music.disconnect()

signal.signal(signal.SIGALRM, sleep_handler)

def get_command():
    command = ''
    while True:
        c = getche()
        if c == '\n':
            return 'STOP' if command == '' else command
        if c in ['+', '-']:
            return c
        if c in [str(x) for x in range(10)]:
            command += c
        else:
            print('garbage received: "' + str(c) + '", clearing command')
            command = ''


def main():
    music = musicpd.MPDClient()
    music.connect('localhost', 6600)
    music.replay_gain_mode('track')
    music.volume(100)
    music.update()
    music.disconnect()

    while True:
        try:
            code = get_command()
        except OverflowError:
            # because alarm fired
            continue

        music.connect('localhost', 6600)

        try:
            if code == 'STOP':
                print('STOP')
                music.clear()
            elif code == '8686':
                call('/sbin/poweroff')
            elif code == '-':
                print('previous')
                music.previous()
            elif code == '+':
                print('next')
                music.next()
            else:
                music.clear()
                music.load(code + '.m3u')
                music.consume(0)
                music.repeat(0)
                if code == '999':
                    music.random(1)
                else:
                    music.random(0)
                music.play()
                signal.alarm(MAXPLAYTIME)
                print('Now playing: ' + code)
        except Exception as e:
            print('got an error: ' + str(e))
        music.disconnect()


if __name__ == '__main__':
    # this should be called from a script which reruns it on failure.
    print("listening for song ids...")
    main()
