# pip install Flask Flask-SQLAlchemy flask-wtf WTForms-SQLAlchemy flask-login
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, url_for, Response, flash, session
from models import Analytics, Bookmarks, Comments, Followers, Notifications, Posts, Reports, Types, db, News, Users
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, login_required, logout_user, LoginManager, current_user

from webforms import LoginForm, Search, SignUpForm, WriteNewsForm, WritePost

from flask_statistics import Statistics

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

statistics = Statistics(app, db, Analytics)

@app.route("/")
def hello_world():
    signup = SignUpForm()
    signin = LoginForm()
    news = News.query.order_by().all()
    if not current_user.is_anonymous:
        if current_user.username == 'admin':
            return redirect('/Admindashboard')
    return render_template("index.html", signup = signup, signin = signin, news = news)

@app.route('/statistics')
def statistics():
    return redirect('/statistics')

@app.route("/logout/<userid>")
@login_required
def logout(userid):
    user = load_user(userid)
    user.status = False
    db.session.commit()
    message = f"{current_user.username}, You are Logged out!"
    notification = Notifications(notifier_id = current_user.id, activity = message)
    logout_user()
    db.session.add(notification)
    db.session.commit()
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
        
        message = f"{username}, You are Welcome to Telenews!"
        user = Users.query.filter_by(username = username, password = password).first()
        if user:
            notification = Notifications(notifier_id = user.id, activity = message)
            db.session.add(notification)
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
                notification = Notifications(notifier_id = current_user.id, activity = f"{current_user.username} logged in!")
                db.session.add(notification)
                db.session.commit()
                return render_template('AdminDashboard.html')
            else:
                notification = Notifications(notifier_id = current_user.id, activity = f"{current_user.username} logged in!")
                db.session.add(notification)
                db.session.commit()
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

@app.route('/delete_acctount/<user_id>')
def delete_account(user_id):
    user = Users.query.get(user_id)
    message = f"You have deleted user: {user.username}"
    notification = Notifications(notifier_id = current_user.id, activity = message)
    db.session.add(notification)
    db.session.commit()
    db.session.delete(user)
    db.session.commit()
    return redirect('/Accountdetails')

@app.route('/onlinestatus')
def get_online_users():
    print(current_user.is_active)
    users = Users.query.order_by(Users.id.desc()).all()
    return render_template("OnlineStatus.html", users = users)

@app.route('/bookmark/<news_id>')
def bookmark(news_id):
    news = News.query.get(int(news_id))
    if news:
        if not Bookmarks.query.filter_by(news_id = news_id, bookmarker_id = current_user.id).first():
            bookmark = Bookmarks(bookmarker_id = current_user.id, news_id = news_id)
            news = News.query.get(news_id)
            message = f"You bookmarked news: {news.title}"
            link = "go to bookmarks!"
            notification = Notifications(notifier_id = current_user.id, activity = message, link = link)
            db.session.add(bookmark)
            db.session.add(notification)
            
            db.session.commit()            
            flash('news bookmarked!')
        else:
            flash('already bookmarked!')
            print("already bookmarked")
    else:
        flash('news not found!')
    return redirect('/newsSummary')


@app.route('/unbookmark/<bookmark_id>')
def unbookmark(bookmark_id):
    bookmark = Bookmarks.query.get(bookmark_id)
    message = f"You Unbookmarked news: {bookmark.news.title}"
    notification = Notifications(notifier_id = current_user.id, activity = message)
    db.session.delete(bookmark)
    db.session.add(notification)
    db.session.commit()
    return redirect('/list')


@app.route("/list")
def list_news():
    bookmarks = Bookmarks.query.order_by().all()
    return render_template("List.html", bookmarks = bookmarks)


@app.route("/Accountdetails")
@login_required
def Account_details():
    signup = SignUpForm()
    signin = LoginForm()
    users = Users.query.order_by(Users.id.desc()).all()
    return render_template("AccountDetails.html", users = users, signup = signup, signin = signin)


@app.route("/Admindashboard")
def Admin_dashboard():
    return render_template("AdminDashboard.html")


@app.route("/Adminnotification")
def Admin_notification():
    news = News.query.order_by(News.id.desc()).all()
    return render_template("AdminNotification.html", news = news)


@app.route("/articleView")
def article_view():
    return render_template("ArticleView.html")
    # return "<p>Hello, World666666666666!</p>"


@app.route("/editprofile")
def edit_profile():
    return render_template("EditProfile.html")

@app.route('/follow/<user_id>')
def follow(user_id):
    user = Users.query.filter_by(id = user_id).first()
    follow_to = user.id
    follow_by = current_user.id
    follow = Followers(follow_by = follow_by, follow_to = follow_to)
    message = f'You start following {user.username}'
    notification = Notifications(notifier_id = current_user.id, activity = message)
    db.session.add(follow)
    db.session.add(notification)
    db.session.commit()
    return redirect("/followerlist")

@app.route('/unfollow/<user_id>')
def unfollow(user_id):
    follow = Followers.query.filter_by(follow_by = current_user.id, follow_to = user_id).first()
    db.session.delete(follow)
    db.session.commit()
    return redirect('/followerlist')
    

@app.route("/followerlist")
def follower_list():
    users = Users.query.filter_by(role = 'journalist').all()
    followers = Followers.query.filter_by(follow_by = current_user.id).all()
    follow_users = []
    following_users = []
    if followers:
        for follow in followers:
            following_users.append(Users.query.filter_by(id = follow.follow_to).first())
        for user in users:
            if user not in following_users:
                follow_users.append(user)
        print(following_users)
    else:
        follow_users = users
    print(follow_users, following_users)
    return render_template("FollowerList.html", follow = follow_users, following = following_users)

@app.route("/generalistNews")
def generalist_news():
    return render_template("GeneralistNews.html")


@app.route("/newsSummary", methods = ['GET', 'POST'])
def news_summary():
    form = Search()
    if form.validate_on_submit():
        searched = request.form['search']
        news = News.query.filter(News.title.like('%' + searched + '%'))
    else:
        news = News.query.order_by(News.id.desc()).all()
    comments = Comments.query.order_by(Comments.id.desc()).all()
    # comments = Comments.query.order_by(Comments.timestamp.desc()).all()
    return render_template("NewsSummary.html", news=news, comments = comments, form = form)

@app.route("/add_comment/<news_id>", methods=['GET', 'POST'])
def add_comment(news_id):
    type = Types.query.filter_by(name = "comment").first()
    description = request.form['comment_area']
    post = Posts(poster_id = current_user.id, type_id = type.id, description = description)
    db.session.add(post)
    db.session.commit()
    
    post = Posts.query.filter_by(poster_id = current_user.id, type_id = type.id).all()
    post = post[len(post)-1]
    news = News.query.filter_by(id = news_id).first()
    comment = Comments(post_id = post.id, news_id = news.id)   

    message = f"{current_user.username}, you just commented on {news.article.poster.username}'s news"
    notification = Notifications(notifier_id = current_user.id, activity = message)

    db.session.add(comment)
    db.session.add(notification)

    db.session.commit()
    return redirect('/newsSummary')

@app.route('/delete_comment/<post_id>')
def delete_comment(post_id):
    post = Posts.query.filter_by(id = post_id).first()
    comment = Comments.query.filter_by(comment_post = post).first()
    message = f'Your comment on post {comment.commented_news.title} deleted!'
    notification = Notifications(notifier_id = post.poster.id, activity = message)
    
    db.session.delete(post)
    db.session.add(notification)
    db.session.commit()
    return redirect('/newsSummary')

@app.route('/delete_news/<post_id>')
def delete_news(post_id):
    print(post_id)
    post = Posts.query.filter_by(id = post_id).first()
    news = News.query.filter_by(article = post).first()
    message = f'Your news {news.title} deleted!'
    print(news.title)
    notifications = Notifications(notifier_id = post.poster.id, activity = message)

    db.session.delete(post)
    db.session.add(notifications)
    db.session.commit()
    return redirect('/Adminnotification')

@app.route('/report_comment/<comment_id>')
def report_comment(comment_id):
    comment = Comments.query.filter_by(id = comment_id).first()
    report = Reports(reporter_id = current_user.id, post_id = comment.comment_post.id, reason = "None")
    message = f'Your comment on post {comment.commented_news.title} is reported!'
    notification = Notifications(notifier_id = current_user.id, activity = message)
    
    db.session.add(report)
    db.session.add(notification)
    db.session.commit()
    return redirect('/newsSummary')

# @app.route("/comment/<int:news_id>/", methods=["GET", 'POST'])
# def add_comment_reply(news_id, refer=True):
#     parent_id = request.args.get('parent_id')
#     if request.method == 'POST':
#         reply = Comments(
#             news_id=news_id, parent_id=parent_id, text=request.form['comment_area'])

#         db.session.add(reply)
#         db.session.commit()
#         if refer:
#             return redirect(url_for('summary_view', news_id=news_id))
#         else:
#             return redirect(request.referrer)
#         # flash("Your comment has been added. Welcome!")
#     return render_template('AddReplyToPost.html', parent_id=parent_id, news_id=news_id)


# @app.route("/comment/<int:news_id>/", methods=["GET", 'POST'])
# def add_comment(news_id):
#     if request.method == 'POST':
#         reply = Comments(

#             news_id=news_id, text=request.form['comment_area'])

#         db.session.add(reply)
#         db.session.commit()
#         # flash("Your comment has been added. Welcome!")
#     print(request.referrer, 'G')
#     return redirect(request.referrer)

#     # return render_template("news/add_comments.html", news_id=news_id, parent_id=parent_id)


# @app.route("/comment/delete/<int:comment_id>/", methods=["GET"])
# def delete_comment(comment_id):
#     reply = Comments.query.get(comment_id)
#     db.session.delete(reply)
#     db.session.commit()
#     # flash("Your comment has been added. Welcome!")
#     return redirect(request.referrer)


@app.route("/news/delete/<int:news_id>/", methods=["GET"])
def delete_post(news_id):
    news = News.query.get(news_id)
    post = news.article
    message = f'Your news article is deleted'
    notification = Notifications(notifier_id = current_user.id, activity = message)
    db.session.delete(post)
    db.session.commit()
    # flash("Your comment has been added. Welcome!")
    return redirect(url_for('news_summary'))


@app.route("/notifications")
def full_notifications():
    notifications = Notifications.query.filter_by(notifier_id = current_user.id).all()
    notifications.reverse()
    return render_template("Notifications.html", notifications = notifications)


@app.route("/reportedComments")
def reported_comments():
    reports = Reports.query.order_by(Reports.id.desc()).all()
    reported_comments = []
    for report in reports:
        if report.post.type.name == 'comment':
            reported_comments.append(report)
    return render_template("ReportedComments.html", comments = reported_comments, edit = False)


@app.route("/reportednews")
def reported_news():
    reports = Reports.query.order_by(Reports.id.desc()).all()
    reported_news = []
    for report in reports:
        if report.post.type.name == 'news':
            reported_news.append(report)
    return render_template("ReportedNews.html", news = reported_news)


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

@app.route('/news/<int:id>')
def get_news_img(id):
    news = News.query.filter_by(id=id).first()
    if not news:
        return 'Img Not Found!', 404

    return Response(news.image, mimetype=news.mimetype)

@app.route("/summaryview/<int:news_id>")
def summary_view(news_id):
    news = News.query.get(news_id)
    comments = Comments.query.filter_by(commented_news=news)
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
