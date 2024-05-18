import sirope


class ExpensesDto():
    def __init__(self, name, amount, user):
        self._name = name
        self._amount = amount
        self._user = user

    @property
    def name(self):
        return self._name

    @property
    def amount(self):
        return int(self._amount)

    @property
    def user(self):
        return self._user


    @staticmethod
    def get_expense(s:sirope.Sirope, ooid):
        return s.load(ooid)

    @staticmethod
    def get_ooid(s:sirope.Sirope, expense):
        return s.save(expense)

    @staticmethod
    def delete_expense(s:sirope.Sirope, ooid):
        s.delete(ooid)

    def __str__ (self):
        return f"{self.name}, {self.amount}"