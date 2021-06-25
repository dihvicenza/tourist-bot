import os
import psycopg2
import csv
import requests
import ast
import time
from pprint import pprint

def database_connect():
    try:
        print("Trying to connect to database...")
        conn = psycopg2.connect(host="pg1.cfhdttxorzlt.eu-south-1.rds.amazonaws.com", port=5432, database="tourist_bot", user="tourist_bot_admin", password="daUqe%z*qqj&C7n.oR8iX,]4")
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        print('Connected to database!')

        query = f"SELECT * FROM alloggio WHERE comune='VICENZA' and tipologia='BED AND BREAKFAST' and animali=true"
        query += ";"
        
        conn = psycopg2.connect(host="pg1.cfhdttxorzlt.eu-south-1.rds.amazonaws.com", port=5432, database="tourist_bot", user="tourist_bot_admin", password="daUqe%z*qqj&C7n.oR8iX,]4")
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(query)
        result = cur.fetchall()
        response = []
        for row in result:
            dicty = {}
            dicty['id'] = row[0]
            dicty['nome'] = row[1]
            dicty['indirizzo'] = row[3]
            dicty['stelle'] = row[5]
            if row[6] != "":
                dicty['sito'] = row[6]
            if row[7] != "":
                dicty['telefono'] = row[7]
            if row[8] != "":
                dicty['email'] = row[8]

            #piscina, ac, parcheggio, ristorante, animali, parcogiochi, sauna, palestra
            add = []
            for i in range(9,17):
                add.append(row[i])
            dicty["additional"] = add
            
            dicty['lat'] = row[17]
            dicty['lon'] = row[18]
            pprint(dicty)
        cur.close()
        conn.close()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        print("Database connection terminated!")

if __name__ == '__main__':
    database_connect()