import numpy as np
import wave
import sys
import argparse
from contextlib import closing
from struct import pack
from pylab import *
# from itertools import *

nchannels = 0
framerate = 0
nframes = 0
width = 0

def pcm2float(sig, dtype=np.float64):
    """
    Convert PCM signal to floating point with a range from -1 to 1.

    Use dtype=np.float32 for single precision.

    Parameters
    ----------
    sig : array_like
        Input array, must have (signed) integral type.
    dtype : data-type, optional
        Desired (floating point) data type.

    Returns
    -------
    ndarray
        normalized floating point data.
    """

    sig = np.asarray(sig)  # make sure it's a NumPy array
    assert sig.dtype.kind == 'i', "'sig' must be an array of signed integers!"
    dtype = np.dtype(dtype)  # allow string input (e.g. 'f')

    # Note that 'min' has a greater (by 1) absolute value than 'max'!
    # Therefore, we use 'min' here to avoid clipping.
    return sig.astype(dtype) / dtype.type(-np.iinfo(sig.dtype).min)


def read_data(f, verbose, plotf):
    global nchannels, framerate, nframes, width
    with closing(wave.open(f)) as w:
        nchannels = w.getnchannels()
        framerate = w.getframerate()
        nframes = w.getnframes()
        width = w.getsampwidth()
        
        print("sampling rate = {0} Hz, length = {1} samples, channels = {2}, sample \
            width = {3} bytes".format(framerate, nframes, nchannels, width))
        data = w.readframes(nframes)

    sig = np.frombuffer(data, dtype='<i2')
    sig = sig.reshape(-1, nchannels)
    if (verbose):
        print(sig)

    if (plotf):
        normalized = pcm2float(sig, float32)
        plot(normalized)
        show()

    return sig

def string2dec(str):
    return [ord(c) for c in str]

def padd_message(msg, nframes):
    pad_amount = nframes - len(msg)
    if (pad_amount > 0):
        msg+=[0]*(pad_amount)
    return msg

def normalize_data(data):
    normalized = []
    for arr in data:
        mean = sum(arr)//len(arr)
        normalized.append(mean)
    return normalized

def rot13(msg, normalized):
    for i in range(len(normalized)):
        if normalized[i]+255 < sys.maxsize:
            msg[i]+= normalized[i]
        else: 
            msg[i]+= (normalized[i]-255)
    return msg

# TODO: grouper to chunk large files for more efficient writing
# def grouper(n, iterable, fillvalue=None):
#     "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
#     args = [iter(iterable)] * n
#     return zip_longest(fillvalue=fillvalue, *args)


def main():
    global plot_flag
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help="Name of file to ouput")
    parser.add_argument('-p', '--plot', action='store_true', help="Show Plot of Audio Channels")
    parser.add_argument('-t', '--text', help="Text to encode" )
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('filename', help="The file containing message or in which we wish to encode one.")
    args = parser.parse_args()

    if args.output == None:
        output = 'new.wav'
    else: 
        output = args.output
    
    print('output file: ', output)

    data = read_data(args.filename, args.verbose, args.plot)
    
    if args.text == None:
        print('frames: {frames}'.format(frames=nframes))
        while True:
            word = input("> ")
            if len(word) <= nframes:
                break
            print('Error: Length of input is greater than {0}'.format(nframes))
    else:
        word = args.text
        if len(word) > nframes:
            print('Error: Length of input is greater than {0}, the max size of a message for this file'.format(nframes))
            return
 
    msg = padd_message(string2dec(word), nframes)

    msg = rot13(msg, normalize_data(data))
    
    if(args.verbose):
        print('encode: ', msg)

    transform = np.hstack((data, np.atleast_2d(msg).T))
    transform = np.reshape(transform, (np.product(transform.shape),))

    with closing(wave.open(output, 'w')) as w:
        w.setparams((nchannels+1, width, framerate, nframes, 'NONE', 'not compressed'))
        frames = b''.join(pack('h', int(sample)) for sample in transform)
        w.writeframes(frames)


if __name__ == '__main__':
    sys.exit(main())