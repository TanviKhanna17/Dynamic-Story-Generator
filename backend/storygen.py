import os
from fetchfromdb import fetch_all_data
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client with a different model
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_mood(persons):
    """Determines the dominant emotions and concerns of the user."""
    emotions = []
    concerns = []
    personal_details = []

    for person in persons:
        if person["relation"] == "Feeling" or person["relation"] == "State of Mind":
            emotions.append(person["target"])
        elif person["relation"] == "Concern":
            concerns.append(person["target"])
        else:
            personal_details.append(f"{person['source']} → ({person['relation']}) → {person['target']}")

    return emotions, concerns, personal_details

def generate_uplifting_story():
    """Generates a mood-lifting story based on user's emotions, concerns, and all extracted data."""

    data = fetch_all_data()
    persons = data["Persons"]
    entities = data["Entities"]

    if not persons:
        print("No persons found in the database to create a story.")
        return

    # 🔎 Step 1: Analyze Mood & Data
    emotions, concerns, personal_details = analyze_mood(persons)

    # 🟢 Step 2: Construct a Story Prompt with ALL Data
    prompt = "Create an uplifting, motivational, and comforting short story for the user based on the following details:\n\n"

    # 🟡 Include Extracted Emotions
    if emotions:
        prompt += "📌 **User's Current Emotions:**\n"
        for emotion in emotions:
            prompt += f"- {emotion}\n"

    # 🔵 Include Extracted Concerns
    if concerns:
        prompt += "\n📌 **User's Concerns:**\n"
        for concern in concerns:
            prompt += f"- {concern}\n"

    # 🔴 Include ALL Extracted Data (Persons + Entities)
    prompt += "\n📌 **Additional Details About User:**\n"
    for detail in personal_details:
        prompt += f"- {detail}\n"
    
    for entity in entities:
        prompt += f"- {entity['source']} → ({entity['relation']}) → {entity['target']}\n"

    # ✨ Positive Story Instructions
    prompt += """
    
📖 **Instructions for the Story:**
- The story should be **uplifting, inspiring, and emotionally reassuring**.
- Acknowledge the user's **current emotions** but **guide them towards hope, courage, and happiness**.
- Use **gentle, warm, and encouraging storytelling**.
- The story should be **positive and heartwarming**, leaving the user feeling **lighter, hopeful, and motivated**.
- **Incorporate the user's details into the story** in a natural way.
- **End with an inspiring message** about growth, love, and resilience.

💡 **Example Start:**
"Tanvi sat by the window, feeling a little lost. The day had been overwhelming, and emotions ran high. But as she looked at the sky, she noticed something—the way the sun always set, only to rise again. Just like that, she knew... tomorrow held new possibilities."

Now, using the given emotions, concerns, and extracted data, **create a unique, comforting story.**

JUST RETURN THE STORY, NO ELSE THINKING OR ANYTHING ONLY STORY.
    """

    # 🔥 Step 3: Call Groq API (Different Model)
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="deepseek-r1-distill-qwen-32b",
        stream=False,
    )

    # Extract the generated story
    generated_story = response.choices[0].message.content

    return generated_story

if __name__ == "__main__":
    print("\n📖 Generating a **mood-lifting** story with Groq...\n")
    story = generate_uplifting_story()
    if story:
        print(story)
