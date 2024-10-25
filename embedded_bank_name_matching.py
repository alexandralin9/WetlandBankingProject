
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz, process
import re

# Sample data embedded directly in the script
withdrawals_data = {
    'Name': ['Wetland A', 'Wetland B', 'Wetland C'],
    'Impact LocationLatitude': [34.05, 36.16, 40.71],
    'Impact LocationLongitude': [-118.24, -115.15, -74.00]
}

banks_data = {
    'Name': ['Wetland A1', 'Wetland B2', 'Wetland C3'],
    'Latitude': [34.05, 36.16, 40.71],
    'Longitude': [-118.24, -115.15, -74.00]
}

withdrawals_df = pd.DataFrame(withdrawals_data)
banks_df = pd.DataFrame(banks_data)

# Function to clean bank names
def clean_bank_name(name):
    """
    Clean and standardize bank names for better matching.
    """
    if pd.isna(name):
        return ""
    
    # Convert to string and lowercase
    name = str(name).lower()
    
    # Remove common suffixes and prefixes
    remove_terms = [
        'mitigation bank', 'bank', 'mb', 'conservation bank', 'cb', 
        'in-lieu fee program', 'ilf', 'program', 'umbrella', 
        'conservation area', 'preserve', 'restoration'
    ]
    
    for term in remove_terms:
        name = name.replace(term, '')
    
    # Remove special characters and extra spaces
    name = re.sub(r'[^a-z0-9\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def match_bank_names(withdrawals_df, banks_df, threshold=80):
    """
    Match bank names between withdrawals and banks dataframes using fuzzy matching.
    
    Parameters:
    -----------
    withdrawals_df : pandas DataFrame
        DataFrame containing withdrawal records
    banks_df : pandas DataFrame
        DataFrame containing bank records
    threshold : int
        Minimum similarity score to consider a match (0-100)
        
    Returns:
    --------
    pandas DataFrame
        Original withdrawals DataFrame with matched bank names and scores
    """
    # Clean bank names in both dataframes
    withdrawals_df['Clean_Name'] = withdrawals_df['Name'].apply(clean_bank_name)
    banks_df['Clean_Name'] = banks_df['Name'].apply(clean_bank_name)
    
    # Create a dictionary of unique clean bank names
    unique_bank_names = banks_df['Clean_Name'].unique()
    
    # Function to find best match for each withdrawal
    def find_best_match(name):
        if pd.isna(name) or name == "":
            return pd.Series({'Matched_Bank_Name': np.nan, 'Match_Score': 0})
        
        best_match = process.extractOne(
            name,
            unique_bank_names,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=threshold
        )
        
        if best_match:
            return pd.Series({
                'Matched_Bank_Name': best_match[0],
                'Match_Score': best_match[1]
            })
        return pd.Series({'Matched_Bank_Name': np.nan, 'Match_Score': 0})
    
    # Apply matching
    match_results = withdrawals_df['Clean_Name'].apply(find_best_match)
    
    # Add results to original dataframe
    result_df = withdrawals_df.copy()
    result_df['Matched_Bank_Name'] = match_results['Matched_Bank_Name']
    result_df['Match_Score'] = match_results['Match_Score']
    
    # Get original bank names and details for matches
    bank_name_map = banks_df.set_index('Clean_Name')['Name'].to_dict()
    result_df['Original_Bank_Name'] = result_df['Matched_Bank_Name'].map(bank_name_map)
    
    return result_df

def analyze_matching_results(matched_df):
    """
    Analyze the results of the matching process.
    """
    total_records = len(matched_df)
    matched_records = matched_df['Matched_Bank_Name'].notna().sum()
    match_rate = (matched_records / total_records) * 100
    
    score_distribution = matched_df['Match_Score'].describe()
    
    print(f"Matching Analysis:")
    print(f"Total Records: {total_records}")
    print(f"Matched Records: {matched_records}")
    print(f"Match Rate: {match_rate:.2f}%")
    print("
Score Distribution:")
    print(score_distribution)
    
    # Sample of matches at different score levels
    print("
Sample matches at different score levels:")
    for score in [100, 90, 80]:
        sample = matched_df[matched_df['Match_Score'] >= score].head(3)
        print(f"
Score >= {score}:")
        print(sample[['Name', 'Original_Bank_Name', 'Match_Score']])

def main():
    """
    Example usage of the matching functions.
    """
    # Perform matching
    matched_results = match_bank_names(withdrawals_df, banks_df)
    
    # Analyze results
    analyze_matching_results(matched_results)

if __name__ == "__main__":
    main()
