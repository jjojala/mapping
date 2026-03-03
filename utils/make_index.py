import sys
import laspy
import pandas as pd
from pathlib import Path

def print_usage():
    print(f"Usage: {Path(sys.argv[0]).name} <output_index.csv> <las_file1.laz> [<las_file2.laz> ...]")
    print(f"   or: {Path(sys.argv[0]).name} <output_index.csv> --dir <laz_directory>")
    sys.exit(1)

def collect_laz_files_from_dir(directory):
    return list(Path(directory).glob("*.laz"))

def main():
    if len(sys.argv) < 3:
        print_usage()

    bbox_file = sys.argv[1]

    # Tarkista --dir optio
    if sys.argv[2] == "--dir":
        if len(sys.argv) != 4:
            print_usage()
        las_dir = Path(sys.argv[3])
        if not las_dir.is_dir():
            print(f"Error: {las_dir} is not a directory.")
            sys.exit(2)
        las_files = collect_laz_files_from_dir(las_dir)
        if not las_files:
            print(f"No .laz files found in {las_dir}")
            sys.exit(3)
    else:
        las_files = [Path(f) for f in sys.argv[2:]]

    print("Luodaan LAS-tiedostojen bounding box -indeksi...")

    bbox_list = []
    for las_path in las_files:
        with laspy.open(las_path) as las:
            min_x, max_x = las.header.mins[0], las.header.maxs[0]
            min_y, max_y = las.header.mins[1], las.header.maxs[1]
            bbox_list.append({
                "file": str(las_path.resolve()),
                "min_x": min_x,
                "max_x": max_x,
                "min_y": min_y,
                "max_y": max_y
            })

    pd.DataFrame(bbox_list).to_csv(bbox_file, index=False)
    print(f"Bounding box -indeksi tallennettu {bbox_file}")

if __name__ == "__main__":
    main()
