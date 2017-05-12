from peewee import *

from model.alias import Alias
from model.faq import Category

if __name__ == "__main__":
    Alias.create_table(fail_silently=True)
