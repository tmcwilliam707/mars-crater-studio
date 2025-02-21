import numpy as np
import pymeshlab as ml
from scipy.ndimage import zoom
from pathlib import Path
import logging
from tqdm import tqdm
import sys
import subprocess
import struct
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MemoryOptimizedConverter:
    def __init__(self, chunk_size=1024):
        self.chunk_size = chunk_size

    def load_pgm_chunked(self, file_path):
        """Load PGM file in chunks to reduce memory usage."""
        # Read header
        with open(file_path, 'rb') as f:
            header = f.readline().decode('utf-8').strip()
            if header != 'P5':
                raise ValueError('Not a valid PGM file')
            
            # Skip comments
            while True:
                line = f.readline().decode('utf-8').strip()
                if not line.startswith('#'):
                    break
            
            width, height = map(int, line.split())
            max_value = int(f.readline().decode('utf-8').strip())
            header_offset = f.tell()
            
            # Pre-allocate array
            heightmap = np.zeros((height, width), dtype=np.uint8)
            
            # Read data in chunks
            for i in tqdm(range(0, height, self.chunk_size), desc="Loading PGM"):
                chunk_height = min(self.chunk_size, height - i)
                chunk_size = chunk_height * width
                chunk_data = np.frombuffer(f.read(chunk_size), dtype=np.uint8)
                heightmap[i:i+chunk_height] = chunk_data.reshape((chunk_height, width))
            
            return heightmap, max_value

    def create_terrain_mesh(self, heightmap, scale_factor=1.0):
        """Create terrain mesh with proper scaling and normals."""
        height, width = heightmap.shape
        
        # Create vertex grid
        x = np.linspace(-width/2, width/2, width) * scale_factor
        y = np.linspace(-height/2, height/2, height) * scale_factor
        X, Y = np.meshgrid(x, y)
        
        # Scale height values
        Z = heightmap.astype(np.float32) * scale_factor
        
        # Create vertices
        vertices = np.zeros((width * height, 3))
        vertices[:, 0] = X.flatten()
        vertices[:, 2] = Y.flatten()  # Swap Y and Z for proper orientation
        vertices[:, 1] = Z.flatten()  # Height becomes Y in 3D space
        
        # Create faces
        faces = []
        for i in range(height - 1):
            for j in range(width - 1):
                v0 = i * width + j
                v1 = v0 + 1
                v2 = (i + 1) * width + j
                v3 = v2 + 1
                faces.extend([[v0, v2, v1], [v1, v2, v3]])
        
        faces = np.array(faces)
        
        # Create mesh
        ms = ml.MeshSet()
        new_mesh = ml.Mesh(vertices, faces)
        ms.add_mesh(new_mesh)
        
        # Calculate normals
        ms.compute_normal_per_vertex()
        
        return ms

    def optimize_mesh(self, ms, target_faces):
        """Optimize mesh while preserving quality."""
        current_faces = ms.current_mesh().face_number()
        logger.info(f"Initial faces: {current_faces}")
        
        if current_faces > target_faces:
            # First cleaning pass
            ms.meshing_remove_unreferenced_vertices()
            ms.meshing_repair_non_manifold_edges()
            
            # Decimation with quality preservation
            ms.meshing_decimation_quadric_edge_collapse(
                targetfacenum=target_faces,
                qualitythr=0.5,
                preserveboundary=True,
                preservenormal=True,
                optimalplacement=True
            )
            
            # Final cleaning
            ms.meshing_repair_non_manifold_edges()
            ms.meshing_remove_duplicate_faces()
            ms.meshing_remove_duplicate_vertices()
            
            logger.info(f"Optimized to {ms.current_mesh().face_number()} faces")

    def validate_glb(self, glb_path):
        """Validate GLB file format."""
        with open(glb_path, 'rb') as f:
            # Check magic number
            magic = f.read(4)
            if magic != b'glTF':
                return False
            
            # Check version
            version = struct.unpack('<I', f.read(4))[0]
            if version != 2:
                return False
            
            return True

    def convert_to_glb(self, obj_path, glb_path):
        """Convert OBJ to GLB using gltf-pipeline."""
        try:
            # First convert to GLTF
            temp_gltf = obj_path.with_suffix('.gltf')
            
            # Use obj2gltf for initial conversion
            subprocess.run([
                'obj2gltf',
                '-i', str(obj_path),
                '-o', str(temp_gltf)
            ], check=True)
            
            # Use gltf-pipeline for final conversion with Draco compression
            subprocess.run([
                'gltf-pipeline',
                '-i', str(temp_gltf),
                '-o', str(glb_path),
                '--draco.compressionLevel', '7',
                '--draco.quantizePositionBits', '14',
                '--draco.quantizeNormalBits', '10',
                '--draco.quantizeTexcoordBits', '12'
            ], check=True)
            
            # Clean up temporary file
            os.remove(temp_gltf)
            
            if not self.validate_glb(glb_path):
                raise ValueError("Generated GLB file is invalid")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Conversion command failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during conversion: {e}")
            raise

    def pgm_to_glb(self, pgm_path, obj_path, glb_path, target_width=1024, target_faces=500000):
        """Convert PGM to GLB with validation."""
        try:
            pgm_path = Path(pgm_path)
            obj_path = Path(obj_path)
            glb_path = Path(glb_path)
            
            # Load heightmap
            logger.info("Loading heightmap...")
            heightmap, max_value = self.load_pgm_chunked(pgm_path)
            
            # Normalize heightmap
            heightmap = heightmap.astype(np.float32) / max_value
            
            # Downsample if needed
            if heightmap.shape[1] > target_width:
                scale = target_width / heightmap.shape[1]
                new_height = int(heightmap.shape[0] * scale)
                logger.info(f"Downsampling to {target_width}x{new_height}")
                heightmap = zoom(heightmap, (scale, scale), order=1)
            
            # Create mesh
            logger.info("Creating terrain mesh...")
            ms = self.create_terrain_mesh(heightmap, scale_factor=1.0)
            
            # Optimize
            logger.info("Optimizing mesh...")
            self.optimize_mesh(ms, target_faces)
            
            # Save OBJ
            logger.info("Saving intermediate OBJ...")
            ms.save_current_mesh(str(obj_path))
            
            # Convert to GLB
            logger.info("Converting to GLB...")
            self.convert_to_glb(obj_path, glb_path)
            
            # Cleanup
            os.remove(obj_path)
            
            logger.info("Conversion completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            raise

if __name__ == "__main__":
    converter = MemoryOptimizedConverter()
    try:
        converter.pgm_to_glb(
            'lat-30_lon000.pgm',
            'mars.obj',
            'crater.glb',
            target_width=2048,
            target_faces=750000
        )
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        sys.exit(1)