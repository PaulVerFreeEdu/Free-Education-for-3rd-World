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

# HTML Template for interactive AI chat with chat history and buttons
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
            if (!question) {
                question = document.getElementById("question").value;
                document.getElementById("question").value = "";
            }
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
        }
        
        document.addEventListener("DOMContentLoaded", function() {
            document.getElementById("question").addEventListener("keypress", function(event) {
                if (event.key === "Enter") {
                    askAI();
                }
            });
        });
    </script>
</head>
<body>
    <h1>Welcome to AI Education Chat</h1>
    <div class="chat-box">
        <div id="chat"></div>
        <button onclick="askAI('Start Learning')">Start Learning</button>
        <button onclick="askAI('1')">Beginner</button>
        <button onclick="askAI('2')">Intermediate</button>
        <button onclick="askAI('3')">Advanced</button>
        <br>
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
    user_id = "default_user"  # Temporary ID system (can be extended for multi-user tracking)
    question = data.get("question", "").strip().lower()
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {"level": None, "progress": 0}
    
    translator = Translator()
    detected_lang = translator.detect(question).lang
    
    if "start learning" in question:
        user_sessions[user_id]["level"] = None
        response = "What is your current learning level?\n1. Beginner (Basic literacy, math)\n2. Intermediate (Science, Technology)\n3. Advanced (Entrepreneurship, Sustainability)\nPlease type 1, 2, or 3."
    elif question in ["1", "2", "3"] and user_sessions[user_id]["level"] is None:
        user_sessions[user_id]["level"] = question
        user_sessions[user_id]["progress"] = 1
        response = get_lesson(user_sessions[user_id]["level"], user_sessions[user_id]["progress"])
    elif user_sessions[user_id]["level"]:
        user_sessions[user_id]["progress"] += 1
        response = get_lesson(user_sessions[user_id]["level"], user_sessions[user_id]["progress"])
    else:
        response = "I can guide you step by step! Type 'Start Learning' to begin."
    
    if detected_lang != "en":
        response = translator.translate(response, dest=detected_lang).text
    
    return jsonify({"answer": response})

def get_lesson(level, progress):
    lessons = {
        "1": [
            "**Lesson 1: Basic Literacy**\n- Letters and Sounds\n- How to form simple words\n- Understanding basic sentences",
            "**Lesson 2: Basic Writing**\n- Constructing simple sentences\n- Writing short stories\n- Understanding punctuation",
            "**Lesson 3: Basic Math**\n- Counting numbers\n- Simple addition and subtraction\n- Basic multiplication and division"
        ],
        "2": [
            "**Lesson 1: Introduction to Science**\n- What is science?\n- Observations and experiments\n- Basic elements of nature",
            "**Lesson 2: Introduction to Technology**\n- Understanding digital tools\n- The internet and its uses\n- Basic programming concepts",
            "**Lesson 3: Physics Basics**\n- Understanding motion and energy\n- Simple machines and their uses"
        ],
        "3": [
            "**Lesson 1: Introduction to Business**\n- What is a business?\n- How do businesses operate?\n- Understanding trade and economy",
            "**Lesson 2: Financial Literacy**\n- Budgeting and saving money\n- Understanding investments\n- Managing personal and business finances",
            "**Lesson 3: Sustainable Development**\n- Environmental conservation\n- Sustainable business practices\n- Social entrepreneurship"
        ]
    }
    
    if progress > len(lessons[level]):
        return "You've completed this level! Would you like to start another level or review previous lessons?"
    return lessons[level][progress - 1]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
