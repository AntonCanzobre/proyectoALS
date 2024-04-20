import json
import flask
import sirope
import flask_login
import redis
from model.userdto import UserDto
from model.groupdto import GroupDto

def create_app():
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    lmanager = flask_login.login_manager.LoginManager()
    fapp = flask.Flask(__name__)
    syrp = sirope.Sirope(redis_obj=redis_client)

    fapp.config.from_file("config.json", load=json.load)
    lmanager.init_app(fapp)
    return fapp, lmanager, syrp

app, lm, srp = create_app()

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

        user = UserDto.find(srp, email)
        if user:
            if user.chk_password(password):
                print(user)
                
                flask_login.login_user(user_loader(email))
                return flask.redirect("/home")

    return flask.render_template("auth/login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "POST":
        username = flask.request.form.get('username')
        name = flask.request.form.get('name')
        email = flask.request.form.get('email')
        password = flask.request.form.get('password')

        if not (username and name and email and password):
            flask.flash("Todos los campos son obligatorios", "error")
            return flask.redirect('/register')

        if UserDto.exist_username(srp, username=username):
            flask.flash("Ese nombre de usuario ya existe", "error")
            return flask.redirect('/register')

        if UserDto.find(srp, email=email):
            flask.flash("Ese email ya esta en uso", "error")
            return flask.redirect('/register')
        

        user = UserDto(name=name, username=username, email=email, password=password)
        
        user_data = {
            "username" : username,
            "name": name,
            "email": email,
            "password": password,
        }
        
        ooid = srp.save(user)
        print(user)
        print(ooid)


        return flask.redirect('/login')

    return flask.render_template("auth/register.html")

@app.route("/home", methods=["GET"])
@flask_login.login_required
def home():
    user = UserDto.current_user()
    username = ""
    if user:
        username = user.username

    # grupo1 = GroupDto("Grupo 1", "", ["anton", "Persona2", "Persona3"], 100)
    # grupo2 = GroupDto("Grupo 2", "", ["Persona4", "Persona5"], 150)
    # grupo3 = GroupDto("Grupo 3", "", ["Persona6", "Persona7", "anton"], 200)
    
    # srp.save(grupo1)
    # srp.save(grupo2)
    # srp.save(grupo3)

    groups_list = GroupDto.get_all_groups(srp,username=username)

    sust = { 
        "groups_list" : groups_list,
    }

    g = GroupDto.search_group(srp, "Grupo 1", username)
    print(g)

    return flask.render_template("home.html", username=username, **sust)

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user() # Cerrar sesión
    return flask.redirect("/")
