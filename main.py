from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from utils.password_hashing import PasswordHash

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SESSION_COOKIE_HTTPONLY'] = False
db = SQLAlchemy(app)

# database model
class Users(db.Model):
    id = db.Column(db.Integer)
    username = db.Column(db.String(50), primary_key=True)
    passwordHash = db.Column(db.String(200), nullable=False)
    cpr = db.Column(db.String(9), nullable=False)

@app.route('/', methods=['GET'])
def default():
    if session.get('username', None):
        return redirect(url_for('home', submenu=None))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the database to check if the username exists
        user = Users.query.filter_by(username=username).first()
        
        # Check if the username exists in the loaded user data
        if user and password_hashing.verify_password(user.passwordHash, password):
            session['username'] = username
            cpr = user.cpr
            return redirect(url_for('home', submenu=None))  # Redirect to the "home" route
    
        else:
            error_message = "Invalid username or password. Please try again."
    
    return render_template('login.html', error_message=error_message)
 
  
@app.route('/home', methods=['GET', 'POST'])
@app.route('/home/<submenu>', methods=['GET', 'POST']) # Show cpr
@app.route('/home/<submenu>/<subsubmenu>', methods=['GET', 'POST']) # Show password hash
def home(submenu=None, subsubmenu= None):
    username = session.get('username', None)
    if username:
        user = Users.query.filter_by(username=username).first()
        if user:
            if submenu is None:
                return render_template("home.html", submenu=submenu, cpr=user.cpr) # Basic home page
            else:
                matching_username = Users.query.filter_by(username=submenu).first() # If user with given username exists:
                if matching_username:
                    if subsubmenu is None:
                        return render_template("home.html", submenu=submenu, cpr=matching_username.cpr) # Display the existing user's (not necessarily logged in) cpr, IF WE DONT REQUEST TO SEE PASSWORD HASH
                    else:
                        if subsubmenu == matching_username.cpr: # Check if cpr belongs to the logged in user. if yes, display password hash
                            return render_template("home.html", submenu=submenu, subsubmenu=subsubmenu, password = matching_username.passwordHash, cpr=subsubmenu)
                        elif Users.query.filter_by(cpr = subsubmenu).first(): # If cpr doesnt belong to logged user, return verbose error
                            return render_template("home.html", submenu=submenu, cpr=matching_username.cpr, error_message=f"Error. User with username {username} tried to access information about {Users.query.filter_by(cpr = subsubmenu).first().username}")
    
    # If no valid user or matching username is found, return a "Not Found" response
    abort(404)



@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template("logout.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cpr = request.form['cpr']
        
        # Check if the username already exists in the database
        existing_user = Users.query.filter_by(username=username).first()
        
        if existing_user:
            error_message = "Username already exists. Please choose another username."
        else:
            # Create a new user record and add it to the database
            password_hash = password_hashing.hash_password(password)
            new_user = Users(username=username, passwordHash=password_hash, cpr=cpr)
            db.session.add(new_user)
            db.session.commit()            
            return redirect(url_for('login'))
    
    return render_template('register.html', error_message=error_message)

@app.route('/view_users', methods=['GET'])
def view_users():
    # Query all user entries from the Users table
    users = Users.query.all()
    
    return render_template('view_users.html', users=users)

if __name__ == "__main__":

    # Initialize database
    with app.app_context():
        db.create_all()


    # Initialize password hashing
    hashing_algorithm = "sha256"
    password_hashing = PasswordHash(hashing_algorithm)
    
    app.run(debug=True)