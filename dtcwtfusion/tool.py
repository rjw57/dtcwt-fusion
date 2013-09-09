"""
Construct a fused image from several input images.

Usage:
    dtcwt_fuse [options] <OUTPUT> [<IMAGE>...]

Options:

    --help, -h              Show a brief usage summary.
    --verbose, -v           Be more verbose in logging output.
    --level-count=N         Use N levels of DT-CWT. [default: 4]
    --merge-method=METHOD   Use METHOD to merge frames.
                            See discussion below. [default: separate_phase]

IMAGE specifies one or more images to use as an input frame. The fused image is
written to <OUTPUT> in PNG format.

The merge method can be one of the following:

    mean            The arithmetic mean of all input images.
    separate_phase  Average phase separately from magnitude.

"""
from __future__ import print_function, division

import logging
log = logging.getLogger()

import sys

from .util import load_and_transform_image

from docopt import docopt
from dtcwt import dtwavexfm2, dtwaveifm2
from PIL import Image
import numpy as np

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
        log.basicConfig(level=log.INFO)
    else:
        log.basicConfig(level=log.WARN)

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
        log.error('Unknown merge method: {0}'.format(opts['--merge-method']))
        log.error('Choose from: {1}'.format(', '.join(MERGE_METHODS.keys())))
        sys.exit(1)

    # Load input images and transform them with the DTCWT
    log.info('Loading input images')
    input_xfmd = list(load_and_transform_image(fn, xfmargs=xfmargs) for fn in opts['<IMAGE>'])

    # Use selected merge strategy
    log.info('Merging using method "{0}"...'.format(opts['--merge-method']))
    merged_xfm = merge_cb(input_xfmd)

    # Inverse transform merged result
    merged = dtwaveifm2(merged_xfm[0], merged_xfm[1], biort=xfmargs['biort'], qshift=xfmargs['qshift'])

    # Save merge result
    log.info('Saving result to {0}'.format(opts['<OUTPUT>']))
    merged_im = Image.fromarray(np.clip(merged, 0, 255).astype(np.uint8))
    merged_im.save(opts['<OUTPUT>'], format='PNG')

# vim:sw=4:sts=4:et
