from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import PyPDF2
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import openai
import uuid
import os

app = Flask(__name__)
CORS(app)

# Initialize Pinecone, OpenAI, and SentenceTransformer
pc = Pinecone(api_key="e7dc8a53-f644-48fe-a8f2-875cdf161aa5")
index = pc.Index("textboook-index")
openai.api_key = "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"
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def get_embedding(text):
    return embed_model.encode(text).tolist()

def add_textbook_to_index(pdf_path):
    try:
        text = extract_text_from_pdf(pdf_path)
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            index.upsert(vectors=[(str(uuid.uuid4()), embedding, {"text": chunk, "source": pdf_path})])
        
        return True
    except Exception as e:
        print(f"Error adding textbook: {e}")
        return False

def get_relevant_context(query):
    query_embedding = get_embedding(query)
    results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
    context = ""
    for match in results['matches']:
        context += f"\nFrom {match['metadata']['source']}:\n{match['metadata']['text']}\n"
    return context

def get_ai_response(query, context):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on textbook information. Use the provided context to answer the user's question. If the context doesn't contain relevant information, say so."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]
    )
    return response.choices[0].message['content']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    context = get_relevant_context(user_message)
    response = get_ai_response(user_message, context)
    return jsonify({'response': response})

@app.route('/upload', methods=['POST'])
def upload_textbook():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    if file and file.filename.endswith('.pdf'):
        filename = str(uuid.uuid4()) + '.pdf'
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        success = add_textbook_to_index(filepath)
        os.remove(filepath)  # Remove the file after processing
        if success:
            return jsonify({'success': True, 'message': 'File uploaded and processed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Error processing file'})
    else:
        return jsonify({'success': False, 'message': 'Invalid file type'})

if __name__ == '__main__':
    app.run(debug=True)