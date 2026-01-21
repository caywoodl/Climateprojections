import xarray as xr
import numpy as np
from pathlib import Path
from tqdm import tqdm
import rasterio
from rasterio.transform import from_origin
import re

# ======================================================
# USER CONFIGURATION
# ======================================================
# Directory containing processed NetCDF files (one year per file)
DATA_DIR = Path("path/to/processed_netcdf_directory")

# Output directory for TDD GeoTIFFs
OUTPUT_DIR = DATA_DIR / "TDD_GeoTIFFs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================
# MAIN PROCESSING FUNCTION
# ======================================================
def calculate_tdd_and_export_geotiffs(data_dir: Path, output_dir: Path):
    """
    Calculates annual Thawing Degree Days (TDD) from daily
    near-surface air temperature (tas) and exports results
    as GeoTIFF rasters.
    """

    # -----------------------------------
    # FIND ALL NETCDF FILES
    # -----------------------------------
    nc_files = sorted(data_dir.glob("*.nc"))
    print(f"Found {len(nc_files)} NetCDF files")

    # -----------------------------------
    # LOOP OVER FILES
    # -----------------------------------
    for nc_file in tqdm(nc_files, desc="Calculating TDD and exporting GeoTIFFs"):

        # Extract year from filename
        match = re.search(r"(20\d{2})", nc_file.name)
        if match:
            year = match.group(1)
        else:
            year = nc_file.stem  # fallback

        # Open NetCDF
        ds = xr.open_dataset(nc_file)

        # --------------------------------
        # TDD CALCULATION
        # --------------------------------
        tdd = ds["tas"].where(ds["tas"] > 0, 0).sum(dim="time")
        tdd_data = tdd.values.astype(np.float32)

        # --------------------------------
        # EXTRACT COORDINATES
        # --------------------------------
        lat = ds["lat"].values
        lon = ds["lon"].values

        # Calculate pixel resolution
        pixel_width = lon[1] - lon[0]
        pixel_height = lat[1] - lat[0]

        # Define affine transform (top-left origin)
        transform = from_origin(
            lon.min(),
            lat.max(),
            pixel_width,
            pixel_height
        )

        # --------------------------------
        # WRITE GEOTIFF
        # --------------------------------
        out_tif = output_dir / f"TDD_{year}.tif"

        with rasterio.open(
            out_tif,
            "w",
            driver="GTiff",
            height=tdd_data.shape[0],
            width=tdd_data.shape[1],
            count=1,
            dtype="float32",
            crs="EPSG:4326",
            transform=transform,
            compress="lzw"
        ) as dst:
            dst.write(tdd_data, 1)

        ds.close()

    print(f"✅ TDD GeoTIFFs created for all years in: {output_dir}")


# ======================================================
# SCRIPT ENTRY POINT
# ======================================================
if __name__ == "__main__":
    calculate_tdd_and_export_geotiffs(DATA_DIR, OUTPUT_DIR)
