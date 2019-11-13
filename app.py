from flask import Flask, render_template, request,redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin,login_user,current_user,login_required,logout_user
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.secret_key = "abc"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"

class User(UserMixin,db.Model):
    __tablename__ = 'users' # hidden table name in sql
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(225), nullable= False, unique= True)
    password = db.Column(db.String(225), nullable= False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self,password):
        return check_password_hash(self.password,password)

db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/',methods=['GET'])
def root():
    return render_template("view/body.html")



@app.route('/signup', methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('blog'))
    if request.method == "POST":
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            flash('Email address already exists.')
            return redirect(url_for("signup"))
        new_user = User(email = request.form['email'], firstname= request.form['firstname'],lastname=request.form['lastname'])
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        flash("You have signed up successfully", 'success')
        return redirect(url_for("signup"))
    return render_template("signup.html")


@app.route('/signin', methods=['GET','POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('blog'))
    if request.method == "POST":
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            if user.check_password(request.form['password']):
                login_user(user)
                flash('welcome {0}'.format(user.email), 'success')
                return redirect(url_for("blog"))
            flash('Incorrect Email or Password','warning')
            return redirect(url_for("signin"))
        flash('Incorrect Email or Password','warning')
        return redirect(url_for("signin"))
    return render_template("signin.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("root"))


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    body = db.Column(db.String(200), nullable = False)
    author = db.Column(db.String(200), nullable = False)
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

db.create_all()

@app.route('/blog', methods=['GET','POST'])
#add new entry
def blog():
    if not current_user.is_authenticated:
        return redirect(url_for("signin"))
    if request.method == "POST":
        new_blog = Blog(title = request.form['title'],body = request.form['body'],author=request.form['author'])
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for("blog"))
    posts = Blog.query.all()
    return render_template('blog.html', posts = posts)

#delete an entry
@app.route('/blog/<id>', methods = ['GET','POST'])
def delete_blog(id):
    if request.method == "POST":
        post = Blog.query.filter_by(id = id).first()
        if not post:
            return "there is no such post"
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for("blog"))
    return "Not allowed"

# @app.route('/blog/<id>', methods = ['GET', 'POST'])
# def update_blog(id):
#     if request.method == "POST":
#         new_blog = Blog(title = request.form['title'],body = request.form['body'],author=request.form['author'])
#         db.session.add(new_blog)
#         db.session.commit()


if __name__ == "__main__":
    app.run(debug = True)