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

# HTML Template for interactive AI chat with chat history
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Education Chat</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; text-align: center; }
        .chat-box { width: 50%; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px gray; }
        .message { text-align: left; margin: 10px 0; }
        .user { color: blue; }
        .ai { color: green; }
        input { width: 80%; padding: 10px; margin-top: 10px; }
        button { padding: 10px 20px; cursor: pointer; }
    </style>
    <script>
        async function askAI() {
            let question = document.getElementById("question").value;
            if (!question.trim()) return;
            
            let chatBox = document.getElementById("chat");
            chatBox.innerHTML += `<p class='message user'><strong>You:</strong> ${question}</p>`;
            
            let response = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: question })
            });
            let data = await response.json();
            chatBox.innerHTML += `<p class='message ai'><strong>AI:</strong> ${data.answer}</p>`;
            
            document.getElementById("question").value = "";
        }
    </script>
</head>
<body>
    <h1>Welcome to AI Education Chat</h1>
    <div class="chat-box">
        <div id="chat"></div>
        <input type="text" id="question" placeholder="Ask a question...">
        <button onclick="askAI()">Ask</button>
    </div>
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
    translator = Translator()
    detected_lang = translator.detect(question).lang
    
    if len(question.split()) <= 3:
        course_suggestions = "Here are some courses you might find interesting:\n"
        for course, description in platform.courses.items():
            course_suggestions += f"- {course}: {description}\n"
        response = f"I can help with many subjects! Which topic interests you?\n{course_suggestions}"
    else:
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
    
    if detected_lang != "en":
        response = translator.translate(response, dest=detected_lang).text
    
    return jsonify({"answer": response})

class AIEducationPlatform:
    def __init__(self):
        self.courses = {
            "basic_literacy": "Learn basic reading and writing skills in your language.",
            "math_fundamentals": "Basic arithmetic: addition, subtraction, multiplication, and division.",
            "science_basics": "Introduction to biology, chemistry, and physics.",
            "computer_science": "Learn the basics of coding, AI, and web development.",
            "entrepreneurship": "Learn how to start and manage a small business.",
            "environment_sustainability": "How to live sustainably and care for the environment.",
        }
        self.translator = Translator()
        self.database = "ai_education.db"
        self.init_database()
    
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
