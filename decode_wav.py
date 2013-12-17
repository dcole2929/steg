import wave
import sys
import argparse
import numpy as np
from contextlib import closing
from pylab import *

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
    global plot_flag
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
    
    if verbose:
        print(sig)

    if plotf:
        normalized = pcm2float(sig, float32)
        plot(normalized)
        show()

    return sig

def get_mean(data):
    normalized = []
    ochannels = len(data[0])
    for arr in data:
        mean = (sum(arr) - arr[ochannels-1])//(ochannels - 1)
        normalized.append(mean)
    return normalized

def decode13(data, normalized):
    msg = ''
    i = 0
    for x in data[:,len(data[0]) - 1]:
        if (x - normalized[i]) == 0.0:
            break;
        msg += chr(int(x - normalized[i]))
        i+=1
    print(msg)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--plot', action="store_true", help="Tells program to print plot")
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.add_argument('filename', help="The file containing message or in which we wish to encode one.")
    args = parser.parse_args()
    
    filename = args.filename

    data = read_data(filename, args.verbose, args.plot)
    decode13(data, get_mean(data))

if __name__ == "__main__":
    sys.exit(main())