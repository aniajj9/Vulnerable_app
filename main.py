from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"
user_data = {} # Initialize an empty dictionary to store user data

def load_user_data():
    try:
        with open('database.json', 'r') as db_file:
            return json.load(db_file)
    except FileNotFoundError:
        return {}

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None  # Initialize the error message as None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Load user data from the JSON file on each login attempt
        user_data = load_user_data()
        
        # Check if the username exists in the loaded user data
        if username in user_data and user_data[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error_message = "Invalid username or password. Please try again."
    
    return render_template('login.html', error_message=error_message)

    
    
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template("logout.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None  # Initialize the error message as None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Load user data from the JSON file
        user_data = load_user_data()
        
        # Check if the username already exists
        if username in user_data:
            error_message = "Username already exists. Please choose another username."
        else:
            # Add the new user to the user_data dictionary
            user_data[username] = password
            
            # Save the user_data dictionary to the database.json file
            with open('database.json', 'w') as db_file:
                json.dump(user_data, db_file)
            
            return redirect(url_for('login'))
    
    return render_template('register.html', error_message=error_message)


if __name__ == "__main__":
    # Load existing user data from the database.json file if it exists
    try:
        with open('database.json', 'r') as db_file:
            user_data = json.load(db_file)
    except FileNotFoundError:
        pass
    
    app.run(debug=True)