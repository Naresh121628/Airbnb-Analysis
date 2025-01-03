# Importing Libraries
import pandas as pd
import pymongo
import streamlit as st
import plotly.express as px
from PIL import Image

# Setting up page configuration
icon = Image.open("ICN.png")
st.set_page_config(layout="wide")

# CREATING CONNECTION WITH MONGODB ATLAS AND RETRIEVING THE DATA
client = pymongo.MongoClient("mongodb+srv://Naresh:Aswini1216@cluster1.my0b6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
db = client.sample_airbnb
col = db.listingsAndReviews

# READING THE CLEANED DATAFRAME
df = pd.read_csv('Airbnb_data.csv')

# Displaying Title
st.write("""
<div style='text-align:center'>
    <h1 style='color:#FF5349;'>Airbnb Analysis Application</h1>
</div>
""", unsafe_allow_html=True)

# Creating tabs for Overview and Explore
tab1, tab2 = st.tabs(["Overview", "Explore"])

# OVERVIEW PAGE
with tab1:
    tab3, tab4 = st.tabs(["$\huge 📝 RAW DATA $", "$\huge🚀 INSIGHTS $"])

    # RAW DATA TAB
    with tab3:
        col1, col2 = st.columns(2)
        if col1.button("Click to view Raw data"):
            col1.write(col.find_one())
        # DATAFRAME FORMAT
        if col2.button("Click to view Dataframe"):
            col1.write(col.find_one())
            col2.write(df)

    # INSIGHTS TAB
    with tab4:
        # Sidebar filters with unique keys for each multiselect widget
        country = st.sidebar.multiselect(
            'Select a country', 
            options=sorted(df.country.unique()), 
            default=[], 
            key="country_select"
        )

        prop = st.sidebar.multiselect(
            'Select property_type', 
            options=sorted(df.property_type.unique()), 
            default=[], 
            key="property_type_select"
        )

        room = st.sidebar.multiselect(
            'Select room_type', 
            options=sorted(df.room_type.unique()), 
            default=[], 
            key="room_type_select"
        )

        price = st.sidebar.slider(
            'Select price', 
            min_value=int(df.price.min()), 
            max_value=int(df.price.max()), 
            value=(int(df.price.min()), int(df.price.max())),
            key="price_slider"
        )

        # CONVERTING THE USER INPUT INTO QUERY
        query = f'country in {country} & room_type in {room} & property_type in {prop} & price >= {price[0]} & price <= {price[1]}'

        # Creating columns for charts
        col1, col2 = st.columns(2, gap='medium')

        with col1:
            # Top 10 Property Types Bar Chart
            df1 = df.query(query).groupby(["property_type"]).size().reset_index(name="listings").sort_values(by='listings', ascending=False)[:10]
            fig = px.bar(df1, x='listings', y='property_type', orientation='h', color='property_type', color_continuous_scale=px.colors.sequential.Agsunset)
            st.plotly_chart(fig, use_container_width=True)

            # Top 10 Hosts Bar Chart
            df2 = df.query(query).groupby(["host_name"]).size().reset_index(name="listings").sort_values(by='listings', ascending=False)[:10]
            fig = px.bar(df2, x='listings', y='host_name', orientation='h', color='host_name', color_continuous_scale=px.colors.sequential.Agsunset)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Total Listings in Each Room Type Pie Chart
            df1 = df.query(query).groupby(["room_type"]).size().reset_index(name="counts")
            fig = px.pie(df1, names='room_type', values='counts', color_discrete_sequence=px.colors.sequential.Rainbow)
            fig.update_traces(textposition='outside', textinfo='value+label')
            st.plotly_chart(fig, use_container_width=True)

            # Total Listings by Country Choropleth Map
            country_df = df.query(query).groupby(['country'], as_index=False)['Name'].count().rename(columns={'Name': 'Total_listings'})
            fig = px.choropleth(country_df, locations='country', locationmode='country names', color='Total_listings', color_continuous_scale=px.colors.sequential.Plasma)
            st.plotly_chart(fig, use_container_width=True)

# EXPLORE PAGE
with tab2:
    st.markdown("## Explore more about the Airbnb data")

    # Sidebar filters with unique keys for each multiselect widget
    #country = st.sidebar.multiselect(
    #    'Select a country', 
    #    options=sorted(df.country.unique()), 
    #    default=[], 
    #    key="country_select_explore"
    #)
#
    #prop = st.sidebar.multiselect(
    #    'Select property_type', 
    #    options=sorted(df.property_type.unique()), 
    #    default=[], 
    #    key="property_type_select_explore"
    #)
#
    #room = st.sidebar.multiselect(
    #    'Select room_type', 
    #    options=sorted(df.room_type.unique()), 
    #    default=[], 
    #    key="room_type_select_explore"
    #)
#
    #price = st.sidebar.slider(
    #    'Select price', 
    #    min_value=int(df.price.min()), 
    #    max_value=int(df.price.max()), 
    #    value=(int(df.price.min()), int(df.price.max())),
    #    key="price_slider_explore"
    #)

    # CONVERTING THE USER INPUT INTO QUERY
    query = f'country in {country} & room_type in {room} & property_type in {prop} & price >= {price[0]} & price <= {price[1]}'

    # Heading 1
    st.markdown("## Price Analysis")

    # Creating columns for charts
    col1, col2 = st.columns(2, gap='medium')

    with col1:
        # Avg Price by Room Type Bar Chart
        pr_df = df.query(query).groupby('room_type', as_index=False)['price'].mean().sort_values(by='price')
        fig = px.bar(data_frame=pr_df, x='room_type', y='price', color='price', title='Avg price in each Room type')
        st.plotly_chart(fig, use_container_width=True)

        # Heading 2
        st.markdown("## Availability Analysis")

        # Availability by Room Type Box Plot
        fig = px.box(data_frame=df.query(query), x='room_type', y='availability_365', color='room_type', title='Availability by room_type')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Avg Price in Countries Scatter Geo
        country_df = df.query(query).groupby('country', as_index=False)['price'].mean()
        fig = px.scatter_geo(data_frame=country_df, locations='country', color='price', hover_data=['price'], locationmode='country names', size='price', title='Avg price in each country', color_continuous_scale='agsunset')
        col2.plotly_chart(fig, use_container_width=True)

        # Blank Space
        st.markdown("#   ")
        st.markdown("#   ")

        # Avg Availability in Countries Scatter Geo
        country_df = df.query(query).groupby('country', as_index=False)['availability_365'].mean()
        country_df.availability_365 = country_df.availability_365.astype(int)
        fig = px.scatter_geo(data_frame=country_df, locations='country', color='availability_365', hover_data=['availability_365'], locationmode='country names', size='availability_365', title='Avg Availability in each country', color_continuous_scale='agsunset')
        st.plotly_chart(fig, use_container_width=True)
