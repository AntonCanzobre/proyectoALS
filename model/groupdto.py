import sirope


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