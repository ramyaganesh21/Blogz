from flask import Flask, request, redirect, render_template,session,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:happyday@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "cG56KLWmmn90223an33"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    date_posted =db.Column(db.DateTime)
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))


    def __init__ (self, title, body, owner, date_posted=None):
        self.title = title
        self.body = body
        if date_posted is None:
            date_posted = datetime.utcnow()
        self.date_posted = date_posted
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(50))
    blog = db.relationship('Blog',backref='owner')  

    def __init__ (self, user_name, password):
        self.user_name = user_name
        self.password = password

@app.before_request
def required_login():
    allowed_routes = ['login','signup','index','blog']
    if request.endpoint not in allowed_routes and 'user_name' not in session:
        return redirect('/login')
            

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users, heading ='Blog Users')


@app.route('/blog')
def blog():
    posts = Blog.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('user')

    if user_id:
        posts = Blog.query.filter_by (owner_id=user_id)
        return render_template('user.html',posts=posts, heading = "User Posts")


    if blog_id:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post)

    return render_template('blog.html', posts=posts)    
    

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    
    owner = User.query.filter_by(user_name = session['user_name']).first()

    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']
        date_posted = datetime.now()
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "Please enter a Blog title"
        if not blog_body:
            body_error = "Please enter a Blog entry"

        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body,owner)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', heading ='New Blog Entry')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']

        user = User.query.filter_by(user_name = user_name).first()
        if user and user.password == password:
            session['user_name'] = user_name
            flash("Logged in")
            return redirect('/newpost')

        else:
           flash('User password incorrect, or user does not exist', 'error' )
           

    return render_template('login.html', heading = "Login")

@app.route('/signup', methods = ['POST','GET'])

def signup():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        verify = request.form['verify']

      

        existing_user = User.query.filter_by(user_name = user_name).first()

        if password != verify:
            flash('password does not match',"error")
        elif len (user_name) < 3 or len(password) <3:
            flash('Username and password must be more than 3 characters',"error") 
        elif existing_user:
            flash('Username already exists','error')
        else:
            new_user = User(user_name,password)
            db.session.add(new_user)
            db.session.commit()
            session['user_name'] = user_name
            return redirect ('/newpost')
       
    return render_template('signup.html', heading = "Sign-Up")   

@app.route('/logout')
def logout():
    del session['user_name']
    return redirect ('/blog') 






if  __name__ == "__main__":
    app.run()