import mysql.connector

bot_token = ")T8gBRffdud4)AnY*^rUvjQrtV%FfIgSmpUsW6b+&V+V(VJ4JvWC&U$^D%!n%DNK"

# GOOGLE API KEY FOR PERSPECTIVE API
API_KEY = ''

# MySQL credentials
host = 'localhost'
database = 'wwcbot'
user = 'wwcbot'
password = 'vErYsEcUrE'
hoi = False

def setup():
    connection = mysql.connector.connect(host=host,
                                         database=database,
                                         user=user,
                                         password=password,
                                         autocommit=True)

    cursor = connection.cursor()
    return cursor, connection