import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset
df = pd.read_csv('vehicles_us.csv')

#splitting 'model' to give a seperate column called 'manufacturer'
df['manufacturer'] = df['model'].apply(lambda x:x.split()[0])
# Remove the 'manufacturer' column and store it
manufacturer_column = df.pop('manufacturer')
# Insert the 'manufacturer' column at the second position (index 1)
df.insert(2, 'manufacturer', manufacturer_column)
# Renaming 'type' column to 'body type' for improved user friendliness
df.rename(columns={'type': 'body_type'}, inplace=True)

# Streamlit header
st.header('Data viewer')

# Checkbox to include/exclude manufacturers with less than 1000 ads
show_manuf_1k_ads = st.checkbox('Include manufacturers with less than 1000 ads', key='show_manuf_1k_ads_1')
if not show_manuf_1k_ads:
    df = df.groupby('manufacturer').filter(lambda x: len(x) > 1000)

# Display the dataframe
st.dataframe(df)

st.header('Vehicle types by manufacturer')
st.write(px.histogram(df, x='manufacturer', color='body_type'))

st.header('Histogram of `condition` vs `model_year`')
st.write(px.histogram(df, x='model_year', color='condition'))

st.header('Compare price distribution between manufacturers')
manufac_list = sorted(df['manufacturer'].unique())
manufacturer_1 = st.selectbox('Select manufacturer 1', manufac_list, index=manufac_list.index('chevrolet'), key='manufacturer_1')
manufacturer_2 = st.selectbox('Select manufacturer 2', manufac_list, index=manufac_list.index('hyundai'), key='manufacturer_2')

mask_filter = (df['manufacturer'] == manufacturer_1) | (df['manufacturer'] == manufacturer_2)
df_filtered = df[mask_filter]

normalize = st.checkbox('Normalize histogram', value=True, key='normalize')
histnorm = 'percent' if normalize else None
st.write(px.histogram(df_filtered, x='price', nbins=30, color='manufacturer', histnorm=histnorm, barmode='overlay'))

# Streamlit header for the scatter plot
st.header('Depreciation Rates of Price vs Mileage for All Manufacturers')

# Dropdown menu to select manufacturer
manufacturers = ['All'] + sorted(df['manufacturer'].unique())
selected_manufacturer = st.selectbox('Select a Manufacturer', manufacturers, key='selected_manufacturer_scatter')


# Filter the dataframe based on the selected manufacturer
if selected_manufacturer != 'All':
    filtered_df = df[df['manufacturer'] == selected_manufacturer]
else:
    filtered_df = df

# Checkboxes to toggle scatter points and correlation lines
show_trendline = st.checkbox('Show Correlation Line', value=True)

# Determine trendline parameter based on checkbox
trendline = "ols" if show_trendline else None

# Create the scatter plot
fig = px.scatter(filtered_df, x='odometer', y='price', color='model', 
                 title=f'Depreciation Rates of Price vs Mileage for {selected_manufacturer}' if selected_manufacturer != 'All' else 'Depreciation Rates of Price vs Mileage for All Manufacturers',
                 labels={'odometer': 'Odometer Reading (miles)', 'price': 'Price (USD)'}, 
                 hover_data=['model_year', 'condition'],
                 trendline=trendline)

# Display the scatter plot
st.plotly_chart(fig)

# Add text explanation below the scatter plot
st.write("Steeper lines indicate faster depreciation rates.")

# Streamlit header for the histogram
st.header('Average Listed Days by Model')

# Dropdown menu to select manufacturer
manufacturers = ['All'] + sorted(df['manufacturer'].unique())
selected_manufacturer = st.selectbox('Select a Manufacturer', manufacturers, key='selected_manufacturer')

# Radio button to select the sort order
sort_order = st.radio('Sort Order', ['Alphabetical', 'Ascending by Average Listed Days'], key='sort_order')

# Filter the dataframe based on the selected manufacturer
if selected_manufacturer != 'All':
    filtered_df = df[df['manufacturer'] == selected_manufacturer]
else:
    filtered_df = df

# Calculate average listed days by model for the filtered data
average_listed_days = filtered_df.groupby('model')['days_listed'].mean().reset_index()
average_listed_days.columns = ['model', 'average_listed_days']

# Sort the data based on the selected sort order
if sort_order == 'Alphabetical':
    average_listed_days = average_listed_days.sort_values(by='model')
else:
    average_listed_days = average_listed_days.sort_values(by='average_listed_days', ascending=True)

# Create the histogram using Plotly Express
fig = px.histogram(average_listed_days, x='average_listed_days', y='model', color='model', 
                   title=f'Average Listed Days by Model for {selected_manufacturer}' if selected_manufacturer != 'All' else 'Average Listed Days by Model for All Manufacturers',
                   labels={'model': 'Model', 'average_listed_days': 'Average Listed Days'},
                   color_discrete_sequence=px.colors.qualitative.Dark24,
                   orientation='h')

# Display the histogram in Streamlit
st.plotly_chart(fig)