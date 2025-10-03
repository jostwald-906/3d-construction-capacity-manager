"""
3D Model Parser for OBJ, GLTF, GLB, FBX, and other 3D formats
Extracts bounding box and geometry data for voxelization
Uses trimesh library for robust parsing of many formats
"""
import trimesh
from typing import Dict

def parse_3d_model(file_path: str, format: str) -> Dict:
    """
    Parse a 3D model file and return bounding box using trimesh
    Supports: OBJ, GLTF, GLB, FBX, STL, PLY, DAE, and more

    Args:
        file_path: Path to the 3D model file
        format: File format extension (obj, gltf, glb, fbx, etc.)

    Returns:
        Dictionary with bounding box coordinates and vertices
    """
    try:
        # Load mesh with trimesh (handles all formats automatically)
        mesh = trimesh.load(file_path, force='mesh')

        # Handle scene vs single mesh
        if isinstance(mesh, trimesh.Scene):
            # If it's a scene with multiple meshes, combine them
            meshes = [geom for geom in mesh.geometry.values() if isinstance(geom, trimesh.Trimesh)]
            if not meshes:
                raise ValueError("No valid meshes found in scene")
            mesh = trimesh.util.concatenate(meshes)

        # Extract vertices
        vertices = mesh.vertices.tolist()

        # Get bounding box
        bounds = mesh.bounds  # Returns [[min_x, min_y, min_z], [max_x, max_y, max_z]]

        return {
            'min_x': float(bounds[0][0]),
            'max_x': float(bounds[1][0]),
            'min_y': float(bounds[0][1]),
            'max_y': float(bounds[1][1]),
            'min_z': float(bounds[0][2]),
            'max_z': float(bounds[1][2]),
            'vertices': vertices
        }
    except Exception as e:
        raise ValueError(f"Failed to parse {format.upper()} file: {str(e)}")
