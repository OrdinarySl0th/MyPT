from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import PyPDF2
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import anthropic
import uuid
import os
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Initialize Pinecone, SentenceTransformer, and Anthropic
pc = Pinecone(api_key="")
index = pc.Index("textboook-index")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
anthropic_client = anthropic.Anthropic(api_key="")

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
        logging.error(f"Error adding textbook: {e}")
        return False

def get_relevant_context(query):
    try:
        query_embedding = get_embedding(query)
        results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
        context = ""
        for match in results['matches']:
            context += f"\nFrom {match['metadata']['source']}:\n{match['metadata']['text']}\n"
        return context
    except Exception as e:
        logging.error(f"Error in get_relevant_context: {str(e)}")
        return ""

def get_ai_response(query, context):
    try:
        response = anthropic_client.messages.create(
            model="claude-2.1",
            max_tokens=1000,
            system="you are a knowledgeable assistant who takes in information about injuries or aches and pains and goals from a user and then will pretend to be a physical therapist and output an organized exercise plan with instructions on how to perform the suggested exercises using Markdown. Use headers, lists, bold, italic, and code blocks. The plan will cover the next 4 weeks and should will help them get free of their pain and get them started towards their goals.",
            messages=[
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ]
        )
        return response.content[0].text
    except Exception as e:
        logging.error(f"Error in get_ai_response: {str(e)}")
        return "I'm sorry, but I encountered an error while processing your request."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        app.logger.debug(f"Received chat request: {request.json}")
        user_message = request.json['message']
        context = get_relevant_context(user_message)
        response = get_ai_response(user_message, context)
        return jsonify({'response': response})
    except Exception as e:
        logging.error(f"Error in chat route: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
