import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables from .env file
load_dotenv()

# Retrieve credentials from .env
URI = os.getenv("URI")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# def run_query(query, parameters=None):
#     """Executes a Cypher query in Neo4j"""
#     with driver.session() as session:
#         session.run(query, parameters or {})

def test_connection():
    try:
        with driver.session() as session:
            result = session.run("RETURN 1")
            print("Connection successful: ", result.single()[0])
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")

test_connection()
