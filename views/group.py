import flask
import sirope
import flask_login

from model.Userdto import UserDto
from model.Groupdto import GroupDto
from model.Expensesdto import ExpensesDto

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
    
    if new_participant_username in list_participants:
        return flask.jsonify({'message': 'El usuario ya esta en la lista.'}), 400
        
    user_exists = UserDto.find_username(s=srp, username=new_participant_username) 

    if user_exists:
        list_participants.append(user_exists.username)

        data = {"participant": user_exists.username, 
                "people":list_participants} 
        return flask.jsonify(data), 200
    else:
        return flask.jsonify({'message': 'El usuario no existe en la base de datos.'}), 400


@flask_login.login_required
@group_blpr.route("/view/<name>", methods=["GET"])
def group_view(name):
    user = UserDto.current_user()
    group = GroupDto.search_group(s=srp, name=name, username=user.username)

    

    sust = {
        "group":group,
        "expenses":group.get_array_expenses(srp)
    }
    
    return flask.render_template("viewGroup.html", **sust)


@flask_login.login_required
@group_blpr.route("/view/<name>/expense/add", methods=["GET", "POST"])
def add_expense(name):

    
    user = UserDto.current_user();
    group = GroupDto.search_group(s=srp, name=name, username=user.username)
    print(group)
    if flask.request.method == "GET":

        expense = ExpensesDto("","",0,"")
        sust = {
            "group":group,
            "expense":expense
        }
        if flask.request.method == "GET":
            
            return flask.render_template("addExpense.html", **sust)
    
    if flask.request.method == "POST":
        sust = {
            "group":group
        }

        name_expense = flask.request.form.get("name-expense")
        amount_expense = flask.request.form.get("amount-expense")
        user_expense = flask.request.form.get("user-expense")

        user_exists = UserDto.find_username(s=srp, username=user_expense) 
        print(user_exists)
        if user_exists:
            if group.contains_user(username=user_expense):
                expense = ExpensesDto(len(group.expenses), name_expense,amount_expense, user_expense)
                group.add_expense(srp, expense)
                ooid = srp.save(group)
                print(ooid)

                return flask.redirect("/group/view/" + group.name)
            return "terrible"
        return user_expense


