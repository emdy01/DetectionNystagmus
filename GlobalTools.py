from GazeTracking.gaze_tracking.GazeTracker import GazeTracker as gt
import os, numpy, csv, cv2
import xlsxwriter as xl
from SaccadeRecognition import SaccadeRecognition

class GlobalTools():
    def __init__(self): # constructeur
        self.tracker = gt() # eye tracker
        self.NotEnoughSamples = False # devient True si le nombre de coordonnées acquises est insuffisant (inférieur à 10)
        self.DetectionRate = 0 # taux de détection des pupilles

    def GetDR(self): # accesseur
        return self.DetectionRate

    def GetNES(self): # accesseur
        return self.NotEnoughSamples

    def FromDataToLists(self, xG,yG,xD,yD):
        """
        Stocke les coordonnées successives des marqueurs des pupilles dans les
        listes xG, yG, xD, yD. Les deux premières listes  correspondent à l'oeil
        gauche, les suivantes à l'oeil droit.
        """

        if self.tracker.pupils_located == True:
            OG = self.tracker.pupil_left_coords()
            xG.append(OG[0])
            yG.append(OG[1])

            OD = self.tracker.pupil_right_coords()
            xD.append(OD[0])
            yD.append(OD[1])

        """
        Les listes ainsi remplies ont même longueur car à chaque trame vidéo
        analysée, les deux pupilles sont détectées.
        """
    def PostReadingAnalyze(self, xG, T, time):
        """
        Sur base des abscisses de l'oeil gauche (xG) et de la durée du flux vidéo
        (time), cette fonction calcule les temps auxquels les trames vidéos sont
        enregistrées et les stocke dans la liste T. Elle renvoie le nombre
        d'éléments de xG.

        """
        if (xG == []):
            long = 0
        else :
            long = len(xG)
            intervalle = float(time)/long
            for i in range(1, long):
                T.append(intervalle*i)

        return long

    def v(self,dcurr, dprev, tcurr, tprev):
        # calcul de vitesse : v = d/t
        d = dcurr - dprev
        t = abs(tcurr - tprev)
        v = float(d)/float(t)
        return v

    def ConcatList(self,A,B): # concaténation de listes
        return [A,B]

    def intersampleVelocity(self, l, L, R, T):
        """
        Calcul des vitesses de déplacements des deux yeux en x et en y
        et stockage dans des listes
        l : nombre de jeux de coordonnées
        L : [xG,yG]
        R : [xD,yD]
        T : liste des temps auxquels sont enregistrées les trames vidéo
        """
        vgdata = [[0],[0]] # Vitesses de déplacement de l'oeil gauche
        vddata = [[0],[0]] # Vitesses de déplacement de l'oeil droit
        for i in range(1,l-1):
            # Calcul de chaque valeur
            VxOG = self.v(L[0][i], L[0][i-1],T[i]/1000,T[i-1]/1000)
            VyOG = self.v(L[1][i], L[1][i-1],T[i]/1000,T[i-1]/1000)
            VxOD = self.v(R[0][i], R[0][i-1],T[i]/1000,T[i-1]/1000)
            VyOD = self.v(R[1][i], R[1][i-1],T[i]/1000,T[i-1]/1000)
            # Stockage dans les listes
            vgdata[0].append(VxOG)
            vgdata[1].append(VyOG)
            vddata[0].append(VxOD)
            vddata[1].append(VyOD)
        return numpy.array(vgdata), numpy.array(vddata)

    def SingleExcelLine(self, ws, i, SingleSac):
        """
        Ecriture dans Excel d'une seule ligne du tableau renvoyé par
        SaccadeRecognition::Microsacc() (SingleSac)
        ws et i sont gérés par la fonction FromDataToExcel.
        """
        for a in range(6):
            if a == 2: # Ecriture de la direction dominante du nystagmus
                if SingleSac[a] == 0:
                    ws.write(i, a, 'H')
                else:
                    ws.write(i, a, 'V')
            else: # Ecriture des autres valeurs de la ligne
                ws.write(i,  a, SingleSac[a])

    def FromFramesToData(self, l, long, xG,yG,xD,yD, T, mode):
        """
        Processus de traitement numérique des coordonnées acquises.
        l : nombres de trames vidéos.
        long : nombres de trames vidéos analysées.
        xG, yG, xD, yD : listes de coordonnées des yeux
        T : liste des temps auxquels sont enregistrées les trames vidéo
        mode : realtime ou videofile
        """
        self.DetectionRate = (long/l)*100 # calcul du taux de détection

        if long < 10:
            self.NotEnoughSamples = True
            return 0

        L = self.ConcatList(xG, yG)
        R = self.ConcatList(xD, yD)


        Vg, Vd = self.intersampleVelocity(long, L,R,T)
        saccade = SaccadeRecognition(L,R,Vg,Vd, T)
        sacG, sacD = saccade.launch(mode)
        return sacG, sacD



    def FromDataToExcel(self, wdir, l, long, xG,yG,xD,yD, T, mode):
        """
        Processus de traitement numérique des coordonnées acquises et de stockage
        des résultats dans les fichiers de sortie de type Excel.
        wdir : chemin d'accès du fichier de sortie
        l : nombres de trames vidéos.
        long : nombres de trames vidéos analysées.
        xG, yG, xD, yD : listes de coordonnées des yeux
        T : liste des temps auxquels sont enregistrées les trames vidéo
        mode : realtime ou videofile
        """
        if self.FromFramesToData(l, long, xG,yG,xD,yD, T, mode) == 0:
            return # on sort de la fonction s'il n'y a pas assez d'éléments à analyser
        else:
            sacG, sacD = self.FromFramesToData(l, long, xG,yG,xD,yD, T, mode)

            file = xl.Workbook(wdir) # fichier Excel

            OG = file.add_worksheet("Oeil gauche") # Feuille de résultats pour l'oeil gauche
            OD = file.add_worksheet("Oeil droit") # Feuille de résultats pour l'oeil droit

            OG.write(0,0,"Taux de détection")
            OG.write(0,1,self.DetectionRate)
            # En-têtes
            OG.write(2,0,"Début de la saccade (ms)")
            OG.write(2,1,"Fin de la saccade (ms)")
            OG.write(2,2,"Direction")
            OG.write(2,3,"Amplitude (px)")
            OG.write(2,4,"Vitesse maximale (px/s)")
            OG.write(2,5,"Fréquence (bat/s)")

            nsac = sacG.shape[0]

            for sac in range(nsac): # Ecriture ligne par ligne
                SingleSac = sacG[sac]
                self.SingleExcelLine(OG, sac + 3, SingleSac)



            OD.write(0, 0, "Taux de détection")
            OD.write(0, 1, self.DetectionRate)
            # En-têtes
            OD.write(2,0,"Début de la saccade")
            OD.write(2,1,"Fin de la saccade")
            OD.write(2,2,"Direction")
            OD.write(2,3,"Amplitude (px)")
            OD.write(2,4,"Vitesse maximale (px/s)")
            OD.write(2,5,"Fréquence (bat/s)")

            nsac = sacD.shape[0]

            for sac in range(nsac):# Ecriture ligne par ligne
                SingleSac = sacD[sac]
                self.SingleExcelLine(OD, sac + 3, SingleSac)

            file.close()

    def FromDataToCSV(self, wdir, l, long, xG,yG,xD,yD, T, mode):
        """
        Processus de traitement numérique des coordonnées acquises et de stockage
        des résultats dans les fichiers de sortie de type CSV.
        wdir : chemin d'accès du fichier de sortie
        l : nombres de trames vidéos.
        long : nombres de trames vidéos analysées.
        xG, yG, xD, yD : listes de coordonnées des yeux
        T : liste des temps auxquels sont enregistrées les trames vidéo
        mode : realtime ou videofile
        """
        if self.FromFramesToData(l, long, xG,yG,xD,yD, T, mode) == 0:
            return # on sort de la fonction s'il n'y a pas assez d'éléments à analyser
        else:
            sacG, sacD = self.FromFramesToData(l, long, xG,yG,xD,yD, T, mode)
            lenG = len(sacG)
            lenD = len(sacD)

            with open(wdir,'w',newline='') as fichiercsv: # Fichier de sortie
                writer=csv.writer(fichiercsv)

                writer.writerow([self.DetectionRate])
                writer.writerow([])

                for i in range(lenG):
                    writer.writerow(list(sacG[i]))

                writer.writerow([])

                for i in range(lenD):
                    writer.writerow(list(sacD[i]))

