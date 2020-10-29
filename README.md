# NumKey Music Player

Lets you play music (a playlist, using [musicpd](https://www.musicpd.org/)) by typing a number on a keypad, like a jukebox.

I have this installed on RPIs in my kids' rooms, with no screen, and just a numeric keypad and speaker attached.


I just have it start on boot. Poor man's daemon - not even dealing with systemd, having the pi boot without password straight to terminal (no X), and in `.profile`:


```
if [[ $(tty) == '/dev/tty1' ]]; then
   setleds -D +num
   sudo kbdrate -d 9001 # so mashing key doesn't hurt
   mpd
   cd qrplay
   while true; do
       ./nkplay.py
   done
fi
```
