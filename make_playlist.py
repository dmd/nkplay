#!/usr/bin/env python3

import os, sys
from tempfile import gettempdir
from os.path import join as pjoin
import shutil
from glob import glob
import random
import string
import qrcode
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle
from reportlab.lib import colors

playlistdir = '.'

def id_generator(size=3):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def uniq_id():
    newid = id_generator()
    while os.path.exists(pjoin(playlistdir, newid + '.m3u')):
        print('exists, trying again')
        newid = id_generator()
    return newid

def qr(code=None, force=False):
    qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            )
    newid = code if code is not None else uniq_id()
    if os.path.exists(pjoin(playlistdir, newid + '.m3u')) and not force:
        print('Code "' + newid + '" already exists.')
        sys.exit(1)

    qr.add_data(newid)
    img = qr.make_image()

    return newid, img


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate a playlist and printable QR/Album Art.')
    parser.add_argument('directory', type=str, help='Directory to find music and album art.')
    parser.add_argument('-c', '--code', type=str, help='Code to use instead of random.')
    parser.add_argument('-f', '--force', action='store_true', help='Overwrite if specified code already exists.')
    parser.add_argument('-s', '--size', choices=['3by3', 'creditcard'], default='creditcard', help='Card size')

    args = parser.parse_args()

    newid, img = qr(args.code, args.force)

    # playlist m3u

    playlist = []
    for ext in ('*.mp3', '*.m4a', '*.aac'):
        playlist.extend(glob(pjoin(args.directory, ext)))

    if len(playlist) == 0:
        print("Nothing found.")
        sys.exit(1)

    fn_m3u = newid + '.m3u'
    with open(pjoin(playlistdir, fn_m3u), 'w') as p:
        p.write('\n'.join(playlist) + '\n')
    print('Wrote playlist to ' + fn_m3u)
    
    # qr code

    fn_qr = newid + '_qr.png'
    with open(pjoin(gettempdir(), fn_qr), 'wb') as p:
        img.save(p)

    # album art

    exts = ('*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG')
    albumarts = []
    for ext in exts:
        albumarts.extend(glob(pjoin(args.directory, ext)))
    
    if len(albumarts) > 0:
        albumart = albumarts[0]
    else:
        albumart = 'default.png'

    # pdf

    fn_pdf = newid + '_print.pdf'
    doc = SimpleDocTemplate(pjoin(playlistdir, fn_pdf))
    if args.size == '3by3':
        part_art = Image(albumart, width=3*inch, height=3*inch)
        part_qr = Image(pjoin(gettempdir(), fn_qr), width=3*inch, height=3*inch)
        part_table = Table([[part_art], [part_qr]])
        part_table.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 0.25, colors.black, None, (1,1,1))]))
        doc.build([part_table])
    elif args.size == 'creditcard':
        colwidths = [2.125*inch, 1.25*inch]
        rowheights = [2.125*inch, 2.125*inch]
        part_art = Image(albumart, width=2*inch, height=2*inch)
        part_qr = Image(pjoin(gettempdir(), fn_qr), width=2*inch, height=2*inch)
        part_table = Table([[part_art, ],[part_qr, newid]], colwidths, rowheights)
        part_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 0.25, colors.black, None, (1,1,1)),
            ('LINEBELOW', (0,0), (-1,0), 0.25, colors.black, None, (1,1,1)),
            ('ALIGN', (1,1), (1,1), 'CENTER'),
            ('VALIGN', (1,1), (1,1), 'MIDDLE'),
]))
        doc.build([part_table])
    print('Wrote playcard to ' + fn_pdf)

    os.unlink(pjoin(gettempdir(), fn_qr))

if __name__ == "__main__":
    main()


