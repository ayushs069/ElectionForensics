"""
Module: prepare_geodata.py
Purpose: Loads, processes, and provides parliamentary constituency geometries and
         dissolved state boundary polygons for Uttar Pradesh, Bihar, and West Bengal.
         Properly accounts for historical boundary bifurcations:
         - Bihar and Jharkhand separation (pre-2000 vs post-2000)
         - Uttar Pradesh and Uttarakhand separation (pre-2000 vs post-2000)
         - Delimitation eras: pre-2008 (< 2009) vs post-2008 (>= 2009)
"""

import os
import warnings
import geopandas as gpd
import shapely
from shapely.ops import unary_union

warnings.filterwarnings("ignore", category=UserWarning)

STATE_CODE_MAP = {
    "UTTAR PRADESH": {
        "pre2008_undivided": ["S24", "S28"], # UP (80) + Uttarakhand/Uttaranchal (5) = 85
        "pre2008_divided": ["S24"],          # UP (80)
        "post2008": ["S24"],                 # UP post-delimitation (80)
    },
    "BIHAR": {
        "pre2008_undivided": ["S04", "S27"], # Bihar (40) + Jharkhand (14) = 54
        "pre2008_divided": ["S04"],          # Bihar (40)
        "post2008": ["S04"],                 # Bihar post-delimitation (40)
    },
    "WEST BENGAL": {
        "pre2008_undivided": ["S25"],        # WB (42)
        "pre2008_divided": ["S25"],          # WB (42)
        "post2008": ["S25"],                 # WB post-delimitation (42)
    }
}

class GeoDataManager:
    def __init__(self, repo_dir=None):
        if repo_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            repo_dir = os.path.join(base_dir, "india-constituency-maps")
        self.repo_dir = repo_dir
        self.pre_shp_path = os.path.join(repo_dir, "pre2008", "parliamentary", "india_parliamentary.shp")
        self.post_shp_path = os.path.join(repo_dir, "post2008", "parliamentary", "india_parliamentary.shp")
        self._pre_gdf = None
        self._post_gdf = None

    def _load(self):
        if self._pre_gdf is None:
            self._pre_gdf = gpd.read_file(self.pre_shp_path)
            if self._pre_gdf.crs is None or self._pre_gdf.crs.to_epsg() != 4326:
                self._pre_gdf = self._pre_gdf.set_crs(epsg=4326, allow_override=True)
            self._pre_gdf["geometry"] = shapely.make_valid(self._pre_gdf["geometry"])
            self._pre_gdf["PC_NAME_CLEAN"] = self._pre_gdf["PC_NAME"].astype(str).str.upper().str.strip()
            
        if self._post_gdf is None:
            self._post_gdf = gpd.read_file(self.post_shp_path)
            if self._post_gdf.crs is None or self._post_gdf.crs.to_epsg() != 4326:
                self._post_gdf = self._post_gdf.set_crs(epsg=4326, allow_override=True)
            self._post_gdf["geometry"] = shapely.make_valid(self._post_gdf["geometry"])
            self._post_gdf["PC_NAME_CLEAN"] = self._post_gdf["PC_NAME"].astype(str).str.upper().str.strip()

    def get_state_geodata(self, state_name, election_year):
        """
        Returns (constituencies_gdf, state_boundary_geom, era_label).
        """
        self._load()
        state_key = state_name.upper().strip()
        if state_key not in STATE_CODE_MAP:
            raise ValueError(f"State '{state_name}' not supported. Expected one of {list(STATE_CODE_MAP.keys())}")

        is_post_delimitation = (election_year >= 2009)
        is_pre_bifurcation = (election_year < 2004) # 1951 - 1999 were undivided states

        if is_post_delimitation:
            codes = STATE_CODE_MAP[state_key]["post2008"]
            source_gdf = self._post_gdf
            era_label = "Post-2008 Delimitation"
        else:
            if is_pre_bifurcation:
                codes = STATE_CODE_MAP[state_key]["pre2008_undivided"]
                era_label = "Pre-2008 (Undivided State)"
            else:
                codes = STATE_CODE_MAP[state_key]["pre2008_divided"]
                era_label = "Pre-2008 (Post-2000 Bifurcated)"
            source_gdf = self._pre_gdf

        state_constituencies = source_gdf[source_gdf["ST_CODE"].isin(codes)].copy()
        state_constituencies["geometry"] = shapely.make_valid(state_constituencies["geometry"])
        
        # Calculate centroids accurately in projected CRS (EPSG:7755 - India)
        try:
            centroids_proj = state_constituencies.to_crs(epsg=7755).geometry.centroid.to_crs(epsg=4326)
            state_constituencies["centroid_x"] = centroids_proj.x
            state_constituencies["centroid_y"] = centroids_proj.y
        except Exception:
            c = state_constituencies.geometry.centroid
            state_constituencies["centroid_x"] = c.x
            state_constituencies["centroid_y"] = c.y
        
        # Dissolve constituencies to obtain the state outer boundary
        state_boundary_geom = unary_union(state_constituencies["geometry"])
        state_boundary_geom = shapely.make_valid(state_boundary_geom)
        
        return state_constituencies, state_boundary_geom, era_label

if __name__ == "__main__":
    manager = GeoDataManager()
    for s in ["UTTAR PRADESH", "BIHAR", "WEST BENGAL"]:
        for y in [1977, 2004, 2019]:
            gdf, bnd, era = manager.get_state_geodata(s, y)
            print(f"{s} ({y}) [{era}]: {len(gdf)} constituencies, Boundary: {bnd.geom_type}, Centroids: ({gdf.centroid_x.mean():.2f}, {gdf.centroid_y.mean():.2f})")
