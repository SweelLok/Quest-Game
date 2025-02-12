from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_id, username, gmail, password, email_verified):
        self.user_id = user_id
        self.username = username
        self.gmail = gmail
        self.password = password
        self.email_verified = email_verified
        
    def get_id(self):
        return str(self.user_id)
    