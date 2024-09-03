#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import streamlit as st
import types

def my_hash_func(obj):
    # Define your custom hashing logic here if needed
    return hash(str(obj))

@st.cache(hash_funcs={types.FunctionType: my_hash_func})
def load_data():
    url = 'https://github.com/michaelrosen3/pitch_plot_generator/blob/main/pitch_plot_data_excel_v2.xlsx?raw=true'
    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors
    return pd.read_excel(BytesIO(response.content))

# Example usage in Streamlit app
data = load_data()

# Load data once
statcast_data = load_data()

def plot_pitch_movement(pitcher_name):
    pitcher_data = statcast_data[statcast_data['player_name'] == pitcher_name]

    # Get unique pitch types for the pitcher
    pitch_types = pitcher_data['pitch_type'].unique()

    # Define a color palette with more distinct colors
    num_colors = len(pitch_types)
    pitch_color_dict = {
        'FF': '#D22D49', 'FT': '#DE6A04', 'SI': '#FE9D00', 'FC': '#933F2C', 
        'CH': '#1DBE3A', 'FS': '#3BACAC', 'SC': '#60DB33', 'FO': '#55CCAB', 
        'ST': '#DDB33A', 'SL': '#EEE716', 'CU': '#00D1ED', 'KC': '#6236CD', 
        'KN': '#3C44CD'
    }
    colors = [pitch_color_dict.get(pt, '#999999') for pt in pitch_types]

    plt.figure(figsize=(8, 8))
    for i, pitch_type in enumerate(pitch_types):
        pitches = pitcher_data[pitcher_data['pitch_type'] == pitch_type]
        plt.scatter(pitches['pfx_x'] * -12, pitches['pfx_z'] * 12, label=pitch_type, color=colors[i], alpha=0.7)

    # Add labels and title
    plt.axis('square')
    plt.xlabel('Horizontal Movement, pitcher perspective (inches)')
    plt.ylabel('Vertical Movement, pitcher perspective (inches)')
    plt.title(f'{pitcher_name} Pitch Plot (2024)')

    # Set x and y limits
    plt.xlim(-25, 25)
    plt.ylim(-25, 25)

    # Set x and y ticks
    plt.xticks(ticks=range(-25, 26, 5))
    plt.yticks(ticks=range(-25, 26, 5))

    # Add x-y lines
    plt.axhline(0, color='black', linestyle='--', linewidth=0.5)
    plt.axvline(0, color='black', linestyle='--', linewidth=0.5)

    # Add legend
    plt.legend()

    st.pyplot(plt)

# Streamlit app layout
st.title('Pitch Plot Generator')

st.text('FF: Four-Seam Fastball\n'
        'SI: Sinker\n'
        'CH: Changeup\n'
        'CU: Curveball\n'
        'SL: Slider\n'
        'FC: Cutter\n'
        'FS: Splitter\n'
        'KC: Knuckle Curve\n'
        'ST: Sweeper')

# Create a list of unique player names for the dropdown menu
player_names = sorted(statcast_data['player_name'].unique())

# Dropdown menu for player name selection
pitcher_name = st.selectbox('Search player name', [''] + player_names)

# Define firm start and end dates for the slider
firm_start_date = pd.to_datetime('2024-03-28')
firm_end_date = pd.to_datetime('2024-08-31')

# Date range slider with default range from March 28, 2024, to August 31, 2024
date_range = st.slider(
    'Select date range',
    min_value=firm_start_date,
    max_value=firm_end_date,
    value=(firm_start_date, firm_end_date),
    format="YYYY-MM-DD"
)

start_date, end_date = date_range

# Generate plot when the button is clicked
if st.button('Generate Pitch Plot'):
    if pitcher_name and pitcher_name in statcast_data['player_name'].unique():
        # Filter data based on the selected player and date range
        filtered_data = statcast_data[
            (statcast_data['player_name'] == pitcher_name) & 
            (statcast_data['game_date'] >= start_date) & 
            (statcast_data['game_date'] <= end_date)
        ]
        
        if not filtered_data.empty:
            plot_pitch_movement(filtered_data, pitcher_name)
        else:
            st.write('No data available for the selected date range.')
    else:
        st.write('Player not found. Please check the name and try again.')