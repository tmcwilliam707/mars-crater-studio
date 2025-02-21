import pandas as pd
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# List of CSV files
csv_files = [
    "public/data/themis_lat-30_lon060_craters.csv",
    "public/data/themis_lat30_lon300_craters.csv",
    "public/data/themis_lat30_lon000_craters.csv"  # Add your actual file paths here
]

# Initialize an empty DataFrame to store aggregated statistics
all_stats = []

for csv_file in csv_files:
    # Check if the CSV file exists
    if os.path.exists(csv_file):
        # Load the CSV file
        df = pd.read_csv(csv_file)
        
        # Extract lat, lon from filename for context
        filename = os.path.basename(csv_file)
        lat_str = filename.split('lat')[1].split('_')[0]
        lon_str = filename.split('lon')[1].split('_')[0]
        lat = int(lat_str)
        lon = int(lon_str)
        df['latitude'] = lat
        df['longitude'] = lon
        logger.info(f"Loaded {csv_file} with {len(df)} craters")
        
        # Calculate aggregated statistics
        mean_stats = {
            'total_craters': len(df),
            'mean_diameter_km': df['diameter_km'].mean(),
            'median_diameter_km': df['diameter_km'].median(),
            'min_diameter_km': df['diameter_km'].min(),
            'max_diameter_km': df['diameter_km'].max(),
            'mean_depth_km': df['depth_km'].mean(),
            'median_depth_km': df['depth_km'].median(),
            'min_depth_km': df['depth_km'].min(),
            'max_depth_km': df['depth_km'].max(),
            'mean_circularity': df['circularity'].mean()
        }
        
        # Append the statistics to the list
        all_stats.append(mean_stats)
        
        # Log the results
        logger.info("\nAggregated Mean Statistics (kilometers):")
        for key, value in mean_stats.items():
            if isinstance(value, float):
                logger.info(f"{key}: {value:.2f} km")
            else:
                logger.info(f"{key}: {value}")
    else:
        logger.error(f"CSV file not found: {csv_file}")

# Save aggregated statistics to a CSV file
output_file = "public/data/mean_stats_summary.csv"
mean_stats_df = pd.DataFrame(all_stats)
mean_stats_df.to_csv(output_file, index=False)
logger.info(f"Saved aggregated stats to {output_file}")