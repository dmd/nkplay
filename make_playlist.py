#!/usr/bin/env python3

import os, sys
import shutil
from glob import glob
import random
import string
import qrcode
from qrcode.image.pure import PymagingImage

playlistdir = 'playlists'

def id_generator(size=3):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def uniq_id():
    newid = id_generator()
    while os.path.exists(os.path.join(playlistdir, newid + '.m3u')):
        print('exists, trying again')
        newid = id_generator()
    return newid

def qr():
    qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=30,
            border=4,
            image_factory=PymagingImage,
            )
    
    newid = uniq_id()
    qr.add_data(newid)
    img = qr.make_image()

    return newid, img


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate a playlist and printable QR/Album Art.')
    parser.add_argument('directory', type=str, help='Directory to find music and album art.')
    args = parser.parse_args()

    newid, img = qr()
    playlist = glob(os.path.join(args.directory, '*.m??'))

    if len(playlist) == 0:
        print("Nothing found.")
        sys.exit(1)
    
    fn_m3u = newid + '.m3u'
    with open(os.path.join(playlistdir + fn_m3u), 'w') as p:
        p.write('\n'.join(playlist) + '\n')
    print('Wrote playlist to ' + fn_m3u)
    
    fn_qr = newid + '_qr.png'
    with open(os.path.join(playlistdir, fn_qr), 'wb') as p:
        img.save(p)
    print('Wrote QR to ' + fn_qr)

    exts = ('*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG')
    albumarts = []
    for ext in exts:
        albumarts.extend(glob(os.path.join(args.directory, ext)))
    
    if len(albumarts) > 0:
        albumart = albumarts[0]
    else:
        albumart = 'default.jpg'

    _, ext = os.path.splitext(albumart)
    fn_aa = newid + '_aa' + ext
    shutil.copyfile(albumart, os.path.join(playlistdir, fn_aa))
    print('Wrote album art to ' + fn_aa)

if __name__ == "__main__":
    main()


