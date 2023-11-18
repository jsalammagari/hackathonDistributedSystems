
from flask import Flask, request, jsonify, render_template
import requests
import os
import sqlite3
import PyPDF2
import io
import os
from PyPDF2 import PdfReader

app = Flask(__name__, static_url_path='', static_folder='.')

OPENAI_API_URL = 'https://api.openai.com/v1/engines/davinci/completions'
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# SQLite Database setup
DATABASE = 'chatbot.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY,
            query TEXT,
            response TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_response_from_db(query):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT response FROM chat_history WHERE query = ?', (query,))
    response = c.fetchone()
    conn.close()
    return response[0] if response else None

def store_query_response(query, response):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO chat_history (query, response) VALUES (?, ?)', (query, response))
    conn.commit()
    conn.close()

PDF_FOLDER = '/pdfFolder'  # TODO: Update this path to the folder containing PDF files

def search_pdf_docs(query):
    for filename in os.listdir(PDF_FOLDER):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(PDF_FOLDER, filename)
            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text and query.lower() in text.lower():
                        start = max(text.lower().find(query.lower()) - 30, 0)
                        end = min(start + 30 + len(query), len(text))
                        return text[start:end]  # Return the text surrounding the query
            except Exception as e:
                print(f'Error reading {pdf_path}: {e}')
                continue
    return None


def get_response_from_openai(query):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    data = {
        'prompt': query,
        'max_tokens': 150
    }
    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['text'].strip()
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question')
    
    # First, check in the database
    response = get_response_from_db(question)
    
    if not response:
        # Search in PDF documents
        response = search_pdf_docs(question)

        if not response:
            # Finally, query OpenAI
            response = get_response_from_openai(question)

            # Store the new query and response in the database
            if response:
                store_query_response(question, response)

    return jsonify({'response': response})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
