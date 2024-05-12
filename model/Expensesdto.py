



class expensesDto():
    def __init__(self, id, name, amount, user):
        self._id = id
        self._name = name
        self._amount = amount
        self._user = user

    @property
    def id(self):
        return self._id
    @property
    def name(self):
        return self._name

    @property
    def amount(self):
        return self._amount

    @property
    def user(self):
        return self._user