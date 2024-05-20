import json
import flask
import sirope
import flask_login
import redis

from model.Userdto import UserDto
from model.Groupdto import GroupDto

from views.group import group_blpr

def create_app():
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    lmanager = flask_login.login_manager.LoginManager()
    fapp = flask.Flask(__name__)
    syrp = sirope.Sirope(redis_obj=redis_client)

    fapp.config.from_file("instance/config.json", load=json.load)
    lmanager.init_app(fapp)
    fapp.register_blueprint(group_blpr)

    return fapp, lmanager, syrp

app, lm, srp = create_app()

@app.context_processor
def utility_processor():
    return dict(zip=zip)

@lm.user_loader
def user_loader(email):
    return UserDto.find(srp, email)

@lm.unauthorized_handler
def unauthorized_handler():
    flask.flash("Unauthorized")
    return flask.redirect("/")

@app.route('/')
def get_index():
    
    return flask.redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if UserDto.current_user():
        return flask.redirect("/home")
    if flask.request.method == "POST":
        email = flask.request.form.get("email")
        password = flask.request.form.get("password")

        if not (email and password):
            flask.flash("Todos los campos son obligatorios", "errorAuth")
            return flask.redirect('/login')

        user = UserDto.find(srp, email)
        if user:
            if user.chk_password(password):
                print(user)
                
                flask_login.login_user(user_loader(email))
                return flask.redirect("/home")
        else:
            flask.flash("Ese email no existe en el sistema", "errorEmail")
    return flask.render_template("auth/login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "POST":
        username = flask.request.form.get('username')
        name = flask.request.form.get('name')
        email = flask.request.form.get('email')
        password = flask.request.form.get('password')

        if not (username and name and email and password):
            flask.flash("Todos los campos son obligatorios", "errorAuth")
            return flask.redirect('/register')

        if UserDto.exist_username(srp, username=username):
            flask.flash("Ese nombre de usuario ya existe", "errorUsername")
            return flask.redirect('/register')

        if UserDto.find(srp, email=email):
            flask.flash("Ese email ya esta en uso", "errorEmail")
            return flask.redirect('/register')
        

        user = UserDto(name=name, username=username, email=email, password=password)
        
        user_data = {
            "username" : username,
            "name": name,
            "email": email,
            "password": password,
        }
        
        ooid = srp.save(user)


        return flask.redirect('/login')

    return flask.render_template("auth/register.html")

@app.route("/home", methods=["GET"])
@flask_login.login_required
def home():
    user = UserDto.current_user()
    username = ""
    if user:
        username = user.username

    groups_list, urls_groups = GroupDto.get_all_groups(srp,username=username)
    
    sust = { 
        "username":username,
        "groups_list" : groups_list,
        "srp":srp,
        "urls_groups" : urls_groups
    }

    

    return flask.render_template("home.html", **sust)

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user() # Cerrar sesión
    return flask.redirect("/")
