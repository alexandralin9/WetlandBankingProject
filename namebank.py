
import pandas as pd
import numpy as np
# from fuzzywuzzy import fuzz, process
from rapidfuzz import fuzz, process, utils
import re
from tqdm import tqdm

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
    print("Cleaned names")
    
    # Create a dictionary of unique clean bank names
    unique_bank_names = banks_df['Clean_Name'].unique()
    print(unique_bank_names)
    print(withdrawals_df['Clean_Name'])
    
    # Function to find best match for each withdrawal
    best_matches = {}
    def find_best_match(name):
        if pd.isna(name) or name == "":
            return pd.Series({'Matched_Bank_Name': np.nan, 'Match_Score': 0})

        if name in best_matches:
            return best_matches[name]
        
        best_match = process.extractOne(
            name,
            unique_bank_names,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=threshold,
            # scorer=fuzz.WRatio,
            processor=utils.default_process
        )
        
        if best_match:
            return_val = pd.Series({
                'Matched_Bank_Name': best_match[0],
                'Match_Score': best_match[1]
            })
            best_matches[name] = return_val
            return return_val
        return pd.Series({'Matched_Bank_Name': np.nan, 'Match_Score': 0})
    
    # Apply matching
    match_results = withdrawals_df['Clean_Name'].progress_apply(find_best_match)
    print('Matched results')
    
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
    print("Score Distribution:")
    print(score_distribution)
    
    # Sample of matches at different score levels
    print("Sample matches at different score levels:")
    for score in [100, 90, 80]:
        sample = matched_df[matched_df['Match_Score'] >= score].head(3)
        print(f"Score >= {score}:")
        print(sample[['Name', 'Original_Bank_Name', 'Match_Score']])

def main():
    """
    Example usage of the matching functions.
    """
    # Load your data
    # withdrawals_file = 'withdrawals.csv'  # Replace with your file
    # banks_file = 'banks.csv'  # Replace with your file
    withdrawals_file = 'Bank and ILF Program Credit Tracking 2024_10_16.csv'
    banks_file = 'All banks .xlsx'  # Replace with your file
    tqdm.pandas()
    
    try:
        withdrawals_df = pd.read_csv(withdrawals_file)
        banks_df = pd.read_excel(banks_file)
        
        # Perform matching
        matched_results = match_bank_names(withdrawals_df, banks_df)
        
        # Analyze results
        analyze_matching_results(matched_results)
        
        # Save results
        matched_results.to_csv('matched_results.csv', index=False)
        print("Results saved to 'matched_results.csv'")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure input files exist and are in the correct location.")

if __name__ == "__main__":
    main()
