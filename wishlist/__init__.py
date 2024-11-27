import flask
import logging
from sqlalchemy import orm
from sqlalchemy import Column, String, Integer, BigInteger, create_engine


app = flask.Flask("wishlist", template_folder="templates")


@app.template_filter()
def render_html(markup: str) -> str:
    import re

    # Регулярное выражение для поиска ссылок вида http(s)://...
    pattern = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'

    def make_link(match):
        link = match.group(0)
        return f'<a href="{link}" target="_blank">{link}</a>'

    # Применяем регулярное выражение к строке и заменяем найденные ссылки
    result = re.sub(pattern, make_link, markup)

    # Возвращаем результат в виде безопасного HTML-кода
    return result
    

Base = orm.declarative_base()
class Wish(Base):
    __tablename__ = "wish"
    id = Column(Integer, primary_key=True, autoincrement=True)

    text = Column(String(2048), nullable=False)
    owner_id = Column(BigInteger, nullable=False)
    taken_id = Column(BigInteger, nullable=True)

    def __str__(self):
        return str({k: getattr(self, k) for k in self.__table__.columns.keys()})

    def __repr__(self):
        return str({k: getattr(self, k) for k in self.__table__.columns.keys()})


class User(Base):
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    bio = Column(String(1000), nullable=True)



@app.before_request
def before_request():
    flask.session.permanent = True
    logging.info("Request: %s %s", flask.request.method, flask.request.url)


@app.route("/login")
def login():
    user_id = flask.request.args.get("id")
    first_name = flask.request.args.get("first_name")
    photo_url = flask.request.args.get("photo_url")

    logging.info("Login: %s %s %s", user_id, first_name, photo_url)

    flask.session['user_id'] = int(user_id)
    flask.session['name'] = first_name
    flask.session['photo'] = photo_url

    return flask.redirect(f'/{user_id}')


@app.route("/logout")
def logout():
    flask.session.pop("user_id")
    flask.session.pop("name")
    flask.session.pop("photo")

    return flask.redirect('/')


@app.route("/<id>")
@app.route("/index")
@app.route("/")
def index(id: int = None):
    if id == "favicon.ico":
        flask.abort(404)

    env = dict(**flask.session, bio="")
    env["user_id"] = int(env.get("user_id", 0))
    user = session.query(User).get(id or env["user_id"])
    logging.info("user: %s", user)
    if user is not None:
        env["bio"] = (user.bio or "").strip()
    logging.info("Index/session: %s", env)

    if "user_id" in env and id is None:
        id = env["user_id"]

    env["id"] = int(id)

    if id is not None:
        wishlist = session.query(Wish).filter_by(owner_id=id)
        env["wishlist"] = wishlist.order_by(Wish.id.asc()).all()

    return flask.render_template("index.jinja2", env=env)


@app.route("/bio", methods=["POST"])
def bio():
    env = dict(**flask.session)
    logging.info("Bio/session: %s", env)

    bio = flask.request.form.get("bio")
    if bio is not None:
        user = session.query(User).get(int(env["user_id"]))
        logging.info("user: %s", user)
        if user is None:
            session.add(User(id=int(env["user_id"]), bio=bio))
        else:
            user.bio = bio
        session.commit()

    return flask.redirect(f"/{env['user_id']}")


@app.route("/wish/<id>", methods=["POST"])
@app.route("/wish", methods=["POST"])
def wish(id: int = None):
    env = dict(**flask.session)
    from_id = flask.request.referrer.split("/")[-1]
    logging.info("Wish/session: %s from %s", env, from_id)

    if id is None:
        session.add(wish:=Wish(
            text = flask.request.form.get("text"),
            owner_id = int(env["user_id"]),
        ))
        logging.info("Commiting wish %s", wish)
        session.commit()
        return flask.redirect(f'/{from_id}')
    
    wish: Wish = session.query(Wish).get(id)

    if wish.taken_id is not None and int(env["user_id"]) == wish.owner_id:
        session.delete(wish)

    elif int(env["user_id"]) == wish.owner_id:
        txt = flask.request.form.get("text", wish.text)
        if txt == "":
            session.delete(wish)
        else:
            wish.text = txt

    elif int(env["user_id"]) != wish.owner_id:
        if wish.taken_id == int(env["user_id"]):
            wish.taken_id = None
        else:
            wish.taken_id = int(env["user_id"])

    session.commit()

    return flask.redirect(f'/{from_id}')


def init():
    global session

    logging.basicConfig(format="%(asctime)s %(message)s")
    logging.getLogger().setLevel(0)

    app.config['SECRET_KEY'] = "YOUWILLNEVERGUESSTHIS"

    app.jinja_env.globals.update(int=int)
    app.jinja_env.globals.update(BOTID="7290461904")
    app.jinja_env.globals.update(BOTNAME="wish4wish_bot")
    app.jinja_env.globals.update(BOTDOMAIN="wishlist.vesnin.site")


    db = create_engine("postgresql://postgres:postgres@postgres/wishlist")
    Base.metadata.create_all(db)
    Session = orm.sessionmaker(db)
    session = Session()