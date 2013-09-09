"""
Construct a registered image from several input images.

Usage:
    dtcwt_register [options] <OUTPUT> [<IMAGE>...]

Options:

    --help, -h              Show a brief usage summary.
    --verbose, -v           Be more verbose in logging output.
    --level-count=N         Use N levels of DT-CWT. [default: 4]
    --merge-method=METHOD   Use METHOD to merge registered frames.
                            See discussion below. [default: separate_phase]

IMAGE specifies one or more images to use as an input frame. The registered
image is written to <OUTPUT> in PNG format.

The merge method can be one of the following:

    mean            The arithmetic mean of all input images.
    separate_phase  Average phase separately from magnitude.

"""
from __future__ import print_function, division

import logging
import sys

from docopt import docopt
from dtcwt import dtwavexfm2, dtwaveifm2
import matplotlib
matplotlib.use('pdf')

import matplotlib.pyplot as plt
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
    logging.info('Loading image from {0}'.format(filename))
    im = as_luminance(plt.imread(filename)).astype(np.float32)
    return dtwavexfm2(im, **(xfmargs or {}))

def merge_mean(xfms):
    """Merge low pass and high pass images by taking mean over all frames.
    
    """
    # Extract an array of low-pass images and an array of arrays of high-pass
    Yls, Yhs = zip(*xfms)

    # Take low-pass mean
    Yl_mean = np.mean(Yls, axis=0)

    # Convert arrays of arrays of hig-pass image into an array of arrays of
    # high-pass images for the same level. Then take mean.
    Yh_mean = list(np.mean(x, axis=0) for x in zip(*Yhs))

    return Yl_mean, Yh_mean

def merge_separate_phase_mean(xfms):
    """Merge low pass and high pass images by taking mean over all frames.
    Merge phase images using separate magnitude and phase averaging.
    
    """
    # Extract an array of low-pass images and an array of arrays of high-pass
    Yls, Yhs = zip(*xfms)

    # Take low-pass mean
    Yl_mean = np.mean(Yls, axis=0)

    def phase_average(images):
        """Return the phase average of images."""
        sum_ = np.sum(images, axis=0)
        detail = np.max(np.abs(images), axis=0)
        return (sum_ / np.abs(sum_)) * detail

    # Convert arrays of arrays of high-pass image into an array of arrays of
    # high-pass images for the same level. Then take mean.
    Yh_mean = list(phase_average(x) for x in zip(*Yhs))

    return Yl_mean, Yh_mean

# Available merging methods
MERGE_METHODS = {
    'mean': merge_mean,
    'separate_phase': merge_separate_phase_mean,
}

def main():
    # Parse command line options
    opts = docopt(__doc__)

    # Set up logging level appropriately
    if opts['--verbose']:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARN)

    # Get global transform arguments options
    xfmargs = {
        'nlevels': int(opts['--level-count']),
        'biort': 'near_sym_b',
        'qshift': 'qshift_d',
    }

    # Choose merge function
    try:
        merge_cb = MERGE_METHODS[opts['--merge-method']]
    except KeyError:
        logging.error('Unknown merge method: {0}'.format(opts['--merge-method']))
        logging.error('Choose from: {1}'.format(', '.join(MERGE_METHODS.keys())))
        sys.exit(1)

    # Load input images and transform them with the DTCWT
    logging.info('Loading input images')
    input_xfmd = list(load_and_transform_image(fn, xfmargs=xfmargs) for fn in opts['<IMAGE>'])

    # Use selected merge strategy
    logging.info('Merging using method "{0}"...'.format(opts['--merge-method']))
    merged_xfm = merge_cb(input_xfmd)

    # Inverse transform merged result
    merged = dtwaveifm2(merged_xfm[0], merged_xfm[1], biort=xfmargs['biort'], qshift=xfmargs['qshift'])

    # Save merge result
    logging.info('Saving result to {0}'.format(opts['<OUTPUT>']))
    if len(merged.shape) < 3:
        merged = plt.cm.gray(merged/255.0)
    plt.imsave(opts['<OUTPUT>'], merged, format='png')

# vim:sw=4:sts=4:et
