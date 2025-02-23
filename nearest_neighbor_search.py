# SOME METHODS MAY BE AI GENERATED

from flask import Flask, jsonify, render_template, request, session
from waitress import serve
from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np
from typing import List, Dict, Set
import re

class CourseRecommender:
    def __init__(self, faiss_index_path: str, metadata_path: str, major_requirements_path: str):
        self.index = faiss.read_index(faiss_index_path)
        with open(metadata_path, "r") as f:
            self.courses = json.load(f)
        with open(major_requirements_path, "r") as f:
            self.major_requirements = json.load(f)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def _parse_prerequisites(self, prereq_text: str) -> Set[str]:
        if not prereq_text or prereq_text.lower() == 'none':
            return set()
        pattern = r'([A-Z]+\s*[A-Z]*\s*\d{3})'
        matches = re.findall(pattern, prereq_text)
        return set(matches)

    def _extract_query_constraints(self, query: str) -> Dict:
        constraints = {"credits": None, "level": None, "subject": None}
        credit_match = re.search(r'(\d+)\s*credit', query.lower())
        if credit_match:
            constraints["credits"] = int(credit_match.group(1))
        level_indicators = {
            "introductory": ["intro", "beginning", "basic", "elementary"],
            "intermediate": ["intermediate", "middle"],
            "advanced": ["advanced", "upper", "difficult", "complex"]
        }
        for level, indicators in level_indicators.items():
            if any(indicator in query.lower() for indicator in indicators):
                constraints["level"] = level
        return constraints

    def _apply_constraints(self, course: Dict, constraints: Dict) -> bool:
        if constraints["credits"] and course["Credits"] != constraints["credits"]:
            return False
        return True

    def _get_course_level(self, course_code: str) -> int:
        match = re.search(r'\d{3}', course_code)
        if not match:
            return 1
        course_num = int(match.group())
        if course_num < 300:
            return 1
        elif course_num < 500:
            return 2
        else:
            return 3

    def _calculate_major_requirement_score(self, course_code: str, completed_courses: Set[str]) -> float:
        score = 0.0
        course_subject = course_code.split()[0]
        for req_category, requirements in self.major_requirements.items():
            if course_code in requirements.get("required_courses", []):
                score += 1.0
            if course_subject in requirements.get("required_subjects", []):
                score += 0.5
            course_level = self._get_course_level(course_code)
            if course_level in requirements.get("required_levels", []):
                score += 0.3
            if "required_credits" in requirements:
                remaining_credits = requirements["required_credits"] - sum(
                    self.courses[c]["Credits"] for c in completed_courses if c.startswith(course_subject)
                )
                if remaining_credits > 0:
                    score += 0.2
            if "course_sequences" in requirements:
                for sequence in requirements["course_sequences"]:
                    if course_code in sequence:
                        sequence_index = sequence.index(course_code)
                        prev_courses = sequence[:sequence_index]
                        if all(c in completed_courses for c in prev_courses):
                            score += 0.4
        return min(score, 1.0)

    def search_courses(self, query: str, completed_courses: Set[str], top_k: int = 5) -> List[Dict]:
        constraints = self._extract_query_constraints(query)
        initial_k = top_k * 3
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, initial_k)
        results = []
        seen_courses = set()
        for idx, distance in zip(indices[0], distances[0]):
            course = self.courses[idx]
            course_code = course["Course Code"]
            if course_code in seen_courses or course_code in completed_courses:
                continue
            seen_courses.add(course_code)
            if not self._apply_constraints(course, constraints):
                continue
            prereqs = self._parse_prerequisites(course["Prerequisites"])
            missing_prereqs = prereqs - completed_courses
            course_level = self._get_course_level(course_code)
            major_req_score = self._calculate_major_requirement_score(course_code, completed_courses)
            semantic_score = float(1 / (1 + distance))
            combined_score = 0.6 * semantic_score + 0.4 * major_req_score
            result = {
                "course_info": {
                    "name": course["Course Name"],
                    "code": course_code,
                    "credits": course["Credits"],
                    "description": course["Description"],
                    "prerequisites": course["Prerequisites"],
                    "learning_outcomes": course["Learning Outcomes"]
                },
                "recommendation_info": {
                    "relevance_score": semantic_score,
                    "major_requirement_score": major_req_score,
                    "combined_score": combined_score,
                    "missing_prerequisites": list(missing_prereqs),
                    "course_level": course_level,
                    "matches_constraints": True
                }
            }
            results.append(result)
            if len(results) >= top_k:
                break
        results.sort(key=lambda x: (len(x["recommendation_info"]["missing_prerequisites"]) == 0, x["recommendation_info"]["combined_score"]), reverse=True)
        return results

recommender = CourseRecommender(
    faiss_index_path="courses.faiss",
    metadata_path="course_metadata.json",
    major_requirements_path="cs_major_requirements.json"
)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/chat')
def index():
    return render_template("chat.html")

@app.route('/set_major', methods=['POST'])
def set_major():
    selected_major = request.form.get("major")
    if selected_major:
        session['major'] = selected_major
        return jsonify({"message": "Major selected successfully!", "major": selected_major}), 200
    return jsonify({"error": "No major selected"}), 400

@app.route('/get_major', methods=['GET'])
def get_major():
    major = session.get('major', "Not selected")
    return jsonify({"major": major})

@app.route('/generate_response', methods=['POST'])
def generate_response():
    user_message = request.json.get("message")
    completed_courses = set(request.json.get("completed_courses", []))

    if not user_message:
        return jsonify({"error": "No message received"}), 400

    recommendations = recommender.search_courses(user_message, completed_courses, top_k=5)

    formatted_response = [
        {
            "Course Name": rec["course_info"]["name"],
            "Course Code": rec["course_info"]["code"],
            "Credits": rec["course_info"]["credits"],
            "Description": rec["course_info"]["description"],
            "Prerequisites": rec["course_info"]["prerequisites"] or "None",
            "Relevance Score": round(rec["recommendation_info"]["combined_score"] * 100, 2),
            "Missing Prerequisites": [
                prereq for prereq in rec["recommendation_info"]["missing_prerequisites"]
                if prereq not in completed_courses
            ],
        }
        for rec in recommendations
    ]

    return jsonify({"response": formatted_response})


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)