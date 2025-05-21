from dotenv import load_dotenv
import os
import re
from flask import Flask, request, jsonify
import fitz  # PyMuPDF
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

@app.route('/extract', methods=['POST'])
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

