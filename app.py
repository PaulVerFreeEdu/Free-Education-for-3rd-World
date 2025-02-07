import random
import requests
import sqlite3
import json
import speech_recognition as sr
from googletrans import Translator
import deepl
import logging
from flask import Flask, jsonify, request, render_template_string
import openai

# Configuratie van logging voor foutopsporing en analyse
logging.basicConfig(filename='ai_education.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
user_sessions = {}  # Store user progress

# OpenAI API Key (Replace with actual API key)
OPENAI_API_KEY = "your_openai_api_key"
openai.api_key = OPENAI_API_KEY

# Function to generate AI-powered lessons dynamically
def generate_lesson(user_question):
    prompt = f"Create an educational lesson based on this question: {user_question}. Include an explanation, examples, and a quiz question."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an educational AI assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

# HTML Template for interactive AI chat
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
        user_sessions[user_id] = {"progress": 0}
    
    if "start learning" in question:
        response = "What subject would you like to learn?"
        buttons = ["Math", "Science", "Literacy", "Technology"]
    else:
        lesson_content = generate_lesson(question)
        response = lesson_content
        buttons = ["Next Lesson"]
    
    return jsonify({"answer": response, "buttons": buttons})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
