import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import mysql_query, mongodb_find, mongodb_aggregate, neo4j_query, plot_collaboration_graph

# Function to cache MySQL queries
@st.cache_data
def fetch_mysql_query(query):
    return mysql_query(query)

# Function to cache MongoDB aggregation
@st.cache_data
def fetch_mongodb_aggregate(collection, pipeline):
    return mongodb_aggregate(collection, pipeline)

# Streamlit layout
st.set_page_config(layout="wide")
st.title("US University CS Faculty Dashboard")
st.markdown("**Author: Chaochao Zhou (cz76@illinois.edu)**")

# Create grid layout
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<h2 style='font-size:24px;'>Faculty Distribution</h2>", unsafe_allow_html=True)

    # Query database
    query = """
    SELECT u.name AS universities, COUNT(*) AS num_professors
    FROM faculty f, university u
    WHERE f.university_id = u.id
    GROUP BY u.name
    ORDER BY num_professors DESC;
    """
    data = fetch_mysql_query(query)

    # Sidebar for user input
    k = st.slider("Select number of universities", min_value=1, max_value=len(data), value=10) 

    # Select top k universities
    top_k_data = data.head(k)

    # If k < len(data), add a row for "others"
    if k < len(data):
        others_count = data.iloc[k:]['num_professors'].sum()
        others_row = pd.DataFrame([['Others', others_count]], columns=['universities', 'num_professors'])
        top_k_data = pd.concat([top_k_data, others_row], ignore_index=True)       

    # Create a pie chart
    fig, ax = plt.subplots()
    ax.pie(top_k_data['num_professors'], labels=top_k_data['universities'], autopct='%1.1f%%', startangle=140)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)

with col2:
    st.markdown("<h2 style='font-size:24px;'>Top Professors with Most Publications</h2>", unsafe_allow_html=True)
    university = st.selectbox("Select a university", 
                              data['universities'].tolist(), 
                              index=data['universities'].tolist().index("University of illinois at Urbana Champaign"))
    
    query = f"""
    SELECT f.name AS professor, COUNT(*) AS num_publications
    FROM faculty f, university u, faculty_publication fp
    WHERE f.university_id = u.id AND f.id = fp.faculty_Id AND u.name = '{university}'
    GROUP BY f.id
    ORDER BY num_publications DESC
    LIMIT 10;
    """
    prof_data = fetch_mysql_query(query)
    
    st.dataframe(prof_data)

with col3:
    st.markdown("<h2 style='font-size:24px;'>Top Professors with Most Citations</h2>", unsafe_allow_html=True)
    university1 = st.selectbox("Select a university", 
                              data['universities'].tolist(), 
                              index=data['universities'].tolist().index("University of illinois at Urbana Champaign"),
                              key='unique_university_selectbox')
    
    query = f"""
    SELECT f.name AS professor, SUM(p.num_citations) AS num_citations
    FROM faculty f, university u, publication p, faculty_publication fp
    WHERE f.university_id = u.id AND f.id = fp.faculty_Id AND p.ID = fp.publication_ID AND u.name = '{university1}'
    GROUP BY f.id
    ORDER BY num_citations DESC
    LIMIT 10;
    """
    prof_data = fetch_mysql_query(query)
    
    st.dataframe(prof_data)

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("<h2 style='font-size:24px;'>Faculty Information</h2>", unsafe_allow_html=True)
    
    # Query to get the list of professors from the view
    query = "SELECT name FROM sorted_faculty_names;"    
    professors = fetch_mysql_query(query)['name'].dropna()
    professors = professors[professors.str.contains('[a-zA-Z]', regex=True)]
    
    if 'selected_professor' not in st.session_state:
        st.session_state.selected_professor = "Kevin Chenchuan Chang"
    
    selected_professor = st.selectbox("Select a professor", professors,
                                      index=professors.tolist().index(st.session_state.selected_professor))
    
    st.session_state.selected_professor = selected_professor
    
    # Query to get the selected professor's information
    query = f"""
    SELECT f.name, f.position, f.email, f.phone, f.research_interest, u.name AS university, f.photo_url
    FROM faculty f, university u
    WHERE f.university_id = u.id AND f.name = '{selected_professor}';
    """
    prof_info = fetch_mysql_query(query).iloc[0]
    
    st.image(prof_info['photo_url'], width=150)  # Display the professor's photo
    st.write(f"**Faculty Name:** {prof_info['name']}")
    st.write(f"**Position:** {prof_info['position']}")
    st.write(f"**Email Address:** {prof_info['email']}")
    st.write(f"**Phone Number:** {prof_info['phone']}")
    st.write(f"**Research Area:** {prof_info['research_interest']}")
    st.write(f"**University:** {prof_info['university']}")

with col5:
    st.markdown("<h2 style='font-size:24px;'>Collaboration Graph</h2>", unsafe_allow_html=True)

    if 'selected_professor_collab' not in st.session_state:
        st.session_state.selected_professor_collab = "Kevin Chenchuan Chang"
    
    selected_professor1 = st.selectbox("Select a professor", professors,
                                       index=professors.tolist().index(st.session_state.selected_professor_collab), 
                                       key='unique_selected_professor')

    st.session_state.selected_professor_collab = selected_professor1

    # Query to get the collaboration graph for the selected professor
    collaboration_query = f"""
    MATCH (p1:FACULTY {{name: '{selected_professor1}'}})-[:PUBLISH]->(pub:PUBLICATION)<-[:PUBLISH]-(p2:FACULTY)
    RETURN p1.name AS professor1, p2.name AS professor2, COUNT(pub) AS collaboration_count
    """
    collaboration_data = neo4j_query(collaboration_query)
    
    # Plot the collaboration graph
    plot_collaboration_graph(collaboration_data)

with col6:
    st.markdown("<h2 style='font-size:24px;'>Top Keywords in Publications by Year</h2>", unsafe_allow_html=True)
    pipeline = [
        {"$group": {"_id": "$year"}},
        {"$sort": {"_id": 1}}
    ]
    years = fetch_mongodb_aggregate("publications", pipeline)
    years['_id'] = years['_id'].astype(int)
    years = years[years['_id'] >= 1900]
    min_year, max_year = years['_id'].min(), years['_id'].max()   
    year = st.slider("Select Year", min_value=1948, max_value=2021, value=2021)

    # Define the aggregation pipeline for keywords
    pipeline = [
        {"$unwind": "$keywords"},
        {"$match": {"year": {"$eq": year}}},
        {"$group": {"_id": "$keywords.name", "pub_cnt": {"$sum": 1}}},
        {"$sort": {"pub_cnt": -1}},
        {"$limit": 10}
    ]
    keywords_data = fetch_mongodb_aggregate("publications", pipeline)

    # Create a bar plot
    fig, ax = plt.subplots()
    ax.barh(keywords_data['_id'], keywords_data['pub_cnt'])
    ax.set_xlabel("Publication Count")
    ax.set_ylabel("Keywords")
    ax.invert_yaxis()
    st.pyplot(fig)
