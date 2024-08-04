import pandas as pd
import mysql.connector
from pymongo import MongoClient
from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st


def mysql_query(query):
    # Establish a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="test_root",
        database="academicworld"
    )
    # Execute the query and store the result in a DataFrame
    df = pd.read_sql(query, conn)
    # Close the database connection
    conn.close()
    return df


# Prepared statements are a feature of SQL databases that allow you to precompile SQL statements 
# so they can be executed multiple times with different parameters efficiently. 
# This can significantly reduce the time it takes to execute similar queries repeatedly and 
# also help prevent SQL injection attacks.

# Function to connect to MySQL and run a prepared statement
def mysql_prepared_query(query, params):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="test_root",
        database="academicworld"
    )
    cursor = conn.cursor(prepared=True)
    cursor.execute(query, params)
    data = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=column_names)
    cursor.close()
    conn.close()
    return df


def mongodb_find(collection, query_filter={}, projection={}):
    client = MongoClient("mongodb://localhost:27017/")  
    db = client["academicworld"]  
    collection = db[collection]
    data = list(collection.find(query_filter, projection))
    client.close()
    return pd.DataFrame(data)


def mongodb_aggregate(collection, pipeline):
    client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
    db = client["academicworld"]  # Replace with your database name
    collection = db[collection]
    data = list(collection.aggregate(pipeline))
    client.close()
    return pd.DataFrame(data)


def neo4j_query(query):
    uri = "bolt://localhost:7687"
    user = 'neo4j'
    password = 'ilovecs411'
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session(database="academicworld") as session:
        result = session.run(query)
        data = pd.DataFrame([dict(record) for record in result])
    driver.close()
    return data


def plot_collaboration_graph(collaboration_data):
    G = nx.Graph()

    for _, row in collaboration_data.iterrows():
        G.add_edge(row['professor1'], row['professor2'], weight=row['collaboration_count'])

    pos = nx.spring_layout(G)
    weights = nx.get_edge_attributes(G, 'weight').values()

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, 
            edge_color='gray', width=list(weights), font_size=12)
    st.pyplot(plt)