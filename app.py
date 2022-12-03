# pip install Flask Flask-SQLAlchemy flask-wtf WTForms-SQLAlchemy flask-login
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, url_for, Response, flash, session
from models import Bookmarks, Posts, Types, db, News, Users
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, login_required, logout_user, LoginManager, current_user

from webforms import LoginForm, SignUpForm, WriteNewsForm

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'any secret string'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'my_db.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_DOMAIN'] = False
app.config['WTF_CSRF_ENABLED'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_SECURE'] = False

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return Users.query.get(int(user_id))


with app.app_context():
    db.create_all()
    # types = [Types(name = "news"), Types(name = "comment"), Types(name = "reply")]
    # for type in types:
    #     db.session.add(type)
    # db.session.commit()

csrf = CSRFProtect()
csrf.init_app(app)


@app.route("/")
def hello_world():
    signup = SignUpForm()
    signin = LoginForm()
    return render_template("index.html", signup = signup, signin = signin)


@app.route("/logout/<userid>")
@login_required
def logout(userid):
    user = load_user(userid)
    user.status = False
    db.session.commit()
    logout_user()
    users = Users.query.order_by().all()
    for user in users:
        print(user.is_active)
        print(current_user.is_active)
    signin = LoginForm()
    signup = SignUpForm()
    return render_template("index.html",  signin = signin, signup = signup)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    signup = SignUpForm()
    signin = LoginForm()
    if signup.validate_on_submit():
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        # role = 'admin'
        password = request.form['password']
        profile = request.files['profile']
        image_data = profile.read()
        mimetype = profile.mimetype
        status = False

        user = Users(username = username, email = email, role = role, password = password, profile_pic = image_data, mimetype = mimetype, status = status)
        db.session.add(user)
        db.session.commit()
    return render_template("index.html", signup = signup, signin = signin)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    signin = LoginForm()
    signup = SignUpForm()
    print(request.form['submit'])
    if signin.validate_on_submit():
        user = Users.query.filter_by(username = request.form['username'], password = request.form['password']).first()
        if user:
            login_user(user)
            user.status = True
            db.session.commit()
            session['username'] = user.username
            flash('You are loged in')
            if current_user.role == 'admin':
                return render_template('AdminDashboard.html')
            else:
                return render_template('Notifications.html')
        else:
            flash('You are loged in')
            return render_template('index.html', signin = signin, signup = signup)
    else:
        return render_template('index.html', signin = signin, signup = signup)

@app.route('/<int:id>')
def get_profile(id):
    user = Users.query.filter_by(id=id).first()
    if not user:
        return 'Img Not Found!', 404

    return Response(user.profile_pic, mimetype=user.mimetype)

@app.route('/onlinestatus')
def get_online_users():
    print(current_user.is_active)
    # print(session["username"])
    users = Users.query.order_by().all()
    return render_template("OnlineStatus.html", users = users)

@app.route('/bookmark/<news_id>')
def bookmark(news_id):
    news = News.query.get(int(news_id))
    if news:
        bookmark = Bookmarks(bookmarker_id = current_user.id, news_id = news_id)
        db.session.add(bookmark)
        db.session.commit()
        flash('news bookmarked!')
    else:
        flash('news not found!')
    return redirect('/newsSummary')


@app.route("/Accountdetails")
@login_required
def Account_details():
    return render_template("AccountDetails.html")


@app.route("/Admindashboard")
def Admin_dashboard():
    return render_template("AdminDashboard.html")


@app.route("/Adminnotification")
def Admin_notification():
    return render_template("AdminNotification.html")


@app.route("/articleView")
def article_view():
    return render_template("ArticleView.html")
    # return "<p>Hello, World666666666666!</p>"


@app.route("/editprofile")
def edit_profile():
    return render_template("EditProfile.html")


@app.route("/followerlist")
def follower_list():
    return render_template("FollowerList.html")


@app.route("/generalistNews")
def generalist_news():
    return render_template("GeneralistNews.html")


@app.route("/list")
def list_news():
    return render_template("List.html")


@app.route("/newsSummary")
def news_summary():
    news = News.query.order_by(News.id.desc()).all()
    # comments = Comments.query.order_by(Comments.timestamp.desc()).all()
    return render_template("NewsSummary.html", news=news)


@app.route("/comment/<int:news_id>/", methods=["GET", 'POST'])
def add_comment_reply(news_id, refer=True):
    parent_id = request.args.get('parent_id')
    if request.method == 'POST':
        reply = Comments(
            news_id=news_id, parent_id=parent_id, text=request.form['comment_area'])

        db.session.add(reply)
        db.session.commit()
        if refer:
            return redirect(url_for('summary_view', news_id=news_id))
        else:
            return redirect(request.referrer)
        # flash("Your comment has been added. Welcome!")
    return render_template('AddReplyToPost.html', parent_id=parent_id, news_id=news_id)


@app.route("/comment/<int:news_id>/", methods=["GET", 'POST'])
def add_comment(news_id):
    if request.method == 'POST':
        reply = Comments(

            news_id=news_id, text=request.form['comment_area'])

        db.session.add(reply)
        db.session.commit()
        # flash("Your comment has been added. Welcome!")
    print(request.referrer, 'G')
    return redirect(request.referrer)

    # return render_template("news/add_comments.html", news_id=news_id, parent_id=parent_id)


@app.route("/comment/delete/<int:comment_id>/", methods=["GET"])
def delete_comment(comment_id):
    reply = Comments.query.get(comment_id)
    db.session.delete(reply)
    db.session.commit()
    # flash("Your comment has been added. Welcome!")
    return redirect(request.referrer)


@app.route("/news/delete/<int:news_id>/", methods=["GET"])
def delete_post(news_id):
    reply = News.query.get(news_id)
    db.session.delete(reply)
    db.session.commit()
    # flash("Your comment has been added. Welcome!")
    return redirect(url_for('news_summary'))


@app.route("/notifications")
def full_notifications():
    return render_template("Notifications.html")


# @app.route("/onlinestatus")
# def online_status():
#     return render_template("OnlineStatus.html")


@app.route("/reportedComments")
def reported_comments():
    return render_template("ReportedComments.html")


@app.route("/reportednews")
def reported_news():
    return render_template("ReportedNews.html")


@app.route("/reportedcommmetsAdmin")
def reported_commnets_admin():
    comments = Comments.query.filter_by(report=1)
    return render_template("ReportedCommentsAdmin.html", comments=comments)


@app.route("/comment/report/<int:comment_id>")
def add_report_comment(comment_id):
    comment = Comments.query.get(comment_id)
    comment.report = 1
    db.session.commit()
    return redirect(request.referrer)


@app.route("/summaryview/<int:news_id>")
def summary_view(news_id):
    news = News.query.get(news_id)

    comments = Comments.query.filter_by(news_id=news_id)
    return render_template("SummaryView.html", news=news, comments=comments)


@app.route("/writenews", methods=['GET', 'POST'])
def write_news():
    write_news_form = WriteNewsForm()
    post = Posts.query.order_by().all()
    last_post = post[len(post)-1]
    print(last_post.id)

    if request.method == 'POST':
        description = request.form['description']
        poster_id = current_user.id
        type = Types.query.filter_by(name = "news").first()
        type_id = type.id

        image = request.files['image']
        image_data = image.read()
        mimetype = image.mimetype
        title = request.form['title']

        post = Posts(poster_id = current_user.id, type_id = type_id, description = description)
        db.session.add(post)
        db.session.commit()

        post = Posts.query.order_by().all()
        last_post = post[len(post)-1]

        news = News(post_id = last_post.id, title = title, category_id = 1, image = image_data, mimetype = mimetype)
        db.session.add(news)
        db.session.commit()
        
        flash("Your News is Successfully Published")
        return redirect("/writenews")
    return render_template("WriteNews.html", news_form = write_news_form)


@app.route("/yournewsarticles")
def yournews_articles():
    return render_template("YourNewsArticles.html")


if __name__ == '__main__':
    app.run(debug=True, port=8000)
