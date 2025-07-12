import numpy as np

def line_length_transform(d, sfx=256, llw=0.04, badch=None):
    """
    Author: David Caldwell, 2025
    Performs line length transformation on EEG data using the line length method.

    Parameters
    ----------
    d : array_like
        Vector or matrix of EEG data. if 2D - time x channels 
    sfx : float
        Sampling frequency of the data. (default is 256 Hz)
    llw : float, optional
        Line length window in seconds (default is 0.04).
    badch : array_like, optional
        Logical index of bad channels (1=bad, 0=ok; default is None).

    Returns
    -------
    d_ll : array_like
        Line length transformed data, same size as input `d` with NaNs at the end
        for the last `llw` seconds.

    Based on Estellar et al 2001, DOI 10.1109/IEMBS.2001.1020545
    Inspired by MATLAB code from Jon Kleen 

    """
    d = np.asarray(d)  # ensure input is an array
    d = np.squeeze(d)  # remove any singleton dimensions

    # check inputs to make sure valid 

    if np.ndim(d) > 2:
        raise ValueError('Accepts only vector or 2-D matrix for data')
    if np.ndim(d) == 2:
        if d.shape[0] < d.shape[1]:
            d = d.T  # flip if needed for loop (assumes longer dimension is time)
    if badch is None:
        badch = np.zeros(d.shape[0], dtype=bool)  # default: all channels ok

    # calculate line length
    # Will be same size as d with tail end (<llw) padded with NaNs.

    # number of samples in the transform window
    numsamples=round(llw*sfx); 
    # shape of input - use this to determine if input is a vector or matrix - 
    # if 1 is present in shape, its a vector
    array_or_mat = d.ndim

    if d.ndim == 1:
        # initialize empty array w/ nan , fill in below 
        d_ll = np.full(d.shape, np.nan)
        for index in range(len(d) - numsamples):
           d_ll[index] = np.sum(np.abs(np.diff(d[index:index + numsamples])))

    else:
        # initialize empty array w/ nan, fill in below
       d_ll = np.full(d.shape, np.nan)
       # loop through each channel
       # and calculate line length for each channel
       # note: this assumes d is a 2D array with shape (time, channel)
       for index in range(d.shape[0] - numsamples):
           d_ll[index,:] = np.sum(np.abs(np.diff(d[index:index + numsamples],axis=0)), axis=0)

    return d_ll
