# Python ECoG analysis 
Python ECoG utilities and example demo scripts for working with both example datasets, simulated data, and ECoG Trauma Data from SFGH 

## Organization
``py_ecog_utils``: contains the various functions to be imported/called.   
``data`` has locally stored data, if this were stored locally. otherwise may be on Wynton 
``scripts`` has the various demo ``.ipynb`` and ``.py`` script files    
Install with ``pip install -e .`` to be able to import modules   
Dependencies are in ```python_version.txt``` and ```requirements_python.txt```

## Scripts for ECoG trauma data 
```interpolate_h5py_local.py``` - local script for .h5 interpolation. Run first  
```search_artifacts.py``` - script looking for sections of bad/artifactual data. Run second
```compare_depth_strip.py``` - script to compare recordings from ECoG strip electrodes, cylinder laid on cortex, and cylinder through bolt 

## Other Notebooks and Scripts
```example_line_length.ipynb```: example notebook of simulated ```neurodsp``` data and line length transform.  
```mat_moberg_sort_load.py```: code to load, organize, and concatenate ```.mat``` files converted by Moberg 


David J. Caldwell 2025 
