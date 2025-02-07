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
user_sessions = {}  # Store user progress

# Function to generate structured lessons with exercises for all levels and subjects
def generate_lesson(subject, level, progress):
    lessons = {
        "math": {
            "beginner": [
                {"title": "Lesson 1: Counting Numbers", "explanation": "Numbers help us count objects. Let's start by counting from 1 to 10.", "quiz": "Count to 10 and tell me the number after 5."},
                {"title": "Lesson 2: Basic Addition", "explanation": "Addition means putting numbers together. Example: 2 + 3 = 5.", "quiz": "What is 4 + 2?"},
                {"title": "Lesson 3: Multiplication Basics", "explanation": "Multiplication is repeated addition. Example: 3 × 2 = 6.", "quiz": "What is 5 × 3?"}
            ],
            "intermediate": [
                {"title": "Lesson 1: Fractions", "explanation": "Fractions are parts of a whole. Example: 1/2 means half.", "quiz": "What is 1/4 + 1/4?"},
                {"title": "Lesson 2: Algebra Basics", "explanation": "Algebra uses letters to represent numbers. Example: x + 2 = 5, find x.", "quiz": "If x + 3 = 7, what is x?"}
            ],
            "advanced": [
                {"title": "Lesson 1: Calculus Introduction", "explanation": "Calculus studies rates of change and areas under curves.", "quiz": "What is the derivative of x^2?"},
                {"title": "Lesson 2: Probability and Statistics", "explanation": "Probability measures chance. Example: A coin flip has a 50% chance of heads.", "quiz": "What is the probability of rolling a 6 on a die?"}
            ]
        },
        "science": {
            "beginner": [
                {"title": "Lesson 1: Living and Non-Living Things", "explanation": "Living things grow and move. Example: A cat is living, a rock is not.", "quiz": "Is a tree living or non-living?"},
                {"title": "Lesson 2: Basic Human Body", "explanation": "The human body has systems like digestion and breathing.", "quiz": "Which organ pumps blood?"}
            ],
            "intermediate": [
                {"title": "Lesson 1: Cells and Microorganisms", "explanation": "Cells are the building blocks of life.", "quiz": "What is the powerhouse of the cell?"},
                {"title": "Lesson 2: Electricity Basics", "explanation": "Electricity powers many devices. Example: A light bulb needs electricity.", "quiz": "What material conducts electricity?"}
            ],
            "advanced": [
                {"title": "Lesson 1: Physics - Motion and Forces", "explanation": "Newton's laws describe motion.", "quiz": "What is Newton's first law?"},
                {"title": "Lesson 2: Chemistry - Chemical Reactions", "explanation": "Chemical reactions transform substances.", "quiz": "What gas do plants produce during photosynthesis?"}
            ]
        }
    }
    
    if subject in lessons and level in lessons[subject] and progress < len(lessons[subject][level]):
        lesson = lessons[subject][level][progress]
        return f"**{lesson['title']}**\n{lesson['explanation']}\n**Quiz:** {lesson['quiz']}"
    return "You have completed all lessons in this subject! Would you like to start another subject?"

# HTML Template for interactive AI chat with dynamic buttons
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Education Chat</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; text-align: center; }
        .chat-box { width: 50%; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px gray; padding-bottom: 20px; }
        .message { text-align: left; margin: 10px 0; }
        .user { color: blue; }
        .ai { color: green; }
        input { width: 80%; padding: 10px; margin-top: 10px; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
    </style>
    <script>
        async function askAI(question) {
            let chatBox = document.getElementById("chat");
            if (!question) {
                question = document.getElementById("question").value;
                document.getElementById("question").value = "";
            }
            if (!question.trim()) return;
            
            chatBox.innerHTML += `<p class='message user'><strong>You:</strong> ${question}</p>`;
            
            let response = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: question })
            });
            let data = await response.json();
            chatBox.innerHTML += `<p class='message ai'><strong>AI:</strong> ${data.answer}</p>`;
            
            updateButtons(data.buttons);
        }
    </script>
</head>
<body>
    <h1>Welcome to AI Education Chat</h1>
    <div class="chat-box">
        <div id="chat"></div>
        <div id="buttons">
            <button onclick="askAI('Start Learning')">Start Learning</button>
        </div>
        <input type="text" id="question" placeholder="Type here...">
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/ask", methods=["POST"])
def ask_ai():
    data = request.json
    user_id = "default_user"
    question = data.get("question", "").strip().lower()
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {"level": None, "subject": None, "progress": 0}
    
    if "start learning" in question:
        response = "What is your current learning level?"
        buttons = ["Beginner", "Intermediate", "Advanced"]
    elif question in ["beginner", "intermediate", "advanced"]:
        user_sessions[user_id]["level"] = question
        response = "Select a subject to start learning."
        buttons = ["Math", "Science"]
    elif question in ["math", "science"]:
        user_sessions[user_id]["subject"] = question
        response = generate_lesson(user_sessions[user_id]["subject"], user_sessions[user_id]["level"], user_sessions[user_id]["progress"])
        buttons = ["Next Lesson"]
    else:
        response = "I can guide you step by step! Type 'Start Learning' to begin."
    
    return jsonify({"answer": response, "buttons": buttons})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
