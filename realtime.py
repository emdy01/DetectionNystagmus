from time import *
import cv2, os
from GlobalTools import GlobalTools

class realtime(GlobalTools):
    def __init__(self, WPath): # constructeur
        """
        WPath : chemin d'accès du fichier de sortie
        """
        GlobalTools.__init__(self)
        self.wdir = WPath
        self.cap = cv2.VideoCapture(0) # accès à la caméra


    def read(self):
        """
        Gère :
        1) le lancement et l'arrêt de la caméra
        2) le repérage des pupilles, le stockage de leurs coordonnées et le lissage
        de ces dernières
        3) le calcul des temps où les trames vidéos ont été enregistrées
        """
        cv2.namedWindow("realtime")
        xG, xD, yG, yD = [], [], [], [] # listes de coordonnées des yeux
        T = [0] # temps où les trames vidéos ont été enregistrées
        l = 0 # contiendra le nombre total de trames vidéos enregistrées
        while True: # Phase où le sujet peut cadrer son visage
            ret, frame = self.cap.read()
            cv2.imshow("realtime", frame) # retour caméra
            if cv2.waitKey(1) & 0xFF == ord(' '):
                break # Quand le sujet appuie sur la barre espace, on passe à la deuxième phase
        StartTime = time() # Lancement du chronomètre
        while True: # Phase d'enregistrement et d'analyse des trames vidéos
            l += 1
            ret, frame = self.cap.read()
            self.tracker.refresh(frame) # analyse des trames vidéos
            af = self.tracker.annotated_frame()
            cv2.imshow("realtime", af) # retour caméra avec marquage des pupilles
            self.FromDataToLists(xG,yG, xD,yD) # stockage des coordonnées dans les listes
            if cv2.waitKey(1) & 0xFF == ord(' '):
                break # Quand le sujet appuie sur la barre espace, la caméra s'arrête

        StopTime = time() #Arrêt du chronomètre
        Duration = (StopTime - StartTime)*1000 # Calcul de la durée de l'enregistrement en millisecondes
        self.cap.release()
        cv2.destroyAllWindows()

        long = self.PostReadingAnalyze(xG,T,Duration) # Remplissage de T et détermination du nombre de jeux de coordonnées

        # lissage des données
        for i in range(long):
            if xG[i] <= xG[i-1] + 1:
                xG[i] = xG[i-1]
            if yG[i] <= yG[i-1] + 1:
                yG[i] = yG[i-1]
            if xD[i] <= xD[i-1] + 1:
                xD[i] = xD[i-1]
            if yD[i] <= yD[i-1] + 1:
                yD[i] = yD[i-1]


        return l,long, xG, yG, xD, yD, T


    def launch(self, format):
        """
        Processus allant du lancement de la caméra à l'écriture du fichier de
        sortie.
        format : extensions du fichier de sortie
        """
        l, long, xG, yG, xD, yD, T = self.read()
        if format == ".xlsx":
            self.FromDataToExcel(self.wdir, l, long, xG, yG, xD, yD, T, "rt")
        if format == ".csv":
            self.FromDataToCSV(self.wdir, l, long, xG, yG, xD, yD, T, "rt")


