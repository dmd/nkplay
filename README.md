# QR Music Player

Lets you play music (a playlist, using [musicpd](https://www.musicpd.org/)) by showing the camera a QR code with the playlist name.

Includes a tool to generate printable cards with album art and QR code. Also includes (because I decided this would be easier) a tool to generate a set of 12 random (or not random) QR codes on an Avery 22816 sheet, which are the right size to stick onto a credit-card sized token.

# Installation

Use [pipenv](https://pipenv.readthedocs.io/en/latest/basics/).

# for nkplayer

I'm just having it start on boot. Poor man's daemon - not even dealing with systemd, having the pi boot without password straight to terminal (no X), and in `.profile`:


```
if [[ $(tty) == '/dev/tty1' ]]; then
   sudo kbdrate -d 9001 # so mashing key doesn't hurt
   mpd
   cd qrplay
   while true; do
       ./nkplay.py
   done
fi
```
