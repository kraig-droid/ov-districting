import numpy as np
from shapely.ops import unary_union
from shapely.geometry import LineString
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

# Read the boundary file
boundary = gpd.read_file('./docs/boundary_07_30_24.geojson')
num_linestrings = len(boundary.geometry.iloc[0].geoms)
print(f"Number of linestrings: {num_linestrings}")

# Get the MultiLineString geometry
multiline = boundary.geometry.iloc[0]

# Buffer and unbuffer to close small gaps
buffered = multiline.buffer(0.00001)  # Adjust this value as needed
unbuffered = buffered.exterior

# Convert to a single LineString
boundary_without_gaps = LineString(unbuffered.coords)

# Create a new GeoDataFrame
boundary_line_gdf = gpd.GeoDataFrame(geometry=[boundary_without_gaps], crs=boundary.crs)

# Print some info
print(f"Original number of linestrings: {len(multiline.geoms)}")
print(f"New LineString length: {boundary_without_gaps.length:.6f}")
print(f"Is valid: {boundary_without_gaps.is_valid}")
print(f"Is simple: {boundary_without_gaps.is_simple}")
print(f"Is ring: {boundary_without_gaps.is_ring}")


import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

boundary.plot(ax=ax1)
ax1.set_title('Original MultiLineString')

boundary_line_gdf.plot(ax=ax2)
ax2.set_title('Single LineString without gaps')

plt.tight_layout()
plt.show()


# Original MultiLineString
print("Original MultiLineString:")
print(f"Number of linestrings: {len(boundary.geometry.iloc[0].geoms)}")
print(f"Total length: {boundary.geometry.length.iloc[0]:.6f}")
print(f"Bounding box: {boundary.total_bounds}")

print("\nNew LineString:")
print(f"Length: {boundary_without_gaps.length:.6f}")
print(f"Number of points: {len(boundary_without_gaps.coords)}")
print(f"Bounding box: {boundary_line_gdf.total_bounds}")

# Check if the bounding boxes are similar
bb_original = boundary.total_bounds
bb_new = boundary_line_gdf.total_bounds
bb_difference = np.abs(bb_original - bb_new).sum()

print(f"\nSum of absolute differences in bounding box coordinates: {bb_difference:.8f}")
print("(A small value indicates the shapes are similar)")

# Check start and end points
start_point = boundary_without_gaps.coords[0]
end_point = boundary_without_gaps.coords[-1]
print(f"\nStart point: {start_point}")
print(f"End point: {end_point}")
print(f"Start and end points are {'the same' if start_point == end_point else 'different'}")

boundary_gdf = gpd.GeoDataFrame(geometry=[boundary_without_gaps], crs=boundary.crs)

# Write to GeoJSON file
boundary_gdf.to_file("boundary_07_30_24_without_gaps.geojson", driver="GeoJSON")



# Read the candidate blocks
blocks = gpd.read_file('./docs/candidate-blocks-3.geojson')

from shapely.geometry import Polygon

# Create a Polygon from the boundary LineString
boundary_polygon = Polygon(boundary_without_gaps)

# List to store modified blocks
modified_blocks_list = []

# Process each block
for idx, block in blocks.iterrows():
    if boundary_polygon.contains(block.geometry):
        modified_blocks_list.append(block)
    elif boundary_polygon.intersects(block.geometry):
        new_geometry = block.geometry.intersection(boundary_polygon)
        if not new_geometry.is_empty:
            new_block = block.copy()
            new_block.geometry = new_geometry
            modified_blocks_list.append(new_block)
    # Blocks completely outside the boundary are not added to the list

# Create a new GeoDataFrame from the list of modified blocks
modified_blocks = gpd.GeoDataFrame(modified_blocks_list, crs=blocks.crs)

# Print some information
print(f"Original number of blocks: {len(blocks)}")
print(f"Number of blocks after processing: {len(modified_blocks)}")

# Save the modified blocks to a new file
modified_blocks.to_file('modified_candidate_blocks.geojson', driver='GeoJSON')

print("Modified blocks saved to 'modified_candidate_blocks.geojson'")