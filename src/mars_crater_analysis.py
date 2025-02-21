import numpy as np
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import matplotlib.pyplot as plt
from skimage import feature, measure, draw
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Increase the maximum image size limit
Image.MAX_IMAGE_PIXELS = None

class ThemisAnalyzer:
    def __init__(self):
        self.base_url = "https://www.mars.asu.edu/data/thm_dir_100m/large/"
        self.resolution_km = 0.1  # 100m per pixel
        
    def download_tile(self, lat, lon):
        """
        Download a THEMIS tile based on latitude and longitude
        
        Parameters:
        lat: int - Latitude band (-30 or -60)
        lon: int - Longitude (0, 60, 120, 180, 240, or 300)
        """
        filename = f"lat{lat}_lon{lon:03d}.pgm"
        url = self.base_url + filename
        
        # Create a local cache directory if it doesn't exist
        if not os.path.exists('themis_cache'):
            os.makedirs('themis_cache')
            
        local_file = f"themis_cache/{filename}"
        
        # Check if we already have this file cached
        if os.path.exists(local_file):
            print(f"Loading cached file: {filename}")
            return local_file
            
        print(f"Downloading {filename} from {url}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get total file size
            total_size = int(response.headers.get('content-length', 0))
            print(f"Total file size: {total_size} bytes")
            
            # Download with progress bar
            with open(local_file, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
                            
            print(f"Downloaded {filename} successfully.")
            return local_file
            
        except requests.RequestException as e:
            print(f"Error downloading file: {e}")
            return None
            
    def process_tile_section(self, image_path, start_row=0, rows=100):
        """
        Process a section of a THEMIS tile to detect craters
        """
        # Load just the section we want to process
        with Image.open(image_path) as img:
            region = img.crop((0, start_row, img.width, start_row + rows))
            image_section = np.array(region)
            
        # Normalize the section
        image_normalized = (image_section - np.min(image_section)) / (np.max(image_section) - np.min(image_section))
        
        # Detect edges
        edges = feature.canny(
            image_normalized,
            sigma=2,
            low_threshold=0.1,
            high_threshold=0.3
        )
        
        # Find contours
        contours = measure.find_contours(edges, 0.5)
        
        # Analyze contours
        craters = []
        for contour in contours:
            # Adjust y coordinates to account for section offset
            contour[:, 0] += start_row
            
            # Create a binary mask from the contour
            mask = np.zeros_like(edges, dtype=bool)
            rr, cc = draw.polygon(contour[:, 0], contour[:, 1], mask.shape)
            mask[rr, cc] = True
            
            # Calculate properties
            props = measure.regionprops(mask.astype(int))
            if props:
                area = props[0].area
                perimeter = props[0].perimeter
                
                diameter_km = np.sqrt(4 * area / np.pi) * self.resolution_km
                
                # Only include craters larger than 1km
                if diameter_km >= 1.0:
                    craters.append({
                        'diameter_km': diameter_km,
                        'circularity': 4 * np.pi * area / (perimeter ** 2),
                        'center_x': int(np.mean(contour[:, 1])),
                        'center_y': int(np.mean(contour[:, 0])),
                        'confidence': min(1.0, 4 * np.pi * area / (perimeter ** 2))
                    })
                
        return craters

    def analyze_tile(self, lat, lon):
        """
        Analyze a complete THEMIS tile
        """
        # Download or get cached file
        image_path = self.download_tile(lat, lon)
        if not image_path:
            return None, None, None
            
        # Get image dimensions
        with Image.open(image_path) as img:
            total_rows = img.height
            
        # Process the image in sections to manage memory
        section_size = 100  # Process 100 rows at a time
        all_craters = []
        
        print("Detecting craters...")
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.process_tile_section, image_path, start_row, min(section_size, total_rows - start_row))
                for start_row in range(0, total_rows, section_size)
            ]
            for future in tqdm(futures):
                section_craters = future.result()
                all_craters.extend(section_craters)
            
        crater_df = pd.DataFrame(all_craters)
        
        # Calculate statistics
        stats = {
            'latitude': lat,
            'longitude': lon,
            'total_craters': len(crater_df),
            'mean_diameter': crater_df['diameter_km'].mean() if len(crater_df) > 0 else 0,
            'median_diameter': crater_df['diameter_km'].median() if len(crater_df) > 0 else 0,
            'min_diameter': crater_df['diameter_km'].min() if len(crater_df) > 0 else 0,
            'max_diameter': crater_df['diameter_km'].max() if len(crater_df) > 0 else 0
        }
        
        # Create a summary visualization
        print("Creating visualization...")
        fig, ax = plt.subplots(figsize=(15, 15))
        
        # Load a smaller version of the image for visualization
        with Image.open(image_path) as img:
            img_small = img.resize((1000, 1000))
            image_small = np.array(img_small)
            
        # Normalize for display
        image_normalized = (image_small - np.min(image_small)) / (np.max(image_small) - np.min(image_small))
        
        ax.imshow(image_normalized, cmap='gray')
        
        # Scale crater coordinates to match resized image
        scale_factor = 1000 / total_rows
        for _, crater in crater_df.iterrows():
            circle = plt.Circle(
                (crater['center_x'] * scale_factor, 
                 crater['center_y'] * scale_factor),
                crater['diameter_km'] / (2 * self.resolution_km) * scale_factor,
                fill=False,
                color='red',
                alpha=crater['confidence']
            )
            ax.add_patch(circle)
            
        ax.set_title(f'Detected Craters (Lat {lat}, Lon {lon})')
        
        return crater_df, stats, fig

# Example usage
if __name__ == "__main__":
    analyzer = ThemisAnalyzer()
    
    # Example: analyze the first tile
    lat = -30
    lon = 0
    
    try:
        craters, stats, figure = analyzer.analyze_tile(lat, lon)
        
        if craters is not None:
            # Print statistics
            print("\nCrater Statistics:")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"{key}: {value:.2f}")
                else:
                    print(f"{key}: {value}")
            
            # Save results
            output_base = f"themis_lat{lat}_lon{lon:03d}"
            craters.to_csv(f'{output_base}_craters.csv', index=False)
            figure.savefig(f'{output_base}_detection.png', dpi=300)
            
            print(f"\nResults saved as {output_base}_craters.csv and {output_base}_detection.png")
            
    except Exception as e:
        print(f"Error processing tile: {e}")