import pymongo
import json

import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import networkx as nx
import igviz as ig
from wordcloud import WordCloud



conn_str = "" #mongoDB connection string
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
db = client['scsedash']

def get_research_areas():
    f = open ('./data/research_areas.json', "r")
    broader_to_specific_areas = json.loads(f.read())
    f.close()
    return dict(broader_to_specific_areas)


def find_name_using_keyword(keywords=[]):
    '''
    Identifies all professors with specified keyword
    '''  
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
    cursor = db.DBLP_publications.find({"name":name},{"_id":0,"name":1,"num_contributions":1})
    result = []
    for dic in cursor:
        result.append(dic)
    return result


def get_list_of_keywords():
    '''
    Get the entire list of keywords 
    '''
    collection = db['keywordsAndNames']
    result = collection.distinct('keyword')
    return result


def get_keywords_given_name(name):
    '''
    Get the list of keywords given professor's name
    '''
    cursor = db.professors.find({"name":name},{"_id":0})
    result = []
    for dic in cursor:
        result.append(dic)
    return result[0]['keywords']


def plot_year_of_involvement(data):
    #years = sorted([int(year) for year in data['num_contributions'].keys()])
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
    fig = px.bar(df, x='Year', y=list(contribution_types), title=f'{data["name"]}',
                 labels={'value': 'Number of Contributions', 'variable': 'Contribution Type'},
                 barmode='relative',color='variable', color_discrete_map=custom_color_scale)

    # Show the chart
    fig.update_layout(xaxis_title='Year', yaxis_title='Number of Contributions',
                     plot_bgcolor='white',paper_bgcolor='#ebd2b9')
    
    # Display the Plotly chart in Streamlit
    st.subheader("Year of Involvement")
    st.plotly_chart(fig)


def find_publications(name):
    cursor = db.DBLP_publications.find({"name":name},{"_id":0,"num_contributions":0})
    data = []
    for dic in cursor:
        data.append(dic)
    if len(data) == 0:
        return print("Sorry, currently no publication data is found.")
    else:
        return data[0]


def display_publications_by_year(name):
    data = find_publications(name)
    if not data['publications']:
        st.error("No publications found for this author.")
        return

    all_years = sorted(map(int, data['publications'].keys()), reverse=True)
    # Create a slider for selecting the range of years
    years_range = st.slider(
        "Select the range of years to display publication information",
        min_value=min(all_years),
        max_value=max(all_years),
        value=(min(all_years), max(all_years))
    )

    # Display the publication by year and then type
    for year in all_years:
        if years_range[0] <= year <= years_range[1]:
            with st.expander(f"{year}"):
                publications = data['publications'][str(year)]
                for category, papers in publications.items():
                    st.markdown(f"#### {category}")
                    for paper in papers:
                        st.markdown(f"**Title:** {paper['title']}  \n"
                                    f"**Coauthors:** {', '.join(paper['coauthors'])}  \n"
                                    f"**Conference/Venue:** {paper['conference_name']}  \n"
                                    f"**URL:** {paper['url']}")
                    st.divider()


def display_publications_by_type(name):
    data = find_publications(name)
    years = sorted(map(int, data['publications'].keys()), reverse=True)

    # Get a list of all unique publication types
    unique_types = set()
    for year_data in data['publications'].values():
        unique_types.update(year_data.keys())

    # Display the publications by type and year
    for publication_type in unique_types:
        with st.expander(publication_type):
            for year in years:
                year_data = data['publications'].get(str(year), {})
                publications = year_data.get(publication_type, [])
                if publications:
                    st.markdown(f"#### {year}")
                    for paper in reversed(publications):  # Show the most recent publications on top
                        st.markdown(f"**Title:** {paper['title']}  \n"
                                    f"**Coauthors:** {', '.join(paper['coauthors'])}  \n"
                                    f"**Conference/Venue:** {paper['conference_name']}  \n"
                                    f"**URL:** {paper['url']}")


def display_word_cloud(name,key):
    st.subheader("Publication Keywords")
    data = find_publications(name)
    if not data['publications']:
        st.error("No publications found for this author.")
        return

    all_years = sorted(map(int, data['publications'].keys()), reverse=True)
    years_range = st.slider(
        "Select the range of years to display publication keywords",
        min_value=min(all_years),
        max_value=max(all_years),
        value=(min(all_years), max(all_years)),
        key=key
    )

    # Generate a word cloud for the selected range of years
    selected_years = [str(year) for year in range(years_range[0], years_range[1] + 1)]
    text = ""
    for year in selected_years:
        if year in data['publications']:
            publications = data['publications'][year]
            # Combine all paper titles into a single string
            text = " ".join(str(paper['title']) for category in publications.values() for paper in category if paper['title'] is not None)
    if text:
        # Create a WordCloud object
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        
        # Display the word cloud using matplotlib
        st.set_option('deprecation.showPyplotGlobalUse', False)  # Avoid warning
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        #plt.title(f"Word Cloud for {min_year} to {max_year}")
        st.pyplot(plt)
    else:
        st.error(f"No publications found for the selected year range.")


def display_top_coauthors(name):
    # Load the data from the JSON file
    with open('./data/coauthors.json', "r") as f:
        data = json.load(f)
    st.subheader("Top Coauthors")

    selected_value = st.slider("Number of coauthors:", min_value=1, max_value=10, value=5, step=1)
    st.write(f"**Top {selected_value} Coauthors for {name} (based on DBLP)**")

    coauthor_data = []
    for professor in data:
        if professor["name"] == name:
            coauthors = professor["coauthors"]
            # Loop through the coauthors and add their data to the list
            for coauthor in coauthors[:selected_value]:
                coauthor_data.append((coauthor['coauthor_name'], coauthor['times']))
    df_coauthors = pd.DataFrame(coauthor_data, columns=["name (DBLP)", "number of collaborations"])

    fig = px.bar(df_coauthors, 
                 x="name (DBLP)", 
                 y="number of collaborations",
                 title=f"Top {selected_value} Coauthors for {name}",
                 labels={"name (DBLP)": "Coauthor Name", "number of collaborations": "Number of Collaborations"},
                 color="number of collaborations",
                 color_continuous_scale=px.colors.sequential.Plasma)

    fig.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig, use_container_width=True)


def plot_scse_bar():
    st.markdown("#### Top Research Areas")
    df = pd.read_csv('./data/research_area_with_counts.csv')
    df = df.sort_values(by='Number of Professors', ascending=False)
    
    fig = px.pie(df, 
                 values='Number of Professors', 
                 names='Broader Area', 
                 title="Research Area Distribution by Number of Professors")

    fig.update_traces(textinfo='percent+label')
    fig.update_layout(
        title="Research Area Distribution by Number of Professors",
    )

    st.plotly_chart(fig, use_container_width=True) 


def display_top_n_keywords():
    df = pd.read_csv('./data/keywords_count.csv')
    df = df[1:]  # Assuming the first row is not relevant
    st.markdown("#### Top Keywords")
    st.markdown("Use the slider to select and display keywords associated with the highest number of professors participating in the research.")

    selected_value = st.slider("Number of Keywords", min_value=1, max_value=len(df), value=10, step=1)

    df_sorted = df.sort_values(by='Number of Professors', ascending=False)
    df_top_n = df_sorted.head(selected_value)
    
    # Find the max value for highlighting
    max_professors = df_top_n['Number of Professors'].max()
    df_top_n['Color'] = 'LightSkyBlue'
    df_top_n.loc[df_top_n['Number of Professors'] == max_professors, 'Color'] = 'Crimson'

    fig = px.bar(df_top_n, x='Keywords', y='Number of Professors', 
                 color='Color', color_discrete_map="identity",
                 title="Top Keywords by Number of Professors")

    fig.update_layout(showlegend=False)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


def build_adjacency_matrix():
    f = open ('./data/coauthors_scse.json', "r")
    filtered_professors_data = json.loads(f.read())
    f.close()
    # plot overall network
    # Step 1: Create a list of unique professor names
    professors = set()
    for entry in filtered_professors_data:
        professors.add(entry['name'])
        for coauthor in entry['coauthors']:
            professors.add(coauthor['coauthor_name'])

    # Step 2: Create an empty adjacency matrix
    adjacency_matrix = {professor: {} for professor in professors}

    # Step 3: Populate the adjacency matrix
    for entry in filtered_professors_data:
        professor = entry['name']
        for coauthor in entry['coauthors']:
            coauthor_name = coauthor['coauthor_name']
            times = coauthor['times']
            adjacency_matrix[professor][coauthor_name] = times

    # Step 4: Create a NetworkX graph (G) from the adjacency matrix
    G = nx.Graph(adjacency_matrix)
    return G, adjacency_matrix


def display_overall_graph():
    G, adjacency_matrix = build_adjacency_matrix()

    nx.set_node_attributes(G, adjacency_matrix,"type")
    nx.set_edge_attributes(G, 5, "edge_prop")

    fig = ig.plot(G,title="SCSE Network Graph", layout="circular", 
                  colorscale='YlOrRd')
    st.plotly_chart(fig, use_container_width=True)


def display_treemap():
    df = pd.read_csv("./data/keywords_count.csv")
    df = df[1:]
    fig = px.treemap(df, path=[px.Constant("SCSE"),'broad_topic', 'Keywords'], values='Number of Professors',
                 color_continuous_scale='RdBu',color='Number of Professors',
                 title='Research Areas and Keywords by Number of Professors')

    # Display the treemap in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def display_individual_graph(professor_name):
    subgraph = nx.Graph()
    subgraph.add_node(professor_name)

    # Dictionary to store the frequency of collaborations among professors
    collaboration_counts = {}
    _, adjacency_matrix = build_adjacency_matrix()
    # Loop through all adjacency matrices
    for professor, matrix in adjacency_matrix.items():
        if professor != professor_name:
            if professor_name in matrix:
                weight = matrix[professor_name]
                subgraph.add_node(professor)
                subgraph.add_edge(professor_name, professor, weight=weight)
                # Check if other professors have connections with the target professor
                for other_professor, other_weight in matrix.items():
                    if other_professor != professor_name and other_weight > 0:
                        if (professor, other_professor) not in collaboration_counts:
                            collaboration_counts[(professor, other_professor)] = other_weight
                        else:
                            collaboration_counts[(professor, other_professor)] += other_weight

    # Add edges for collaborations among professors
    for (professor_1, professor_2), frequency in collaboration_counts.items():
        if frequency > 0:
            subgraph.add_edge(professor_1, professor_2, weight=frequency)

    nx.set_node_attributes(subgraph, 3, "prop")
    nx.set_edge_attributes(subgraph, 5, "edge_prop")

    fig = ig.plot(subgraph, title=f"{professor_name}'s graph",
            node_label_position="top center",
            edge_label="weight", 
            edge_label_position="bottom center",
            layout="circular",
            colorscale='YlOrRd') 
    st.plotly_chart(fig, use_container_width=True)


def conference_count_plot(name):
    f = open ('./data/all_conference_count.json', "r")
    all_professors_data = json.loads(f.read())
    f.close()
    for professor in all_professors_data:
        if professor['name'] == name:
            data = professor

    df = pd.DataFrame(data['counts']).T
    df.index = df.index.map(int)  
    df = df.sort_index() 

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df['C'], mode='lines', name='C', stackgroup='one'
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['B'], mode='lines', name='B', stackgroup='one'
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['A'], mode='lines', name='A', stackgroup='one'
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['A*'], mode='lines', name='A*', stackgroup='one'
    ))

    # Customize the layout
    fig.update_layout(
        title='Number of Conferences by Year',
        xaxis_title='Year',
        yaxis_title='Conference Count',
        xaxis=dict(tickmode='linear'),
        yaxis=dict(type='linear')
    )
    st.plotly_chart(fig, use_container_width=True)


faculty_intro = '''
NTU School of Computer Science and Engineering (SCSE) is a leading computer science and engineering school for higher learning that is known for its excellent curriculum, outstanding impactful research, and talented faculty. Today, we are ranked Top 10 for Computer Science in the latest US News and World Report Best Global Universities listing. and NTU has been recognised as the top university for AI research and citation impact. SCSE serves a critical role in the university and society as we harness the power of digital technology and tech-enabled solutions to not only enhance the learning and research experience of our students and staff, but also to create innovative solutions for some of the grand challenges facing our world.'''