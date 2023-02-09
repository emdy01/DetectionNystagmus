import guizero as gz
import tkinter as tk
from tkinter.ttk import Combobox
import os, time, configparser
wdir = os.path.dirname(os.path.abspath("Software.py"))
os.chdir(wdir)
from realtime import realtime
from videofile import videofile
from threading import Thread, Event


class Software():

    def __init__(self): # constructeur
        # Initialisation et paramétrage de tous les éléments de l'interface graphique

        self.app = gz.App(title = "Détection logicielle de Nystagmus", layout ="grid")

        self.app.height = 800

        self.app.width = 1400

        self.mode = gz.Text(self.app, text = "Choisir le mode \n - 'realtime video' si vous voulez faire une analyse en temps réel \n - 'videofile' si vous voulez analyser une vidéo enregistrée au préalable", grid = [2,1])
        self.mode.text_size = 12

        self.option = gz.ButtonGroup(self.app, grid = [2,2], options = ["real time video", "videofile"], horizontal = True)
        self.option.text_size = 12



        self.ok = gz.PushButton(self.app, grid = [2,3], text = "Ok", command = self.StartSoft)
        self.ok.text_size = 12
        self.rectangle = gz.TextBox(self.app, grid = [2,4])
        self.rectangle.width = 150
        self.PathList = []



        self.path = Combobox(self.app.tk,  textvariable  = "Chemin d'accès du fichier de sortie", values = self.PathList, postcommand = self.CallbackOutput, font = ("Arial", 12))
        self.path.insert(0, "Fichier de sortie")
        self.app.add_tk_widget(self.path, visible = False, grid = [2,5], width = 100)

        self.PathBrowser = gz.PushButton(self.app, grid = [3,5], text = "Parcourir...", visible = False, command = self.browseOutputFiles)
        self.PathBrowser.text_size = 12

        self.PathOK = gz.PushButton(self.app, grid = [2,7], text = "Ok", visible = False)
        self.PathOK.text_size = 12

        self.NomList = []

        self.nom = Combobox(self.app.tk,  textvariable  = "Chemin d'accès du fichier vidéo", values = self.NomList, postcommand = self.CallbackVideo, font = ("Arial", 12))
        self.nom.insert(0, "Fichier vidéo")
        self.app.add_tk_widget(self.nom, visible = False, grid = [2,6], width = 100)


        self.NomBrowser = gz.PushButton(self.app, grid = [3,6], text = "Parcourir...", visible = False, command = self.browseVideoFiles)
        self.NomBrowser.text_size = 12

        self.aide = gz.Text(self.app, grid = [2,4], visible = False)
        self.aide.text_size = 12
        self.aide.tk.config(justify = 'left')

        self.state = gz.Text(self.app, grid = [2,8], visible = False)
        self.state.text_size = 12

        self.OuvrirAideCompre = gz.PushButton(self.app, grid = [3,9], text = "Outils d'interprétation", visible = False, command = self.OpenHelp)
        self.OuvrirAideCompre.text_size = 12



        self.AideCompre = gz.Window(self.app, title = "Outils d'interprétation", visible = False)
        self.TexteAideCompre = gz.Text(self.AideCompre, text = "Fichier Excel : \n \n Ce fichier est divisé en deux feuilles : 'Oeil gauche' et 'Oeil droit'. \n Pour chaque feuille : \n La première ligne indique le taux de détection des pupilles par le logiciel. \n Ensuite, outre l'en-tête du tableau, chaque ligne correspond à un nystagmus de l'oeil. \n Les deux premières colonnes indiquent les temps de début et de fin de nystagmus, en millisecondes.  \n La troisième colonne indique la direction dominante du nystagmus : H pour horizontale, V pour verticale. \n La quatrième colonne indique l'amplitude du nystagmus, en pixels. \n La cinquième colonne indique la fréquence du nystagmus, en battements par seconde. \n \n Fichier CSV : \n \n La première ligne de ce fichier correspond au taux de détection des pupilles par le logiciel. \n Ensuite il est divisé en deux paragraphes. Celui du haut correspond à l'oeil gauche, celui du bas à l'oeil droit. \n Pour chaque paragraphe : \n Chaque série de valeur correspond à un nystagmus de l'oeil. \n Les deux premières valeurs indiquent les temps de début et de fin de nystagmus, en millisecondes.  \n La troisième valeur indique la direction dominante du nystagmus : 0 pour une dominante horizontale, 1 pour une dominante verticale. \n La quatrième valeur indique l'amplitude du nystagmus, en pixels. \n La cinquième valeur indique la fréquence du nystagmus, en battements par seconde.")
        self.TexteAideCompre.text_size = 12
        self.AideCompre.width = 1000
        self.FermerAideCompre = gz.PushButton(self.AideCompre, align = "bottom", text = "Fermer", command = self.CloseHelp)
        self.OuvrirAideCompre.text_size = 12


        self.arret = gz.PushButton(self.app, text = "Arrêter le logiciel", grid = [3,11], command = self.StopSoft)


        self.new = gz.PushButton(self.app, text = "Nouvelle analyse", grid = [3,10], command = self.reset, visible = False)

        self.arret.text_size = 12

        self.new.text_size = 12

    def reset(self):
        # retour à l'interface de lancement du logiciel
        self.PathOK.visible = False
        self.PathOK.enable()
        self.aide.visible = False
        self.state.visible = False
        self.new.visible = False
        self.OuvrirAideCompre.visible = False
        self.app.add_tk_widget(self.path, visible = False)
        self.app.add_tk_widget(self.nom, visible = False, grid = [3,2])
        self.path.set("Fichier de sortie")
        self.nom.set("Fichier vidéo")
        self.PathBrowser.visible = False
        self.NomBrowser.visible = False

    def OpenHelp(self):
        self.AideCompre.show()

    def CloseHelp(self):
        self.AideCompre.hide()


    def realtimeMode(self):
        # Gestion du mode temps réel

        file = self.path.get() # Récupération du chemin d'accès du fichier de sortie

        if file not in self.PathList:
            self.PathList.append(file) # actualisation de la liste de chemins utilisés

        ext = os.path.splitext(file)[1] # Récupération de l'extension du fichier de sortie
        tr = realtime(file) # Instanciation de la classe realtime
        self.state.visible = True
        tr.launch(ext) # Lancement du processus implémenté dans cette classe

        #Gestion des feedbacks
        if tr.GetNES() == True:
            self.state.value = "Quantité de données insuffisante. Veuillez lancer une nouvelle analyse."
            self.new.visible = True
        else :
            DR = str(tr.GetDR())
            if ext == ".xlsx":
                self.state.value = "Le fichier Excel est prêt ! \nLe taux de détection est de " + DR + "%."

            if ext == ".csv":
                self.state.value = "Le fichier CSV est prêt ! \nLe taux de détection est de " + DR + "%."
            self.new.visible = True
            self.OuvrirAideCompre.visible = True

    def videofileMode(self):
        # Gestion du mode vidéo préenregistrée


        vid = self.nom.get() # Récupération du chemin d'accès du fichier vidéo
        file = self.path.get() # Récupération du chemin d'accès du fichier de sortie

        if file not in self.PathList:
            self.PathList.append(file) # actualisation de la liste de chemins utilisés

        if vid not in self.NomList:
            self.NomList.append(vid) # actualisation de la liste de chemins utilisés

        ext = os.path.splitext(file)[1] # Récupération de l'extension du fichier de sortie
        self.state.visible = True
        vf = videofile(vid, file) # Instanciation de la classe videofile
        vf.launch(ext) # Lancement du processus implémenté dans cette classe

        #Gestion des feedbacks
        if vf.GetNES() == True:
            self.state.value = "Quantité de données insuffisante. Veuillez lancer une nouvelle analyse."
            self.new.visible = True
        else:
            DR = str(vf.GetDR())

            if ext == ".xlsx":
                self.state.value = "Le fichier Excel est prêt ! \nLe taux de détection est de " + DR + "%."

            if ext == ".csv":
                self.state.value = "Le fichier CSV est prêt ! \nLe taux de détection est de " + DR + "%."

            self.state.visible = True
            self.new.visible = True
            self.OuvrirAideCompre.visible = True

    def StartSoft(self):
        #  Adaptation de l'interface graphique au mode choisi par l'utilisateur
        if self.option.value == "real time video":
            self.PathOK.update_command(self.realtimeMode)
            self.aide.value = "Bienvenue dans le mode 'real time video' ! \n Voici les étapes à suivre pour générer un fichier de résultats : \n 1) A l'aide du bouton 'Parcourir' ci-dessous, sélectionner le fichier Excel ou CSV dans lequel les résultats de l'analyse seront stockés. \n 2) Cliquez sur 'OK' et attendez que la caméra démarre (cela peut prendre quelques secondes). \n 3) Assurez-vous que la pièce soit bien éclairée, que la tête du patient remplisse l'image et soit fixe et que ses yeux soient grand ouverts. \n 4) Appuyez sur la barre espace du clavier pour lancer la localisation en temps réel des pupilles, puis réappuyer une deuxième fois pour l'arrêter. \n 5) Votre fichier est prêt ! Pour obtenir un guide d'interprétation de celui-ci, cliquez sur le bouton 'Outils d'interprétation' à droite."
            self.app.add_tk_widget(self.path, visible = True, grid = [2,5], width= 100)
            self.aide.visible = True
            self.PathOK.visible = True
            self.PathBrowser.visible = True
        if self.option.value == "videofile":
            self.aide.value = "Bienvenue dans le mode 'videofile' ! \n Voici les étapes à suivre pour générer un fichier de résultats : \n 1) Sélectionner ci-dessous le fichier Excel ou CSV dans lequel les résultats de l'analyse seront stockés (champ du haut), ainsi que le fichier vidéo à analyser (champ du bas). \n Aidez-vous pour cela des boutons 'Parcourir' à côtés des champs. \n Astuce : pour une interprétation immédiate des résultats, préférez le format Excel. \n 2) Cliquez sur 'OK' et patientez le temps que le logiciel analyse la vidéo (cela peut prendre quelques minutes). \n 3)  Un message s'affiche : votre fichier est prêt ! Pour obtenir un guide d'interprétation de celui-ci, cliquez sur le bouton 'Outils d'interprétation' à droite."
            self.PathOK.update_command(self.videofileMode)
            self.app.add_tk_widget(self.path, visible = True, grid = [2,5], width = 100)
            self.aide.visible = True
            self.PathOK.visible = True
            self.app.add_tk_widget(self.nom, visible = True, grid = [2,6], width = 100)
            self.PathBrowser.visible = True
            self.NomBrowser.visible = True

    def browseOutputFiles(self): # Gestion du navigateur permettant de choisir les fichiers de sortie
        filename = tk.filedialog.askopenfilename(initialdir = os.path.dirname(os.path.abspath("Software.py")), title = "Sélectionner un fichier", filetypes = (("Fichier Excel", "*.xlsx"),("Fichier CSV","*.csv")))
        self.path.set(filename)


    def CallbackOutput(self): # Gestion d'un élément de l'interface graphique
        self.path['values'] = self.PathList

    def browseVideoFiles(self): # Gestion du navigateur permettant de choisir les fichiers vidéo (le cas échéant)
        filename = tk.filedialog.askopenfilename(initialdir = os.path.dirname(os.path.abspath("Software.py")), title = "Sélectionner un fichier", filetypes = (("Fichier MP4", "*.mp4"),("Fichier AVI", "*.avi"), ("Fichier MKV", "*.mkv"), ("Fichier MOV","*.mov"), ("Fichier TS", "*.ts"), ("Fichier WMV", "*.wmv")))
        self.nom.set(filename)


    def CallbackVideo(self): # Gestion d'un élément de l'interface graphique
        self.nom['values'] = self.NomList

    def StopSoft(self): # Arrêt du logiciel
        self.app.destroy()

    def launch(self): # Lancement du logiciel
        self.app.display()

if __name__ == "__main__":
    Soft = Software()
    Soft.launch()
