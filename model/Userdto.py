import sirope
import flask_login
import werkzeug.security as safe

class UserDto(flask_login.UserMixin):
    def __init__(self, name, username, email, password):
        self._name = name
        self._username = username
        self._email = email
        self._password = safe.generate_password_hash(password)
    
    @property
    def email(self):
        return self._email
    
    @property
    def name(self):
        return self._name
    
    @property
    def username(self):
        return self._username

    def get_id(self):
        return self.email

    def chk_password(self, pswd):
        return safe.check_password_hash(self._password, pswd)

    @staticmethod
    def exist_username(s:sirope.Sirope, username:str):
        return s.find_first(UserDto, lambda u: u.username == username)

    @staticmethod
    def current_user():
        usr = flask_login.current_user

        if usr.is_anonymous:
            flask_login.logout_user()
            usr = None
            
        return usr

    @staticmethod
    def find(s: sirope.Sirope, email: str) -> "UserDto":
        return s.find_first(UserDto, lambda u: u.email == email)

    @staticmethod
    def find_username(s: sirope.Sirope, username: str) -> "UserDto":
        return s.find_first(UserDto, lambda u: u.username == username)
    
    
    def __str__(self):
        return f"{self.name}, {self.username}, {self.email}"