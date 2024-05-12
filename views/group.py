import flask
import sirope
import flask_login

from model.Userdto import UserDto
from model.Groupdto import GroupDto

def get_blprint():
    group_module = flask.blueprints.Blueprint("group_blpr", __name__,
                                    url_prefix="/group",
                                    template_folder="templates/group",
                                    static_folder="static/group")
    syrp = sirope.Sirope()
    return group_module, syrp

group_blpr, srp = get_blprint()

@flask_login.login_required
@group_blpr.route("/add", methods=["GET", "POST"])
def group_add():
    if flask.request.method == "GET":
        user = UserDto.current_user()
        group = GroupDto("", "", [user.username], [])

        sust = {
            "usr": user,
            "group": group
        }
        return flask.render_template("crearGroup.html", **sust)
    elif flask.request.method == 'POST':
        name_group = flask.request.form.get("name-group")
        description_group = flask.request.form.get("description-group")
        list_participants = flask.request.form.getlist("participants[]")
        print (list_participants)

        if not (name_group and description_group and list_participants):
            flask.flash("Todos los campos son obligatorios", "error")
            return flask.redirect('/group/add')


        group = GroupDto(name_group,description_group, list_participants, [])
        ooid = srp.save(group)
        print(ooid)
        print(group)

        return flask.redirect('/')




@flask_login.login_required
@group_blpr.route("/search", methods=["POST"])
def group_search():
    new_participant_username = flask.request.json.get('newParticipant')
    list_participants = flask.request.json.get('participants')
    print(list_participants)
    
    if new_participant_username in list_participants:
        return flask.jsonify({'message': 'El usuario ya esta en la lista.'}), 400
        
    user_exists = UserDto.find_username(s=srp, username=new_participant_username)  # Asume que 'srp' está definido

    if user_exists:
        list_participants.append(user_exists.username)
        print(list_participants)

        data = {"participant": user_exists.username, 
                "participants":list_participants} 
        return flask.jsonify(data), 200
    else:
        return flask.jsonify({'message': 'El usuario no existe en la base de datos.'}), 400


