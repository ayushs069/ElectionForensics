# Methodology Notes

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
