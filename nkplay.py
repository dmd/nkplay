#!/usr/bin/env python3

from time import time
from getch import getch
import musicpd

# this version is for use with a numeric keypad entry
# because the camera isn't working for me in low light
# of course this means playlists can only have numeric names.

def get_command():
    command = ''
    while True:
        c = getch()
        if c == '\n':
            return 'STOP' if command == '' else command
        if c in ['+', '-']:
            return c
        if c in [str(x) for x in range(10)]:
            command += c
            if command == '00':
                return '00'
        else:
            print('garbage received, clearing command')
            command = ''


def main():
    music = musicpd.MPDClient()
    music.connect('localhost', 6600)
    music.volume(100)
    music.update()

    while True:
        code = get_command()

        try:
            if code == 'STOP':
                print('STOP')
                music.clear()
            elif code == '-':
                print('previous')
                music.previous()
            elif code == '+':
                print('next')
                music.next()
            else:
                music.clear()
                music.load(code + '.m3u')
                music.consume(1)
                music.play()
                print('Now playing: ' + code)
        except:
            print('got an error')


if __name__ == '__main__':
    # this should be called from a script which reruns it on failure.
    print("listening for song ids...")
    main()
