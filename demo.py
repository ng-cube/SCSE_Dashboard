import streamlit as st
import pandas as pd
import numpy as np
from utils import get_list_of_keywords, find_name_using_keyword, get_keywords_given_name,find_num_contributions_using_name
from utils import plot_year_of_involvement, plot_scse_bar, display_overall_graph, display_individual_graph
from utils import display_publications_by_year, display_publications_by_type, display_top_n_keywords, faculty_intro
from utils import get_research_areas, display_top_coauthors,display_word_cloud, display_treemap, conference_count_plot

# Config
st.set_page_config(
    page_title="SCSE Dashboard",
    page_icon="🚀",
    layout="wide",
)

# Load data from CSV
data = pd.read_csv('./data/professors_new.csv',encoding='unicode_escape')

smiley = "😄"
star = "⭐"  
hi = "Hi 👋"  
email_emoji = "📧"
school = "🏫"
link_emoji = "🔗"
paper = "📚"

# Page header
page_intro = """
Welcome to the NTU School of Computer Science and Engineering Faculty Dashboard. 
Here, you can explore information about our esteemed professors!
"""
intro_with_icons = f"{smiley}{hi}{page_intro}{star}  \n You may choose some topics using the sidebar. The professors' individual profiles can be viewed under the professor tab, and you may view multiple profiles under the tab called 'View More'."
st.title("SCSE Dashboard")
st.markdown(intro_with_icons, unsafe_allow_html=True)

# Create a topic selection dropdown
with st.sidebar:
    options = st.multiselect(
                'Selected topics',
                get_list_of_keywords(),
                [])
    st.subheader('List of professors')
    list_of_professors = find_name_using_keyword(options)
    for item in list_of_professors:
        st.write(item)


tab1, tab2, tab3 = st.tabs(["💻SCSE", "✒️Professors", "⭐View More"])

with tab1:
    display_treemap()
    col1, col2 = st.columns(2,gap='large')
    with col1:
        with st.expander("Introduction"):
            st.markdown(faculty_intro)
        st.markdown(f"#### Research Areas")
        st.markdown(f"**Expand the broader area to reveal the list of associated keywords.**")
        for broader_area, specific_areas in get_research_areas().items():
            with st.expander(broader_area):
                for specific_area in specific_areas:
                    st.write(f'- {specific_area}')

        display_overall_graph()
   

    with col2:
        subcol4,subcol5,subcol6 = st.columns(3)
        with subcol4:
            st.metric("World Ranking","No. 4",delta=3)
        with subcol5:
            st.metric("Top 2% Scientists","31")
        with subcol6:
            st.metric("Research Projects","S$300m")
        plot_scse_bar()   
        display_top_n_keywords()


#==================================================================================================================  
# Professor page
with tab2:
    col1, col2 = st.columns(2,gap='large')
    with col1:
        if list_of_professors:
            selected_professor = st.selectbox("Which professor's information would you like to view?", list_of_professors)
        else:
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

            publications_count = professor_data['publications_count'].iloc[0]
            publications_count = int(publications_count) if not pd.isna(publications_count) else None
            
            top_conference_count = professor_data['top_conference_count'].iloc[0]
            top_conference_count = int(top_conference_count) if not pd.isna(top_conference_count) else None

        else:
            professor_data = data

        # Display professor details
        if professor_data.empty:
            st.warning("No professor found with the given selection.")
        else:
            st.subheader("Professor Details",divider='rainbow')
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
            if selected_professor in ['Sourav Saha Bhowmick','Tay Kian Boon','Ke Yiping, Kelly']:
                print("Sorry, currently no publication data is found.")
            else:
                st.subheader("Publications",divider='rainbow')
                
                subtab1, subtab2 = st.tabs(["By year","By type"])
                with subtab1:
                    display_publications_by_year(selected_professor)
                with subtab2:
                    display_publications_by_type(selected_professor)
                    
    with col2:
        # Display bar chart   
        if selected_professor in ['Sourav Saha Bhowmick','Tay Kian Boon','Ke Yiping, Kelly']:
            print("Sorry, currently no publication data is found.")
        else:
            subcol1,subcol2,subcol3 = st.columns(3)
            with subcol1:
                st.metric("Citations",no_citation)
            with subcol2:
                st.metric("Publications",publications_count)
            with subcol3:
                st.metric("Top Conferences",top_conference_count)
            count_publications = find_num_contributions_using_name(selected_professor)    
            plot_year_of_involvement(count_publications[0]) 
            conference_count_plot(selected_professor)
            display_word_cloud(selected_professor,key='individual')
            display_top_coauthors(selected_professor)
            display_individual_graph(selected_professor)

#======================================================================================
    with tab3:
        subcol7, subcol8 = st.columns(2,gap="large")
        with subcol7:
            if list_of_professors:
                selected_professor_a = st.selectbox("Please select a professor:", list_of_professors, key='select_a')
            else:
                selected_professor_a = st.selectbox("Please select a professor:", data['Full Name'], key='select_a')
            if selected_professor_a:
                professor_data_a = data[data['Full Name'] == selected_professor_a]         
                biography_a = professor_data_a['biography'].iloc[0]

                citation = professor_data_a['Citations (All)'].iloc[0] 
                no_citation = int(citation) if not pd.isna(citation) else None

                publications_count = professor_data_a['publications_count'].iloc[0]
                publications_count = int(publications_count) if not pd.isna(publications_count) else None
                
                top_conference_count = professor_data_a['top_conference_count'].iloc[0]
                top_conference_count = int(top_conference_count) if not pd.isna(top_conference_count) else None
            else:
                professor_data_a = data
            if professor_data_a.empty:
                st.warning("No professor found with the given selection.")

            with st.expander("Research Interest"):
                research_interest_a = get_keywords_given_name(selected_professor_a)
                for item in research_interest_a:
                    st.markdown(f"- **{item}**")
            with st.expander("Biography"):
                st.write(biography_a)
              # Display bar chart   
            if selected_professor_a in ['Sourav Saha Bhowmick','Tay Kian Boon','Ke Yiping, Kelly']:
                print("Sorry, currently no publication data is found.")
            else:
                subcol1,subcol2,subcol3 = st.columns(3)
                with subcol1:
                    st.metric("Citations",no_citation)
                with subcol2:
                    st.metric("Publications",publications_count)
                with subcol3:
                    st.metric("Top Conferences",top_conference_count)
                count_publications = find_num_contributions_using_name(selected_professor_a)    
                plot_year_of_involvement(count_publications[0]) 
                conference_count_plot(selected_professor_a)
                display_word_cloud(selected_professor_a,key='wordcloud_a')
     
        with subcol8:
            if list_of_professors:
                selected_professor_b = st.selectbox("Please select a professor:", list_of_professors, key='select_b')
            else:
                selected_professor_b = st.selectbox("Please select a professor:", data['Full Name'], key='select_b')
            if selected_professor_b:
                professor_data_b = data[data['Full Name'] == selected_professor_b]         
                biography_b = professor_data_b['biography'].iloc[0]

                citation = professor_data_b['Citations (All)'].iloc[0] 
                no_citation = int(citation) if not pd.isna(citation) else None

                publications_count = professor_data_b['publications_count'].iloc[0]
                publications_count = int(publications_count) if not pd.isna(publications_count) else None
                
                top_conference_count = professor_data_b['top_conference_count'].iloc[0]
                top_conference_count = int(top_conference_count) if not pd.isna(top_conference_count) else None
            else:
                professor_data_b = data
            if professor_data_b.empty:
                st.warning("No professor found with the given selection.")

            with st.expander("Research Interest"):
                research_interest_b = get_keywords_given_name(selected_professor_b)
                for item in research_interest_b:
                    st.markdown(f"- **{item}**")
            with st.expander("Biography"):
                st.write(biography_b)
              # Display bar chart   
            if selected_professor_b in ['Sourav Saha Bhowmick','Tay Kian Boon','Ke Yiping, Kelly']:
                print("Sorry, currently no publication data is found.")
            else:
                subcol1,subcol2,subcol3 = st.columns(3)
                with subcol1:
                    st.metric("Citations",no_citation)
                with subcol2:
                    st.metric("Publications",publications_count)
                with subcol3:
                    st.metric("Top Conferences",top_conference_count)
                count_publications = find_num_contributions_using_name(selected_professor_b)    
                plot_year_of_involvement(count_publications[0]) 
                conference_count_plot(selected_professor_b)
                display_word_cloud(selected_professor_b,key='wordcloud_b')
            
            