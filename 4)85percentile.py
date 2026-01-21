import rasterio
import numpy as np
from pathlib import Path
from tqdm import tqdm
import re

# ======================================================
# USER CONFIGURATION
# ======================================================
# Directory containing annual TDD GeoTIFFs
TDD_DIR = Path("path/to/TDD_GeoTIFFs")

# Output directory for hotspot rasters
OUTPUT_DIR = TDD_DIR / "TDD_hotspots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================
# MAIN FUNCTION
# ======================================================
def create_tdd_hotspots(tdd_dir: Path, output_dir: Path, percentile: float = 85):
    """
    Binarizes annual TDD GeoTIFFs using the specified percentile
    threshold to generate hotspot rasters.
    """

    # -----------------------------------
    # FIND ALL TDD GEOTIFFS
    # -----------------------------------
    tif_files = sorted(tdd_dir.glob("*.tif"))
    print(f"Found {len(tif_files)} TDD GeoTIFFs")

    # -----------------------------------
    # LOOP OVER EACH YEAR
    # -----------------------------------
    for tif in tqdm(tif_files, desc=f"Creating {percentile}th percentile hotspot rasters"):

        # Extract year from filename
        match = re.search(r"(20\d{2})", tif.name)
        if match:
            year = match.group(1)
        else:
            year = tif.stem  # fallback

        # Open TDD raster
        with rasterio.open(tif) as src:
            tdd_array = src.read(1)
            profile = src.profile  # preserve metadata

        # Calculate percentile threshold
        threshold = np.nanpercentile(tdd_array, percentile)

        # Binarize: 1 if >= percentile threshold, else 0
        hotspot = np.where(tdd_array >= threshold, 1, 0).astype(np.uint8)

        # Update profile for single-band binary output
        profile.update(dtype=rasterio.uint8, count=1, compress="lzw")

        # Save output
        out_file = output_dir / f"TDD_hotspot_{year}.tif"
        with rasterio.open(out_file, 'w', **profile) as dst:
            dst.write(hotspot, 1)

    print(f"✅ {percentile}th percentile hotspot GeoTIFFs created for all years in: {output_dir}")


# ======================================================
# SCRIPT ENTRY POINT
# ======================================================
if __name__ == "__main__":
    create_tdd_hotspots(TDD_DIR, OUTPUT_DIR)

