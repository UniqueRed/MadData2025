from flask import Flask, jsonify, render_template, request, session
from waitress import serve

major = ''
app = Flask(__name__)
app.secret_key = 'your_secret_key'  

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/chat')
def index():
    return render_template("chat.html")

@app.route('/set_major', methods=['POST'])
def set_major():
    selected_major = request.form.get("major")
    if selected_major:
        session['major'] = selected_major 
        return jsonify({"message": "Major selected successfully!", "major": selected_major}), 200
    return jsonify({"error": "No major selected"}), 400

@app.route('/get_major', methods=['GET'])
def get_major():
    major = session.get('major', "Not selected")
    print(major) # Debugging in the Terminal
    return jsonify({"major": major})


#ALBERT EDIT THIS PART
@app.route('/generate_response', methods=['POST'])
def generate_response():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message received"}), 400
    
    #Integrate LLM model here  #ALBERT
    ai_response = f"(LLM Response Placeholder) You said: {user_message}"
    
    return jsonify({"response": ai_response})

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
