import sqlite3
import webbrowser as wb

# Attention symbole : retirer
# Renommer fichier pour enlever symboles non ascii et +
# Adapter taille image (et poids)

database = "/Users/juliettedebono/Desktop/Films.db"

conn = sqlite3.connect(database)
cur = conn.cursor()

cur.execute("""SELECT Titre, Réalisateur FROM Films WHERE id > 300 LIMIT 10""")
lien = cur.fetchall()

for i in lien:
    link = "https://www.ecosia.org/images?q={0}+{1}+affiche".format(i[0], i[1]).replace(" ", "+")
    print("{0}_{1}_affiche".format(i[0], i[1]).replace(" ", "_").replace(":", ""))
    if link != "":
        wb.open(link)

conn.close
