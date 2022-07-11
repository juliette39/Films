# -*- coding: utf8 -*-

import sqlite3
import webbrowser as wb
import tkinter as tk
from tkinter import filedialog
from tkinter import font
import darkmode as dm
import sys

try:
    import pandas
except ModuleNotFoundError:
    import subprocess
    subprocess.call(['pip', 'install', 'pandas'])
    import pandas

## Initialisations

# Liens

path = sys.argv[0]
path = "/".join(path.split("/")[:-1]) + "/Resources"

database = path + "/Films.db"
fichierODS = path + "/Films.ods"
# fichierArtistes = "/Applications/Films.app/Contents/Resources/Artistes.csv"
databaseInfos = path + "/datas.db"

# Description
description = {'Numéro' : 'Nombre de DVD situés\navant lui', 'Emplacement' : "Emplacement du DVD :\ncommence par l'étage,\npuis éventuellement\nsi dans un coffret (C)\net/ou avec les initiales de\nce qui réunit les films autour", 'Titre' : 'Titre du film', 'Réalisateur' : 'Nom de réalisateur du film', 'Langue' : 'Langue originale du film', 'Date' : 'Date de sortie du film', 'Durée' : 'Durée en minutes du film', 'Colorisation' : 'Film est en couleur ou\nen noir et blanc', 'Voix' : 'Film muet ou parlant', 'Disque' : 'DVD ou Blue-Ray', 'Type' : 'Film, Dessin Animé,\nCourt-métrage, Documentaire,\nSpectacle, Concert', 'Acteurs' : 'Acteurs du film'}
legende = list(description.keys())
infoslegende = ["Titre du film :", "Réalisateur·rice du film :", "Langue du film :", "Intervalle de date du film :", "Durée max du film :", "Colorisation du film :", "Voix du film :", "Disque :", "Type :", "Vu ou non par :", "Acteur·rice·s dans le film :"]

# Mode sombre
dark = "black"
light = "white"
darkmode = dm.Dark(databaseInfos, dark, light, dark)

## Fonctions pour application

def updateDataBase():

    conn = sqlite3.connect(database)
    cur = conn.cursor()

    try:
        cur.execute("""SELECT * FROM Films;""")

    except sqlite3.OperationalError:

        # Créer table avec bon type

        try:
            # Création table Films
            pandas.read_excel(fichierODS, "Films").to_sql("Films", conn, if_exists='replace', index=False)
        except ModuleNotFoundError:
            import subprocess
            subprocess.call(['pip', 'install', 'odfpy'])
            pandas.read_excel(fichierODS, "Films").to_sql("Films", conn, if_exists='replace', index=False)
        finally:
            # Création table Artistes
            pandas.read_excel(fichierODS, "Artistes").to_sql("Artistes", conn, if_exists='replace', index=False)
            # pandas.read_csv(fichierArtistes, delimiter =",").to_sql("Artistes", conn, if_exists='append', index=False)

        conn.commit()
    conn.close

def transformReq():
    """Transforme les caractéristiques en requête
    Renvoie un message d'erreur si il y a une donnée mal entrée"""

    req = """SELECT * FROM FILMS WHERE"""
    erreur = None

    titre = titreEntry.get().replace("'", "’")
    real = realEntry.get().replace("'", "’")
    langue = langueEntry.get().replace("'", "’")
    date = dateEntry.get().replace("'", "’")
    duree = dureeEntry.get().replace("'", "’")
    couleur = couleurEntry.get().replace("'", "’")
    voix = voixEntry.get().replace("'", "’")
    disque = disqueEntry.get().replace("'", "’")
    typ = typeEntry.get().replace("'", "’")
    vision = visionEntry.get().replace("'", "’")
    acteurs = acteurEntry.get().replace("'", "’")

    if titre != "":
        req += """ LOWER(Titre) LIKE "%s" AND""" % ("%" + titre.lower() + "%")
    if real != "":
        req += """ LOWER(Réalisateur) LIKE "%s" AND""" % ("%" + real.lower() + "%")
    if langue != "":
        req += """ LOWER(Langue) LIKE "%s" AND""" % ("%" + langue.lower() + "%")
    if date != "":
        date = date.replace(" ", "").split('-')
        debut = " date > %s AND"%date[0]
        try:
            fin =  " date < %s AND"%date[1]
        except IndexError:
            fin = ""
        req += debut + fin
    if duree != "":
        req += """ Durée <= %s AND""" % (duree)
    if couleur != "":
        req += """ LOWER(Colorisation) LIKE "%s" AND""" % ("%" + couleur.lower() + "%")
    if voix != "":
        req += """ LOWER(Voix) LIKE "%s" AND""" % ("%" + voix.lower() + "%")
    if disque != "":
        req += """ LOWER(Disque) LIKE "%s" AND""" % ("%" + disque.lower() + "%")
    if typ != "":
        req += """ LOWER(Type) LIKE "%s" AND""" % ("%" + typ.lower() + "%")
    if vision != "":
        vision = vision.replace(":", "").replace(",", "").replace("=", "").lower()
        while "  " in vision:
            vision = vision.replace("  ", " ")
        visListe = vision.split(" ")
        if len(visListe) < 2:
            visListe.append("")
            erreur = "Mauvais donnée de vision des films"
        if "pas" in visListe[1]:
            indice = 0
        else:
            indice = 1
        req += """ LOWER("Vu %s") LIKE "%s" AND""" % (visListe[0], str(indice) + '%')
    if acteurs != "":
        acteurs = acteurs.split(", ")
        for acteur in acteurs:
            req += """ Acteurs LIKE '%s' AND""" % (("%"+ acteur +"%",))
    req = req.strip(" AND")
    return req, erreur

def Aide():
    """Affiche une fenêtre donnant des indications sur l'application"""

    aide = tk.Toplevel(root)
    aide.title("Aide")

    textAide = """ Entrez les informations puis recherchez le film avec ces caractéristiques
 Si vous n'entrez rien, tout est séléctionné
 Le bouton 'Film Aléatoire' choisi un film aléatoirement avec les caractéristiques demandées
 Le bouton 'Tout les films' montre tout les films correspondants à ces caractéristiques
 Une fois tous les films affichés, vous pouvez en séléctionner un et cliquer sur info,
 les infos de ce film apparaîtront
 Pour les caractéristiques vous avez :
    Titre : Donnez des éléments du titre du film
    Réalisateur : Donnez un nom ou prénom du réalisateur
    Langue : Langue du film (Anglais, Français, Italien, Suèdois, Espagnol, Japonais
    Date : Intervalle de date de réalisation du film :
        Séparé par '-' ex : 1950-2000
    Durée : Durée max du film en minutes
    Colorisation : Couleur ou NB
    Voix : Muet ou Parlant
    Disque : DVD ou BR (Blue-Ray)
    Type : Film, Série, Dessin animé, Concert, Spectacle, Doc, Court Métrage
    Vu ou non par :
        Séparé par ' ' ex : Juliette pas vu
    Acteurs : Nom ou prénom des acteurs présents dans le film :
        Séparé par ', ' ex : Hepburn, Bogart"""

    aideLabel = tk.Text(aide, font = police, height = 22, width = 70)
    aideLabel.insert(1.0, textAide)
    aideLabel.configure(state='disabled')
    aideLabel.grid(column = 1, row = 0)
    roots.append(aide)
    darkmode.lancer(roots)
    return None

def Affiche_fen_tup(tup):
    """Affichie dans une nouvelle fenêtre les informations du tuple du film"""

    legende2 = legende

    def Info():
        try:
            value = filmList.get(filmList.curselection())
        except tk.TclError:
            # Selection dans colonne 1
            value = legendeList.get(legendeList.curselection())
            texte = description[value]
            legende = tk.Toplevel(root)
            legende.title("Légende")
            legendeText = tk.Text(legende, font = police, height = texte.count("\n") + 1, width = 25)
            legendeText.insert(1.0, texte)
            legendeText.configure(state='disabled')
            legendeText.grid(column = 1, row = 0)
            roots.append(legende)
            darkmode.lancer(roots)

        else:
            conn = sqlite3.connect(database)
            cur = conn.cursor()

            # Séléction dans colonne 2
            etage = filmList.curselection()[0]
            if etage == 0:
                print("Numéro")
            if etage == 1:
                print("Emplacement")
                #TODO : Expliquer notation
            if etage == 2:
                print("Titre")
                cur.execute("""SELECT Liens FROM Films WHERE Titre = ?""", (value,))
                lienFilm = cur.fetchone()
                if lienFilm is not None:
                    wb.open(lienFilm[0])
                else:
                    wb.open("https://www.ecosia.org/search/?q={}".format(value.replace(" ", "+")))
            if etage == 3 or etage > 10:
                # Ligne artiste
                cur.execute("""SELECT Lien FROM Artistes WHERE Nom = ?""", (value,))
                lienArtiste = cur.fetchone()
                if lienArtiste is not None:
                    wb.open(lienArtiste[0])
                else:
                    wb.open("https://www.ecosia.org/search/?q={}".format(value.replace(" ", "+")))
            if etage == 4:
                cur.execute("""SELECT * FROM Films WHERE Langue = ?""", (value,))
                films = cur.fetchall()
                Total(films, value)

            if etage == 5:
                cur.execute("""SELECT * FROM Films WHERE Date = ?""", (value,))
                films = cur.fetchall()
                Total(films, value)
            if etage == 6:
                cur.execute("""SELECT * FROM Films WHERE Durée <= ?""", (value,))
                films = cur.fetchall()
                value = "Inférieur à " + value
                Total(films, value)
            if etage == 7:
                cur.execute("""SELECT * FROM Films WHERE Colorisation = ?""", (value,))
                films = cur.fetchall()
                if value == "NB":
                    value = 'Noir et blanc'
                Total(films, value)
            if etage == 8:
                cur.execute("""SELECT * FROM Films WHERE Voix = ?""", (value,))
                films = cur.fetchall()
                Total(films, value)
            if etage == 9:
                cur.execute("""SELECT * FROM Films WHERE Disque = ?""", (value,))
                films = cur.fetchall()
                Total(films, value)
            if etage == 10:
                cur.execute("""SELECT * FROM Films WHERE Type = ?""", (value,))
                films = cur.fetchall()
                Total(films, value)

            # Affiche_fen_tup(film)
            conn.close

    lar = 7
    try:
        liste = list(tup)
        titre = liste[2]
        result = []
        for info in liste[:11] :
            if info is not None:
                result.append(str(info))
                lon = len(result[-1])
                if lon > lar:
                    lar = lon
            else:
                result.append("")

        try:
            acteurs = liste[14].split(",")
        except AttributeError:
            None
        else:
            for acteur in acteurs:
                result.append(acteur)
                lon = len(acteur)
                if lon > lar:
                    lar = lon
        finally:
            button = True

    except:
        titre = "Erreur"
        result = ["Aucun film ne correspond à votre demande"]
        lar = len(result[0])
        legende2 = [""]
        button = False

    trouve = tk.Toplevel(root)
    trouve.title(titre)

    filmList = tk.Listbox(trouve, height = len(result), width = int(7*lar/6), font = police, selectmode='single')
    for info in result:
        filmList.insert("end", info)

    filmList.configure(bd = 0)
    filmList.grid(column = 1, row = 0)

    legendeList = tk.Listbox(trouve, height = len(result), width = 12, font = police, selectmode='disable')
    legendeList.configure(bd = 0)

    for titre in legende2:
        if titre == "Réalisateur":
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            req = """SELECT Genre FROM Artistes WHERE Nom = "%s\""""%result[3]
            cur.execute(req)
            genre = cur.fetchone()[0]
            if genre == "F":
                titre = "Réalisatrice"

        if titre == "Acteurs":
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            acteurs = result[11:]
            for i in range(len(acteurs)):
                if acteurs[i] == "":
                    del acteurs[i]
            if len(acteurs) == 0:
                # Pas d'acteurs
                titre = ""

            elif len(acteurs) == 1:
                # Un seul acteur : regarder son genre
                req = """SELECT Genre FROM Artistes WHERE NOM = '%s' """%acteurs[0]
                try:
                    genre = cur.fetchone()[0]
                except:
                    pass
                if genre == "F":
                    titre = "Actrice"
                else:
                    titre = "Acteur"
            else:
                # Plusieurs acteurs : regarder leur genre
                req = """SELECT Genre FROM Artistes WHERE NOM = '%s' """%acteurs[0]
                for acteur in acteurs[1:]:
                    req += "OR Nom = '%s' " %acteur
                cur.execute(req)
                genres = cur.fetchall()
                if ("H",) in genres:
                    titre = "Acteurs"
                else:
                    titre = "Actrices"
        legendeList.insert("end", titre)

    legendeList.grid(column = 0, row = 0)

    if button:
        filmCherche = tk.Button(trouve, font = police, command = Info, text = "Info")
        filmCherche.grid(column = 0, row = 10)

    roots.append(trouve)
    darkmode.lancer(roots)

def Alea(event = None):
    """Choisi un film aléatoirement correspondant aux caractéristiques demandées"""

    req, erreur = transformReq()

    if req == """SELECT * FROM FILMS WHERE""":
        req = """SELECT * FROM FILMS"""

    req += """ ORDER BY RANDOM() LIMIT 1"""
    conn = sqlite3.connect(database)
    cur = conn.cursor()

    try:
        cur.execute(req)
        film = cur.fetchone()

    except sqlite3.OperationalError:
        film = []

    Affiche_fen_tup(film)

    conn.commit()
    conn.close

    return None

def Total(liste = None, titre = 'Tous les films'):
    """Choisi tous les films correspondant aux caractéristiques demandées"""

    def Info():
        value = filmList.get(filmList.curselection())
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute("""SELECT * FROM FILMS WHERE Titre = ? LIMIT 1""", (value,))
        film = cur.fetchone()
        conn.close
        Affiche_fen_tup(film)

    trouve = tk.Toplevel(root)
    trouve.title(titre)


    if liste is None or str(type(liste)) == "<class 'tkinter.Event'>":
        req, erreur = transformReq()

        if req == """SELECT * FROM FILMS WHERE""":
            req = """SELECT * FROM FILMS"""
        conn = sqlite3.connect(database)
        cur = conn.cursor()

        try:
            cur.execute(req)
            films_trouves = cur.fetchall()
        except sqlite3.OperationalError:
            films_trouves = []
        conn.close

    else:
        films_trouves, erreur = liste, None

    nb_film = len(films_trouves)
    lar = 7
    if nb_film > 1:
        result = ["%s Films" %nb_film, erreur, ""]

    elif nb_film == 1:
        result = ["1 Film", erreur, ""]

    else:
        result = ["Aucun film ne correspond à votre demande"]
        nb_film = 1
        lar = len(result[0])

    for film in films_trouves:
        new_len = len(film[2])
        if new_len > lar:
            lar = new_len

        result.append(film[2])

    lon = len(result)

    if lon > 30:
        lon = 30

    filmList = tk.Listbox(trouve, height = lon, width = int(6*lar/7), font = police, selectmode = 'single')
    filmList.configure(bd = 0)
    filmCherche = tk.Button(trouve, font = police, command = Info, text = "Info")

    for film in result:
        filmList.insert("end", film)

    filmList.grid(column = 0, row = 0)

    filmCherche.grid(column = 1, row = 0)

    roots.append(trouve)
    darkmode.lancer(roots)

    return None

## Création fenêtre application

root = tk.Tk()
root.title('Films')

# Taille de la fenetre
fenetre = tk.Canvas(root, width = 600, height = 670)
fenetre.config(highlightthickness = 0)
fenetre.pack()

# Police utilisée dans application
police = font.Font(root, size = 20, family = 'Arial')
policelittle = font.Font(root, size = 14, family = 'Arial')

# Création widgets sur fenêtre principale

# titreLabel = tk.Label(root, text = "Titre du film :", font = police)
titreEntry = tk.Entry(root, font = police)

# realLabel = tk.Label(root, text = "Réalisateur.trice du film :", font = police)
realEntry = tk.Entry(root, font = police)

# langueLabel = tk.Label(root, text = "Langue du film :", font = police)
langueEntry = tk.Entry(root, font = police)

# dateLabel = tk.Label(root, text = "Intervalle de date du film :", font = police)
dateEntry = tk.Entry(root, font = police)

# dureeLabel = tk.Label(root, text = "Durée max du film :", font = police)
dureeEntry = tk.Entry(root, font = police)

# couleurLabel = tk.Label(root, text = "Colorisation du film :", font = police)
couleurEntry = tk.Entry(root, font = police)

# voixLabel = tk.Label(root, text = "Voix du film :", font = police)
voixEntry = tk.Entry(root, font = police)

# typeLabel = tk.Label(root, text = "Disque :", font = police)
disqueEntry = tk.Entry(root, font = police)

# typeLabel = tk.Label(root, text = "Type de film :", font = police)
typeEntry = tk.Entry(root, font = police)

# visionLabel = tk.Label(root, text = "Vu ou non par :", font = police)
visionEntry = tk.Entry(root, font = police)

# acteurLabel = tk.Label(root, text = "Acteur.trice.s dans le film :", font = police)
acteurEntry = tk.Entry(root, font = police)

aideButton = tk.Button(root, text = 'Aide', command = Aide, font = police)
aleaButton = tk.Button(root, text = 'Film Aléatoire', command = Alea, font = police)
totalButton = tk.Button(root, text = 'Tous les films', command = Total, font = police)

legendeList1 = tk.Listbox(root, height = len(infoslegende)*2, width = 20, font = police)

for info in infoslegende[:-1]:
    legendeList1.insert("end", info)
    legendeList1.insert("end", "")
legendeList1.insert("end", infoslegende[-1])

legendeList1.bindtags((legendeList1, root, "all")) # Désactiver selection listbox sans colorer en gris
legendeList1.configure(bd = 0)

darkVar = tk.IntVar()
darkCheck = tk.Checkbutton(root, text = 'Mode sombre', variable = darkVar, onvalue = True, offvalue = False, font = police, command = darkmode.switch)

# Touche entrer cliqué
root.bind("<Return>", Total)

# Apparition widget
colonne = (130, 400)
intervalle = 48

fenetre.create_window(colonne[0], 280, window = legendeList1)

ligne = 25
# fenetre.create_window(colonne[0], ligne, window = titreLabel)
fenetre.create_window(colonne[1], ligne, window = titreEntry)

ligne += intervalle
# fenetre.create_window(colonne[0], ligne, window = realLabel)
fenetre.create_window(colonne[1], ligne, window = realEntry)

ligne += intervalle
# fenetre.create_window(colonne[0], ligne, window = langueLabel)
fenetre.create_window(colonne[1], ligne, window = langueEntry)

ligne += intervalle
# fenetre.create_window(colonne[0], ligne, window = dateLabel)
fenetre.create_window(colonne[1], ligne, window = dateEntry)

ligne += intervalle
# fenetre.create_window(colonne[0], ligne, window = dureeLabel)
fenetre.create_window(colonne[1], ligne, window = dureeEntry)

ligne += intervalle
# fenetre.create_window(colonne[0], ligne, window = couleurLabel)
fenetre.create_window(colonne[1], ligne, window = couleurEntry)

ligne += intervalle
# fenetre.create_window(colonne[0], ligne, window = voixLabel)
fenetre.create_window(colonne[1], ligne, window = voixEntry)

ligne += intervalle
# fenetre.create_window(colonne[0], ligne, window = typeLabel)
fenetre.create_window(colonne[1], ligne, window = disqueEntry)

ligne += intervalle
fenetre.create_window(colonne[1], ligne, window = typeEntry)

ligne += intervalle
# fenetre.create_window(colonne[0], ligne, window = visionLabel)
fenetre.create_window(colonne[1], ligne, window = visionEntry)

ligne += intervalle
# fenetre.create_window(colonne[0], ligne, window = acteurLabel)
fenetre.create_window(colonne[1], ligne, window = acteurEntry)

ligne += 60
fenetre.create_window(colonne[0], ligne, window = aleaButton)

ligne += 40
fenetre.create_window(colonne[0], ligne, window = totalButton)
fenetre.create_window(colonne[1], ligne, window = aideButton)

ligne += 40
fenetre.create_window(colonne[0], ligne, window = darkCheck)

updateDataBase()
roots = [root]
darkmode.lancer(roots, darkCheck)

# Création fenêtre
root.mainloop()