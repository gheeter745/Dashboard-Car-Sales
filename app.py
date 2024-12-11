#For data manipulation
import pandas as pd
import numpy as np

#for data visualization
import plotly.express as px
import plotly.graph_objects as go


#for web application
import streamlit as st

# Loading our dataset
df_vehicles = pd.read_csv('vehicles_us.csv')
# Pulling up the top 10 data entries for sampling purposes
df_vehicles.head(10)

# Displaying general summary information about the plan's dataframe
df_vehicles.info()

#Creating a new variable for duplicated values
duplicate_rows = df_vehicles[df_vehicles.duplicated()]
print(duplicate_rows)

# Checking for Missing Values
rows_with_missing_values = df_vehicles.isnull().any(axis=1).sum()
print(f"Rows with any missing values: {rows_with_missing_values}")

#splitting 'model' to give a seperate column called 'manufacturer'
df_vehicles['manufacturer'] = df_vehicles['model'].apply(lambda x:x.split()[0])
# Remove the 'manufacturer' column and store it
manufacturer_column = df_vehicles.pop('manufacturer')
# Insert the 'manufacturer' column at the first position (index 1)
df_vehicles.insert(0, 'manufacturer', manufacturer_column)
# Remove the manufacturer's names from the 'model' column
df_vehicles['model'] = df_vehicles.apply(lambda row: row['model'].replace(row['manufacturer'] + ' ', ''), axis=1)
# Renaming 'type' column to 'body type' for improved user friendliness
df_vehicles.rename(columns={'type': 'body_type'}, inplace=True)
# Renaming 'price' column to 'price_USD' for improved user friendliness
df_vehicles.rename(columns={'price': 'price_USD'}, inplace=True)
# Removing the 'cylinders' column and storing it
cylinders_column = df_vehicles.pop('cylinders')
# Insert the 'cylinders' column as column 4
df_vehicles.insert(4, 'cylinders', cylinders_column)
# Removing the 'transmission' column and storing it
transmission_column = df_vehicles.pop('transmission')
# Inserting the 'transmission' column as column 5
df_vehicles.insert(5, 'transmission', transmission_column)
# Removing the 'condition' column and storing it
condition_column = df_vehicles.pop('condition')
# Inserting the 'condition' column as column 10
df_vehicles.insert(10, 'condition', condition_column)
# Removing the 'body_type' column and storing it
body_type_column = df_vehicles.pop('body_type')
# Inserting the 'body_type' column as column 4
df_vehicles.insert(4, 'body_type', body_type_column)
# Removing the 'is_4wd' column and storing it
is_4wd_column = df_vehicles.pop('is_4wd')
# Inserting the 'body_type' column as column 6
df_vehicles.insert(6, 'is_4wd', is_4wd_column)
# Removing the 'odometer' column and storing it
odometer_column = df_vehicles.pop('odometer')
# Inserting the 'odometer' column as column 9
df_vehicles.insert(9, 'odometer', odometer_column)
# Removing the 'price_USD' column and storing it
price_USD_column = df_vehicles.pop('price_USD')
# Inserting the 'price_USD' column as column 13
df_vehicles.insert(13, 'price_USD', price_USD_column)
# Removing the 'model_year' column and storing it
model_year_column = df_vehicles.pop('model_year')
# Inserting the 'model_year' column as column 2
df_vehicles.insert(2, 'model_year', model_year_column)

# 1. Convert 'price' to float64
df_vehicles['price_USD'] = df_vehicles['price_USD'].astype(float)

# 2. Convert 'model_year' to int64
df_vehicles['model_year'] = df_vehicles['model_year'].astype('Int64')  # using 'Int64' to handle NaNs

# 3. Convert 'is_4wd' to boolean and replace values
df_vehicles['is_4wd'] = df_vehicles['is_4wd'].fillna(0).astype(bool)  # Convert to boolean
df_vehicles['is_4wd'] = df_vehicles['is_4wd'].replace({True: 'yes', False: 'no'})  # Replace 1 with 'yes' and 0 with 'no'

# Define a function to fill missing 'model_year' values with the median, converted to an integer
def fill_with_median_int(group):
    median = int(group.median())
    return group.fillna(median)

# Define a function to fill missing 'cylinder' values with the median
def fill_with_median(group):
    median = group.median()
    return group.fillna(median)

# Apply the function to the 'model_year' column, grouped by 'model'
df_vehicles['model_year'] = df_vehicles.groupby('model')['model_year'].transform(fill_with_median_int)

# Apply the function to the 'cylinders' column, grouped by 'model'
df_vehicles['cylinders'] = df_vehicles.groupby('model')['cylinders'].transform(fill_with_median)

# Convert 'model_year' to int64
df_vehicles['model_year'] = df_vehicles['model_year'].astype('Int64')

# Define a function to fill missing values with the mean
def fill_with_mean(group):
    mean = group.mean()
    return group.fillna(mean)

# Group by 'model_year' (or 'model' + 'model_year') and apply the function
df_vehicles['odometer'] = df_vehicles.groupby(['model', 'model_year'])['odometer'].transform(fill_with_mean)

# Fill missing values in the 'paint_color' column with the word "Unspecified"
df_vehicles['paint_color'].fillna('Unspecified', inplace=True)



# Display the DataFrame to verify changes
print(df_vehicles.dtypes)
print(df_vehicles.head())

# Streamlit header
st.header('Data viewer')

# Checkbox to include/exclude manufacturers with less than 1000 ads
show_manuf_1k_ads = st.checkbox('Include manufacturers with less than 1000 ads', key='show_manuf_1k_ads')
if not show_manuf_1k_ads:
    df_vehicles = df_vehicles.groupby('manufacturer').filter(lambda x: len(x) > 1000)

# Dropdown filters for each column except price
columns_to_filter = ['model_year', 'manufacturer', 'model', 'condition', 'cylinders', 'fuel', 'odometer']
for i, column in enumerate(columns_to_filter):
    unique_values = df_vehicles[column].dropna().unique()
    selected_value = st.selectbox(f'Filter by {column}', options=['All'] + list(unique_values), key=f'filter_{column}_{i}')
    if selected_value != 'All':
        df_vehicles = df_vehicles[df_vehicles[column] == selected_value]

# Display the dataframe
st.dataframe(df_vehicles)

st.header('Vehicle types by manufacturer')
st.write(px.histogram(df_vehicles, x='manufacturer', color='body_type'))

st.header('Histogram of `condition` vs `model_year`')
st.write(px.histogram(df_vehicles, x='model_year', color='condition'))

st.header('Compare price distribution between manufacturers')
manufac_list = sorted(df_vehicles['manufacturer'].unique())
manufacturer_1 = st.selectbox('Select manufacturer 1', manufac_list, index=manufac_list.index('chevrolet'), key='manufacturer_1')
manufacturer_2 = st.selectbox('Select manufacturer 2', manufac_list, index=manufac_list.index('hyundai'), key='manufacturer_2')

mask_filter = (df_vehicles['manufacturer'] == manufacturer_1) | (df_vehicles['manufacturer'] == manufacturer_2)
df_filtered = df_vehicles[mask_filter]

normalize = st.checkbox('Normalize histogram', value=True, key='normalize')
histnorm = 'percent' if normalize else None
st.write(px.histogram(df_filtered, x='price_USD', nbins=30, color='manufacturer', histnorm=histnorm, barmode='overlay'))

# Streamlit header for the scatter plot
st.header('Depreciation Rates of Price vs Mileage for All Manufacturers')

# Dropdown menu to select manufacturer
manufacturers = ['All'] + sorted(df_vehicles['manufacturer'].unique())
selected_manufacturer = st.selectbox('Select a Manufacturer', manufacturers, key='selected_manufacturer_scatter')

# Filter the dataframe based on the selected manufacturer
if selected_manufacturer != 'All':
    filtered_df = df_vehicles[df_vehicles['manufacturer'] == selected_manufacturer]
else:
    filtered_df = df_vehicles

# Checkbox to toggle visibility of scatter plot
show_scatter = st.checkbox('Show Scatter Plot', value=True, key='show_scatter')

if show_scatter:
    # Checkboxes to toggle scatter points and correlation lines
    show_trendline = st.checkbox('Show Correlation Line', value=True, key='show_trendline')

    # Determine trendline parameter based on checkbox
    trendline = "ols" if show_trendline else None

    # Create the scatter plot
    fig = px.scatter(filtered_df, x='odometer', y='price_USD', color='model', 
                     title=f'Depreciation Rates of Price vs Mileage for {selected_manufacturer}' if selected_manufacturer != 'All' else 'Depreciation Rates of Price vs Mileage for All Manufacturers',
                     labels={'odometer': 'Odometer Reading (miles)', 'price_USD': 'Price (USD)'}, 
                     hover_data=['model_year', 'condition'],
                     trendline=trendline)

    # Display the scatter plot
    st.plotly_chart(fig)

    # Add text explanation below the scatter plot
    st.write("Steeper lines indicate faster depreciation rates.")

# Streamlit header for the histogram
st.header('Average Listed Days by Model')

# Dropdown menu to select manufacturer
selected_manufacturer_hist = st.selectbox('Select a Manufacturer', manufacturers, key='selected_manufacturer_hist')

# Radio button to select the sort order
sort_order = st.radio('Sort Order', ['Alphabetical', 'Ascending by Average Listed Days'], key='sort_order')

# Filter the dataframe based on the selected manufacturer
if selected_manufacturer_hist != 'All':
    filtered_df_hist = df_vehicles[df_vehicles['manufacturer'] == selected_manufacturer_hist]
else:
    filtered_df_hist = df_vehicles

# Calculate average listed days by model for the filtered data
average_listed_days = filtered_df_hist.groupby('model')['days_listed'].mean().reset_index()
average_listed_days.columns = ['model', 'average_listed_days']

# Sort the data based on the selected sort order
if sort_order == 'Alphabetical':
    average_listed_days = average_listed_days.sort_values(by='model')
else:
    average_listed_days = average_listed_days.sort_values(by='average_listed_days', ascending=True)

# Create the histogram using Plotly Express
fig_hist = px.histogram(average_listed_days, x='average_listed_days', y='model', color='model', 
                        title=f'Average Listed Days by Model for {selected_manufacturer_hist}' if selected_manufacturer_hist != 'All' else 'Average Listed Days by Model for All Manufacturers',
                        labels={'model': 'Model', 'average_listed_days': 'Average Listed Days'},
                        color_discrete_sequence=px.colors.qualitative.Dark24,
                        orientation='h')

# Display the histogram in Streamlit
st.plotly_chart(fig_hist)
