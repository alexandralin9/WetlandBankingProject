
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def process_wetland_data(input_file):
    """
    Process wetland mitigation bank data and calculate distances
    between impact sites and banks.
    """
    # Read the input Excel file
    df = pd.read_excel(input_file)
    
    # Define wetland keywords for filtering
    wetland_keywords = [
        'wetland', 'Wetlands', 'Marsh', 'Palustrine', 'Estuarine', 'Swamp', 
        'Bog', 'Meadow', 'Vernal Pool', 'PEM', 'PSS', 'PFO', 'PUB'
    ]
    
    # Filter for wetlands based on credit classification
    pattern = '|'.join(wetland_keywords)
    wetlands_df = df[
        df['Credit Classification or Subdivision'].str.contains(pattern, case=False, na=False)
    ]
    
    # Calculate distances
    wetlands_df['Distance_km'] = wetlands_df.apply(
        lambda row: haversine_distance(
            row['Impact LocationLatitude'], 
            row['Impact LocationLongitude'],
            row['Latitude'],
            row['Longitude']
        ) if pd.notnull(row['Impact LocationLatitude']) and 
           pd.notnull(row['Impact LocationLongitude']) and
           pd.notnull(row['Latitude']) and
           pd.notnull(row['Longitude'])
        else np.nan,
        axis=1
    )
    
    # Add distance in miles
    wetlands_df['Distance_miles'] = wetlands_df['Distance_km'] * 0.621371
    
    # Sort by distance
    wetlands_df = wetlands_df.sort_values('Distance_km')
    
    return wetlands_df

def generate_summary_statistics(df):
    """
    Generate summary statistics for the wetland data
    """
    stats = {
        'total_transactions': len(df),
        'distance_stats': df['Distance_km'].describe().to_dict(),
        'top_wetland_types': df['Credit Classification or Subdivision'].value_counts().head().to_dict(),
        'top_states': df['State List_y'].value_counts().head().to_dict()
    }
    return stats

def save_to_excel(df, output_filename='wetlands_complete_data.xlsx'):
    """
    Save the processed data to an Excel file with formatted columns
    """
    with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        
        # Format column widths
        worksheet = writer.sheets['Sheet1']
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column].width = min(adjusted_width, 50)

def main():
    """
    Main function to process wetland data and generate outputs
    """
    # Process the data
    input_file = 'All banks (5).xlsx'  # Change this to your input file name
    wetlands_df = process_wetland_data(input_file)
    
    # Generate statistics
    stats = generate_summary_statistics(wetlands_df)
    
    # Save to Excel
    save_to_excel(wetlands_df)
    
    # Print summary statistics
    print(f"Processing complete!")
    print(f"Total wetland transactions: {stats['total_transactions']}")
    print("
Distance Statistics (km):")
    for stat, value in stats['distance_stats'].items():
        print(f"{stat}: {value:.2f}")
    
    print("
Top 5 Wetland Types:")
    for wetland_type, count in stats['top_wetland_types'].items():
        print(f"{wetland_type}: {count}")
    
    print("
Top 5 States:")
    for state, count in stats['top_states'].items():
        print(f"{state}: {count}")

if __name__ == "__main__":
    main()
