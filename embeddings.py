from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np

with open("courses.json", "r") as f:
    courses = json.load(f)

descriptions = [
    f"{course.get('Course Name', '')} {course.get('Course Code', '')} {course.get('Credits', '')} {course.get('Prerequisites', '')} {course.get('Description', '')} {course.get('General Education Requirements', '')} {course.get('Learning Outcomes', '')}"
    for course in courses
]

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(descriptions, convert_to_numpy=True)

d = embeddings.shape[1]

index = faiss.IndexFlatL2(d)
index.add(embeddings)

faiss.write_index(index, "courses.faiss")

with open("course_metadata.json", "w") as f:
    json.dump(courses, f)
