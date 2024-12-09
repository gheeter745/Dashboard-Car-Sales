import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset
df_vehicles = pd.read_csv('vehicles_us.csv')

#splitting 'model' to give a seperate column called 'manufacturer'
df_vehicles['manufacturer'] = df_vehicles['model'].apply(lambda x:x.split()[0])
# Remove the 'manufacturer' column and store it
manufacturer_column = df_vehicles.pop('manufacturer')
# Insert the 'manufacturer' column at the second position (index 1)
df_vehicles.insert(2, 'manufacturer', manufacturer_column)
# Renaming 'type' column to 'body type' for improved user friendliness
df_vehicles.rename(columns={'type': 'body_type'}, inplace=True)

# Remove the manufacturer's name from the 'model' column
df_vehicles['model'] = df_vehicles['model'].apply(lambda x: x.split(' ', 1)[1] if ' ' in x else x)

display(df_vehicles)
# Fill missing values for columns with numerical value
numerical_to_fill = {
    'price': 0,
    'model_year': 0,
    'cylinders': 0,
    'odometer': 9000000,
    'is_4wd': 0      
}
df_vehicles.fillna(value=numerical_to_fill, inplace=True)

text_to_fill = ['manufacturer', 'model', 'condition', 'fuel', 'transmission', 'body_type', 'paint_color']
shared_fill_value = 'Unspecified'

df_vehicles[text_to_fill] = df_vehicles[text_to_fill].fillna(shared_fill_value)


# Streamlit header
st.header('Data viewer')

# Checkbox to include/exclude manufacturers with less than 1000 ads
show_manuf_1k_ads = st.checkbox('Include manufacturers with less than 1000 ads', key='show_manuf_1k_ads')
if not show_manuf_1k_ads:
    df_vehicles = df_vehicles.groupby('manufacturer').filter(lambda x: len(x) > 1000)

# Display the dataframe
st.dataframe(df_vehicles)


st.header('Vehicle types by manufacturer')
st.write(px.histogram(df_vehicles, x='manufacturer', color='type'))

st.header('Histogram of `condition` vs `model_year`')
st.write(px.histogram(df_vehicles, x='model_year', color='condition'))

st.header('Compare price distribution between manufacturers')
manufac_list = sorted(df['manufacturer'].unique())
manufacturer_1 = st.selectbox('Select manufacturer 1', manufac_list, index=manufac_list.index('chevrolet'))
manufacturer_2 = st.selectbox('Select manufacturer 2', manufac_list, index=manufac_list.index('hyundai'))

mask_filter = (df_vehicles['manufacturer'] == manufacturer_1) | (df_vehicles['manufacturer'] == manufacturer_2)
df_filtered = df[mask_filter]

normalize = st.checkbox('Normalize histogram', value=True)
histnorm = 'percent' if normalize else None
st.write(px.histogram(df_filtered, x='price', nbins=30, color='manufacturer', histnorm=histnorm, barmode='overlay'))

# Streamlit header for the scatter plot
st.header('Depreciation Rates of Price vs Mileage for All Manufacturers')

# Dropdown menu to select manufacturer
manufacturers = ['All'] + sorted(df_vehicles['manufacturer'].unique())
selected_manufacturer = st.selectbox('Select a Manufacturer', manufacturers)

# Filter the dataframe based on the selected manufacturer
if selected_manufacturer != 'All':
    filtered_df = df_vehicles[df_vehicles['manufacturer'] == selected_manufacturer]
else:
    filtered_df = df_vehicles

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
    filtered_df = df_vehicles[df_vehicles['manufacturer'] == selected_manufacturer]
else:
    filtered_df = df_vehicles

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