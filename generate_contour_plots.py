"""
Election Margin Contour Plot Generator
Generates 54 geographically accurate contour plots (3 states × 18 years)
States: Uttar Pradesh, Bihar, West Bengal
Years: 1951-2024 (18 elections)

Uses actual parliamentary constituency GIS boundaries from india-constituency-maps.
Pre-2008 boundaries for elections before 2009; post-2008 boundaries for 2009+.
Contour variable: margin = winner_votes - runnerup_votes
Interpolation: Inverse Distance Weighting (IDW)
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
from scipy.spatial import cKDTree
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely.validation import make_valid
import shapely
import re
from difflib import SequenceMatcher

warnings.filterwarnings('ignore')

# -----------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------
BASE_DIR = r"d:\sem-5_projects\PRJ-3"
DATA_CSV = os.path.join(BASE_DIR, "data", "processed", "alltime_csv_india.csv")
MAPS_DIR = os.path.join(BASE_DIR, "india-constituency-maps")
OUTPUT_BASE = os.path.join(BASE_DIR, "outputs", "Contour_Plots")

ELECTION_YEARS = [1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984,
                   1989, 1991, 1996, 1998, 1999, 2004, 2009, 2014, 2019, 2024]

STATE_CONFIGS = [
    ("UTTAR PRADESH",  "Uttar Pradesh", "Uttar_Pradesh", "S24", "S24"),
    ("BIHAR",          "Bihar",         "Bihar",         "S04", "S04"),
    ("WEST BENGAL",    "West Bengal",   "West_Bengal",   "S25", "S25"),
]

JET_COLORS = ['#0000FF', '#00FFFF', '#00FF00', '#FFFF00', '#FF0000']
CMAP_JET = LinearSegmentedColormap.from_list('election_jet', JET_COLORS, N=256)

DPI = 600
GRID_POINTS = 300


# -----------------------------------------------------------------
# NAME NORMALISATION
# -----------------------------------------------------------------
# Pre-1962 constituency names used district qualifiers like:
#   "BANARAS DISTRICT (CENTRAL)", "ALLAHABAD DISTT (EAST) CUM JAUNPUR DISTT (WEST)"
# Strategy: extract the primary city/district name (first meaningful token)

_STOP_WORDS = {'DISTRICT', 'DISTT', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'CENTRAL',
               'CUM', 'AND', 'OF', 'THE', 'AREA', 'REGION', 'RURAL', 'URBAN',
               'SADAR', 'TOWN', 'CITY', 'CONSTITUENCY', 'PARLIAMENTARY', 'PART'}

def normalise(name: str) -> str:
    name = str(name).upper().strip()
    name = re.sub(r'[()&\-]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    spelling_map = {
        'BAHARAICH': 'BAHRAICH',
        'BAHARAMPUR': 'BERHAMPORE',
        'COOCHBEHAR': 'COOCH BEHAR',
        'BADAUN': 'BUDAUN',
        'BARRACKPORE': 'BARRACKPUR',
        'ARAMBAGH': 'ARAMBAG',
        'BARDHAMAN DURGAPUR': 'BURDWAN DURGAPUR',
        'BARDHAMAN PURBA': 'BURDWAN PURBA',
        'BURDWAN   DURGAPUR': 'BURDWAN DURGAPUR',
        'BURDWAN - DURGAPUR': 'BURDWAN DURGAPUR',
        'BANARAS': 'VARANASI',
        'BENARES': 'VARANASI',
        'BANARAS DISTRICT CENTRAL': 'VARANASI',
        'BANARAS DISTRICT EAST': 'VARANASI',
        'BANARAS DISTRICT WEST': 'VARANASI',
        'FYZABAD': 'FAIZABAD',
        'FAIZABAD': 'FAIZABAD',
    }
    return spelling_map.get(name, name)


def extract_primary(name: str) -> str:
    """Extract the first non-stopword token — useful for old district-based names."""
    n = normalise(name)
    tokens = n.split()
    primary = [t for t in tokens if t not in _STOP_WORDS]
    return primary[0] if primary else n


def fuzzy_score(a: str, b: str) -> float:
    na, nb = normalise(a), normalise(b)
    if na == nb:
        return 1.0
    seq = SequenceMatcher(None, na, nb).ratio()
    ta = set(na.split())
    tb = set(nb.split())
    overlap = len(ta & tb) / max(len(ta), len(tb)) if ta and tb else 0
    # Also try primary-token matching for old district names
    pa, pb = extract_primary(a), extract_primary(b)
    primary_score = 1.0 if pa == pb else SequenceMatcher(None, pa, pb).ratio() * 0.85
    return max(seq, overlap * 0.9, primary_score)


def best_match(csv_name: str, shp_names: list, threshold: float = 0.60):
    best_score, best_name = 0, None
    for sn in shp_names:
        s = fuzzy_score(csv_name, sn)
        if s > best_score:
            best_score, best_name = s, sn
    if best_score >= threshold:
        return best_name, best_score
    return None, best_score


# -----------------------------------------------------------------
# IDW INTERPOLATION
# -----------------------------------------------------------------
def idw_interpolate(points_xy, values, grid_x, grid_y, power=2):
    grid_xy = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    tree = cKDTree(points_xy)
    k = min(len(values), 12)
    distances, indices = tree.query(grid_xy, k=k)
    distances = np.where(distances == 0, 1e-10, distances)
    weights = 1.0 / (distances ** power)
    weights_norm = weights / weights.sum(axis=1, keepdims=True)
    result = (weights_norm * values[indices]).sum(axis=1)
    return result.reshape(grid_x.shape)


# -----------------------------------------------------------------
# MASK GRID TO POLYGON
# -----------------------------------------------------------------
def mask_grid_to_polygon(grid_x, grid_y, z_grid, polygon):
    flat = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    try:
        # Shapely 2.x vectorised contains
        pts = shapely.points(flat[:, 0], flat[:, 1])
        mask = shapely.contains(polygon, pts)
    except Exception:
        try:
            from shapely.vectorized import contains as sv_contains
            mask = sv_contains(polygon, flat[:, 0], flat[:, 1])
        except Exception:
            mask = np.array([polygon.contains(Point(x, y)) for x, y in flat])
    z = z_grid.copy().astype(float)
    z[~mask.reshape(grid_x.shape)] = np.nan
    return z


# -----------------------------------------------------------------
# LOAD SHAPEFILE  (with geometry repair)
# -----------------------------------------------------------------
def load_shapefile(state_code: str, pre_post: str) -> gpd.GeoDataFrame:
    path = os.path.join(MAPS_DIR, pre_post, "parliamentary",
                        f"{state_code}_PC.shp")
    gdf = gpd.read_file(path)
    # Fix any invalid geometries (buffer(0) or make_valid)
    def fix_geom(g):
        if g is None:
            return g
        if not g.is_valid:
            g = make_valid(g)
        if not g.is_valid:
            g = g.buffer(0)
        return g
    gdf['geometry'] = gdf['geometry'].apply(fix_geom)
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()
    gdf['centroid_x'] = gdf.geometry.centroid.x
    gdf['centroid_y'] = gdf.geometry.centroid.y
    return gdf


# -----------------------------------------------------------------
# MATCH ELECTION DATA TO GIS
# -----------------------------------------------------------------
def match_election_to_gis(df_election, gdf, state_display, year):
    lookup = {}
    for _, row in gdf.iterrows():
        key = normalise(row['PC_NAME'])
        lookup[key] = {
            'x': row['centroid_x'], 'y': row['centroid_y'],
            'raw_name': row['PC_NAME'],
        }
    shp_names = list(gdf['PC_NAME'])
    records, unmatched = [], []

    for _, row in df_election.iterrows():
        csv_name = row['cst_n']
        margin = row['margin']
        n_csv = normalise(csv_name)

        if n_csv in lookup:
            info = lookup[n_csv]
            records.append({'cst_n': csv_name, 'margin': margin,
                            'lon': info['x'], 'lat': info['y'],
                            'matched_gis_name': info['raw_name'], 'match_score': 1.0})
        else:
            matched_raw, score = best_match(csv_name, shp_names, threshold=0.65)
            if matched_raw:
                info = lookup[normalise(matched_raw)]
                records.append({'cst_n': csv_name, 'margin': margin,
                                'lon': info['x'], 'lat': info['y'],
                                'matched_gis_name': info['raw_name'],
                                'match_score': round(score, 3)})
            else:
                unmatched.append({'state': state_display, 'year': year,
                                  'cst_n': csv_name, 'best_score': round(score, 3)})
    return pd.DataFrame(records), unmatched


# -----------------------------------------------------------------
# MAKE CONTOUR PLOT
# -----------------------------------------------------------------
def make_contour_plot(df_matched, gdf, state_display, year, vmin, vmax, out_path):
    # Ensure all geometries are valid before union
    valid_geoms = [make_valid(g) if g is not None and not g.is_valid else g
                   for g in gdf.geometry if g is not None]
    state_poly = unary_union(valid_geoms)
    minx, miny, maxx, maxy = state_poly.bounds
    px = (maxx - minx) * 0.02
    py = (maxy - miny) * 0.02
    xi = np.linspace(minx - px, maxx + px, GRID_POINTS)
    yi = np.linspace(miny - py, maxy + py, GRID_POINTS)
    grid_x, grid_y = np.meshgrid(xi, yi)

    pts = df_matched[['lon', 'lat']].values
    vals = df_matched['margin'].values

    if len(pts) < 3:
        print(f"  [SKIP] {state_display} {year}: only {len(pts)} matched points")
        return

    zi = idw_interpolate(pts, vals, grid_x, grid_y, power=2)
    zi = mask_grid_to_polygon(grid_x, grid_y, zi, state_poly)

    fig, ax = plt.subplots(figsize=(10, 11), facecolor='white')
    ax.set_facecolor('white')

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    levels = np.linspace(vmin, vmax, 21)

    cf = ax.contourf(grid_x, grid_y, zi, levels=levels, cmap=CMAP_JET,
                     norm=norm, alpha=0.88, extend='both')
    ax.contour(grid_x, grid_y, zi, levels=levels[::4], colors='black',
               linewidths=0.3, alpha=0.35)

    # Constituency boundaries
    gdf.boundary.plot(ax=ax, edgecolor='black', linewidth=0.45, zorder=3)

    # State outline
    state_gdf = gpd.GeoDataFrame(geometry=[state_poly], crs=gdf.crs)
    state_gdf.boundary.plot(ax=ax, edgecolor='black', linewidth=1.8, zorder=4)

    # High / Low markers
    high_idx = df_matched['margin'].idxmax()
    low_idx  = df_matched['margin'].idxmin()
    hr = df_matched.loc[high_idx]
    lr = df_matched.loc[low_idx]

    ax.scatter(hr['lon'], hr['lat'], color='red', s=130, marker='*',
               zorder=6, edgecolors='darkred', linewidths=0.6)
    ax.annotate(
        f"▲ {hr['cst_n']}\n{int(hr['margin']):,}",
        xy=(hr['lon'], hr['lat']), xytext=(8, 6), textcoords='offset points',
        fontsize=5.5, color='darkred', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                  edgecolor='red', alpha=0.88, linewidth=0.7), zorder=7)

    ax.scatter(lr['lon'], lr['lat'], color='blue', s=130, marker='*',
               zorder=6, edgecolors='darkblue', linewidths=0.6)
    ax.annotate(
        f"▼ {lr['cst_n']}\n{int(lr['margin']):,}",
        xy=(lr['lon'], lr['lat']), xytext=(8, -14), textcoords='offset points',
        fontsize=5.5, color='darkblue', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                  edgecolor='blue', alpha=0.88, linewidth=0.7), zorder=7)

    # Scatter centroids
    ax.scatter(df_matched['lon'], df_matched['lat'],
               c=df_matched['margin'], cmap=CMAP_JET, norm=norm,
               s=18, zorder=5, edgecolors='black', linewidths=0.3)

    # Colorbar
    cbar = fig.colorbar(cf, ax=ax, fraction=0.032, pad=0.01, shrink=0.85)
    cbar.set_label('Vote Margin (Winner − Runner-up)', fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    ticks = np.linspace(vmin, vmax, 6)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f'{int(v):,}' for v in ticks])

    # Legend
    legend_els = [
        Patch(facecolor='red',  label=f'Highest: {hr["cst_n"]} ({int(hr["margin"]):,})'),
        Patch(facecolor='blue', label=f'Lowest:  {lr["cst_n"]} ({int(lr["margin"]):,})'),
    ]
    ax.legend(handles=legend_els, loc='lower left', fontsize=5.5,
              framealpha=0.9, edgecolor='grey')

    bnd = "Pre-2008 boundaries" if year < 2009 else "Post-2008 boundaries"
    ax.set_title(
        f"{state_display} — {year} General Election\n"
        f"Vote Margin Contour  ({len(df_matched)} constituencies | {bnd})",
        fontsize=10, fontweight='bold', pad=10)
    ax.set_xlabel("Longitude", fontsize=7)
    ax.set_ylabel("Latitude",  fontsize=7)
    ax.tick_params(labelsize=6)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', linewidth=0.3, alpha=0.4)

    plt.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {os.path.basename(out_path)}")


# =================================================================
# MAIN
# =================================================================
print("=" * 60)
print("Election Margin Contour Plot Generator")
print("=" * 60)

print("\nLoading election data ...")
df_all = pd.read_csv(DATA_CSV)
df_all['margin'] = df_all['winner_votes'] - df_all['runnerup_votes']

print("Pre-loading shapefiles ...")
shapefiles = {}
for csv_state, display_name, folder_name, pre_code, post_code in STATE_CONFIGS:
    shapefiles[(csv_state, 'pre')]  = load_shapefile(pre_code, 'pre2008')
    shapefiles[(csv_state, 'post')] = load_shapefile(post_code, 'post2008')
    print(f"  {display_name}: pre2008({pre_code}) | post2008({post_code})")

print("\nComputing colour scale ranges ...")
state_vranges = {}
for csv_state, display_name, *_ in STATE_CONFIGS:
    df_s = df_all[(df_all['state_n'] == csv_state) & (df_all['yr'].isin(ELECTION_YEARS))]
    vmin = float(df_s['margin'].quantile(0.02))
    vmax = float(df_s['margin'].quantile(0.98))
    state_vranges[csv_state] = (vmin, vmax)
    print(f"  {display_name}: [{vmin:,.0f} – {vmax:,.0f}]")

all_unmatched = []
summary_rows  = []

print("\nGenerating 54 contour plots ...\n")
plot_n = 0
for csv_state, display_name, folder_name, pre_code, post_code in STATE_CONFIGS:
    out_dir = os.path.join(OUTPUT_BASE, folder_name)
    os.makedirs(out_dir, exist_ok=True)
    vmin, vmax = state_vranges[csv_state]

    for year in ELECTION_YEARS:
        out_file = os.path.join(out_dir, f"{folder_name}_{year}_contour.png")
        # Skip if already successfully saved
        if os.path.exists(out_file) and os.path.getsize(out_file) > 10000:
            print(f"  [SKIP-EXISTS] {display_name} {year}")
            plot_n += 1
            continue

        bkey = 'post' if year >= 2009 else 'pre'
        gdf  = shapefiles[(csv_state, bkey)]
        df_yr = df_all[(df_all['state_n'] == csv_state) & (df_all['yr'] == year)].copy()

        if df_yr.empty:
            print(f"  [WARN] No data: {display_name} {year}")
            continue

        df_matched, unmatched = match_election_to_gis(df_yr, gdf, display_name, year)
        all_unmatched.extend(unmatched)

        if df_matched.empty:
            print(f"  [SKIP] {display_name} {year}: no matches")
            continue

        hr = df_matched.loc[df_matched['margin'].idxmax()]
        lr = df_matched.loc[df_matched['margin'].idxmin()]
        summary_rows.append({
            'state': display_name, 'year': year,
            'n_matched': len(df_matched), 'n_unmatched': len(unmatched),
            'highest_cst': hr['cst_n'], 'highest_margin': int(hr['margin']),
            'highest_gis': hr['matched_gis_name'],
            'lowest_cst': lr['cst_n'],  'lowest_margin': int(lr['margin']),
            'lowest_gis':  lr['matched_gis_name'],
            'boundary': f"{'pre' if year < 2009 else 'post'}2008",
        })

        print(f"[{plot_n+1:02d}] {display_name} {year}: "
              f"{len(df_matched)}/{len(df_yr)} matched ({len(unmatched)} unmatched)")
        make_contour_plot(df_matched, gdf, display_name, year, vmin, vmax, out_file)
        plot_n += 1

# -----------------------------------------------------------------
# SAVE REPORTS
# -----------------------------------------------------------------
reports_dir = os.path.join(OUTPUT_BASE, "Reports")
os.makedirs(reports_dir, exist_ok=True)

pd.DataFrame(summary_rows).to_csv(
    os.path.join(reports_dir, "margin_summary.csv"), index=False)
print(f"\nSaved: Reports/margin_summary.csv ({len(summary_rows)} rows)")

if all_unmatched:
    pd.DataFrame(all_unmatched).to_csv(
        os.path.join(reports_dir, "unmatched_constituencies.csv"), index=False)
    print(f"Saved: Reports/unmatched_constituencies.csv ({len(all_unmatched)} rows)")

NOTES = """# Methodology Notes

## Boundary Usage
- 1951-2004: Pre-2008 parliamentary boundaries (pre2008/parliamentary/)
- 2009-2024: Post-2008 parliamentary boundaries (post2008/parliamentary/)

## Historical Splits
### Bihar / Jharkhand (split 2000)
Pre-2000 Bihar data includes Jharkhand constituencies. Pre-2008 Bihar shapefile
(S04, 40 PCs) covers the undivided Bihar. Jharkhand constituencies in the CSV
for 1951-1999 may be unmatched against the Bihar shapefile.

### UP / Uttarakhand (split 2000)
Pre-2000 UP data may include Uttarakhand constituencies. The pre-2008 UP shapefile
(S24, 80 PCs) covers the post-split boundaries; old districts like Almora, Nainital,
Garhwal are present as unmatched for early elections.

## Name Matching
1. Exact: normalised string equality
2. Token overlap: Jaccard similarity on word tokens (weight 0.9)
3. Fuzzy: SequenceMatcher ratio
Threshold: 0.65. Unmatched below threshold recorded in unmatched_constituencies.csv.

## Interpolation
IDW (power=2, k=12 nearest neighbours), 300x300 grid, clipped to state polygon.

## Colour Scale
Consistent per state across all 18 years (2nd-98th percentile of all years).
Jet palette: Blue (low) -> Cyan -> Green -> Yellow -> Red (high).

## Approximations
- Centroids are geometric, not population-weighted.
- IDW creates smooth surfaces; true margins have sharp political boundaries.
- Old constituency names (1951-1967) may use district aggregates.
"""

with open(os.path.join(reports_dir, "methodology_notes.md"), 'w') as f:
    f.write(NOTES)
print("Saved: Reports/methodology_notes.md")

# Final tally
total_plots = sum(1 for r, d, files in os.walk(OUTPUT_BASE)
                  for f in files if f.endswith('.png'))
print(f"\n{'='*60}")
print(f"COMPLETE. Plots generated: {plot_n}")
print(f"PNG files in output:       {total_plots}")
print(f"Expected:                  54")
print(f"Output: {OUTPUT_BASE}")
print(f"{'='*60}")
