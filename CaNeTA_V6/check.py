# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 16:02:09 2024

@author: uqylin13
"""

import pandas as pd

# Load the Excel file
file_path = 'Results.xlsx'  # Replace with your Excel file path
df = pd.read_excel(file_path)

# Filter columns that start with 'P(Degree >= X) stable:'
filtered_columns = [col for col in df.columns if col.startswith('P(Degree >= X) stable:')]

# Initialize variables to track the change in order and the previous "state"
change_orders = []
previous_state = None

# Iterate through filtered columns to detect changes in the final string after '_'
for col in filtered_columns:
    # Extract the part after 'stable:' and split by '_'
    parts = col.split('stable:')[-1].strip().split('_')
    # Extract the order and state
    order, state = parts[0], parts[1]
    
    # If it's the first iteration or if the state has changed since the last column
    if previous_state is None or state != previous_state:
        change_orders.append(int(order))  # Record the order as an integer
    
    # Update the previous_state for the next iteration
    previous_state = state

# Output the recorded orders as a list
print(change_orders)
