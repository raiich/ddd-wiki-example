from flask import Flask, redirect, request, session

from mywiki.application.edit import ArticleEditService
from mywiki.application.view import ArticleViewService
from mywiki.domain.model.user.authentication import AuthenticationService
from mywiki.domain.model.user.identification import anonymous
from mywiki.domain.model.view.article import Article
from mywiki.infrastructure.flask import SessionUserIdentificationService

app = Flask(__name__)
app.secret_key = 'keep this really secret'

identification_service: SessionUserIdentificationService
authenticator: AuthenticationService

edit_service: ArticleEditService
view_service: ArticleViewService


@app.route('/')
def index():
    header_html = """<h3>Articles</h3>"""
    user = identification_service.identify(session)
    articles = view_service.get_article_list(user)

    if articles:
        def elem(article: Article):
            return """<li><a href="/articles/{article_id}">{location}</a></li>""".format(
                article_id=article.id, location=location(article))

        body_html = "\n".join(map(lambda a: elem(a), articles))
        body_html = """
        <ul>
        {content}
        </ul>
        """.format(content=body_html)
    else:
        body_html = "<p>no article available</p>"

    if user == anonymous:
        menu_html = """
        <a href="/login">Login</a>
        """
    else:
        menu_html = """
        <a href="/logout">Logout : {username}</a>
        """.format(username=user.username)

    menu_html += """ / <a href="new">Create New Article</a>"""
    return header_html + body_html + "<hr />" + menu_html


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = authenticator.authenticate(request.form['username'], request.form['password'])
        session['user_id'] = user_id
        return redirect('/')
    return """
    <form method="post">
        <p>username: <input type="text" name="username" value="admin" /></p>
        <p>password: <input type="password" name="password" value="dragon" /> ← `dragon` </p>
        <p><input type="submit" value="Login" /></p>
    </form>
    """


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


@app.route('/new', methods=['GET', 'POST'])
def new_article():
    user = identification_service.identify(session)
    if request.method == 'POST':
        content = request.form['content']
        split = request.form['location'].rsplit('/', 1)
        assert len(split) <= 2
        if len(split) == 1:
            category, title = "", split[0]
        else:
            category, title = split
        edit_service.create(user, category, title, content)
        return redirect("/")
    return editor_ui()


@app.route('/articles/<article_id>')
def show_article_latest(article_id):
    user = identification_service.identify(session)
    article = view_service.view(user, article_id)
    return show_article_ui(article)


@app.route('/articles/<article_id>/<revision>/edit')
def edit_article(article_id, revision):
    user = identification_service.identify(session)
    source = edit_service.read(user, article_id, int(revision))
    action = '/articles/{article_id}/{revision}'.format(article_id=article_id, revision=revision)
    return editor_ui(action=action, source=source)


@app.route('/articles/<article_id>/<revision>', methods=['GET', 'POST'])
def show_article_revision(article_id, revision):
    user = identification_service.identify(session)
    if request.method == 'POST':
        content = request.form['content']
        split = request.form['location'].rsplit('/', 1)
        assert len(split) <= 2
        if len(split) == 1:
            category, title = "", split[0]
        else:
            category, title = split
        edit_service.update(user, article_id, category, title, content, int(revision))
        return redirect("/")
    article = view_service.view(user, article_id, int(revision))
    return show_article_ui(article)


@app.route('/articles/<article_id>/<revision>/discard')
def discard_article(article_id, revision):
    user = identification_service.identify(session)
    edit_service.delete(user, article_id, int(revision))
    return redirect('/')


def location(article: Article) -> str:
    if article:
        return article.category + "/" + article.title if article.category else article.title


def editor_ui(action="", source=None):
    loc, content = (location(source), source.content) if source else ("top/README", "# README \n- TODO")
    return """
    <form method="post" action="{action}">
        <p>Category/Title: <input type="text" name="location" size="70" value="{location}"/></p>
        <p><textarea name="content" cols="80" rows="10">{content}</textarea></p>
        <p><input type="submit" value="Save Article" /></p>
    </form>
    """.format(action=action, location=loc, content=content)


def show_article_ui(article: Article):
    return """
    <h3>Category/Title: {location}</h3>
    <hr />
    {content}
    <hr />
    <a href="/articles/{article_id}/{revision}/edit">edit</a>
    / <a href="/articles/{article_id}/{revision}/discard">discard</a>
    """.format(article_id=article.id, location=location(article), content=article.html, revision=article.revision)


def run():
    app.run(debug=True)
