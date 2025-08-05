# 
# due to variability in moberg export and naming, extract strings, flatten them, and compare against subsets 
# of note, this code assumes that the first two elements in the split string are the relevant ones, proceed at your own peril if not 
# also , assumes that for waveforms and trends, that each data field comes in pairs, with a timestamp field 2nd. 
# For eeg/hfeeg, assumes only one timestamp field

# %% imports 
import h5py
import numpy as np
import pandas as pd
import os
from pathlib import Path
import glob
from py_ecog_utils import interpolate_h5
import re

#%% get working directory and load in resample rates

print("Starting script...")

# run this code from py_ecog_utils directory 
script_path = os.getcwd()
root_path = script_path
#root_path = str(Path(script_path).parents[0])
data = '/data'
data_h5 = '/data/hdf5dir'
save_dir = root_path + '/data/hdf5dir_interpolated/'

# This variable is defined but not used later in the script.
files_int = glob.glob(root_path + data_h5 + '/*.h5')

resamp_rates = pd.read_csv(root_path + data +"/H5_resample_rates.csv")
fs_dict = dict(zip(resamp_rates["Field"].values, resamp_rates["Resample_rate"].values))

fs_dict_split = [re.split(r"[,_]",x.lower()) for x in fs_dict.keys()]
fs_dict_flat = [x[0] + x[1] for x in fs_dict_split]

# redefine fs_dict to be a flat dictionary
fs_dict_flatten = dict(zip(fs_dict_flat, fs_dict.values()))
fs_dict = fs_dict_flatten

#%% run through files and interpolate
for fn in files_int:
    if not fn.endswith('.h5'):
        continue  # skip files that are not .h5

    print(f"Processing file: {fn}")
    # Open the HDF5 file
    with h5py.File(fn, 'r') as f:
        # Check if the file is empty
        if len(f.keys()) == 0:
            print(f"File {fn} is empty. Skipping.")
            continue
        # If the file is not empty, process it
        print(f"File {fn} is not empty. Processing...")

        last_part_name = os.path.basename(fn)
        last_part_name_split = last_part_name.split('_')
        
        # Create a save filename
        save_filename = "interp_" + last_part_name_split[1] + ".h5"

        print(fn)

        ##########################################
        #for storing signal gaps
        gaps_dict = dict()

        resampled_HFEEG = dict()
        resampled_HFEEG_metadata = dict()

        resampled_EEG = dict()
        resampled_EEG_metadata = dict()

        resampled_trends = dict()
        resampled_trends_metadata = dict()

        resampled_waveforms = dict()
        resampled_waveforms_metadata = dict()

# check if HFEEG is present, 
        if any("timestamps" in s.lower() for s in f["EEG"].keys()) and any("hfeeg" in s.lower() for s in f["EEG"].keys()):

            if "EEG" in f.keys():
                #check if timestamps are present
                # if timestamps are not present, skip this file
                    # find the index of the timestamps
                    index_timestamps_hfeeg = [index_timestamps_hfeeg for index_timestamps_hfeeg, chan in enumerate(f["EEG"].keys()) if "timestamps" in chan.lower()]
                    keys = [key for key in f["EEG"].keys()]


                    for chan in f["EEG"].keys():
                        if "timestamps" in chan.lower():
                            continue
                        if len(f["EEG"][chan][:]) == 0:
                            continue
                        resamp_signal_info, gaps = interpolate_h5.process_signal(f["EEG"][chan][:], f["EEG"][keys[index_timestamps_hfeeg[0]]][:], 2000, flip_signal=False, max_gap = (1/2000)*1e6+500000)
                        if len(resamp_signal_info[0]) == 0 or len(resamp_signal_info[1]) == 0:
                            continue
                        resampled_HFEEG[chan] = resamp_signal_info
                        gaps_dict[chan] = gaps
                        resampled_HFEEG_metadata[chan] = {"units":f["EEG"][chan].attrs['units'],
                                        "start_time": min(resampled_HFEEG[chan][0]),
                                        "end_time": max(resampled_HFEEG[chan][0]),
                                        "number_points": len(resampled_HFEEG[chan][0]),
                                        "hz":2000}

        # EEG

        if "EEG" in f.keys():
            #check if timestamps are present
            # if timestamps are not present, skip this file
            if any("timestamps" in s.lower() for s in f["EEG"].keys()):
                # find the index of the timestamps
                index_timestamps = [index_timestamps for index_timestamps, chan in enumerate(f["EEG"].keys()) if "timestamps" in chan.lower()]
                keys = [key for key in f["EEG"].keys()]

                for chan in f["EEG"].keys():
                    if 'timestamps' in chan.lower():
                        continue
                    if len(f["EEG"][chan][:]) == 0:
                        continue
                    resamp_signal_info, gaps = interpolate_h5.process_signal(f["EEG"][chan][:], f["EEG"][keys[index_timestamps[0]]][:], 256, flip_signal=False, max_gap = (1/256)*1e6+500000)
                    if len(resamp_signal_info[0]) == 0 or len(resamp_signal_info[1]) == 0:
                        continue
                    resampled_EEG[chan] = resamp_signal_info
                    gaps_dict[chan] = gaps
                    resampled_EEG_metadata[chan] = {"units":f["EEG"][chan].attrs['units'],
                                            "start_time": min(resampled_EEG[chan][0]),
                                            "end_time": max(resampled_EEG[chan][0]),
                                            "number_points": len(resampled_EEG[chan][0]),
                                            "hz":256}

        # Trends

        if "Trends" in f.keys():
            if len(f["Trends"].keys()) >= 1:
                if any("timestamps" in s.lower() for s in f["Trends"].keys()):
                    keys = [key for key in f["Trends"].keys()]
                    
                    for signal_key in f["Trends"]:
                        index_int = keys.index(signal_key)

                        #make flatten list of hdf5 keys to match against
                        signal_key_split_flatten_temp = re.split(r"[,_]",signal_key.lower())
                        signal_key_split_flatten = signal_key_split_flatten_temp[0] + signal_key_split_flatten_temp[1]

                        if "timestamps" in signal_key.lower():
                            continue
                        if len(f["Trends"][signal_key][:]) == 0:
                            continue
                        if signal_key_split_flatten not in fs_dict.keys():
                            print(f"{signal_key} sample rate uknown. skipping. add field with fs to csv table and rerun.")
                            continue
                        resamp_signal_info, gaps = interpolate_h5.process_signal(f["Trends"][signal_key][:], f["Trends"][keys[index_int+1]][:], fs_dict[signal_key_split_flatten], 
                                                                    flip_signal=False, max_gap = (1/fs_dict[signal_key_split_flatten])*1e6+500000)
                        if len(resamp_signal_info[0]) == 0 or len(resamp_signal_info[1]) == 0:
                            continue
                        resampled_trends[signal_key] = resamp_signal_info
                        gaps_dict[signal_key] = gaps
                        resampled_trends_metadata[signal_key] = {"units":f["Trends"][signal_key].attrs['units'],
                                        "start_time": min(resampled_trends[signal_key][0]),
                                        "end_time": max(resampled_trends[signal_key][0]),
                                        "number_points": len(resampled_trends[signal_key][0]),
                                        "hz":fs_dict[signal_key_split_flatten]}

        # Waveforms


        if "Waveforms" in f.keys():
            if len(f["Waveforms"]) >= 1:
                if any("timestamps" in s.lower() for s in f["Waveforms"].keys()):
                    keys = [key for key in f["Waveforms"].keys()]

                    for signal_key in keys:
                        index_int = keys.index(signal_key)

                        #make flatten list of hdf5 keys to match against
                        signal_key_split_flatten_temp = re.split(r"[,_]",signal_key.lower())
                        signal_key_split_flatten = signal_key_split_flatten_temp[0] + signal_key_split_flatten_temp[1]

                        if "timestamps" in signal_key.lower():
                            continue
                        if len(f["Waveforms"][signal_key][:]) == 0:
                            continue
                        if signal_key_split_flatten not in fs_dict.keys():
                            print(f"{signal_key} sample rate unknown. skipping. add field with fs to csv table and rerun.")
                            continue
                        resamp_signal_info, gaps = interpolate_h5.process_signal(f["Waveforms"][signal_key][:], f["Waveforms"][keys[index_int + 1]][:], fs_dict[signal_key_split_flatten], 
                                                                    flip_signal=False, max_gap = (1/fs_dict[signal_key_split_flatten])*1e6+500000)
                        if len(resamp_signal_info[0]) == 0 or len(resamp_signal_info[1]) == 0:
                            continue             
                        resampled_waveforms[signal_key] = resamp_signal_info
                        gaps_dict[signal_key] = gaps 
                        resampled_waveforms_metadata[signal_key] = {"units":f["Waveforms"][signal_key].attrs['units'],
                                "start_time": min(resampled_waveforms[signal_key][0]),
                                "end_time": max(resampled_waveforms[signal_key][0]),
                                "number_points": len(resampled_waveforms[signal_key][0]),
                                "hz":fs_dict[signal_key_split_flatten]}


        


        # save upsampled results to a new file
        with h5py.File(os.path.join(save_dir, save_filename), 'w') as hf:

            for data_name, data_dict, metadata_dict in zip(["EEG", "HFEEG", "Trends", "Waveforms"],
                                            [resampled_EEG, resampled_HFEEG, resampled_trends, resampled_waveforms],
                                            [resampled_EEG_metadata, resampled_HFEEG_metadata, resampled_trends_metadata, resampled_waveforms_metadata]):

                if len(data_dict.keys()) <= 0:
                    continue            

                filtered_grp = hf.require_group(data_name)
                for key in data_dict.keys():
                    dataset = filtered_grp.create_dataset(key,  data=data_dict[key][1], compression='gzip', compression_opts=9)
                    #does not save timestamps since signal is evenly spaced between start and end points
                    for metadata_field, metadata_value in metadata_dict[key].items():
                        dataset.attrs[metadata_field] = metadata_value
# %%
