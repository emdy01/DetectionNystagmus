from moviepy.editor import VideoFileClip as vfc
import cv2, os
from time import *
wdir = os.path.dirname(os.path.abspath("videofile.py"))
os.chdir(wdir)
from GlobalTools import GlobalTools

class videofile(GlobalTools):
    def __init__(self, WFilePath, OutputPath):
        """
        WFilePath : chemin d'accès du fichier vidéo
        OutputPath : chemin d'accès du fichier de sortie
        """
        GlobalTools.__init__(self)
        self.video = os.path.basename(WFilePath) # nom du fichier vidéo
        self.cap = cv2.VideoCapture(WFilePath) # upload du fichier vidéo
        self.wdir = OutputPath
        self.time = 0 # contiendra la durée de la vidéo


    def read(self):
        """
        Gère :
        1) l'analyse des métadonnées du fichier vidéo
        2) le repérage des pupilles dans les trames vidéos et le stockage de leurs coordonnées
        3) le calcul des temps où les trames vidéos ont été enregistrées
        """
        xG, xD, yG, yD = [], [], [], [] # listes de coordonnées des yeux
        T = [0] # temps où les trames vidéos ont été enregistrées
        video = vfc(self.video)
        self.NumberOfFrames = int(video.fps * video.duration) # nombre de trames vidéos
        self.time = video.duration * 1000

        l = 0 # contiendra le nombre total de trames vidéos enregistrées

        if (self.cap.isOpened()== False):
            print("Error opening video  file")
            return
        while True:
            ret, frame = self.cap.read()
            if ret == True:
                l += 1
                self.tracker.refresh(frame) # analyse des trames vidéos
                self.FromDataToLists(xG,yG, xD,yD) # stockage des coordonnées dans les listes
            else:
                break

        self.cap.release()
        cv2.destroyAllWindows()
        long = self.PostReadingAnalyze(xG,T,self.time) # Remplissage de T et détermination du nombre de jeux de coordonnées

        return l, long, xG, yG, xD, yD, T



    def launch(self, format):
        """
        Processus allant de la lecture du fichiers vidéos à l'écriture du fichier de
        sortie.
        format : extensions du fichier de sortie
        """
        l, long,  xG, yG, xD, yD, T = self.read()
        if format == ".xlsx":
            self.FromDataToExcel(self.wdir, l, long, xG, yG, xD, yD, T, "rt")
        if format == ".csv":
            self.FromDataToCSV(self.wdir, l, long, xG, yG, xD, yD, T, "rt")

    """
    def __call__(self,ext):
        self.launch(ext)
    """
