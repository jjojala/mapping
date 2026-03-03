#!/usr/bin/env python3
# crop_from_index_merge_legacy.py
import sys
import pathlib
import pandas as pd
import numpy as np
import laspy
import geopandas as gpd
from shapely import union_all, vectorized, contains_xy
from shapely.geometry import box

def load_polygon(poly_path: pathlib.Path):
    gdf = gpd.read_file(poly_path)
    gdf = gdf[gdf.geometry.notnull()]
    if gdf.empty:
        raise ValueError(f"{poly_path}: ei kelvollisia geometrioita")
    return union_all(gdf.geometry)

def bbox_intersects_selection(index_df: pd.DataFrame, poly_bounds):
    min_x, min_y, max_x, max_y = poly_bounds
    sel = (
        (index_df["max_x"] >= min_x) &
        (index_df["min_x"] <= max_x) &
        (index_df["max_y"] >= min_y) &
        (index_df["min_y"] <= max_y)
    )
    return index_df.loc[sel, "file"].tolist()

def main(index_csv, polygon_file):
    index_csv = pathlib.Path(index_csv)
    polygon_file = pathlib.Path(polygon_file)

    poly = load_polygon(polygon_file)
    poly_bounds = poly.bounds

    df = pd.read_csv(index_csv)
    required = {"file", "min_x", "max_x", "min_y", "max_y"}
    if not required.issubset(df.columns):
        raise ValueError(f"index.csv tulee sisältää sarakkeet: {required}")

    candidates = bbox_intersects_selection(df, poly_bounds)
    for p in candidates:
        path = pathlib.Path(p)
        print(path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Käyttö: python crop_by_geometry.py <index.csv> <rajaus.gpkg|geojson>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
