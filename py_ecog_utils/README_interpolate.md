pipeline for interpolating h5 files outputted from moberg cns->h5 conversion pipeline

requirements: numpy, numba, pandas 

**run_resamp.py**: python script that runs the interpolation

- Specify paths for data location and where to save interpolated files here

H5_resample_rates.csv has the rates at which each non-EEG waveform will be resampled. 

NOTE: code is set up with the assumption that all EEG is 256Hz and all HFEEG is 2KHz

NOTE: start time and end time are available in the attributes of signals in the interp h5 files! 

e.g.

> f = h5py.File("interp_file.h5")
> 
> print(f['Trends']['ABP_Dias'].attrs.keys())
> 
> f.close()
> 
> Console output: <KeysViewHDF5 ['end_time', 'hz', 'number_points', 'start_time', 'units']>

NOTE: all times are in unix epoch time format. Refer to moberg documentation for info on how to convert to standard datetime
