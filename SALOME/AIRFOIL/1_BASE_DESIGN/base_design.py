import salome
import GEOM
from salome.geom import geomBuilder
import SMESH
from salome.smesh import smeshBuilder
import math
import logging
from datetime import datetime

# Configuration
output_file_path = "base_design.stl"
log_file_path = "base_design.log"
thickness = 1  # mm
radius = 25.0  # mm
pitch_angle = 5.0  # degrees
cone_angle = 5.0  # degrees


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

# Initialize SALOME
salome.salome_init()

# Create geometry and mesh builders
geompy = geomBuilder.New()
smesh = smeshBuilder.New()

def create_probe_geometry(thickness_mm, radius_mm):
    logging.info(f"Creating probe geometry - thickness: {thickness_mm}mm, radius: {radius_mm}mm")
    
    # Create curved edges
    # Bottom-left corner arc
    center_bl = geompy.MakeVertex(radius_mm, radius_mm, 0)
    start_bl = geompy.MakeVertex(0, radius_mm, 0)
    end_bl = geompy.MakeVertex(radius_mm, 0, 0)
    arc_bl = geompy.MakeArcCenter(center_bl, start_bl, end_bl, False)
    
    # 180-degree jutting section end - semicircle from (175,0) through (200,25) to (175,50)
    start_jutting = geompy.MakeVertex(175, 0, 0)
    end_jutting = geompy.MakeVertex(175, 50, 0)
    intermediate_jutting = geompy.MakeVertex(200, 25, 0)
    arc_jutting_end = geompy.MakeArc(start_jutting, intermediate_jutting, end_jutting)
    
    # Inner concave corner - 90° quarter-circle
    start_inner = geompy.MakeVertex(100+radius_mm, 50, 0)
    end_inner = geompy.MakeVertex(100, 50+radius_mm, 0)
    intermediate_inner = geompy.MakeVertex(100+radius_mm*0.293, 50+radius_mm*0.293, 0)
    arc_inner = geompy.MakeArc(start_inner, intermediate_inner, end_inner)
    
    # Top-right corner
    center_trs = geompy.MakeVertex(100-radius_mm, 100-radius_mm, 0)
    start_trs = geompy.MakeVertex(100, 100-radius_mm, 0)
    end_trs = geompy.MakeVertex(100-radius_mm, 100, 0)
    arc_trs = geompy.MakeArcCenter(center_trs, start_trs, end_trs, False)
    
    # Top-left corner
    center_tl = geompy.MakeVertex(radius_mm, 100-radius_mm, 0)
    start_tl = geompy.MakeVertex(radius_mm, 100, 0)
    end_tl = geompy.MakeVertex(0, 100-radius_mm, 0)
    arc_tl = geompy.MakeArcCenter(center_tl, start_tl, end_tl, False)
        
    # Create straight edges
    # Bottom edge
    p_bottom_start = geompy.MakeVertex(radius_mm, 0, 0)
    p_bottom_end = geompy.MakeVertex(175, 0, 0)
    edge_bottom = geompy.MakeEdge(p_bottom_start, p_bottom_end)
    
    # Top jutting edge
    p_top_jut_start = geompy.MakeVertex(175, 50, 0)
    p_top_jut_end = geompy.MakeVertex(100+radius_mm, 50, 0)
    edge_top_jut = geompy.MakeEdge(p_top_jut_start, p_top_jut_end)
    
    # Top square edge
    p_top_sq_start = geompy.MakeVertex(100-radius_mm, 100, 0)
    p_top_sq_end = geompy.MakeVertex(radius_mm, 100, 0)
    edge_top_sq = geompy.MakeEdge(p_top_sq_start, p_top_sq_end)
    
    # Left edge
    p_left_start = geompy.MakeVertex(0, 100-radius_mm, 0)
    p_left_end = geompy.MakeVertex(0, radius_mm, 0)
    edge_left = geompy.MakeEdge(p_left_start, p_left_end)
        
    # Assemble edges to create wire
    all_edges = [
        arc_bl, edge_bottom, arc_jutting_end, edge_top_jut,
        arc_inner, arc_trs, edge_top_sq, arc_tl, edge_left
    ]
    
    # Create wire and face
    wire = geompy.MakeWire(all_edges)
    l_shaped_face = geompy.MakeFace(wire, 1)
    
    # Extrude to create 3D solid
    vector = geompy.MakeVectorDXDYDZ(0, 0, thickness_mm)
    probe_3d = geompy.MakePrismVecH(l_shaped_face, vector, thickness_mm)
    
    logging.info("Base probe geometry created successfully")
    return probe_3d

def add_flight_angles(geometry, pitch_degrees, cone_degrees):
    logging.info(f"Applying flight angles - pitch: {pitch_degrees}, cone: {cone_degrees}")
    
    # Apply pitch angle (rotation around X-axis)
    x_axis = geompy.MakeVectorDXDYDZ(1, 0, 0)
    pitch_rad = math.radians(pitch_degrees)
    pitch_rotated = geompy.MakeRotation(geometry, x_axis, pitch_rad)
    
    # Apply cone angle (rotation around Y-axis)
    y_axis = geompy.MakeVectorDXDYDZ(0, 1, 0)
    cone_rad = math.radians(cone_degrees)
    final_shape = geompy.MakeRotation(pitch_rotated, y_axis, cone_rad)
    
    logging.info("Flight angles applied successfully")
    return final_shape

def create_final_mesh_and_export(geometry, output_file):
    logging.info(f"Creating mesh and exporting to: {output_file}")
    
    # Create and configure mesh
    mesh = smesh.Mesh(geometry, "Probe_Mesh")
    
    # 3D mesh settings
    algo_3d = mesh.Tetrahedron()
    algo_3d.MaxElementVolume(200.0)
    
    # 2D mesh settings
    algo_2d = mesh.Triangle()
    algo_2d.MaxElementArea(50.0)
    
    # 1D mesh settings
    algo_1d = mesh.Segment()
    algo_1d.NumberOfSegments(8)
    
    # Generate mesh and export STL
    if mesh.Compute():
        mesh.ExportSTL(output_file)
        logging.info(f"STL file successfully exported to: {output_file}")
        return True
    else:
        logging.error("Mesh generation failed")
        return False

if __name__ == "__main__":
    logging.info("=== Starting Probe Design Generation ===")
    probe_geometry = create_probe_geometry(thickness, radius)
    final_geometry = add_flight_angles(probe_geometry, pitch_angle, cone_angle)
    success = create_final_mesh_and_export(final_geometry, output_file_path)
    if success:
        logging.info("=== Probe Design Generation Completed Successfully ===")
    else:
        logging.error("=== Probe Design Generation Failed ===")
        exit(1)
