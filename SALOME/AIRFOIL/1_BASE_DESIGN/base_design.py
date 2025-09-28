#!/usr/bin/env python3
"""
SALOME script to create a probe design STL file.
Creates a 3D probe with 5mm thickness based on a modified rectangle shape.

Design specifications:
- Start with 200mm x 100mm rectangle
- Remove 100mm x 50mm section from one corner  
- Smooth all corners (including inverse) with 25mm radius
- Extrude to 5mm thickness
"""

import salome
import GEOM
from salome.geom import geomBuilder
import SMESH
from salome.smesh import smeshBuilder

# Initialize SALOME
salome.salome_init()

# Create geometry and mesh builders
geompy = geomBuilder.New()
smesh = smeshBuilder.New()

def create_probe_design(output_file="probe_design.stl"):
    # Design parameters
    thickness = 5.0  # mm
    radius = 25.0  # mm
    
    # Create curved edges
    # Bottom-left corner arc
    center_bl = geompy.MakeVertex(radius, radius, 0)
    start_bl = geompy.MakeVertex(0, radius, 0)
    end_bl = geompy.MakeVertex(radius, 0, 0)
    arc_bl = geompy.MakeArcCenter(center_bl, start_bl, end_bl, False)
    
    # 180-degree jutting section end - semicircle from (175,0) through (200,25) to (175,50)
    start_jutting = geompy.MakeVertex(175, 0, 0)
    end_jutting = geompy.MakeVertex(175, 50, 0)
    intermediate_jutting = geompy.MakeVertex(200, 25, 0)
    arc_jutting_end = geompy.MakeArc(start_jutting, intermediate_jutting, end_jutting)
    
    # Inner concave corner - 90° quarter-circle
    start_inner = geompy.MakeVertex(100+radius, 50, 0)
    end_inner = geompy.MakeVertex(100, 50+radius, 0)
    intermediate_inner = geompy.MakeVertex(100+radius*0.293, 50+radius*0.293, 0)
    arc_inner = geompy.MakeArc(start_inner, intermediate_inner, end_inner)
    
    # Top-right corner
    center_trs = geompy.MakeVertex(100-radius, 100-radius, 0)
    start_trs = geompy.MakeVertex(100, 100-radius, 0)
    end_trs = geompy.MakeVertex(100-radius, 100, 0)
    arc_trs = geompy.MakeArcCenter(center_trs, start_trs, end_trs, False)
    
    # Top-left corner
    center_tl = geompy.MakeVertex(radius, 100-radius, 0)
    start_tl = geompy.MakeVertex(radius, 100, 0)
    end_tl = geompy.MakeVertex(0, 100-radius, 0)
    arc_tl = geompy.MakeArcCenter(center_tl, start_tl, end_tl, False)
        
    # Create straight edges
    # Bottom edge
    p_bottom_start = geompy.MakeVertex(radius, 0, 0)
    p_bottom_end = geompy.MakeVertex(175, 0, 0)
    edge_bottom = geompy.MakeEdge(p_bottom_start, p_bottom_end)
    
    # Top jutting edge
    p_top_jut_start = geompy.MakeVertex(175, 50, 0)
    p_top_jut_end = geompy.MakeVertex(100+radius, 50, 0)
    edge_top_jut = geompy.MakeEdge(p_top_jut_start, p_top_jut_end)
    
    # Top square edge
    p_top_sq_start = geompy.MakeVertex(100-radius, 100, 0)
    p_top_sq_end = geompy.MakeVertex(radius, 100, 0)
    edge_top_sq = geompy.MakeEdge(p_top_sq_start, p_top_sq_end)
    
    # Left edge
    p_left_start = geompy.MakeVertex(0, 100-radius, 0)
    p_left_end = geompy.MakeVertex(0, radius, 0)
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
    vector = geompy.MakeVectorDXDYDZ(0, 0, thickness)
    probe_3d = geompy.MakePrismVecH(l_shaped_face, vector, thickness)
    
    # Create and configure mesh
    mesh = smesh.Mesh(probe_3d, "Probe_Mesh")
    
    algo_3d = mesh.Tetrahedron()
    algo_3d.MaxElementVolume(200.0)
    
    algo_2d = mesh.Triangle()
    algo_2d.MaxElementArea(50.0)
    
    algo_1d = mesh.Segment()
    algo_1d.NumberOfSegments(8)
    
    # Generate mesh and export STL
    if mesh.Compute():
        mesh.ExportSTL(output_file)
        return True
    return False

if __name__ == "__main__":
    create_probe_design("probe_design.stl")
