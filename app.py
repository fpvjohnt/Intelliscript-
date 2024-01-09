from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2
import docx

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set a path for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'pptx', 'rtf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize OpenAI client with your API key
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/code-interpreter')
def code_interpreter():
    return render_template('code.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form['message']
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",  # Updated to GPT-4 model
            messages=[{"role": "user", "content": user_message}]
        )
        bot_response = response.choices[0].message['content']
        return jsonify({'query': user_message, 'response': bot_response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)})

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        try:
            extracted_text = process_file(file_path, file.filename)
            response = openai_client.completions.create(
                model="gpt-4",  # Assuming GPT-4 can also handle summarization tasks
                prompt=f"Summarize this document: {extracted_text}",
                max_tokens=1024
            )
            summary = response.choices[0].text.strip()
            return jsonify({'message': 'File uploaded and processed', 'filename': filename, 'summary': summary})
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({'error': 'File not allowed'})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_file(file_path, filename):
    extension = filename.rsplit('.', 1)[1].lower()
    if extension == 'txt':
        with open(file_path, 'r') as file:
            return file.read()
    elif extension == 'pdf':
        text = ''
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfFileReader(pdf_file)
            for page in range(reader.numPages):
                text += reader.getPage(page).extractText()
        return text
    elif extension == 'docx':
        doc = docx.Document(file_path)
        return '\n'.join(paragraph.text for paragraph in doc.paragraphs)
    else:
        raise ValueError('Unsupported file type')

@app.route('/ask-code-question', methods=['POST'])
def ask_code_question():
    data = request.get_json()
    code = data['code']
    question = data['question']
    prompt = f"Explain the following code:\n{code}\n\nQuestion: {question}"
    
    try:
        # Use the chat completion endpoint for a chat model
        response = openai_client.chat.completions.create(
            model="gpt-4",  # Replace with your specific chat model identifier if different
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150
        )
        # The structure of the response object may differ for chat completions.
        # Adjust the following line to match the actual structure.
        return jsonify({'response': response.choices[0].message['content']})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)})
    
if __name__ == '__main__':
    app.run(debug=True)
