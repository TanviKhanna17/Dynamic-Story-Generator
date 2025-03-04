from dbconnect import driver  # Use established Neo4j connection
from extractData import extract_relationships_and_emotions
from extractData import extract_people

# -------------------- Helper Functions --------------------

def is_person(name):
    """Determines if the given entity is a person."""
    person_names = {}  # Expand dynamically if needed
    return name in person_names

def is_bidirectional(relation):
    """Checks if a relationship should be bidirectional."""
    return relation in {"Sibling", "Married", "Colleague", "Friend"}

def is_description_relation(relation):
    """Checks if a relationship is a description or explanation of an entity."""
    return relation in {"Why", "Description", "Reason"}

# -------------------- Neo4j Storage Functions --------------------

def store_person_to_person(session, source, relation, target):
    """Handles Person-to-Person relationships (e.g., Sibling, Friend, Colleague)."""
    query = """
    MERGE (a:Person {name: $source})
    MERGE (b:Person {name: $target})
    MERGE (a)-[:`"""+relation+"""`]->(b)
    """
    session.run(query, source=source, target=target)

    # If the relation is bidirectional, store reverse relation
    if is_bidirectional(relation):
        reverse_query = """
        MERGE (a:Person {name: $target})
        MERGE (b:Person {name: $source})
        MERGE (b)-[:`"""+relation+"""`]->(a)
        """
        session.run(reverse_query, source=target, target=source)

def store_person_to_entity(session, source, relation, target):
    """Handles Person-to-Entity relationships (e.g., Lives In, Works At, Likes)."""
    query = """
    MERGE (a:Person {name: $source})
    MERGE (b:Entity {name: $target})
    MERGE (a)-[:`"""+relation+"""`]->(b)
    """
    session.run(query, source=source, target=target)

def store_entity_to_entity(session, source, relation, target):
    """Handles Entity-to-Entity relationships (e.g., Located In, Why, Category)."""
    query = """
    MERGE (a:Entity {name: $source})
    MERGE (b:Entity {name: $target})
    MERGE (a)-[:`"""+relation+"""`]->(b)
    """
    session.run(query, source=source, target=target)

# -------------------- Main Storage Function --------------------

def store_in_neo4j(persons_list, relationships):
    """Stores extracted relationships in Neo4j, ensuring persons are stored first."""
    with driver.session() as session:
        # 🟢 First, store all identified persons
        for person in persons_list:
            query = "MERGE (p:Person {name: $name})"
            session.run(query, name=person)

        # 🟡 Then, process relationships
        entity_descriptions = {}

        for rel in relationships:
            source = rel["source"]
            relation = rel["relation"]
            target = rel["target"]

            # If this is a description about an entity, store it separately
            if target not in persons_list and is_description_relation(relation):
                entity_descriptions[target] = {"relation": relation, "description": source}
                continue  # Skip normal processing for now

            if source in persons_list and target in persons_list:
                store_person_to_person(session, source, relation, target)
            elif source in persons_list and target not in persons_list:
                store_person_to_entity(session, source, relation, target)
            else:
                store_entity_to_entity(session, source, relation, target)

        # 🔵 Process descriptions and attach them to the correct entities
        for entity, details in entity_descriptions.items():
            query = """
            MERGE (b:Entity {name: $entity})
            MERGE (d:Entity {name: $desc})
            CREATE (d)-[:`"""+details["relation"]+"""`]->(b)
            """
            session.run(query, entity=entity, desc=details["description"])

    print("✅ Data successfully stored in Neo4j!")

# -------------------- Execution Example --------------------

if __name__ == "__main__":
    text = "Tanvi likes her piano as it was her first expensive gift. She has a little brother Rakshit, whom she loves very much. He sends her videos of him playing the piano."
    extracted_data = extract_relationships_and_emotions(text)

    print("📌 Extracted Data:")
    print(extracted_data)

    # Ensure we correctly extract persons and relationships
    persons_list = extract_people(text)
    relationships = extracted_data["relationships"] if "relationships" in extracted_data else []

    store_in_neo4j(persons_list, relationships)
