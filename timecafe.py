from datetime import date
from pgdb import PGSql
import abc
import json

class Storage:
	def __init__(self, attr_name):
		self.name = '_column#' + attr_name

	def __get__(self, obj, cls):
		return getattr(obj, self.name)

	def __set__(self, obj, value):
		setattr(obj, self.name, self)

class Validated(abc.ABC, Storage):
	def __set__(self, obj, value):
		value = self.validate(obj, value) 
		super().__set__(obj, value)

	@abc.abstractmethod
	def validate(self, instance, value):
		"""return validated value or raise ValueError"""

	@abc.abstractmethod
	def formatSQL(self):
		"""return value formated for SQL query"""

class StringField(Validated):
	def validate(self, instance, value):
		if type(value) is not str:
			raise ValueError(f"Parameter {self.name} must be string")

		self.value = value
		return self

	def formatSQL(self):
		return "'{0}'".format(self.value)

class DictField(Validated):
	def validate(self, instance, value):
		self.value = value
		return self

	def formatSQL(self):
		return "'{0}'".format(json.dumps(self.value))

class IntegerField(Validated):
	def validate(self, instance, value):
		if type(value) is not int:
			raise ValueError(f"Parameter {self.name} must be int")

		self.value = value
		return self

	def formatSQL(self):
		return str(self.value)

class DateField(Validated):
	def validate(self, instance, value):
		self.value = value
		return self

	def formatSQL(self):
		return "TO_DATE('{0}','DD/MM/YYYY')".format(self.value)

class BaseModel:
	def __init__(self):
		self._db = PGSql(type(self).__name__)

	def getColumns(self):
		columns = dict()

		for col, val in self.__dict__.items():
			if col.startswith('_column'):
				columns[col.split('#')[1]] = val
		
		return columns

	def add(self):
		columns = self.getColumns()
		self._db.add(columns)

	def update(self):
		old_data = self._db.selectById(self.id.value)
		new_data = self.getColumns()

		update_data = dict()
		update_data['id'] = self.id

		for col, obj in new_data.items():
			if obj.value != old_data[col]:
				update_data[col] = obj

		self._db.update(update_data)

	def delete(self):
		self._db.delete(self)

	@classmethod
	def loadById(cls, idx):
		cls.instance = cls.__new__(cls)
		cls.instance.__init__()

		data = cls.instance._db.selectById(idx)

		for col, val in data.items():
			setattr(cls.instance, col, val)

		return cls.instance

	def __getattr__(self, name):
		return f"Атрибут {name} не был найден"


class timecafes(BaseModel):
	#id антикафе
	id = IntegerField('id')

	#название антикафе
	title = StringField('title')

	#описание антикафе
	description = StringField('description')

	#картинки антикафе
	images = DictField('images')

	#id пользователя, который владеет антикафе
	owner_id = IntegerField('owner_id')

	#id схемы антикафе
	scheme_id = IntegerField('scheme_id')

	#когда создана запись
	created_at = DateField('created_at')

	#когда запись впоследний раз была отредактирована
	edited_at = DateField('edited_at')


#to add anticafe
cafe = timecafes()
cafe.title = "FD антикафе"
cafe.description = "FD - это лучшее антикафе в городе"
cafe.images = ['src1', 'src2', 'src3']
cafe.owner_id = 154
cafe.scheme_id = 1
cafe.created_at = date.today().strftime("%d.%m.%Y")
cafe.edited_at = date.today().strftime("%d.%m.%Y")
cafe.add()

print('-----------------------------------')

#to load anticafe by id
cafe = timecafes.loadById(1)
print(cafe.title.value) #prints title

print('-----------------------------------')

#to update anticafe data
cafe = timecafes.loadById(1)
cafe.title = "New anticafe title"
cafe.update()

print('-----------------------------------')

#to get columns of anticafe object
cafe = timecafes.loadById(1)
columns = cafe.getColumns()

for col, obj in columns.items():
	print(col, ":", obj.value)

print('-----------------------------------')

#to delete anticafe
cafe = timecafes.loadById(1)
cafe.delete()