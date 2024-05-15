import sirope
from model.Expensesdto import ExpensesDto


class GroupDto():
    def __init__(self, name, description, people, expenses):
        self._name = name
        self._description = description
        self._people = people
        self._expenses = expenses
        self._url

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
    
    @property
    def url(self):
        return self._url
    
    @url.setter
    def url(self, s:sirope.Sirope, url):
        self._url = url
        

    

    def contains_user(self, username):
        return username in self._people 
    
    def add_expense(self, s:sirope.Sirope, expense):
        ooid_expense = s.save(expense)
        self._expenses.append(ooid_expense)

    def get_array_expenses(self, s:sirope.Sirope):
        return list(s.multi_load(self._expenses))


    @staticmethod
    def search_group(s:sirope.Sirope, name:str, username:str):  
        list_groups = GroupDto.get_all_groups(s, username=username)
        for g in list_groups:
            if name == g.name:
                return g 
        return None
    
    @staticmethod
    def get_all_groups(s: sirope.Sirope, username: str): #devuelve todos los grupos del usuario
        groups = [] 
        for g in s.load_all(GroupDto):
            if username in g.people:
                groups.append(g)

        return groups
        
    def __str__ (self):
        return f"{self.name}, {self.people}"