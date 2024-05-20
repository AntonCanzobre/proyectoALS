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

        if not (name_group and description_group and list_participants):
            flask.flash("Todos los campos son obligatorios", "errorGroup")
            return flask.redirect('/group/add')
        
        


        group = GroupDto(name_group,description_group, list_participants, [])
        ooid = srp.save(group)

        return flask.redirect('/')

@flask_login.login_required
@group_blpr.route("/edit/<name>", methods=["POST", "GET"])
def edit_group(name):
    if flask.request.method == "GET":
        group = GroupDto.search_by_url(srp, name)

        sust= {
            "url": name,
            "group": group
        }
        return flask.render_template("editGroup.html", **sust)

    if flask.request.method == "POST":
        name_group = flask.request.form.get("name-group")
        description_group = flask.request.form.get("description-group")
        list_participants = flask.request.form.getlist("participants[]")
        

        if not (name_group and description_group and list_participants):
            flask.flash("Todos los campos son obligatorios", "errorGroup")
            return flask.redirect('/group/edit/' + name)
        
        group_edit = GroupDto.search_by_url(srp,name)

        group_edit.edit_group(srp, name_group, description_group, list_participants)

        return flask.redirect("/group/view/"+name)

@flask_login.login_required
@group_blpr.route("/delete/<name>", methods=["POST","GET"])
def delete_group(name):
    if flask.request.method == "GET":
        user = UserDto.current_user()
        username = ""
        if user:
            username = user.username

        groups_list, urls_groups = GroupDto.get_all_groups(srp,username=username)
        
        sust = { 
            "url": name,
            "username":username,
            "groups_list" : groups_list,
            "srp":srp,
            "urls_groups" : urls_groups
        }
        
        return flask.render_template("deleteGroup.html", **sust)
    
    if flask.request.method == "POST":
        srp.delete(srp.oid_from_safe(name))
        
        return flask.redirect("/home")


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
    group = GroupDto.search_by_url(srp,name)
    debts = group.equitable_payment_distribution(srp)

    print("valores de las deudas")
    print(debts)

    sust = {
        "url":name,
        "group":group,
        "expenses":group.get_array_expenses(srp),
        "debts": debts
    }
    
    return flask.render_template("viewGroup.html", **sust)


@flask_login.login_required
@group_blpr.route("/view/<name>/expense/add", methods=["GET", "POST"])
def add_expense(name):

    
    user = UserDto.current_user()
    group = GroupDto.search_by_url(srp,name)
    debts = group.equitable_payment_distribution(srp)

    
    print(group)
    if flask.request.method == "GET":

        expense = ExpensesDto("",0,"")
        sust = {
            "user":user,
            "url":name,
            "group":group,
            "expense":expense,
            "debts": debts

        }
        if flask.request.method == "GET":
            
            return flask.render_template("addExpense.html", **sust)
    
    if flask.request.method == "POST":
        sust = {
            "url":name,
            "group":group

        }

        name_expense = flask.request.form.get("name-expense")
        amount_expense = flask.request.form.get("amount-expense")
        user_expense = flask.request.form.get("user-expense")

        if not (name_expense and amount_expense and user_expense):
            flask.flash("Todos los datos son obligatorios", "errorExpense")
            return flask.redirect("/group/view/"+name+"/expense/add")
        
        if int(amount_expense) < 0:
            flask.flash("La cantidad no puede ser negativa", "errorAmount")
            return flask.redirect("/group/view/"+name+"/expense/add")

        user_exists = UserDto.find_username(s=srp, username=user_expense) 
        print(user_exists)
        if user_exists:
            if group.contains_user(username=user_expense):
                expense = ExpensesDto(name_expense,amount_expense, user_expense)
                group.add_expense(srp, expense)
                ooid = srp.save(group)

                return flask.redirect("/group/view/" + name)
            
        


@flask_login.login_required
@group_blpr.route("/view/<name>/expense/delete/<expense>", methods=["POST"])
def delete_expense(name, expense):
    group = GroupDto.search_by_url(srp, name)
    expense = group.search_expense(srp, expense)
    if expense:
        ooid = ExpensesDto.get_ooid(srp, expense)
        group.delete_expense(srp,ooid)
    
        return flask.redirect("/group/view/" + name)



        




        

