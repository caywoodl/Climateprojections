import xarray as xr
from pathlib import Path
import glob

# ======================================================
# USER CONFIGURATION
# ======================================================
# Set this to the directory containing NetCDF files
# Example:
#   data/CMIP6/GFDL-ESM4/SSP585/
NC_DIR = Path("path/to/netcdf_directory")

# ======================================================
# MAIN SCRIPT
# ======================================================
def inspect_netcdf_files(nc_dir: Path):
    """
    Inspects the structure, metadata, and spatial properties
    of NetCDF climate datasets.
    """

    # Find all NetCDF files
    nc_files = sorted(nc_dir.glob("*.nc"))

    print(f"Found {len(nc_files)} NetCDF files\n")

    for nc in nc_files:
        print("=" * 80)
        print(f"FILE: {nc.name}")

        # Open dataset
        ds = xr.open_dataset(nc)

        # -------------------------
        # BASIC STRUCTURE
        # -------------------------
        print("\n--- DATASET SUMMARY ---")
        print(ds)

        # -------------------------
        # DIMENSIONS
        # -------------------------
        print("\n--- DIMENSIONS ---")
        for dim, size in ds.dims.items():
            print(f"{dim}: {size}")

        # -------------------------
        # COORDINATES
        # -------------------------
        print("\n--- COORDINATES ---")
        for coord in ds.coords:
            values = ds[coord].values
            print(f"{coord}: {values[:5]} ...")

        # -------------------------
        # VARIABLES
        # -------------------------
        print("\n--- VARIABLES ---")
        for var in ds.data_vars:
            print(f"{var}: {ds[var].dims}")

        # -------------------------
        # GLOBAL ATTRIBUTES
        # -------------------------
        print("\n--- GLOBAL ATTRIBUTES ---")
        for attr, value in ds.attrs.items():
            print(f"{attr}: {value}")

        # -------------------------
        # VARIABLE ATTRIBUTES (tas)
        # -------------------------
        if "tas" in ds:
            print("\n--- 'tas' VARIABLE ATTRIBUTES ---")
            for attr, value in ds["tas"].attrs.items():
                print(f"{attr}: {value}")

        # -------------------------
        # SPATIAL EXTENT
        # -------------------------
        if {"lat", "lon"}.issubset(ds.variables):
            lat_min = float(ds["lat"].min())
            lat_max = float(ds["lat"].max())
            lon_min = float(ds["lon"].min())
            lon_max = float(ds["lon"].max())

            print("\n--- SPATIAL EXTENT ---")
            print(f"Latitude range : {lat_min} to {lat_max}")
            print(f"Longitude range: {lon_min} to {lon_max}")

        # -------------------------
        # CRS / PROJECTION CHECK
        # -------------------------
        print("\n--- PROJECTION / CRS INFO ---")
        if "crs" in ds.variables:
            print(ds["crs"].attrs)
        else:
            print("No explicit CRS variable found (CMIP6 data typically use lat/lon, WGS84).")

        ds.close()

    print("\nInspection complete.")


# ======================================================
# SCRIPT ENTRY POINT
# ======================================================
if __name__ == "__main__":
    inspect_netcdf_files(NC_DIR)




