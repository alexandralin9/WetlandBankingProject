
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

df = pd.read_csv('matched_results (2).csv')

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    r = 6371
    return c * r

df['Distance_km'] = df.apply(lambda row: haversine(row['Impact LocationLatitude'], 
                                                    row['Impact LocationLongitude'], 
                                                    row['Matched_Latitude'], 
                                                    row['Matched_Longitude']) 
                             if not any(pd.isnull([row['Impact LocationLatitude'], 
                                                    row['Impact LocationLongitude'], 
                                                    row['Matched_Latitude'], 
                                                    row['Matched_Longitude']])) 
                             else np.nan, axis=1)

output_filename = 'updated_matched_results.csv'
df.to_csv(output_filename, index=False)
