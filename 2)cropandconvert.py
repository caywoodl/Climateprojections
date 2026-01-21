import xarray as xr
import geopandas as gpd
import rioxarray
from pathlib import Path

# ======================================================
# USER CONFIGURATION
# ======================================================
# Directory containing NetCDF climate files
NC_DIR = Path("path/to/netcdf_directory")

# Path to study-area shapefile (e.g., North Slope Borough)
SHP_PATH = Path("path/to/shapefile.shp")

# Output directory for processed NetCDF files
OUT_DIR = Path("path/to/output_directory")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================
# MAIN PROCESSING FUNCTION
# ======================================================
def process_and_clip_netcdf(nc_dir: Path, shp_path: Path, out_dir: Path):
    """
    Converts CMIP6 temperature data from Kelvin to Celsius,
    standardizes longitude, assigns CRS, and clips to a study
    area geometry.
    """

    # -----------------------------------
    # LOAD SHAPEFILE (WGS84)
    # -----------------------------------
    region = gpd.read_file(shp_path).to_crs(epsg=4326)

    # -----------------------------------
    # FIND NETCDF FILES
    # -----------------------------------
    nc_files = sorted(nc_dir.glob("*.nc"))
    print(f"Found {len(nc_files)} NetCDF files")

    # -----------------------------------
    # LOOP & PROCESS FILES
    # -----------------------------------
    for nc in nc_files:
        print(f"Processing: {nc.name}")

        ds = xr.open_dataset(nc)

        # --------------------------------
        # Handle 0–360 longitude convention
        # --------------------------------
        if ds.lon.max() > 180:
            ds = ds.assign_coords(
                lon=(((ds.lon + 180) % 360) - 180)
            ).sortby("lon")

        # --------------------------------
        # Convert temperature: Kelvin → Celsius
        # --------------------------------
        if "tas" in ds:
            ds["tas"] = ds["tas"] - 273.15
            ds["tas"].attrs.update({
                "units": "degC",
                "long_name": "Near-Surface Air Temperature",
                "standard_name": "air_temperature",
                "comment": "Converted from Kelvin to degrees Celsius"
            })

        # --------------------------------
        # Define spatial structure
        # --------------------------------
        ds = ds.rio.write_crs("EPSG:4326", inplace=True)
        ds = ds.rio.set_spatial_dims(
            x_dim="lon",
            y_dim="lat",
            inplace=True
        )

        # --------------------------------
        # CLIP TO STUDY AREA
        # --------------------------------
        ds_clip = ds.rio.clip(
            region.geometry,
            region.crs,
            drop=True
        )

        # --------------------------------
        # SAVE OUTPUT
        # --------------------------------
        out_name = nc.stem + "_CLIPPED_C.nc"
        out_path = out_dir / out_name
        ds_clip.to_netcdf(out_path)

        ds.close()
        ds_clip.close()

    print("All NetCDF files processed, clipped, and converted to °C.")


# ======================================================
# SCRIPT ENTRY POINT
# ======================================================
if __name__ == "__main__":
    process_and_clip_netcdf(NC_DIR, SHP_PATH, OUT_DIR)




