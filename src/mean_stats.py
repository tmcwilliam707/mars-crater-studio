import pandas as pd
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to the CSV file
csv_file = "public/data/themis_lat-30_lon060_craters.csv"  # Replace with your actual file path

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
        'mean_circularity': df['circularity'].mean()
    }
    
    # Log the results
    logger.info("\nAggregated Mean Statistics (kilometers):")
    for key, value in mean_stats.items():
        if isinstance(value, float):
            logger.info(f"{key}: {value:.2f} km")
        else:
            logger.info(f"{key}: {value}")
    
    # Save to CSV in the same directory
    output_file = os.path.join(os.path.dirname(csv_file), 'mean_stats_summary.csv')
    mean_stats_df = pd.DataFrame([mean_stats])
    mean_stats_df.to_csv(output_file, index=False)
    logger.info(f"Saved aggregated stats to {output_file}")
else:
    logger.error(f"CSV file not found: {csv_file}")