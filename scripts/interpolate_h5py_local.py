# %% imports 
import h5py
import numpy as np
import pandas as pd
import os
from pathlib import Path
import glob
from py_ecog_utils import interpolate_h5

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

        # EEG
        resampled_EEG = dict()
        resampled_EEG_metadata = dict()
        if "EEG" in f.keys():
            if "EEG,Composite,SampleSeries,Composite,Amp1020,timestamps" in f["EEG"].keys():
                for chan in f["EEG"].keys():
                    if "Timestamps" in chan:
                        continue
                    if len(f["EEG"][chan][:]) == 0:
                        continue
                    resamp_signal_info, gaps = interpolate_h5.process_signal(f["EEG"][chan][:], f["EEG"]["EEG,Composite,SampleSeries,Composite,Amp1020,timestamps"][:], 256, flip_signal=False, max_gap = (1/256)*1e6+500000)
                    if len(resamp_signal_info[0]) == 0 or len(resamp_signal_info[1]) == 0:
                        continue
                    resampled_EEG[chan] = resamp_signal_info
                    gaps_dict[chan] = gaps
                    resampled_EEG_metadata[chan] = {"units":f["EEG"][chan].attrs['units'],
                                            "start_time": min(resampled_EEG[chan][0]),
                                            "end_time": max(resampled_EEG[chan][0]),
                                            "number_points": len(resampled_EEG[chan][0]),
                                            "hz":256}

        resampled_HFEEG = dict()
        resampled_HFEEG_metadata = dict()
        if "EEG" in f.keys():
            if "HFEEG_Composite_Timestamps" in f["EEG"].keys():
                for chan in f["EEG"].keys():
                    if "Timestamps" in chan:
                        continue
                    if len(f["EEG"][chan][:]) == 0:
                        continue
                    resamp_signal_info, gaps = interpolate_h5.process_signal(f["EEG"][chan][:], f["EEG"]["HFEEG_Composite_Timestamps"][:], 2000, flip_signal=False, max_gap = (1/2000)*1e6+500000)
                    if len(resamp_signal_info[0]) == 0 or len(resamp_signal_info[1]) == 0:
                        continue
                    resampled_HFEEG[chan] = resamp_signal_info
                    gaps_dict[chan] = gaps
                    resampled_HFEEG_metadata[chan] = {"units":f["EEG"][chan].attrs['units'],
                                    "start_time": min(resampled_HFEEG[chan][0]),
                                    "end_time": max(resampled_HFEEG[chan][0]),
                                    "number_points": len(resampled_HFEEG[chan][0]),
                                    "hz":2000}

        # Trends
        resampled_trends = dict()
        resampled_trends_metadata = dict()
        if "Trends" in f.keys():
            if len(f["Trends"].keys()) >= 1:
                for signal_key in f["Trends"]:
                    if "Timestamps" in signal_key:
                        continue
                    if len(f["Trends"][signal_key][:]) == 0:
                        continue
                    if signal_key not in fs_dict.keys():
                        print(f"{signal_key} sample rate uknown. skipping. add field with fs to csv table and rerun.")
                        continue
                    resamp_signal_info, gaps = interpolate_h5.process_signal(f["Trends"][signal_key][:], f["Trends"][signal_key + "_Timestamps"][:], fs_dict[signal_key], 
                                                                flip_signal=False, max_gap = (1/fs_dict[signal_key])*1e6+500000)
                    if len(resamp_signal_info[0]) == 0 or len(resamp_signal_info[1]) == 0:
                        continue
                    resampled_trends[signal_key] = resamp_signal_info
                    gaps_dict[signal_key] = gaps
                    resampled_trends_metadata[signal_key] = {"units":f["Trends"][signal_key].attrs['units'],
                                    "start_time": min(resampled_trends[signal_key][0]),
                                    "end_time": max(resampled_trends[signal_key][0]),
                                    "number_points": len(resampled_trends[signal_key][0]),
                                    "hz":fs_dict[signal_key]}

        # Waveforms
        resampled_waveforms = dict()
        resampled_waveforms_metadata = dict()
        if "Waveforms" in f.keys():
            if len(f["Waveforms"]) >= 1:
                for signal_key in f["Waveforms"]:        
                    if "Timestamps" in signal_key:
                        continue
                    if len(f["Waveforms"][signal_key][:]) == 0:
                        continue
                    if signal_key not in fs_dict.keys():
                        print(f"{signal_key} sample rate uknown. skipping. add field with fs to csv table and rerun.")
                        continue
                    resamp_signal_info, gaps = interpolate_h5.process_signal(f["Waveforms"][signal_key][:], f["Waveforms"][signal_key + "_Timestamps"][:], fs_dict[signal_key], 
                                                                flip_signal=False, max_gap = (1/fs_dict[signal_key])*1e6+500000)
                    if len(resamp_signal_info[0]) == 0 or len(resamp_signal_info[1]) == 0:
                        continue
                    resampled_waveforms[signal_key] = resamp_signal_info
                    gaps_dict[signal_key] = gaps 
                    resampled_waveforms_metadata[signal_key] = {"units":f["Waveforms"][signal_key].attrs['units'],
                            "start_time": min(resampled_waveforms[signal_key][0]),
                            "end_time": max(resampled_waveforms[signal_key][0]),
                            "number_points": len(resampled_waveforms[signal_key][0]),
                            "hz":fs_dict[signal_key]}


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
