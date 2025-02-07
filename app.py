import random
import requests
import sqlite3
import json
import speech_recognition as sr
from googletrans import Translator
import deepl
import logging
from flask import Flask, jsonify, request, render_template_string

# Configuratie van logging voor foutopsporing en analyse
logging.basicConfig(filename='ai_education.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# HTML Template for interactive AI chat
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Education Chat</title>
    <script>
        async function askAI() {
            let question = document.getElementById("question").value;
            let response = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: question })
            });
            let data = await response.json();
            document.getElementById("response").innerText = data.answer;
        }
    </script>
</head>
<body>
    <h1>Welcome to AI Education Chat</h1>
    <input type="text" id="question" placeholder="Ask a question...">
    <button onclick="askAI()">Ask</button>
    <p id="response"></p>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

# API-route om beschikbare cursussen op te halen
@app.route("/courses", methods=["GET"])
def get_courses():
    platform = AIEducationPlatform()
    return jsonify({"courses": list(platform.courses.keys())})

# API-route om de AI een vraag te stellen
@app.route("/ask", methods=["POST"])
def ask_ai():
    data = request.json
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Please provide a question"}), 400
    
    platform = AIEducationPlatform()
    
    # Detect the language of the input question
    translator = Translator()
    detected_lang = translator.detect(question).lang
    
    # Provide general guidance if the question is broad
    general_responses = [
        "I can help you learn many things! Are you interested in math, science, languages, or something else?",
        "There are many subjects to explore! Would you like to start with literacy, technology, or problem-solving skills?",
        "Education is powerful! Do you need help with basic skills, advanced knowledge, or career planning?"
    ]
    
    if len(question.split()) <= 3:  # If the question is too vague
        response = random.choice(general_responses)
    else:
        # Match question to the best course
        best_match = None
        best_match_score = 0
        for course, description in platform.courses.items():
            match_score = sum(1 for word in question.lower().split() if word in course.lower())
            if match_score > best_match_score:
                best_match = course
                best_match_score = match_score
        
        if best_match:
            response = f"Based on your question, you might be interested in '{best_match}': {platform.courses[best_match]}"
        else:
            response = "I couldn't find an exact match, but keep exploring and learning! Try asking in a different way."
    
    # Translate response back to detected language if necessary
    if detected_lang != "en":
        response = translator.translate(response, dest=detected_lang).text
    
    return jsonify({"answer": response})

# API-route om gebruikersvoortgang op te halen (mocked)
@app.route("/progress/<user_id>", methods=["GET"])
def get_progress(user_id):
    return jsonify({"user_id": user_id, "progress": "Not implemented yet"})

class AIEducationPlatform:
    def __init__(self):
        self.courses = {
            "basic_literacy": "Leer basislezen en schrijven in je eigen taal.",
            "math_fundamentals": "Basisrekenen: optellen, aftrekken, vermenigvuldigen en delen.",
            "science_basics": "Introductie tot natuurwetenschappen: biologie, scheikunde en natuurkunde.",
            "advanced_math": "Algebra, statistiek en calculus.",
            "computer_science": "Basisprogrammeren, AI en webontwikkeling.",
            "social_studies": "Geschiedenis, aardrijkskunde en burgerschapsonderwijs.",
            "language_development": "Basisgrammatica en woordenschat in verschillende talen.",
            "agriculture": "Duurzame landbouwtechnieken en voedselproductie.",
            "healthcare_basics": "EHBO, anatomie en medische basiskennis.",
            "entrepreneurship": "Start je eigen kleine onderneming met microfinanciering.",
            "critical_thinking": "Probleemoplossend denken en logica.",
            "academic_research": "Onderzoeksvaardigheden en wetenschappelijke methodologie.",
            "practical_skills": "Handige vaardigheden voor dagelijks leven.",
            "leadership_teamwork": "Hoe werk je samen en neem je leiderschap?",
            "financial_literacy": "Hoe beheer je geld en start je een klein project?",
            "environment_sustainability": "Hoe zorg je voor een duurzame toekomst?",
            "law_politics": "Mensenrechten, basiswetgeving en politieke systemen.",
            "technology_basics": "Digitale vaardigheden en cyberveiligheid.",
            "mechanical_repair": "Basisvaardigheden in het repareren van fietsen, gereedschap en eenvoudige machines.",
            "food_security": "Hoe verbouw en bewaar je voedsel om honger te voorkomen?",
            "renewable_energy": "Hoe kun je zonne- en windenergie gebruiken in je gemeenschap?",
            "disaster_preparedness": "Wat te doen bij natuurrampen zoals overstromingen en aardbevingen?",
            "basic_business": "Hoe start en beheer je een klein bedrijf?",
        }
        self.translator = Translator()
        self.deepl_translator = deepl.Translator("your-deepl-api-key")
        self.speech_recognizer = sr.Recognizer()
        self.database = "ai_education.db"
        self.init_database()
        logging.info("AIEducationPlatform succesvol geïnitialiseerd.")
    
    def init_database(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_progress (
                            user_id TEXT PRIMARY KEY, 
                            goals TEXT, 
                            completed_courses TEXT, 
                            progress_percentage INTEGER)''')
        conn.commit()
        conn.close()
        logging.info("Database geconfigureerd.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
