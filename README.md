# MSNH_Basin_Analysis

# MNSH Basin Analysis using Python

A Python workflow for basin-scale exploration analysis - field inventory, well database QC, formation tops, and 3D play-level visualization - built on Mid North Sea High (MNSH) field, well, and seismic isochron data exported from Petrel.

## Background

Basin-scale exploration analysis (field inventory, play fairway mapping, well database QC) is typically split across two separate licensed tools - Petrel for surfaces and well data, and ArcGIS for thematic/play mapping. This workflow explores whether that combined analysis can be reproduced end-to-end in open-source Python: reading Petrel-exported field, well, and isochron surface data directly (`.xlsx`, wellhead ASCII, IRAP Classic ASCII), QC-ing it, and visualizing basin structure and play levels in 3D without either license open.

## Series Progress

- ✅ Part 1: Field Inventory & Basin Overview (posted on LinkedIn)
- 🔄 Part 2: Well Database QC (in progress)
- ⏳ Part 3: Formation Tops Analysis
- ⏳ Part 4: Well-to-Quad Correlation (scope adjusted - no direct well-to-field join key in the dataset, so correlation is done at quad/block level instead)
- 🔄 Part 5: Basin-Scale 3D Visualization (Total Sediment Thickness + Permian Zechstein proven play level, rotating GIF)

## Tools Used

- Python 3.10
- library: `xtgeo` - reading Petrel-exported isochron surfaces (IRAP Classic ASCII)
- `PyVista` - 3D visualization + rotating GIF export
- `pandas` - field/well data QC and cleaning
- `matplotlib` - field statistics, discovery timeline, histograms

## Files

- `Part 1: Field Inventory` (notebook - field type/reservoir/discovery timeline analysis, GIF)
- `Part 2: Well Database QC` (notebook - flag normalization, quad-level well distribution, in progress)
- `generate_mnsh_3d_gif_v3.py` (Part 5 - isochron surface + wellhead 3D visualization script)

## Requirements

```
pip install pandas numpy matplotlib xtgeo pyvista openpyxl
```

## How to Use

This workflow requires your own Petrel-exported files:

- `FIELD_MASTER_FINAL.xlsx`, `WELL_MASTER_FINAL.xlsx`, `WELL_TOPS_FINAL.xlsx` - field, well, and formation tops master tables
- `Wellhead` - wellhead ASCII export (right-click Wells folder → Export → Well heads), matched to your project's CRS
- `MNSH_Isochron_<Formation>` - isochron surfaces exported as IRAP Classic ASCII (right-click surface → Export → IRAP Classic ASCII)

Update the file paths, formation names, and CRS (EPSG code) in the script to match your own dataset.

## About

Built as part of a self-directed learning project exploring whether basin-scale exploration workflows - normally split across Petrel and ArcGIS - can be reproduced in open-source Python. Documented step-by-step on LinkedIn; follow along for upcoming parts.

This is a work in progress, shared for learning purposes. Feedback and suggestions are very welcome!
