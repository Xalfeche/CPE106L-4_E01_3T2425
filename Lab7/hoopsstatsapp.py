"""
File: hoopstatsapp.py

The application for analyzing basketball stats.
"""

from hoopstatsview import HoopStatsView
import pandas as pd
import os

def cleanStats(df):
    """
    Clean basketball statistics data by splitting columns with 'makes-attempts' format.

    """
    
    # Create a copy of the dataframe to avoid modifying the original
    cleaned_df = df.copy()
    
    # Define the columns to clean and their new column names
    columns_to_clean = {
        'FG': ('FGM', 'FGA'),      # Field Goals Made, Field Goals Attempted
        '3PT': ('3PTM', '3PTA'),   # 3-Point Made, 3-Point Attempted
        'FT': ('FTM', 'FTA')       # Free Throws Made, Free Throws Attempted
    }
    
    # Process each column that needs cleaning
    for original_col, (makes_col, attempts_col) in columns_to_clean.items():
        if original_col in cleaned_df.columns:
            # Find the position of the original column
            col_position = cleaned_df.columns.get_loc(original_col)
            
            # Split the column data
            # Handle potential NaN values and convert to string first
            split_data = cleaned_df[original_col].astype(str).str.split('-', expand=True)
            
            # Create the makes and attempts columns
            makes_series = pd.to_numeric(split_data[0], errors='coerce')
            attempts_series = pd.to_numeric(split_data[1], errors='coerce')
            
            # Remove the original column
            cleaned_df = cleaned_df.drop(columns=[original_col])
            
            # Insert the new columns at the appropriate position
            cleaned_df.insert(col_position, makes_col, makes_series)
            cleaned_df.insert(col_position + 1, attempts_col, attempts_series)
    
    return cleaned_df

def main():
    """Creates the data frame and view and starts the app."""
    frame = pd.read_csv("cleanbrogdonstats.csv")
    HoopStatsView(frame)

if __name__ == "__main__":
    main()