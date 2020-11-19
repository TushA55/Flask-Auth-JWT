from mongoengine import Document
from mongoengine.fields import DateTimeField, EmailField, StringField
from datetime import datetime
import bcrypt

class PasswordField(StringField):
    def validate(self, value):
        super(PasswordField, self).validate(value)
        if value == "":
            self.error("Password can't be empty")
        elif len(value) < 6:
            self.error("Password can't be less than 6 characters") 

class User(Document):
    email = EmailField()
    password = PasswordField()
    data_created = DateTimeField(default=datetime.utcnow)

    def hash_password(self):
        self.password = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt()).decode('utf-8')