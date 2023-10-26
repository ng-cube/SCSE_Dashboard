import pymongo
import plotly.express as px
import pandas as pd
import streamlit as st

def find_name_using_keyword(keywords=[]):
    '''
    Identifies all professors with specified keyword
    '''
    conn_str = "mongodb+srv://jingfang61:5tiCsIsCr58RSBWL@cluster0.h2vp8rc.mongodb.net/"
    client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
    db = client['scsedash'] 
    if len(keywords) == 0:
        names = []
    else:
        cursor = db.keywordsAndNames.find({"keyword": {"$in": keywords}},{"_id":0,"names":1})
        names = set()
        for dic in cursor:
            names.update(dic["names"])
    return names


def find_num_contributions_using_name(name):
    '''
    Identifies number of publications with specified professor
    '''
    conn_str = "mongodb+srv://jingfang61:5tiCsIsCr58RSBWL@cluster0.h2vp8rc.mongodb.net/"
    client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
    db = client['scsedash'] 
    cursor = db.DBLP_publications.find({"name":name},{"_id":0,"name":1,"num_contributions":1})
    result = []
    for dic in cursor:
        result.append(dic)
    return result


def get_list_of_keywords():
    '''
    Get the entire list of keywords 
    '''
    conn_str = "mongodb+srv://jingfang61:5tiCsIsCr58RSBWL@cluster0.h2vp8rc.mongodb.net/"
    client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
    db = client['scsedash'] 
    collection = db['keywordsAndNames']
    result = collection.distinct('keyword')
    return result


def get_keywords_given_name(name):
    '''
    Get the list of keywords given professor's name
    '''
    conn_str = "mongodb+srv://jingfang61:5tiCsIsCr58RSBWL@cluster0.h2vp8rc.mongodb.net/"
    client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
    db = client['scsedash'] 
    cursor = db.professors.find({"name":name},{"_id":0})
    result = []
    for dic in cursor:
        result.append(dic)
    return result[0]['keywords']


def plot_year_of_involvement(data):
    years = sorted([int(year) for year in data['num_contributions'].keys()])
    contribution_types = set()
    for year_data in data['num_contributions'].values():
        contribution_types.update(year_data.keys())

    data_list = []
    for year, year_data in data['num_contributions'].items():
        row = {'Year': int(year)}
        row.update(year_data)
        data_list.append(row)

    df = pd.DataFrame(data_list)

    # Define a custom color scale for contribution types
    custom_color_scale = {
        'Journal Articles': '#aec7e8',  # Light blue
        'Conference and Workshop Papers': '#ff7f0e',  # Orange
        'Informal and Other Publications': '#1f77b4',  # Dark blue
        'Editorship': '#ffbb78',  # Light orange
        'Books and Theses': '#98df8a',  # Light green
        'Parts in Books or Collections': '#d62728',  # Red
        'Reference Works': '#c5b0d5'  # Lavender
    }

    # Create the stacked bar chart
    fig = px.bar(df, x='Year', y=list(contribution_types), title=f'{data["name"]} - Year of Involvement',
                 labels={'value': 'Number of Contributions', 'variable': 'Contribution Type'},
                 barmode='relative',color='variable', color_discrete_map=custom_color_scale)

    # Show the chart
    fig.update_layout(xaxis_title='Year', yaxis_title='Number of Contributions',
                     plot_bgcolor='white',paper_bgcolor='#ebd2b9')
    
    # Display the Plotly chart in Streamlit
    st.subheader("Year of Involvement")
    st.plotly_chart(fig)



