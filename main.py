from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Dummy user validation
        if username == 'admin' and password == 'password':
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')
    
    
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template("logout.html")
    
if __name__ == "__main__":
    app.run(debug=True)