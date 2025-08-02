# code to load in Moberg data in .mat format 
# the working part of this is loading in data, sorting the .mat files, and concatening them 
# %%
## import utilities 
from py_ecog_utils import interpolate_nonuniform_moberg_mat, line_length, bipolar_select, helpers 
import glob 
import os
from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy
from matplotlib import colormaps

# %% get .mat data files 

# run this code from the scripts directory
script_path =  os.getcwd()
data_path = str(Path(script_path).parents[0])
data_specific = '/data/mat_moberg/CSD217_day0_and_1'

files_int = glob.glob(data_path+ data_specific + '/*data_part*of188.mat')

files_int_postfix = []

# build a list of files with postfix, then sort later 
for file in files_int:
    file_int_last = os.path.basename(file)
    file_int_last_split = re.split(r'(\d+)', file_int_last)
    temp_list_number = helpers.find_first_number_in_list_of_strings(file_int_last_split)

    files_int_postfix.append(temp_list_number)

files_int_postfix = np.asarray(files_int_postfix)

sorted_indices = np.argsort(files_int_postfix)

files_int_sorted = [files_int[i] for i in sorted_indices]


# %% loop through data files and load them, concatenate, and get list of all channels that have 'EcoG' in the name

additional_chans = ['F3','F4','F7','F8','Fp1','Fp2','01','02']

index = 1
for file in files_int_sorted:
    data_dict = scipy.io.loadmat(file, squeeze_me=True, struct_as_record=False)
    # get the measurement data and time vector
    measurement_data = data_dict['measurement_data']
    time_vector = data_dict['time_vector']
    if index == 1:
        measurement_data_vec = measurement_data
        time_vector_vec = time_vector
        index += 1
    else:
        measurement_data_vec = np.concatenate((measurement_data_vec,measurement_data),axis=1)
        time_vector_vec = np.concatenate((time_vector_vec,time_vector),axis=0)

    # get the channel names 
    chan_list = data_dict['comp_elements']

    chans_int = [index for index, name in enumerate(chan_list) if 'ECoG' in name]
    chans_int = np.concatenate((chans_int, additional_chans), axis=0)

   
# resample the given data to 256 Hz w/ Vishnu interpolation
# %%
