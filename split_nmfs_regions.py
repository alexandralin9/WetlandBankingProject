import pandas as pd

def split_by_nmfs_region(filename, prefix=""):
    """
    Split a CSV file by NMFS Region and save to separate files.
    
    Args:
        filename (str): Path to the input CSV file
        prefix (str): Prefix to add to output filenames
    """
    # Read the CSV file
    df = pd.read_csv(filename)
    
    # Get unique regions
    regions = df['NMFS Region List'].unique()
    print(f'Unique NMFS Regions found in {filename}:')
    print(regions)
    
    # Split and save files by region
    for region in regions:
        if pd.notna(region):  # Skip null/nan regions
            region_df = df[df['NMFS Region List'] == region]
            output_filename = f'{prefix}NMFS_Region_{region.replace(" ", "_")}.csv'
            region_df.to_csv(output_filename, index=False)
            print(f'Saved {len(region_df)} records for {region} to {output_filename}')

if __name__ == "__main__":
    # Split both files
    print("Splitting OG.csv...")
    split_by_nmfs_region('OG.csv')
    
    print("\nSplitting Bank_Data_with_HUC_Count.csv...")
    split_by_nmfs_region('Bank_Data_with_HUC_Count.csv', prefix='Bank_')
