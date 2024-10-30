from flask import Flask, request, redirect, render_template, url_for, flash
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'rockyrocks'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

# Blog Model
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(20))
    post_date = db.Column(db.DateTime, default=datetime.now())
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Blog {self.title}, {self.post_date}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Page with Navigation to About and Login
@app.route('/')
def index():
    return render_template('index.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password", "danger")
    return render_template('login.html')



# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

# Dashboard Route for CRUD Operations
@app.route('/dashboard')
@login_required
def dashboard():
     posts = Blog.query.all()  # Fetch all posts
     return render_template('dashboard.html', posts=posts)

#  create_post route
@app.route('/create_post',methods=['GET','POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title=request.form['title']
        author=request.form['author']
        content=request.form['content']
        

        new_post=Blog(title=title,author=author, content=content,post_date=datetime.now())
        db.session.add(new_post)
        db.session.commit()

        flash("post created successfully ","success")
        return redirect(url_for('dashboard'))
    return render_template('create_post.html')

# Update_post route
@app.route('/update_post/<int:post_id>',methods=['GET','POST'])
@login_required
def update_post(post_id):
    # get_or_404() is a convenience method that either retrieves the requested item or returns a 404 error if the item isn’t found.
    post=Blog.query.get_or_404(post_id)
    if request.method =='POST':
        post.title=request.form['title']
        post.author=request.form['author']
        post.content=request.form['content']

        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for('dashboard'))
    return render_template('update_post.html', post=post)


# delete_post route
@app.route('/delete_post/<int:post_id>',methods=['POST'])
@login_required
def delete_post(post_id):
    post=Blog.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully!", "success")
    return redirect(url_for('dashboard'))











    

if __name__ == '__main__':
    app.run(debug=True)
