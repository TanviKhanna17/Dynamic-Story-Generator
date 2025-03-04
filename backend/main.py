# from extractData import extract_relationships_and_emotions
# from extractData import extract_people
# from pushneo4j import store_in_neo4j
# import json

# def main():
#     # Step 1: Take user input
#     input_text = input("Enter the text for relationship extraction: ")

#     # Extract persons first
#     persons_list = extract_people(input_text)
#     print("Identified Persons:", persons_list)

#     # Step 2: Extract relationships & emotions using Groq API
#     extracted_data = extract_relationships_and_emotions(input_text,persons_list)

#     print("Extracted Data:\n")
#     for i in extracted_data:
#         print(i)

#     # Step 4: Push extracted data to Neo4j
#     store_in_neo4j(persons_list,extracted_data)
#     print("\n✅ Data successfully pushed to Neo4j!")

# if __name__ == "__main__":
#     main()


from fastapi import FastAPI
from pydantic import BaseModel
from extractData import extract_people, extract_relationships_and_emotions
from pushneo4j import store_in_neo4j
from fetchfromdb import fetch_all_data
from storygen import generate_uplifting_story
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Allow frontend to send requests to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Ensure this matches your React app port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Store user info globally (temporary storage)
user_info = {}

# ✅ Define request body format
class UserInfo(BaseModel):
    name: str
    age: str
    gender: str

class UserInput(BaseModel):
    text: str

class AnswerInput(BaseModel):
    text: str
    user_info: UserInfo

@app.post("/store-user/")
async def store_user(input_data: UserInfo):
    global user_info
    user_info = input_data.dict()
    print("✅ User info stored:", user_info)  # Debugging
    return {"message": "User info stored successfully!", "user_info": user_info}


# ✅ Endpoint to store user info from `UserInfo.tsx`
@app.post("/process-answer/")
async def process_answer(input_data: AnswerInput):
    print("\n🟢 process_answer() STARTED!")  
    print("\n📩 Raw Request Data:", input_data.dict())  # Debugging

    global user_info
    if not user_info:
        print("❌ ERROR: User info is missing!")
        return {"error": "User info is missing. Please start from the beginning."}

    print("\n📝 Received User Info:", user_info)
    print("\n📥 Received User Input:", input_data.text)  # Should print the text

    try:
        full_text = f"{user_info['name']} ({user_info['age']}, {user_info['gender']}): {input_data.text}"
        print("\n🔍 Full Text Input for Extraction:\n", full_text)

        persons = extract_people(full_text)
        print("👥 Identified Persons:", persons)

        relationships = extract_relationships_and_emotions(full_text, persons)
        print("\n🔗 Extracted Relationships & Emotions:", relationships)

        if not persons or not relationships:
            print("❌ ERROR: No persons or relationships extracted! Skipping Neo4j storage.")
            return {"error": "No meaningful data extracted."}

        store_in_neo4j(persons, relationships)
        print("\n✅ Data successfully pushed to Neo4j!")

        return {
            "message": "Processed successfully!",
            "user_info": user_info,
            "full_text": full_text,
            "persons": persons,
            "relationships": relationships
        }

    except Exception as e:
        print("❌ ERROR in processing answer:", str(e))
        return {"error": str(e)}


# ✅ Endpoint to generate final story
@app.get("/generate-story/")
async def generate_story():
    """Fetches extracted data from Neo4j and generates an uplifting story."""
    data = fetch_all_data()
    story = generate_uplifting_story()  # Use fetched data for story generation
    return {"story": story}

