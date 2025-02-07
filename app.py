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
