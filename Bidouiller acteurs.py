import sqlite3
import webbrowser as wb

database = "/Users/juliettedebono/Desktop/Films.db"

conn = sqlite3.connect(database)
cur = conn.cursor()
'''
cur.execute("""Select titre FROM FILMS""")
films = cur.fetchall()

liste = [i[0] for i in films]

for film in liste:
    lien = "https://fr.wikipedia.org/wiki/%s" %(film.replace(" ", "_"))
    cur.execute("""
    UPDATE Films
    SET Liens = "%s"
    WHERE Titre = "%s";"""%(lien, film))

conn.commit()
'''

cur.execute("""SELECT Lien FROM ARTISTES WHERE Genre is Null LIMIT 10""")
lien = cur.fetchall()

for i in lien:
    i = i[0]
    print(i)
    if i != "":
        wb.open(i)

conn.close
