from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
from ChatBot import get_output

app = Flask(__name__)

chat_history=[]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message',methods=['POST'])
def send_message():
    user_question=request.form['user_prompt']
    bot_response=get_output(user_question)
    chat_history.append({'user':user_question,'bot':bot_response})
    return jsonify({'response':bot_response})

@app.route('/get_chat_history')
def get_chat_history():
    return jsonify(chat_history)

if __name__=='__main__':
    app.run(debug=True)

