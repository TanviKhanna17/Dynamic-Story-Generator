import os
import re
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_people(text):
    """Extracts all persons mentioned in the given text using API."""

    prompt = f"""
    Identify and extract all persons mentioned in the following text.
    
    **Format the output as:** 
    - Just return names, one per line.
    - Do not add any extra text or explanations.
    - Do not return relationships, only names.

    **Example Input:**
    "Tanvi and Rakshit went to visit their cousin Siddhant in Mumbai."

    **Expected Output:**
    Tanvi
    Rakshit
    Siddhant

    **Now, analyze the following text:**
    {text}
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        stream=False,
    )

    # Extract names from API response
    extracted_text = chat_completion.choices[0].message.content
    persons_list = [line.strip() for line in extracted_text.strip().split("\n") if line.strip()]

    return persons_list


def extract_relationships_and_emotions(text,persons_list):
    """Extracts structured relationships, attributes, emotions, and state of mind from a given sentence."""
    persons_str = ", ".join(persons_list)
    prompt = f"""
    Extract all possible **relationships, attributes, emotions, and state of mind** about the person(s) mentioned in the following text.
    
    **Identified Persons:** {persons_str}

    **Format the output as:**
    - **Person → (Relation) → Value** (for relationships and attributes)
    - **Person → (Relation) → Person** (if two people are related)
    - **Entity → (Relation) → Entity** (relation between two entities)
    - **Entity → (Feeling) → Emotion** (for emotions and mental state)

    KINDLY ADHERE TO ALL THE GUIDELINES GIVEN BELOW.
    DO NOT RETURN RELATIONSHIPS WHERE DETAILS FOR THE SAME ARE NOT GIVEN, ONLY EXTRACT FROM GIVEN DATA.
    DO NOT RETURN THINGS NOT MENTIONED
    IF IT IS NOT MENTION LEAVE IT
    DO NOT RETURN THIS: "TARGET:NOT MENTIONED
    Avoid redundant relationships** (e.g., "Sibling" and "Brother" should not be separate).

    **Ensure that:**
    - **Personal details** (name, age, gender, nationality, birth/death details) are extracted.
    - **Locations** (place of birth, residence, workplace, significant locations) are included.
    - **Professional roles, achievements, and contributions** (titles, awards, affiliations, key work) are captured.
    - **Dates and events** (birth date, tenure in roles, key events, death date) are extracted.
    - **Relationships between entities** are clearly defined (e.g., "Worked at", "Mentored", "Founded", "Contributed to").
    - **Emotional state and current feelings** are identified (e.g., "Feeling happy", "Experiencing stress", "Feeling nostalgic").
    - **User can feel multiple emotions at a time, hence multiple feelings can exist but not more than 3 at a time.
    - **Concerns, beliefs, and thoughts** are captured (e.g., "Worried about exams", "Believes in persistence", "Feels hopeful").
    - **Tone of the text** is analyzed (e.g., "Optimistic", "Anxious", "Confident", "Frustrated", "Joyful", "Grateful").
    - **No important contextual information is missed**.
    - **Do not form redundant relationships , for example: - Tanvi → (Sibling) → Little brother, Tanvi → (Relationship) → Sister , Tanvi → (Family) → Has a brother
    - **Also give output in given format only, do not write anything else, Tanvi → (State of Mind) → Sadness (inferred from feeling lonely), don't write the part in brackets.
    - **Person-to-person relationships** are correctly identified (e.g., "Tanvi → (Sibling) → Rakshit" instead of "Rakshit → (Relation) → Brother").
    - **Do Not miss out on any relationship.
    - **Do not send out any relationship where any details are not mentioned.


    **Example Input:**
    "Tanvi is feeling anxious about her upcoming exams, but she is hopeful that her hard work will pay off. She lives in Vadodara and enjoys playing chess to relax."

    **Expected Output:**
    Tanvi → (Lives in) → Vadodara
    Tanvi → (Hobby) → Playing Chess
    Tanvi → (Feeling) → Anxious
    Tanvi → (Concern) → Upcoming exams
    Tanvi → (Belief) → Hard work will pay off
    Tanvi → (State of Mind) → Hopeful

    **Now, analyze the following text:**
    The first line of the text is user information:
    If the user refers to as I, this is the user in reference with.

    {text}
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        stream=False,
    )

    extracted_text = chat_completion.choices[0].message.content
    return parse_extracted_text(extracted_text)

def parse_extracted_text(extracted_text):
    """Parses the extracted text into a Neo4j-compatible format."""
    relationships = []
    pattern = r"(.+?)\s*→\s*\((.+?)\)\s*→\s*(.+)"

    for line in extracted_text.strip().split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            source, relation, target = match.groups()
            relationships.append({
                "source": source.strip(),
                "relation": relation.strip(),
                "target": target.strip()
            })

    return relationships

if __name__ == "__main__":
    sentence = "  Tanvi Female 20   Tanvi is 20 years old, she is in her prefinal year of computer science engineering. She loves her family, especially her brother who is 10 years younger than her. She will visit him for his birthday on 28 December. His name is Rakshit. Tanvi misses him a lot."

    # Extract persons first
    persons_list = extract_people(sentence)
    print("Identified Persons:", persons_list)

    # Extract relationships and emotions based on identified persons
    output = extract_relationships_and_emotions(sentence, persons_list)
    
    print("Extracted Data:\n")
    for i in output:
        print(i)

