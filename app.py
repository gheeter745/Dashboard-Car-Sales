import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset
df = pd.read_csv('vehicles_us.csv')

# Extract the manufacturer from the model
df['manufacturer'] = df['model'].apply(lambda x: x.split()[0])

# Streamlit header
st.header('Data viewer')

# Checkbox to include/exclude manufacturers with less than 1000 ads
show_manuf_1k_ads = st.checkbox('Include manufacturers with less than 1000 ads', key='show_manuf_1k_ads')
if not show_manuf_1k_ads:
    df = df.groupby('manufacturer').filter(lambda x: len(x) > 1000)

# Display the dataframe
st.dataframe(df)


st.header('Vehicle types by manufacturer')
st.write(px.histogram(df, x='manufacturer', color='type'))

st.header('Histogram of `condition` vs `model_year`')
st.write(px.histogram(df, x='model_year', color='condition'))

st.header('Compare price distribution between manufacturers')
manufac_list = sorted(df['manufacturer'].unique())
manufacturer_1 = st.selectbox('Select manufacturer 1', manufac_list, index=manufac_list.index('chevrolet'))
manufacturer_2 = st.selectbox('Select manufacturer 2', manufac_list, index=manufac_list.index('hyundai'))

mask_filter = (df['manufacturer'] == manufacturer_1) | (df['manufacturer'] == manufacturer_2)
df_filtered = df[mask_filter]

normalize = st.checkbox('Normalize histogram', value=True)
histnorm = 'percent' if normalize else None
st.write(px.histogram(df_filtered, x='price', nbins=30, color='manufacturer', histnorm=histnorm, barmode='overlay'))

# Streamlit header for the scatter plot
st.header('Depreciation Rates of Price vs Mileage for All Manufacturers')

# Dropdown menu to select manufacturer
manufacturers = ['All'] + sorted(df['manufacturer'].unique())
selected_manufacturer = st.selectbox('Select a Manufacturer', manufacturers)

# Filter the dataframe based on the selected manufacturer
if selected_manufacturer != 'All':
    filtered_df = df[df['manufacturer'] == selected_manufacturer]
else:
    filtered_df = df

# Create the scatter plot with a correlation line
fig = px.scatter(filtered_df, x='odometer', y='price', color='model', 
                 title=f'Depreciation Rates of Price vs Mileage for {selected_manufacturer}' if selected_manufacturer != 'All' else 'Depreciation Rates of Price vs Mileage for All Manufacturers',
                 labels={'odometer': 'Odometer Reading (miles)', 'price': 'Price (USD)'}, 
                 hover_data=['model_year', 'condition'],
                 trendline="ols")

# Display the scatter plot
st.plotly_chart(fig)

# Add text explanation below the scatter plot
st.write("Steeper lines indicate faster depreciation rates.")

# Streamlit header
st.header('Average Listed Days by Model for All Manufacturers')

# Calculate average listed days by model
average_listed_days = df.groupby('model')['days_listed'].mean().reset_index()
average_listed_days.columns = ['model', 'average_listed_days']

# Create the bar chart using Plotly Express
fig = px.bar(average_listed_days, x='model', y='average_listed_days', color='model', 
             title='Average Listed Days by Model for All Manufacturers',
             labels={'model': 'Model', 'average_listed_days': 'Average Listed Days'},
             color_discrete_sequence=px.colors.qualitative.Dark24)

# Display the bar chart in Streamlit
st.plotly_chart(fig)
