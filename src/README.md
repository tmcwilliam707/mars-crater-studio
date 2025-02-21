# Mars Crater Analysis and Visualization Toolkit

## Overview
## BE AWARE KAGGLE WILL CHANGE FILENAME WHEN UPLOADED
This toolkit combines Python-based analysis of Martian crater data with a React-based 3D visualization frontend. It’s designed for researchers and developers to detect craters from THEMIS imagery, generate 3D terrain models, and visualize results in a web interface.

## entire dataset for pgm (large files/ long download time) and statical analysis csv will be available for anyone's ## use if you dont want
## to wait for kaggle to analyze dataset

## Components

- **ThemisAnalyzer (Python)**: Downloads and analyzes THEMIS 100m tiles to detect craters and produce visualizations.
- **MemoryOptimizedConverter (Python)**: Converts PGM heightmaps into optimized 3D GLB models for web viewing.
- **CraterScene (React)**: Renders a 3D scene with a Mars background, intended for displaying GLB models (basic implementation).

> **Note**: Processing large datasets requires significant resources—use a GPU-enabled system or cloud platform (e.g., Kaggle, Google Colab) to avoid crashes on standard hardware.

## Features

- **Crater Detection**: Identifies craters (>1km) in THEMIS tiles using edge detection and contour analysis.
- **3D Modeling**: Generates compressed GLB models from PGM files with memory-efficient chunking.
- **Visualization**: Provides statistical summaries, crater maps (PNG), and a basic 3D web viewer.

## Installation

### Prerequisites

- **Python**: 3.8+
- **Node.js**: 16+ (for React frontend)
- **Hardware**: 16GB+ RAM, GPU recommended.
- **External Tools**:
  - `obj2gltf`: `npm install -g obj2gltf`
  - `gltf-pipeline`: `npm install -g gltf-pipeline`

### Python Dependencies

Install Python libraries:
```bash
pip install numpy pandas pillow requests matplotlib scikit-image tqdm
```

### JavaScript Dependencies

Set up the React frontend:
```bash
cd frontend  # Assuming CraterScene is in a frontend directory
npm install three
npm install  # If you have a package.json
```

## Project Structure
```text
mars-crater-toolkit/
├── themis_analyzer.py         # THEMIS tile analysis
├── memory_optimized_converter.py  # PGM to GLB conversion
├── frontend/
│   ├── src/
│   │   └── CraterScene.js     # React 3D scene component
│   ├── public/
│   │   └── images/
│   │       └── banner.jpg     # Mars background texture
│   └── package.json           # Add if not present
├── themis_cache/              # Cache for THEMIS tiles (auto-created)
└── README.md                  # This file
```

## Usage

### 1. ThemisAnalyzer

**Purpose**: Detects craters in THEMIS tiles and generates visualizations.

**Example**:
```python
from themis_analyzer import ThemisAnalyzer

analyzer = ThemisAnalyzer()
craters, stats, fig = analyzer.analyze_tile(lat=-30, lon=0)
craters.to_csv('themis_lat-30_lon000_craters.csv')
fig.savefig('themis_lat-30_lon000_detection.png', dpi=300)
```

**Output**:
- **CSV**: Crater data (diameter, circularity, coordinates).
- **PNG**: Map with crater overlays.
- **Stats**: Dictionary with crater counts and size metrics.

### 2. MemoryOptimizedConverter

**Purpose**: Converts PGM heightmaps to 3D GLB models.

**Example**:
```python
from memory_optimized_converter import MemoryOptimizedConverter

converter = MemoryOptimizedConverter(chunk_size=1024)
converter.pgm_to_glb(
    pgm_path='themis_cache/lat-30_lon000.pgm',
    obj_path='mars.obj',
    glb_path='crater.glb',
    target_width=2048,
    target_faces=750000
)
```

**Output**: `crater.glb` (3D model, viewable in web browsers or 3D software).

**Parameters**:
- **chunk_size**: Rows per chunk (default: 1024).
- **target_width**: Max width for downsampling (default: 1024).
- **target_faces**: Target face count (default: 500,000).

### 3. CraterScene (React Frontend)

**Purpose**: Displays a 3D scene with a Mars background (extend to load GLB models).

**Setup**:

- Place `CraterScene.js` in `frontend/src/`.
- Add a Mars texture (e.g., `banner.jpg`) to `frontend/public/images/`.
- Run the app:
```bash
cd frontend
npm start
```

**Current Functionality**:

- Renders a Three.js scene with a Mars background texture.
- Camera and lighting setup included.
- **To Extend**: Add a GLB loader (e.g., `GLTFLoader`) to display `crater.glb`.

**Example Extension** (not in provided code):
```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

// Inside useEffect:
const loader = new GLTFLoader();
loader.load('/crater.glb', (gltf) => {
  scene.add(gltf.scene);
});
```

## Workflow

1. **Analyze THEMIS Tiles**: Run ThemisAnalyzer to detect craters and save PGM files to `themis_cache/`.
2. **Generate 3D Models**: Use MemoryOptimizedConverter to convert PGM files to GLB.
3. **Visualize**: Extend CraterScene to load and display GLB models in the browser.

## Performance Notes

- **Memory**: Large PGM files (e.g., 4000x4000) need 16GB+ RAM. Adjust `chunk_size` or `target_width` for lower-spec systems.
- **Time**: Processing can take 10-30 minutes per file—patience required!
- **Caching**: THEMIS tiles are cached in `themis_cache/` to avoid repeated downloads.

## Dependencies

- **Python**: `numpy`, `pandas`, `PIL`, `requests`, `matplotlib`, `skimage`, `tqdm`, `concurrent.futures`, `pymeshlab`, `scipy`, `os`, `subprocess`, `struct`, `pathlib`, `logging`.
- **JavaScript**: `react`, `three`.
- **External**: `obj2gltf`, `gltf-pipeline`.

## Troubleshooting

- **Crashes**: Use a cloud platform if local runs fail (e.g., Colab with high-RAM runtime).
- **Missing Tools**: Ensure `obj2gltf` and `gltf-pipeline` are in your PATH.
- **Texture Errors**: Verify `banner.jpg` exists in `frontend/public/images/`.

## License

MIT License.