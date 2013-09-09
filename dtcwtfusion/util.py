"""Utility functions for working with images and the DTCWT."""

import logging
log = logging.getLogger()

from dtcwt import dtwavexfm2, dtwaveifm2
from PIL import Image
import numpy as np

def as_luminance(im):
    """For 2D arrays, this is a pass-through function. For 3D arrays, compute
    the luminance of the input via the YUV formula:

    Y = 0.299*R + 0.587*G + 0.114*B

    This assumes that depths 0, 1 and 2 correspond to the red, green and blue
    planes respectively.

    """
    im = np.asanyarray(im)

    if len(im.shape) < 3:
        return im

    return 0.299 * im[:,:,0] + 0.587 * im[:,:,1] + 0.115 * im[:,:,2]

def load_and_transform_image(filename, xfmargs=None):
    """Load an image from a file named *filename* and transform it. If
    necessary the image will be transformed into luminance. *xfmargs* is a
    dictionary which is passwd as kwargs to dtwavexfm2.

    """
    log.info('Loading image from {0}'.format(filename))
    im = as_luminance(Image.open(filename)).astype(np.float32)
    return dtwavexfm2(im, **(xfmargs or {}))

def inv_transform_and_save_image(filename, transform, xfmargs=None):
    """Inverse transform assuming Yl, Yh = transform passing biort and qshift
    from xfmargs to dtwaveifm2 if they are present. Save the resulting image to
    filename in PNG format.
    
    """
    im_array = dtwaveifm2(transform[0], transform[1], biort=xfmargs['biort'], qshift=xfmargs['qshift'])
    im = Image.fromarray(np.clip(im_array, 0, 255).astype(np.uint8))
    im.save(filename, format='PNG')

# vim:sw=4:sts=4:et
