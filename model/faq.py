from model.basemodel import BaseModel
from peewee import *
from model.user import User


class FAQ(BaseModel):
    id = PrimaryKeyField()
    question = CharField()
    text = TextField()
    author = ForeignKeyField(User)
    date_added = DateField()
