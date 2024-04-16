import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display, Markdown
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import uuid as uuid
import firebase_admin
import requests
from authlib.integrations.flask_client import OAuth
import secrets
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,login_required,current_user, login_required
import sqlalchemy as sa
from sqlalchemy.sql import text
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_avatars import Avatars
import flask_moment 
from flask_moment import datetime
import flask_filealchemy
import flask_admin 
from flask_admin import Admin
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import os
from PIL import Image


GOOGLE_API_KEY = "API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-1.5-pro-latest"


secret_key = secrets.token_bytes(32)


UPLOAD_FOLDER = 'static/imgs/'



app = Flask(__name__)

admin = Admin(app, template_mode='base.html')

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"


app.config['SECRET_KEY'] = secret_key

db = SQLAlchemy()
migrate  = Migrate(app,db)
 
login_manager = LoginManager()
login_manager.init_app(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER





# Create user model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True,
                         nullable=False)
    password_hash = db.Column(db.String(250),
                         nullable=False)
    username = db.Column(db.String(250), unique=True, 
                         nullable=False)
    name = db.Column(db.String(250),
                         nullable=False)
    bio = db.Column(db.String(1000),nullable = False )

    profile_pic =db.Column(db.String(),nullable = True )

    data_added = db.Column(db.DateTime, default=datetime.utcnow)



    #return string
    def __repr__(self):
        return '<Name %r>' % self.name

    #do Pasword stuff
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash= generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
 
 
# Initialize app with extension
db.init_app(app)
# Create database within app context
 
with app.app_context():
    db.create_all()


 
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(int(user_id))




model = None
@app.route('/')
def home():
    return render_template('index.html')



@app.route('/register', methods=["GET", "POST"])
def register():
  # If the user made a POST request, create a new user
    if request.method == "POST":
        email = Users(email=request.form.get("email"),
                     password=request.form.get("password"),
                     name = request.form.get("firstname") + request.form.get("lastname"),
                     username = request.form.get("username"),
                     bio = " This is a bio!"
                     )
        # Add the user to the database
        db.session.add(email)
        # Commit the changes made
        db.session.commit()
        # Once user account created, redirect them
        # to login route (created later on)
        return redirect(url_for("login"))
    # Renders sign_up template if user made a GET request
    return render_template("sign_up.html")



@app.route("/login", methods=["GET", "POST"])
def login():

	# If a post request was made, find the user by 
	# filtering for the username
	if request.method == "POST":
		email = Users.query.filter_by(
			email=request.form.get("email")).first()
		# Check if the password entered is the 
		# same as the user's password


		if check_password_hash(email.password_hash, request.form.get("password")):
			# Use the login_user method to log in the user
			login_user(email)
			return redirect(url_for('dash'))
		# Redirect the user back to the home
		# (we'll create the home route in a moment)
	return render_template("/login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dash():

    id = current_user.id
    return render_template("dashboard.html")





@app.route('/admin')
@login_required
def admin():
	id = current_user.id
	if id == 1:
		return render_template("admin.html")
	else:
		flash("Sorry you must be the Admin to access the Admin Page...")
		return redirect(url_for('dashboard'))







@app.route('/update/<int:id>', methods=['GET','POST'] )
@login_required
def update(id):

    name_to_update = Users.query.get_or_404(id)
# If the user made a POST request, create a new user
    if request.method == "POST":
        name_to_update.email = request.form.get("email")
        name_to_update.username = request.form.get("username")
        name_to_update.bio = request.form.get('bio') 


        if request.files.get('file'):
            name_to_update.profile_pic = request.files.get('file')
            #grabe Image name
            pic_filename = secure_filename(name_to_update.profile_pic.filename) 
            #set uuiud
            pic_name = str(uuid.uuid1()) +  "_" + pic_filename
            #save image 
            saver = request.files['file']
            
            name_to_update.profile_pic = pic_name
            
            save_pfp = os.path.join(app.config['UPLOAD_FOLDER'], pic_name)

            try:
                db.session.commit()

                output_size = (150, 150)

                i = Image.open( request.files['file'])
                i.thumbnail(output_size)
                i.save(save_pfp)

                flash("User Updated Successfully!")
                return render_template("update.html", name_to_update = name_to_update, id=id)
            except:
                flash("Error!  Looks like there was a problem...try again!")
                return render_template("update.html", name_to_update = name_to_update, id =id)
        else:
            db.session.commit()
            flash("User update successfully!")
            return render_template("update.html", name_to_update = name_to_update, id =id)
    else:
        return render_template("update.html", name_to_update = name_to_update, id = id )

    return render_template("update.html", name_to_update = name_to_update, id = id )





@app.route('/delete', methods=['GET','POST'])
@login_required
def delete():
    db.session.delete(current_user)
    db.session.commit()
    return render_template("/delete.html")


@app.route('/prompt', methods=['GET', 'POST'])
@login_required
def prompt():
    global model
    if request.method == 'POST':
        prompt = request.form['prompt']
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=prompt)
        return redirect(url_for('chatbot'))
    return render_template('prompt.html')





@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chatbot():
    global model
    if request.method == 'POST':
        user_input = request.form['user_input']
        response = model.generate_content(
            user_input,
            safety_settings={
                'HATE': 'BLOCK_NONE',
                'HARASSMENT': 'BLOCK_NONE',
                'SEXUAL': 'BLOCK_NONE',
                'DANGEROUS': 'BLOCK_NONE'
            })
        return render_template('chat.html', user_text=user_input, ai_text=response.text)
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
