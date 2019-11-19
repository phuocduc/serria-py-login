from flask import Flask, render_template, request,redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin,login_user,current_user,login_required,logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

app = Flask(__name__)




app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.secret_key = "abc"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
db = SQLAlchemy(app)

migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(225), nullable= False, unique= True)
    password = db.Column(db.String(225), nullable= False)
    img_url = db.Column(db.Text)

    post = db.relationship('Post',backref="user",lazy=True)

    like_post = db.relationship('Post', secondary="likes", backref="my_likes", lazy=True)
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self,password):
        return check_password_hash(self.password,password)

db.create_all()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    author=db.Column(db.String(255), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    body = db.Column(db.Text, nullable = False)
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()),
    img_url = db.Column(db.Text)
    view_count = db.Column(db.Integer, default = 0)

likes = db.Table('likes',
            db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
            db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True))



db.create_all()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String, nullable = False)
    author_comment= db.Column(db.String, nullable= False)
    user_id = db.Column(db.Integer, nullable = False)
    post_id = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    img_url = db.Column(db.Text)

db.create_all()




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)




@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            flash('Email address already exists.')
            return redirect(url_for("signup"))
        new_user = User(email = request.form['email'], firstname= request.form['firstname'],lastname=request.form['lastname'],img_url = request.form['imgUrl'])
        new_user.set_password(request.form['password'])
    
        db.session.add(new_user)
        db.session.commit()
        flash("You have signed up successfully", 'success')
        return redirect(url_for("signup"))
    return render_template("view/signup.html")


@app.route('/', methods=['GET','POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('main_page'))
    if request.method == "POST":
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            if user.check_password(request.form['password']):
                login_user(user)
                flash('welcome {0}'.format(user.email), 'success')
                return redirect(url_for("main_page"))
            flash('Incorrect Email or Password','warning')
            return redirect(url_for("signin"))
        flash('Incorrect Email or Password','warning')
        return redirect(url_for("signin"))
    return render_template("view/signin.html")



@app.route('/blog', methods=['GET','POST'])
@login_required
def main_page():
    if not current_user.is_authenticated:
        return redirect(url_for("signin"))
    if request.method == "POST":
        new_post = Post(body = request.form['body'],author=current_user.email.split("@")[0],
        img_url = current_user.img_url)
        current_user.post.append(new_post)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("main_page"))
    posts = Post.query.all()
    for post in posts:
        post.comments = Comment.query.filter_by(post_id= post.id).first()
    return render_template('view/blog.html', posts = posts)



#delete an entry
@app.route('/blog/<id>', methods = ['GET','POST'])
def delete_blog(id):
    if request.method == "POST":
        post = Post.query.filter_by(id = id).first()
        if not post:
            return "there is no such post"
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for("main_page"))
    return "Not allowed"



@app.route('/post/<id>', methods=['GET','POST'])
@login_required
def view_post(id):
    post = Post.query.get(id)
    post.view_count +=1
    db.session.commit()
    if request.method == "POST":
        new_comment = Comment(body=request.form['body'],user_id=current_user.id,post_id=id, author_comment=current_user.email.split("@")[0], img_url=current_user.img_url)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("view_post", id=id))
    comments = Comment.query.filter_by(post_id=id).all()
    for comment in comments:
        comment.author_comment = User.query.filter_by(id = comment.user_id).first().email
    return render_template("view/post.html", post=post, comments = comments)

@app.route('/like/post/<int:id>', methods=['POST'])
@login_required
def like_post(id):
    post = Post.query.get(id)
    if not post.my_likes:
        current_user.like_post.append(post)
        db.session.commit()
        return redirect(url_for("main_page"))
    current_user.like_post.remove(post)
    db.session.commit()
    return redirect(url_for("main_page"))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("signin"))



if __name__ == "__main__":
    app.run(debug = True)