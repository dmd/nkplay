#!/usr/bin/env python3

import os
import sys
from tempfile import gettempdir
from os.path import join as pjoin
import random
import string
import qrcode
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image
from reportlab.pdfgen import canvas

tmpdir = gettempdir()


def id_generator(size=4):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def qr(code):
    qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(code)
    return qr.make_image()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate an Avery 22816 sheet of QR codes.')
    parser.add_argument('-c', '--codes', type=str, help='Comma-separated codes to use instead of random.')

    args = parser.parse_args()

    if args.codes is not None:
        codes = args.codes.split(',')
        if len(codes) != 12:
            print('If you specify codes, it must be a comma-separated list of length 12.')
            sys.exit(1)
    else:
        codes = [id_generator() for x in range(12)]

    for code in codes:
        img = qr(code)
        fn_qr = code + '_qr.png'
        with open(pjoin(tmpdir, fn_qr), 'wb') as p:
            img.save(p)

    fn_pdf = '_'.join(codes) + '.pdf'
    c = canvas.Canvas(fn_pdf, pagesize=letter)
    images = []
    labelnum = 0

    for x_pos in (0.63, 3.25, 5.88):
        for y_pos in (0.63, 3.21, 5.79, 8.38):
            c.drawImage(pjoin(tmpdir, codes[labelnum] + '_qr.png'), x_pos*inch, y_pos*inch, width=2*inch, height=2*inch)
            os.unlink(pjoin(tmpdir, codes[labelnum] + '_qr.png'))
            labelnum += 1

    c.showPage()
    c.save()

    print('Wrote playcard to ' + fn_pdf)


if __name__ == "__main__":
    main()
