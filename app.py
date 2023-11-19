from flask import Flask, request, jsonify, render_template
import requests
import sqlite3
import PyPDF2
import io
import openai
import os
from PyPDF2 import PdfReader
import re
import shutil
import urllib.request
from pathlib import Path
from tempfile import NamedTemporaryFile
#from litellm import completion
import fitz
import numpy as np
import openai
import tensorflow_hub as hub
from sklearn.neighbors import NearestNeighbors


recommender = None

app = Flask(__name__, static_url_path='', static_folder='.')

OPENAI_API_URL = 'https://api.openai.com/v1/engines/davinci/completions'
openai.api_key = <your openai api key>

# SQLite Database setup
DATABASE = 'chatbot.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY,query TEXT,response TEXT)')
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

PDF_FOLDER = 'pdfFolder'  # TODO: Update this path to the folder containing PDF files

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
    try:
        response = openai.Completion.create(
        model="text-davinci-002", 
        prompt=query, 
        max_tokens=150
        )
        answer = response['choices'][0]['text'].strip().lstrip('?\n')
        return answer
    except openai.error.OpenAIError as e:
        return  str(e)
    except Exception as e:
        return str(e)


def download_pdf(url, output_path):
    urllib.request.urlretrieve(url, output_path)


def preprocess(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text


def pdf_to_text(path, start_page=1, end_page=None):
    doc = fitz.open(path)
    total_pages = doc.page_count

    if end_page is None:
        end_page = total_pages

    text_list = []

    for i in range(start_page - 1, end_page):
        text = doc.load_page(i).get_text("text")
        text = preprocess(text)
        text_list.append(text)

    doc.close()
    return text_list


def text_to_chunks(texts, word_length=150, start_page=1):
    text_toks = [t.split(' ') for t in texts]
    chunks = []

    for idx, words in enumerate(text_toks):
        for i in range(0, len(words), word_length):
            chunk = words[i : i + word_length]
            if (
                (i + word_length) > len(words)
                and (len(chunk) < word_length)
                and (len(text_toks) != (idx + 1))
            ):
                text_toks[idx + 1] = chunk + text_toks[idx + 1]
                continue
            chunk = ' '.join(chunk).strip()
            chunk = f'[Page no. {idx+start_page}]' + ' ' + '"' + chunk + '"'
            chunks.append(chunk)
    return chunks


class SemanticSearch:
    def __init__(self):
        self.use = hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')
        self.fitted = False

    def fit(self, data, batch=1000, n_neighbors=5):
        self.data = data
        self.embeddings = self.get_text_embedding(data, batch=batch)
        n_neighbors = min(n_neighbors, len(self.embeddings))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors)
        self.nn.fit(self.embeddings)
        self.fitted = True

    def __call__(self, text, return_data=True):
        inp_emb = self.use([text])
        neighbors = self.nn.kneighbors(inp_emb, return_distance=False)[0]

        if return_data:
            return [self.data[i] for i in neighbors]
        else:
            return neighbors

    def get_text_embedding(self, texts, batch=1000):
        embeddings = []
        for i in range(0, len(texts), batch):
            text_batch = texts[i : (i + batch)]
            emb_batch = self.use(text_batch)
            embeddings.append(emb_batch)
        embeddings = np.vstack(embeddings)
        return embeddings


def load_recommender(path, start_page=1):
    global recommender
    if recommender is None:
        recommender = SemanticSearch()

    texts = pdf_to_text(path, start_page=start_page)
    chunks = text_to_chunks(texts, start_page=start_page)
    recommender.fit(chunks)
    return 'Corpus Loaded.'

def load_recommender_with_chunks(chunks):
    global recommender
    if recommender is None:
        recommender = SemanticSearch()

    # Directly use the provided chunks instead of extracting them from a PDF
    recommender.fit(chunks)
    return 'Corpus Loaded.'

def generate_text(prompt, engine="text-davinci-003"):
    # openai.api_key = openAI_key
    try:
        response = openai.Completion.create(
        model="text-davinci-002", 
        prompt=prompt, 
        max_tokens=150
        )
        answer = response['choices'][0]['text'].strip().lstrip('?\n')
        return answer
    except openai.error.OpenAIError as e:
        return  str(e)
    except Exception as e:
        return str(e)


def generate_answer(question):
    topn_chunks = recommender(question)
    prompt = ""
    prompt += 'search results:\n\n'
    for c in topn_chunks:
        prompt += c + '\n\n'

    prompt += (
        "Instructions: Compose a comprehensive reply to the query using the search results given. "
        "Cite each reference using [ Page Number] notation (every result has this number at the beginning). "
        "Citation should be done at the end of each sentence. If the search results mention multiple subjects "
        "with the same name, create separate answers for each. Only include information found in the results and "
        "don't add any additional information. Make sure the answer is correct and don't output false content. "
        "If the text does not relate to the query, simply state 'Text Not Found in PDF'. Ignore outlier "
        "search results which has nothing to do with the question. Only answer what is asked. The "
        "answer should be short and concise. Answer step-by-step. \n\nQuery: {question}\nAnswer: "
    )

    prompt += f"Query: {question}\nAnswer:"
    answer = generate_text(prompt, "text-davinci-003")
    return answer


def ask_file(question: str) -> str:
    texts = []
    
    for file in os.listdir(PDF_FOLDER):
        pdf_path = os.path.join(PDF_FOLDER, file)
        texts.extend(pdf_to_text(str(pdf_path)))

    # Assuming you want to create a single search corpus from all files
    chunks = text_to_chunks(texts)
    load_recommender_with_chunks(chunks)
    return generate_answer(question)

@app.route('/')
def index():
    init_db()
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form.get('question')
    
    # First, check in the database
    response = get_response_from_db(question)
    
    if not response:
        # Search in PDF documents
        response = ask_file(question)#search_pdf_docs(question)

        if response=='Text Not Found in PDF.':
            # Finally, query OpenAI
            response = get_response_from_openai(question)
            # Store the new query and response in the database
            if response:
                store_query_response(question, response)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
