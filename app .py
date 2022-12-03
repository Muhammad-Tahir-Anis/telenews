# pip install Flask Flask-SQLAlchemy flask-wtf WTForms-SQLAlchemy flask-login
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, url_for, Response, flash
from models import db, News, Users
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, login_required, logout_user, LoginManager, current_user

from webforms import LoginForm, SignUpForm

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

csrf = CSRFProtect()
csrf.init_app(app)



@app.route("/")
def hello_world():
    signup = SignUpForm()
    signin = LoginForm()
    return render_template("index.html", signup = signup, signin = signin)


@app.route("/logout")
@login_required
def logout():
    logout_user()
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
        password = request.form['password']
        profile = request.files['profile']
        image_data = profile.read()
        mimetype = profile.mimetype

        user = Users(username = username, email = email, role = role, password = password, profile_pic = image_data, mimetype = mimetype)
        db.session.add(user)
        db.session.commit()
    return render_template("index.html", signup = signup, signin = signin)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    signin = LoginForm()
    signup = SignUpForm()
    print(request.form['submit'])
    user = Users.query.filter_by(username = request.form['username'], password = request.form['password']).first()
    if user:
        login_user(user)
        flash('You are loged in')
        return render_template('Notifications.html')
    else:
        flash('You are loged in')
        return render_template('index.html', signin = signin, signup = signup)

# @app.route("/authenticateUser", methods=['POST'])  # type: ignore
# def authenticate_user():
#     if request.method == 'POST':
#         form_type = request.args.get('form_type')
#         username = request.form['username']
#         password = request.form['password']
#         # users = Users.query.order_by(Users.id.desc()).all()

#         if form_type == 'signin':
#             user = Users.query.filter_by(username=username, password=password).first()
#             print("ayesha", user.username)
#             image = f"/{user.id}"
#             # user.role = "admin"
#             if user is not None:
#                 login_user(user)
#                 if user.role == "admin":
#                     return render_template("AdminDashboard.html")
#                 elif user.role == "journalist":
#                     return render_template("GeneralistNews.html", user = user.username, image = image )
#                 else:
#                     return redirect(url_for('hello_world'))
#         else:
#             # .registration work
#             role = request.form.get('QGEWGewg')
#             pic = request.files['pic']
#             data = pic.read()
#             mimetype = pic.mimetype
#             print(pic.filename)
#             user_obj = Users(username=username, password=password, role=role, profile_pic = data, mimetype = mimetype)
#             db.session.add(user_obj)
#             db.session.commit()

#         return redirect(url_for('hello_world'))


# @app.route('/<int:id>')
# def get_img(id):
#     # img = Img.query.filter_by(id=id).first()
#     if not img:
#         return 'Img Not Found!', 404

#     return Response(img.img, mimetype=img.mimetype)


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
    news = News.query.order_by(News.created_at.desc()).all()
    comments = Comments.query.order_by(Comments.timestamp.desc()).all()
    return render_template("NewsSummary.html", news=news, comments=comments)


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


@app.route("/onlinestatus")
def online_status():
    return render_template("OnlineStatus.html")


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
    print(request.method, 'ash', request.form)
    if request.method == 'POST':
        news_obj = News(title=request.form['news_title'], detail=request.form['news_desc'])
        db.session.add(news_obj)
        db.session.commit()
        return redirect(url_for('news_summary'))
    return render_template("WriteNews.html")


@app.route("/yournewsarticles")
def yournews_articles():
    return render_template("YourNewsArticles.html")


if __name__ == '__main__':
    app.run(debug=True, port=8000)
