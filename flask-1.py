from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Create a new SQLite database if it doesn't exist
conn = sqlite3.connect('chat_history.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS chat_history
             (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)''')
conn.commit()
conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_message = request.form['message']
        save_message('user', user_message)
        bot_response = process_message(user_message)  # Replace with your chatbot logic
        save_message('bot', bot_response)
        return redirect(url_for('index'))
    else:
        conn = sqlite3.connect('chat_history.db')
        c = conn.cursor()
        c.execute("SELECT * FROM chat_history")
        chat_history = c.fetchall()
        conn.close()
        return render_template('index.html', chat_history=chat_history)

def save_message(sender, message):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (sender, message, timestamp) VALUES (?, ?, ?)", (sender, message, timestamp))
    conn.commit()
    conn.close()

def process_message(user_message):
    # Replace with your chatbot logic
    return "This is a sample response from the chatbot."

if __name__ == '__main__':
    app.run(debug=True)