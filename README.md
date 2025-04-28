# NumKey Music Player

Lets you play music (a playlist, using [musicpd](https://www.musicpd.org/)) by typing a number on a [standalone numeric keypad](https://www.amazon.com/Numeric-Keyboard-Computer-Notebook-Letters/dp/B0BNPVMQVT), like a jukebox.

I have this installed on RPIs in my kids' rooms, with no screen, and just a numeric keypad and speaker attached.


I just have it start on boot. Poor man's daemon - not even dealing with systemd, having the pi boot without password straight to terminal (no X), and in `.profile`:


```
if [[ $(tty) == '/dev/tty1' ]]; then
   setleds -D +num
   sudo kbdrate -d 9001 # so mashing key doesn't hurt
   mpd
   cd nkplay
   while true; do
       ./nkplay.py
   done
fi
```

## notes to self for getting it working in our house

```
sudo apt install mpd mpc python3-pip
sudo pip install python-musicpd getch 

sudo apt install shairport-sync  # optional if you want to be able to airplay to it as well

```

`/etc/mpd.conf` edits:

```
music_directory         "/home/dmd/musicplayer"
playlist_directory      "/home/dmd/musicplayer"

audio_output {
        type            "alsa"
        name            "My ALSA Device"
        mixer_type      "software"      # optional
        mixer_device    "default"       # optional
        mixer_control   "PCM"           # optional
}

```
