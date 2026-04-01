import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app) # Allow frontend to communicate with backend

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the client with provided API key (hardcoded for now as agreed)
client = genai.Client(api_key="AIzaSyC-NvnO5AO04k2ieA-myfIMY__wuhBnORI")

@app.route('/api/chat', methods=['POST'])
def chat():
    # Using FormData, extract text from request.form and file from request.files
    user_message = request.form.get('message', '')
    file = request.files.get('file')
    
    if not user_message and not file:
        return jsonify({"error": "No message or file provided"}), 400
        
    contents = []
    filepath = None
    genai_file = None
    
    try:
        # Handle file upload to Google AI (RAG process)
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Use Native File Upload API to add document strictly built-in to Gemini
            print(f"Processing and uploading {filename} to Gemini storage...")
            genai_file = client.files.upload(file=filepath)
            contents.append(genai_file)
            print("File analyzed!")
            
        if user_message:
            contents.append(user_message)
            
        # Send prompt combined with potential document
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
        )
        result_text = response.text
        
    except Exception as e:
        error_msg = str(e)
        if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
            # Fallback to gemini-2.5-flash-lite which has a larger free-tier quota
            try:
                print("Primary hit rate limit. Trying fallback lite model...")
                response = client.models.generate_content(
                    model='gemini-2.5-flash-lite',
                    contents=contents,
                )
                result_text = response.text
            except Exception as fallback_e:
                print(f"Fallback error: {fallback_e}")
                error_str = str(fallback_e)
                if '429' in error_msg or '429' in error_str:
                     return jsonify({"error": "Google API Rate Limit Exceeded. You have sent too many requests on the free tier. Please wait roughly 1 minute or use a new API key."}), 429
                return jsonify({"error": f"API Error: {error_str}"}), 500
        else:
            print(f"Error calling Gemini: {e}")
            return jsonify({"error": "An unexpected error occurred: " + error_msg}), 500
    
    finally:
        # Safe cleanup for local artifact
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            
    return jsonify({"response": result_text})

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
