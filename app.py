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

# Function to fetch educational lessons from open APIs
def fetch_lesson(subject, level):
    api_endpoints = {
        "khan_academy": f"https://www.khanacademy.org/api/internal/_search?q={subject}+{level}&languages=en",
        "wikipedia": f"https://en.wikipedia.org/api/rest_v1/page/summary/{subject.replace(' ', '_')}"
    }
    
    try:
        # Try Khan Academy first
        response = requests.get(api_endpoints["khan_academy"])
        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                return f"**Lesson on {subject.capitalize()} (Level: {level.capitalize()})**\n{data['items'][0]['snippet']}\nSource: Khan Academy"
        
        # Try Wikipedia as a fallback
        response = requests.get(api_endpoints["wikipedia"])
        if response.status_code == 200:
            data = response.json()
            if "extract" in data:
                return f"**Lesson on {subject.capitalize()} (Level: {level.capitalize()})**\n{data['extract']}\nSource: Wikipedia"
    except Exception as e:
        logging.error(f"Error fetching lesson: {str(e)}")
    
    return "No lesson found for this topic. Please try another subject."

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
        
        function updateButtons(buttons) {
            let buttonContainer = document.getElementById("buttons");
            buttonContainer.innerHTML = "";
            if (buttons) {
                buttons.forEach(text => {
                    let btn = document.createElement("button");
                    btn.innerText = text;
                    btn.onclick = () => askAI(text);
                    buttonContainer.appendChild(btn);
                });
            }
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
    
    translator = Translator()
    detected_lang = translator.detect(question).lang
    
    buttons = []
    
    if "start learning" in question:
        user_sessions[user_id]["level"] = None
        response = "What is your current learning level?"
        buttons = ["Beginner", "Intermediate", "Advanced"]
    elif question in ["beginner", "intermediate", "advanced"]:
        user_sessions[user_id]["level"] = question
        response = "Select a subject to start learning."
        buttons = ["Literacy", "Math", "Science", "Technology", "Business"]
    elif question in ["literacy", "math", "science", "technology", "business"]:
        user_sessions[user_id]["subject"] = question
        response = fetch_lesson(user_sessions[user_id]["subject"], user_sessions[user_id]["level"])
        buttons = ["Next Lesson"]
    else:
        response = "I can guide you step by step! Type 'Start Learning' to begin."
    
    if detected_lang != "en":
        response = translator.translate(response, dest=detected_lang).text
    
    return jsonify({"answer": response, "buttons": buttons})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
