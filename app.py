from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
import hashlib
import os

os.system("pip install -r requirements.txt")


app = Flask(__name__)
app.secret_key = "your_secret_key"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:oRCkbqqMy6Cg6wjZoKdI@localhost:5432/users'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@vulnappserver:oRCkbqqMy6Cg6wjZoKdI@vulnappserver.postgres.database.azure.com/postgres'

app.config['SESSION_COOKIE_HTTPONLY'] = False
db = SQLAlchemy(app)

# database model
class Users(db.Model):
    username = db.Column(db.String(50), primary_key=True)
    passwordhash = db.Column(db.String(200), nullable=False)
    cpr = db.Column(db.String(9), nullable=False)


class PasswordHash:

    def __init__(self, hash_algorithm) -> None:
        self.__hash_algorithm = hash_algorithm

    def hash_password(self, password):
        # Hash the password using the specified algorithm
        hash_obj = hashlib.new(self.__hash_algorithm)
        hash_obj.update(password.encode('utf-8'))
        return hash_obj.hexdigest()

    def verify_password(self, hashed_password, password):
        # Verify a password against its hashed version using the specified algorithm
        return hashed_password == self.hash_password(password)
    

# Initialize password hashing
hashing_algorithm = "md5"
password_hashing = PasswordHash(hashing_algorithm)


@app.route('/', methods=['GET'])
def default():
    if session.get('username', None):
        return redirect(url_for('home', submenu=None))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username', None):
        return redirect(url_for('home', submenu=None))
    error_message = None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the database to check if the username exists
        user = Users.query.filter_by(username=username).first()
        
        # Check if the username exists in the loaded user data
        #return render_template('login.html', error_message=f"{password}, {user.passwordhash}, {username}")
        if user:
            if password_hashing.verify_password(user.passwordhash, password):
                session['username'] = username
                return redirect(url_for('home', submenu=None))  # Redirect to the "home" route 
            else:
                error_message = "Invalid password. Please try again."
        else:
            error_message = "Invalid username. Please try again."
    
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
                            return render_template("home.html", submenu=submenu, subsubmenu=subsubmenu, password = matching_username.passwordhash, cpr=matching_username.cpr)
                        elif Users.query.filter_by(cpr = subsubmenu).first(): # If cpr doesnt belong to logged user, return verbose error
                            error_msg = f"Error. You tried to access information about user {submenu} (CPR: {matching_username.cpr}), but query returned information about user {Users.query.filter_by(cpr = subsubmenu).first().username} (CPR: {Users.query.filter_by(cpr = subsubmenu).first().cpr})"
                            return render_template("home.html", submenu=submenu, cpr=matching_username.cpr, error_message=error_msg)
                        else:
                            error_msg = f"Error. You tried to access information about user {submenu} (CPR: {matching_username.cpr}), but query returned information not related to any user ({subsubmenu})"
                            return render_template("home.html", submenu=submenu, cpr=matching_username.cpr, error_message=error_msg)

    # If no valid user or matching username is found, return a "Not Found" response
    abort(404)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template("logout.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = ""
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cpr = request.form['cpr']
        
        # Check if the username already exists in the database
        existing_user = Users.query.filter_by(username=username).first()
        
        if existing_user:
            error_message += "Username already exists. Please choose another username.  "

        # Check if the cpr already exists in the database
        existing_cpr = Users.query.filter_by(cpr=cpr).first()
        
        if existing_cpr:
            error_message += "User with this CPR already exists."
        else:
            # Create a new user record and add it to the database
            password_hash = password_hashing.hash_password(password)
            new_user = Users(username=username, passwordhash=password_hash, cpr=cpr)
            db.session.add(new_user)
            try:
                db.session.commit()  
            except:
                db.session.rollback()      
            return redirect(url_for('login'))
    
    return render_template('register.html', error_message=error_message)

@app.route('/view_users', methods=['GET'])
def view_users():
    # Query all user entries from the Users table
    users = Users.query.all()
    
    return render_template('view_users.html', users=users)

# Remove all entries from Users table. This method is now not run, run it only when you want to clear
@app.route('/clear_users', methods=['GET'])
def clear_users():
    try:
        db.session.query(Users).delete()
        db.session.commit()
    except:
        db.session.rollback() 
    users = Users.query.all()
    return render_template('view_users.html', users=users)   



if __name__ == "__main__":

    # Initialize database
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)