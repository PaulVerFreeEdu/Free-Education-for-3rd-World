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
            let questionInput = document.getElementById("question");
            let question = questionInput.value;
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
            
            questionInput.value = "";
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
        <button onclick="askAI()">Start Learning</button>
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
    question = data.get("question", "").strip()
    
    platform = AIEducationPlatform()
    translator = Translator()
    detected_lang = translator.detect(question).lang
    
    # Initial learning level selection
    if "start learning" in question.lower():
        response = "What is your current learning level?\n1. Beginner (Basic literacy, math)\n2. Intermediate (Science, Technology)\n3. Advanced (Entrepreneurship, Sustainability)\nPlease type 1, 2, or 3."
    elif question in ["1", "2", "3"]:
        if question == "1":
            response = "Great! Let's start with Basic Literacy and Math.\n\n**Lesson 1: Basic Literacy**\n- Letters and Sounds\n- How to form simple words\n- Understanding basic sentences\n\n**Lesson 2: Basic Writing**\n- Constructing simple sentences\n- Writing short stories\n- Understanding punctuation\n\n**Lesson 3: Basic Math**\n- Counting numbers\n- Simple addition and subtraction\n- Basic multiplication and division\n\nWould you like to continue with Literacy or switch to Math?"
        elif question == "2":
            response = "Nice! Science and Technology are exciting fields.\n\n**Lesson 1: Introduction to Science**\n- What is science?\n- Observations and experiments\n- Basic elements of nature\n\n**Lesson 2: Introduction to Technology**\n- Understanding digital tools\n- The internet and its uses\n- Basic programming concepts\n\n**Lesson 3: Physics Basics**\n- Understanding motion and energy\n- Simple machines and their uses\n\nWould you like to explore Chemistry, Biology, or Coding next?"
        elif question == "3":
            response = "Advanced learning! Let's start with Business Basics.\n\n**Lesson 1: Introduction to Business**\n- What is a business?\n- How do businesses operate?\n- Understanding trade and economy\n\n**Lesson 2: Financial Literacy**\n- Budgeting and saving money\n- Understanding investments\n- Managing personal and business finances\n\n**Lesson 3: Sustainable Development**\n- Environmental conservation\n- Sustainable business practices\n- Social entrepreneurship\n\nWould you like to continue with Entrepreneurship, Sustainability, or Business Management?"
    else:
        response = "I can guide you step by step! Type 'Start Learning' to begin."
    
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
