from dbconnect import driver  # Use established Neo4j connection

def fetch_all_persons():
    """Fetches all persons and their relationships from the Neo4j database."""
    query = """
    MATCH (p:Person)-[r]->(t)
    RETURN p.name AS source, type(r) AS relation, t.name AS target
    """  # 🔹 Fetch actual relationship type
    with driver.session() as session:
        results = session.run(query)
        return [{"source": record["source"], "relation": record["relation"], "target": record["target"]} for record in results]

def fetch_all_entities():
    """Fetches all entities and their relationships from the Neo4j database."""
    query = """
    MATCH (e:Entity)-[r]->(t)
    RETURN e.name AS source, type(r) AS relation, t.name AS target
    """  # 🔹 Fetch actual relationship type
    with driver.session() as session:
        results = session.run(query)
        return [{"source": record["source"], "relation": record["relation"], "target": record["target"]} for record in results]

def fetch_all_data():
    """Fetches and prints all stored data from Neo4j."""
    persons = fetch_all_persons()
    entities = fetch_all_entities()

    print("\n📌 Persons and Their Relationships:")
    for person in persons:
        print(f"{person['source']} → ({person['relation']}) → {person['target']}")  # ✅ Fixed key names

    print("\n📌 Entities and Their Relationships:")
    for entity in entities:
        print(f"{entity['source']} → ({entity['relation']}) → {entity['target']}")  # ✅ Fixed key names

    return {"Persons": persons, "Entities": entities}

if __name__ == "__main__":
    print("🔍 Fetching Data from Neo4j...\n")
    data = fetch_all_data()
