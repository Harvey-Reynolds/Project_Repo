#!/usr/bin/env python3
"""
SALOME script to create a 2D square and export it as STL file.
This script should be run within SALOME environment or with SALOME Python.
"""

import sys
import salome

# Initialize SALOME
salome.salome_init()

# Import required modules
import GEOM
from salome.geom import geomBuilder
import SMESH
from salome.smesh import smeshBuilder

# Create geometry builder
geompy = geomBuilder.New()

# Create mesh builder  
smesh = smeshBuilder.New()

def create_2d_square(side_length=10.0, output_file="square_2d.stl"):
    """
    Create a 2D square geometry and export as STL file.
    
    Parameters:
    side_length (float): Side length of the square
    output_file (str): Output STL filename
    """
    
    try:
        # Create vertices for the square
        vertex1 = geompy.MakeVertex(0, 0, 0)
        vertex2 = geompy.MakeVertex(side_length, 0, 0)
        vertex3 = geompy.MakeVertex(side_length, side_length, 0)
        vertex4 = geompy.MakeVertex(0, side_length, 0)
        
        # Create edges
        edge1 = geompy.MakeEdge(vertex1, vertex2)
        edge2 = geompy.MakeEdge(vertex2, vertex3)
        edge3 = geompy.MakeEdge(vertex3, vertex4)
        edge4 = geompy.MakeEdge(vertex4, vertex1)
        
        # Create wire from edges
        wire = geompy.MakeWire([edge1, edge2, edge3, edge4])
        
        # Create face from wire
        square_face = geompy.MakeFace(wire, 1)
        
        # Add to study for visualization
        geompy.addToStudy(square_face, "Square_2D")
        
        print(f"Created 2D square with side length: {side_length}")
        
        # Create mesh
        mesh = smesh.Mesh(square_face, "SquareMesh")
        
        # Define mesh algorithms
        # 2D algorithm - Triangle (Mefisto)
        algo_2d = mesh.Triangle()
        
        # Set hypothesis for mesh density
        hyp_2d = algo_2d.MaxElementArea(1.0)  # Adjust for mesh density
        
        # Generate mesh
        if mesh.Compute():
            print("Mesh generated successfully")
        else:
            print("Error: Failed to generate mesh")
            return False
            
        # Export to STL
        try:
            mesh.ExportSTL(output_file)
            print(f"STL file exported successfully: {output_file}")
            return True
        except Exception as e:
            print(f"Error exporting STL: {e}")
            return False
            
    except Exception as e:
        print(f"Error creating geometry: {e}")
        return False

def create_3d_square_plate(side_length=10.0, thickness=1.0, output_file="square_plate_3d.stl"):
    """
    Create a 3D square plate (extruded 2D square) and export as STL file.
    This is more suitable for STL format which is typically used for 3D objects.
    
    Parameters:
    side_length (float): Side length of the square
    thickness (float): Thickness of the plate
    output_file (str): Output STL filename
    """
    
    try:
        # Create vertices for the square base
        vertex1 = geompy.MakeVertex(0, 0, 0)
        vertex2 = geompy.MakeVertex(side_length, 0, 0)
        vertex3 = geompy.MakeVertex(side_length, side_length, 0)
        vertex4 = geompy.MakeVertex(0, side_length, 0)
        
        # Create edges
        edge1 = geompy.MakeEdge(vertex1, vertex2)
        edge2 = geompy.MakeEdge(vertex2, vertex3)
        edge3 = geompy.MakeEdge(vertex3, vertex4)
        edge4 = geompy.MakeEdge(vertex4, vertex1)
        
        # Create wire and face
        wire = geompy.MakeWire([edge1, edge2, edge3, edge4])
        square_face = geompy.MakeFace(wire, 1)
        
        # Create extrusion vector
        vector = geompy.MakeVectorDXDYDZ(0, 0, thickness)
        
        # Extrude the face to create 3D solid
        square_solid = geompy.MakePrismVecH(square_face, vector, thickness)
        
        # Add to study
        geompy.addToStudy(square_solid, "Square_Plate_3D")
        
        print(f"Created 3D square plate: {side_length}x{side_length}x{thickness}")
        
        # Create mesh
        mesh = smesh.Mesh(square_solid, "SquarePlateMesh")
        
        # 3D mesh algorithm
        algo_3d = mesh.Tetrahedron()
        hyp_3d = algo_3d.MaxElementVolume(2.0)
        
        # 2D mesh for surfaces
        algo_2d = mesh.Triangle()
        hyp_2d = algo_2d.MaxElementArea(1.0)
        
        # 1D mesh for edges
        algo_1d = mesh.Segment()
        hyp_1d = algo_1d.NumberOfSegments(10)
        
        # Generate mesh
        if mesh.Compute():
            print("3D mesh generated successfully")
        else:
            print("Error: Failed to generate 3D mesh")
            return False
            
        # Export to STL
        try:
            mesh.ExportSTL(output_file)
            print(f"3D STL file exported successfully: {output_file}")
            return True
        except Exception as e:
            print(f"Error exporting 3D STL: {e}")
            return False
            
    except Exception as e:
        print(f"Error creating 3D geometry: {e}")
        return False

if __name__ == "__main__":
    print("SALOME 2D Square STL Generator")
    print("=" * 40)
    
    # Create 2D square (as surface mesh)
    print("\nCreating 2D square...")
    success_2d = create_2d_square(side_length=20.0, output_file="square_2d.stl")
    
    # Create 3D square plate (recommended for STL)
    print("\nCreating 3D square plate...")
    success_3d = create_3d_square_plate(side_length=20.0, thickness=2.0, output_file="square_plate_3d.stl")
    
    if success_2d and success_3d:
        print("\nBoth STL files created successfully!")
        print("Files created:")
        print("- square_2d.stl (2D surface)")
        print("- square_plate_3d.stl (3D solid)")
    else:
        print("\nSome errors occurred during generation.")
        
    print("\nScript completed.")