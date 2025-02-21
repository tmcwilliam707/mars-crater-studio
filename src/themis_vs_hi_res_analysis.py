import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import logging
from glob import glob

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarsCraterComparator:
    def __init__(self, themis_dir='path/to/themis_csvs', hirise_csv='path/to/hirise_quarter_craters.csv', output_dir='path/to/output'):
        self.themis_dir = themis_dir
        self.hirise_csv = hirise_csv
        self.output_dir = output_dir
        self.themis_files = glob(os.path.join(themis_dir, 'themis_*_craters.csv'))
        self.themis_dfs = []
        self.hirise_df = None
        
        # Create output directory if it doesn’t exist
        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self):
        """Load THEMIS and HiRISE CSV data."""
        # Load THEMIS CSVs
        if not self.themis_files:
            logger.warning(f"No THEMIS crater CSV files found in {self.themis_dir}")
        else:
            for file in self.themis_files:
                df = pd.read_csv(file)
                # Convert km to meters for consistency
                df['diameter_m'] = df['diameter_km'] * 1000
                df['depth_m'] = df['depth_km'] * 1000
                self.themis_dfs.append(df)
                logger.info(f"Loaded THEMIS data from {file}: {len(df)} craters")
        
        # Load HiRISE CSV
        if os.path.exists(self.hirise_csv):
            self.hirise_df = pd.read_csv(self.hirise_csv)
            logger.info(f"Loaded HiRISE data from {self.hirise_csv}: {len(self.hirise_df)} craters")
        else:
            logger.warning(f"HiRISE file not found: {self.hirise_csv}")

    def compute_stats(self, df, prefix, area_km2=None):
        """Compute basic stats for a DataFrame."""
        stats = {
            f'{prefix}_total_craters': len(df),
            f'{prefix}_mean_diameter_m': df['diameter_m'].mean() if not df.empty else 0,
            f'{prefix}_median_diameter_m': df['diameter_m'].median() if not df.empty else 0,
            f'{prefix}_min_diameter_m': df['diameter_m'].min() if not df.empty else 0,
            f'{prefix}_max_diameter_m': df['diameter_m'].max() if not df.empty else 0,
            f'{prefix}_mean_depth_m': df['depth_m'].mean() if not df.empty else 0,
            f'{prefix}_median_depth_m': df['depth_m'].median() if not df.empty else 0,
            f'{prefix}_min_depth_m': df['depth_m'].min() if not df.empty else 0,
            f'{prefix}_max_depth_m': df['depth_m'].max() if not df.empty else 0,
        }
        if area_km2:
            stats[f'{prefix}_crater_density_km2'] = len(df) / area_km2 if area_km2 > 0 else 0
        return stats

    def aggregate_and_compare(self):
        """Aggregate stats and compare THEMIS vs HiRISE."""
        if not self.themis_dfs and self.hirise_df is None:
            logger.error("No data loaded for comparison")
            return None, None, None

        # Combine THEMIS data
        if self.themis_dfs:
            themis_combined = pd.concat(self.themis_dfs, ignore_index=True)
            # Estimate area (assuming each THEMIS tile is ~100 km x 100 km, adjust if known)
            themis_area_km2 = len(self.themis_files) * 100 * 100  # Rough estimate
            themis_stats = self.compute_stats(themis_combined, 'themis', themis_area_km2)
        else:
            themis_stats = {f'themis_{k}': 0 for k in ['total_craters', 'mean_diameter_m', 'median_diameter_m', 
                                                      'min_diameter_m', 'max_diameter_m', 'mean_depth_m', 
                                                      'median_depth_m', 'min_depth_m', 'max_depth_m', 'crater_density_km2']}
            themis_combined = pd.DataFrame()

        # HiRISE stats
        if self.hirise_df is not None:
            # Area: 26 sub-mosaics, each 10x10 images (2270x2270 pixels), 0.25 m/pixel
            hirise_area_m2 = 26 * (2270 * 2270) * (0.25 ** 2)  # m²
            hirise_area_km2 = hirise_area_m2 / 1e6  # km²
            hirise_stats = self.compute_stats(self.hirise_df, 'hirise', hirise_area_km2)
        else:
            hirise_stats = {f'hirise_{k}': 0 for k in ['total_craters', 'mean_diameter_m', 'median_diameter_m', 
                                                      'min_diameter_m', 'max_diameter_m', 'mean_depth_m', 
                                                      'median_depth_m', 'min_depth_m', 'max_depth_m', 'crater_density_km2']}
            hirise_combined = pd.DataFrame()

        # Comparison
        comparison = {}
        for stat in ['total_craters', 'mean_diameter_m', 'median_diameter_m', 'mean_depth_m', 'crater_density_km2']:
            t_val = themis_stats.get(f'themis_{stat}', 0)
            h_val = hirise_stats.get(f'hirise_{stat}', 0)
            comparison[f'{stat}_diff_m'] = h_val - t_val  # HiRISE - THEMIS
            comparison[f'{stat}_ratio'] = h_val / t_val if t_val != 0 else float('inf')

        return themis_stats, hirise_stats, comparison

    def visualize_comparison(self, themis_stats, hirise_stats, comparison):
        """Visualize stats comparison."""
        stats_to_plot = ['mean_diameter_m', 'mean_depth_m', 'crater_density_km2']
        themis_vals = [themis_stats[f'themis_{s}'] for s in stats_to_plot]
        hirise_vals = [hirise_stats[f'hirise_{s}'] for s in stats_to_plot]
        
        x = np.arange(len(stats_to_plot))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width/2, themis_vals, width, label='THEMIS', color='blue', alpha=0.7)
        ax.bar(x + width/2, hirise_vals, width, label='HiRISE', color='orange', alpha=0.7)
        
        ax.set_ylabel('Value (meters or craters/km²)')
        ax.set_title('THEMIS vs HiRISE Crater Stats Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(['Mean Diameter', 'Mean Depth', 'Crater Density'])
        ax.legend()
        
        # Add difference annotations
        for i, stat in enumerate(stats_to_plot):
            diff = comparison[f'{stat}_diff_m']
            ax.text(i, max(themis_vals[i], hirise_vals[i]) + 0.05 * max(themis_vals + hirise_vals), 
                    f'Diff: {diff:.2f}', ha='center', fontsize=8)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'crater_stats_comparison.png')
        fig.savefig(output_path, dpi=100)
        logger.info(f"Saved comparison plot to {output_path}")
        plt.close(fig)

    def run_analysis(self):
        """Run the full comparison pipeline."""
        self.load_data()
        themis_stats, hirise_stats, comparison = self.aggregate_and_compare()
        
        if themis_stats and hirise_stats:
            # Log stats
            logger.info("\nTHEMIS Combined Stats:")
            for key, value in themis_stats.items():
                logger.info(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
            
            logger.info("\nHiRISE Combined Stats:")
            for key, value in hirise_stats.items():
                logger.info(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
            
            logger.info("\nComparison (HiRISE - THEMIS):")
            for key, value in comparison.items():
                logger.info(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
            
            # Visualize
            self.visualize_comparison(themis_stats, hirise_stats, comparison)
            
            # Save combined stats
            combined_stats = {**themis_stats, **hirise_stats, **comparison}
            output_csv = os.path.join(self.output_dir, 'crater_comparison_stats.csv')
            pd.DataFrame([combined_stats]).to_csv(output_csv, index=False)
            logger.info(f"Saved comparison stats to {output_csv}")
        
        return themis_stats, hirise_stats, comparison

if __name__ == "__main__":
    # Customize these paths for your local setup
    THEMIS_DIR = 'path/to/themis_csvs'  # Where your themis_lat*_craters.csv files are
    HIRISE_CSV = 'path/to/hirise_quarter_craters.csv'  # Path to hirise_quarter_craters.csv
    OUTPUT_DIR = 'path/to/output'  # Where to save results
    
    # Run comparison
    comparator = MarsCraterComparator(themis_dir=THEMIS_DIR, hirise_csv=HIRISE_CSV, output_dir=OUTPUT_DIR)
    themis_stats, hirise_stats, comparison = comparator.run_analysis()
    
    if not themis_stats or not hirise_stats:
        logger.error("Comparison incomplete due to missing data. Check THEMIS_DIR and HIRISE_CSV paths.")