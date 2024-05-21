import sirope
from collections import defaultdict
from model.Expensesdto import ExpensesDto


class GroupDto():
    def __init__(self, name, description, people, expenses):
        self._name = name
        self._description = description
        self._people = people
        self._expenses = expenses

    @property
    def name(self):
        return self._name
    
    @property
    def description(self):
        return self._description
    
    @property
    def people(self):
        return self._people

    @property
    def expenses(self):
        return self._expenses

    def contains_user(self, username):
        return username in self._people 
    

    #Añadir gasto al grupo, guardamos el id del gasto en el array y el gasto a la base de datos
    def add_expense(self, s:sirope.Sirope, expense):
        ooid_expense = s.save(expense)
        self._expenses.append(ooid_expense)

    #editar datos del grupo
    def edit_group(self, s:sirope.Sirope, name_group, description_group, list_participants):
        self._name = name_group
        self._description = description_group
        self._people = list_participants
        s.save(self)

    #devuelve la lista de los gastos del grupo
    def get_array_expenses(self, s:sirope.Sirope):
        return list(s.multi_load(self._expenses))
    
    #devuelve la cantidad total de gastos que tiene el grupo
    def get_total_expenses(self, s:sirope.Sirope):
        total = 0
        for id_exp in self._expenses:
            expense = ExpensesDto.get_expense(s,id_exp)
            total += expense.amount
        return total

    #devuelve el numero de dinero que gasto cada miembro del grupo 
    def payment_calculation(self, s:sirope.Sirope):
        dict = {}
        for person in self._people:
            dict[person] = 0

        for id_exp in self._expenses:
            expense =  ExpensesDto.get_expense(s,id_exp)
            dict[expense.user] = expense.amount
        return dict

    #devuelve el reparto de los gastos entre los miembros del grupo
    def equitable_payment_distribution(self, s:sirope.Sirope):
        total_expenses = self.get_total_expenses(s)
        tam_group = len(self._people)
        person_pay = self.payment_calculation(s)

        payments = {}

        for person in self._people:
            if person in person_pay:
                dict_temp = {}
                deuda = person_pay[person] / tam_group
                for p_temp in self._people:
                    if person != p_temp:
                        dict_temp[p_temp] = round(deuda,2)
            payments[person] = dict_temp

                         
        for person in payments:
            for p_temp in payments[person]:
                if payments[person][p_temp] != 0 and payments[person][p_temp] > payments[p_temp][person]:
                    payments[person][p_temp] = round(payments[person][p_temp] - payments[p_temp][person],2)
                    payments[p_temp][person] = 0
        

        return payments

    #devuelve el gasto con solo el nombre de este
    def search_expense(self, s:sirope.Sirope, name_expense):
        expsenses = self.get_array_expenses(s)
        for e in expsenses:
            if e.name == name_expense:
                return e
        return none

    #elimina el gasto del id enviado
    def delete_expense(self, s:sirope.Sirope, ooid_expense):
        ExpensesDto.delete_expense(s,ooid_expense)
        self._expenses.remove(ooid_expense)
        s.save(self)


    #devuelve el grupo buscado a de un usuario determinado
    @staticmethod
    def search_group(s:sirope.Sirope, name:str, username:str):  
        list_groups, urls_groups = GroupDto.get_all_groups(s, username=username)
        

        for g in list_groups:
            if name == g.name:
                return g 
        return None
    
    #devuelve los grupos de un usuario determinado
    @staticmethod
    def get_all_groups(s: sirope.Sirope, username: str):
        groups = [] 
        urls_groups = []
        for g in s.load_all(GroupDto):
            if username in g.people:
                groups.append(g)
                urls_groups.append(s.safe_from_oid(s.save(g)))

        return groups, urls_groups

    #devuelve el grupo buscado por la clave safe de sirope
    @staticmethod
    def search_by_url(s:sirope.Sirope, url):
        return s.load(s.oid_from_safe(url))

    #Elimina los gastos del grupo y elimina el grupo
    @staticmethod
    def delete_group(s:sirope.Sirope, ooid):
        group = s.load(ooid)
        for e in group.expenses:
            s.delete(e)
        s.delete(ooid)
        
    def __str__ (self):
        return f"{self.name}, {self.people}"