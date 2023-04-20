# Folder with relevant code for working with the A2 fiber probe
Includes refractive index data for water-ethanol mixtures.

Most important file is `plot_bubbles.py`, which is further explained below.

# Doc for `plot_bubbles.py`

Loads and processes data from the A2 Fiber probe, turns them into pretty graphs

## Usage
Expects input to be .evt files from the M2 Analyzer for bubbly flows.
Requires adaptations in source code for changing source folders of the .evt files.

## Outputs
Outputs a figure for each data file, and a boxplot of the combined data.
Output folder is a new folder `/fig/` in the source folder.