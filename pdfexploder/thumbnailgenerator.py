""" thumbnailgenerator - classes for converting pdf documents into
various thumbnails. Uses Wand and command line imagemagick where
necessary.
"""

import os
import shutil
import random
import logging

from subprocess import Popen

from wand.image import Image, Color

log = logging.getLogger(__name__)

class ThumbnailGenerator(object):
    """ Requires an existing pdf file for init, has methods for
    generating thumbnails of various sizes and types.
    """
    def __init__(self, filename):
        """ Require that the filename exists.
        """
        if not os.path.exists(filename):
            raise IOError("Can't find: %s" % filename)

        self.filename = filename

    def top_thumbnail(self):
        """ Read the filename specified during init, return a png file
        format of the first page, resized.
        """
        pdf_filename = "%s[0]" % self.filename
        top_img = Image(filename=pdf_filename)
        top_img.resize(306, 396)
        top_img.format = "png"
        return top_img.make_blob()

    def mosaic_thumbnail(self):
        """ Use wand to create an effect like that in the imagemagick
        command line montage command. Read through each page in the pdf,
        resize it, draw an angled rectangle in gray for the background,
        then the reszied image on top of that.
        """
        
        back_filename = "resources/mosaic_background.png"
        back_img = Image(filename=back_filename)

        # From: # http://stackoverflow.com/questions/18821145/\
        # wand-convert-pdf-to-jpeg-and-storing-pages-in-file-like-objects
        image_pdf = Image(filename=self.filename)
        image_png = image_pdf.convert("png")
        shift = 0
        for page_img in image_png.sequence:
            page_img.resize(80, 103)
            self.composite_gray(back_img, page_img, shift)
            shift += 1

        back_img.format = "png"
        return back_img.make_blob()

    def composite_gray(self, back_img, top_img, shift=100):
        """ Add a gray border to the top image, rotate it randomly,
        composite it onto the background at a shifted position.
        """
        # Random angle, at least 3 degrees off center
        angle = random.randrange(-2, 2) 
        if angle < 0:
            angle -= 3
        else:
            angle += 3

        bg_color = Color("grey")
        border = Image(width=90, height=113, background=bg_color)

        border.composite(left=5, top=5, image=top_img) 
        border.rotate(angle)

        offset_left = 10 + (shift * 80)
        back_img.composite(left=offset_left, top=10, image=border)
