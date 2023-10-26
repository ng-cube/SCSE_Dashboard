import streamlit as st
import pandas as pd
import numpy as np
from warehouse import get_list_of_keywords,find_name_using_keyword, get_keywords_given_name,find_num_contributions_using_name
from warehouse import plot_year_of_involvement
# Config

st.set_page_config(
    page_title="SCSE Dashboard",
    page_icon="🚀",
    layout="wide",
)

# Load data from CSV
data = pd.read_csv('professors_new.csv')

smiley = "😄"  # Smiley emoji
star = "⭐"    # Star emoji
hi = "Hi 👋"   # Hand waving emoji
email_emoji = "📧"
school = "🏫"
link_emoji = "🔗"
paper = "📚"

# Cover page
faculty_intro = """
Welcome to the NTU School of Computer Science and Engineering Faculty Dashboard. 
Here, you can explore information about our esteemed professors!
"""
intro_with_icons = f"{smiley}{hi}{faculty_intro}{star} "
st.title("SCSE Dashboard")
st.markdown(intro_with_icons, unsafe_allow_html=True)

# Create a professor selection dropdown
selected_tab = st.sidebar.radio("Select a page",["Home", "Professors"])
tab_content = st.empty()

# Define the content for each tab
if selected_tab == "Home":

    col1, col2 = st.columns(2,gap='large')
    with col1:
        options = st.multiselect(
            'Selected topics',
            get_list_of_keywords(),
            [])
        st.subheader('List of professors')
        for item in find_name_using_keyword(options):
            st.write(item)
            
    with col2:
        # selected_keyword = st.selectbox("Which topic?", options=list_of_keywords)
        # st.write('You selected:', find_name_using_keyword([selected_keyword]))
        st.markdown("#")


#==================================================================================================================  
elif selected_tab == "Professors":
   
    col1, col2 = st.columns(2,gap='large')
    with col1:
        selected_professor = st.selectbox("Which professor's information would you like to view?", data['Full Name'])

        # Filter data based on selected professor or keyword
        if selected_professor:
            professor_data = data[data['Full Name'] == selected_professor]
            
            email = professor_data['Email'].iloc[0]
            DRNTU_url = professor_data['DR-NTU URL'].iloc[0]
            if pd.isna(professor_data['Website URL'].iloc[0]):
                personal_site = None
            else:
                personal_site = professor_data['Website URL'].iloc[0]
            if pd.isna(professor_data['DBLP URL'].iloc[0]):
                dblp_url = None
            else:
                dblp_url = professor_data['DBLP URL'].iloc[0]
            
            biography = professor_data['biography'].iloc[0]
            citation = professor_data['Citations (All)'].iloc[0] 
            no_citation = int(citation) if not pd.isna(citation) else None
        else:
            professor_data = data

        # Display professor details
        if professor_data.empty:
            st.warning("No professor found with the given selection.")
        else:
            st.subheader("Professor Details")
            st.markdown(f"{email_emoji} **Email:** {email}")
            st.markdown(f"{school} **DR-NTU:** {DRNTU_url}")
            if dblp_url:
                st.markdown(f"{paper} **DBLP:** {dblp_url}")
            if personal_site:
                st.markdown(f"{link_emoji} **Website:** {personal_site}")
            # Expanders
            with st.expander("Research Interest"):
                research_interest = get_keywords_given_name(selected_professor)
                for item in research_interest:
                    st.markdown(f"- **{item}**")
            with st.expander("Biography"):
                st.write(biography)
            
            # Publications
            st.subheader("Publications",divider='rainbow')
            tab1, tab2 = st.tabs(["By year","By type"])
            # with tab1:

            # with tab2:
                    
    with col2:
        # Display bar chart   
        st.metric("Total Citations",no_citation)
        count_publications = find_num_contributions_using_name(selected_professor)    
        plot_year_of_involvement(count_publications[0]) 


            
       
