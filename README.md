This repository contains the methodology and workflow for calculating Thawing Degree Days (TDD) 
and identifying spatial hotspots of permafrost thaw risk in the North Slope Borough of Alaska using downscaled CMIP6 climate projections. 
The workflow integrates Python preprocessing with ArcGIS Pro spatial analysis tools.

Workflow Summary
Download CMIP6 NetCDF projections → Inspect dimensions & metadata
Crop to North Slope Borough → Convert temperatures to °C
Calculate annual TDD → Export GeoTIFF
Classify annual TDD rasters into hotspots → Export binary GeoTIFFs
Generate Space–Time Cube → Visualize spatiotemporal trends
Aggregate decadal rasters → Perform Getis-Ord Gi* analysis
