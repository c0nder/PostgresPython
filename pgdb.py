from os.path import join, dirname
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv(join(dirname(__file__), '.env'))

class PGSql:
	def __init__(self, tableName):
		self.db_name = os.getenv('DB_NAME')
		self.db_user = os.getenv('DB_USER')
		self.db_host = os.getenv('DB_HOST')
		self.db_password = os.getenv('DB_PASSWORD')
		self.db_port = os.getenv('DB_PORT')

		self.conn = psycopg2.connect(f"dbname={self.db_name} user={self.db_user} host={self.db_host} password={self.db_password} port={self.db_port}")
		self.db = self.conn.cursor()
		self.table = tableName

	def add(self, data):
		columns = ", ".join(data.keys())
		values = ", ".join(val.formatSQL() for val in data.values())
		query = "INSERT INTO {0} ({1}) VALUES({2})".format(self.table, columns, values)

		self.db.execute(query)
		self.conn.commit()

	def update(self, data):
		values = ", ".join([f"{col} = {obj.formatSQL()}" for col, obj in data.items() if col != 'id'])
		query = "UPDATE {0} SET {1} WHERE id = {2}".format(self.table, values, data['id'].formatSQL())

		self.db.execute(query)
		self.conn.commit()

	def delete(self, instance):
		query = "DELETE FROM {0} WHERE id = {1}".format(self.table, instance.id.formatSQL())

		self.db.execute(query)
		self.conn.commit()

	def selectById(self, idx):
		query = "SELECT * FROM {0} WHERE id = {1}".format(self.table, idx)

		self.db.execute(query)

		columns = [desc[0] for desc in self.db.description]
		values = self.db.fetchone()

		return dict(zip(columns, values))
