import numpy as np
import pandas as pd
import os
import logging
from glob import glob

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarsCraterComparator:
    def __init__(self, output_dir='path/to/output'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def run_analysis(self):
        """Run comparison with scientific mean diameter."""
        
        # Your mean stats
        your_stats = {
            'total_craters': 1047,
            'mean_diameter_km': 1.7156024707291615,
            'median_diameter_km': 1.54715556557901,
            'min_diameter_km': 1.034176589165282,
            'max_diameter_km': 4.173477802981229,
            'mean_depth_km': 1.2845983951575932,
            'median_depth_km': 1.1392157,
            'min_depth_km': 0.0,
            'max_depth_km': 3.5
        }
        
        logger.info("\nYour Mean Stats:")
        for key, value in your_stats.items():
            logger.info(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
        
        # Scientific benchmark (Robbins & Hynek)
        scientific_mean_diameter_m = 6800  # 6.8 km in meters
        
        logger.info("\nScientific Benchmark (Robbins & Hynek, 2012):")
        logger.info(f"Mean Diameter: {scientific_mean_diameter_m} m (6.8 km)")
        
        # Prepare data for React charts
        comparison_data = {
            'your_mean_diameter_km': your_stats['mean_diameter_km'],
            'scientific_mean_diameter_km': scientific_mean_diameter_m / 1000,  # Convert to km
            'your_mean_depth_km': your_stats['mean_depth_km'],
            'scientific_mean_depth_km': None  # Add scientific mean depth if available
        }
        
        comparison_df = pd.DataFrame([comparison_data])
        comparison_path = os.path.join(self.output_dir, 'comparison_data.csv')
        comparison_df.to_csv(comparison_path, index=False)
        logger.info(f"Saved comparison data to {comparison_path}")

if __name__ == "__main__":
    # Customize the output path
    OUTPUT_DIR = 'public'  # Directory where the output CSV will be saved

    comparator = MarsCraterComparator(output_dir=OUTPUT_DIR)
    comparator.run_analysis()