from peewee import *

"""В модуле реализованы модели базы банных
   с помощью библиотеки PEEWEE"""

DB = SqliteDatabase('DB/base.db')


class BaseModel(Model):
    class Meta:
        database = DB


class Configurations(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(max_length=1024, null=True)            # название библитотеки
    parent = CharField(max_length=1024, null=True)          # родитель
    level = IntegerField(null=True)                         # уровень вложенности
    mark = IntegerField(null=True)                          # признак документ или каталог
    name_docum = CharField(max_length=1024, null=True)      # название название документа
    date = DateTimeField()                                  # дата создания документа
