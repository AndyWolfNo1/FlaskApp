import mysql.connector
import config

class MySQLDatabase:
    __instance = None

    @staticmethod 
    def getInstance():
        if MySQLDatabase.__instance == None:
            MySQLDatabase()
        return MySQLDatabase.__instance

    def __init__(self):
        if MySQLDatabase.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MySQLDatabase.__instance = self
            self.config = {
                'user': config.DB_USERNAME,
                'password': config.DB_PASSWORD,
                'host': config.DB_HOST,
                'database': config.DB_DATABASE,
                'raise_on_warnings': True,
                'charset': 'utf8'
            }
            self.cnx = mysql.connector.connect(**self.config)

    def execute_query_one(self, query, arg):
        cursor = self.cnx.cursor()
        cursor.execute(query, arg)
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def execute_query_questions(self, query):
        cursor = self.cnx.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def execute_query_add_question(self, query, val):
        cursor = self.cnx.cursor()
        cursor.execute(query, val)
        self.cnx.commit()
        cursor.close()