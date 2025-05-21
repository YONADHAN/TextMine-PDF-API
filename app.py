from dotenv import load_dotenv
import os
import re
from flask import Flask, request, jsonify
import fitz  # PyMuPDF
from docx import Document
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

API_SECRET_KEY = os.getenv('API_SECRET_KEY')

def clean_text(text: str) -> str:
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # remove non-ASCII chars
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.route('/')
def index():
    return jsonify({"message": "PDF Text Extractor API"}), 200

@app.route('/extract-pdf', methods=['POST'])
def extract_text():
    api_key = request.headers.get('X-API-KEY')
    if not api_key or api_key != API_SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
    except Exception as e:
        return jsonify({'error': f'Failed to read PDF file: {str(e)}'}), 400

    full_text = ""
    for page in doc:
        page_text = page.get_text()
        cleaned = clean_text(page_text)
        full_text += cleaned + "\n"

    # Return only the raw cleaned text
    return jsonify({"rawText": full_text.strip()})


@app.route('/extract-doc', methods=['POST'])
def extract_doc_text():
    api_key = request.headers.get('X-API-KEY')
    if not api_key or api_key != API_SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith(('.doc', '.docx')):
        return jsonify({'error': 'Invalid file type. Only .doc and .docx allowed'}), 400

    try:
        document = Document(file)
        full_text = ""
        for para in document.paragraphs:
            cleaned = clean_text(para.text)
            full_text += cleaned + "\n"
    except Exception as e:
        return jsonify({'error': f'Failed to read DOCX file: {str(e)}'}), 400

    return jsonify({"rawText": full_text.strip()})


@app.route('/extract-txt', methods=['POST'])
def extract_txt_text():
    api_key = request.headers.get('X-API-KEY')
    if not api_key or api_key != API_SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.txt'):
        return jsonify({'error': 'Invalid file type. Only .txt allowed'}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
        cleaned = clean_text(content)
    except Exception as e:
        return jsonify({'error': f'Failed to read TXT file: {str(e)}'}), 400

    return jsonify({"rawText": cleaned.strip()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

