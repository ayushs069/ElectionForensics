"""
Module: download_boundaries.py
Purpose: Ensures parliamentary constituency GIS boundaries (pre-2008 and post-2008)
         are available locally in the project directory.
Repository: https://github.com/skthewimp/india-constituency-maps.git
"""

import os
import subprocess
import sys

def ensure_boundaries(repo_dir=None):
    """
    Checks if GIS shapefiles exist locally.
    Clones the repository if not already present.
    """
    if repo_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        repo_dir = os.path.join(base_dir, "india-constituency-maps")
    
    pre_shp = os.path.join(repo_dir, "pre2008", "parliamentary", "india_parliamentary.shp")
    post_shp = os.path.join(repo_dir, "post2008", "parliamentary", "india_parliamentary.shp")
    
    if os.path.exists(pre_shp) and os.path.exists(post_shp):
        print(f"[GIS] Required shapefiles found in: {repo_dir}")
        return repo_dir
    
    print(f"[GIS] Boundary shapefiles not found in {repo_dir}. Cloning repository...")
    repo_url = "https://github.com/skthewimp/india-constituency-maps.git"
    try:
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
        print(f"[GIS] Cloned {repo_url} successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to clone boundary repository: {e}", file=sys.stderr)
        raise
    
    if not (os.path.exists(pre_shp) and os.path.exists(post_shp)):
        raise FileNotFoundError(f"[ERROR] Expected shapefiles missing after clone in {repo_dir}")
    
    return repo_dir

if __name__ == "__main__":
    ensure_boundaries()
