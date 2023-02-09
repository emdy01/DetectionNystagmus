import numpy

class SaccadeRecognition() :
    def __init__(self,L,R, Vg, Vd, T): # constructeur
        """
        L : liste de 2 listes. 1° liste : x de OG. 2° liste : y de OG
        R : liste de 2 listes  1° liste : x de OD. 2° liste : y de OD
        Vg et Vd, des listes composées respectivement des vitesses de deéplacement de l'oeil gauche et de l'oeil droit
        T : liste des temps auxquels sont enregistrées les trames vidéo
        """
        self.OG = L
        self.OD = R
        self.Vg = Vg
        self.Vd = Vd
        self.T = T

    def Microsacc(self, data, vdata, T, mode):
        """
        Détection des nystagmus et calcul des paramètres de sorties sur base de
        la méthode d'Engbert et Kliegl.
        Data : liste de coordonnées d'un oeil
        Vdata : liste de vitesses de déplacement d'un oeil
        T : liste des temps auxquels sont enregistrées les trames vidéo
        mode : realtime ou videofile
        """

        # Réglage de la sensibilité
        if mode == "rt":
            minSamples = 2
        if mode == "vf":
            minSamples = 3

        #Méthode d'Engbert et Kliegl
        msdx = numpy.sqrt(numpy.nanmedian(vdata[0,:]**2) - numpy.nanmedian(vdata[0,:])**2)
        msdy = numpy.sqrt(numpy.nanmedian(vdata[1,:]**2) - numpy.nanmedian(vdata[1,:])**2)

        radiusX = 6 * msdx
        radiusY = 6 * msdy

        if radiusX == 0:
            radiusX = 0.00001 # Eviter les cas où on divise par 0
        if radiusY == 0:
            radiusY = 0.00001 # Eviter les cas où on divise par 0

        vabs = numpy.sqrt(vdata[0,:]**2+vdata[1,:]**2)
        calcul = (vdata[0,:]/radiusX)**2 + (vdata[1,:]/radiusY)**2
        one = numpy.array([1 for i in range(len(calcul))])
        idx = numpy.where(numpy.greater(calcul,one))[0]


        N = len(idx)
        sac = []
        nsac = 0
        dur = 1
        a = 1
        k = 0

        while k < N-1:
            if idx[k+1]-idx[k] == 1:
                dur = dur+1
            else:
                if dur >= minSamples:
                    b = k
                    sac.append([idx[a], idx[b], 0, 0, 0, 0])
                    nsac += 1
                a = k+1
                dur = 1
            k += 1
        if dur >= minSamples:
            b = k
            sac.append([idx[a], idx[b], 0, 0, 0, 0])
            nsac += 1

        sac = numpy.array(sac)
        """
        sac est le tableau qui va être renvoyé en sortie de la fonction.
        Chaque ligne correspond à un nystagmus.
        A ce stade du code, les valeurs non nulles correspondent aux indices des temps de début et de fin de nystagmus.
        """


        for s in range(nsac):
            a = int(sac[s, 0])
            b = int(sac[s, 1])
            if a >= b:
                continue # on s'assure que tous les temps de début sont inférieurs aux temps de fin
            vpeak = numpy.max(vabs[a:b]) # vitesse maximale
            delx = data[0][b] - data[0][a] # déplacement du nystagmus en x
            dely = data[1][b] - data[1][a] # déplacement du nystagmus en y
            phi = 180/numpy.pi*numpy.arctan2(dely, delx) # angle du nystagmus par rapport à l'horizontale
            sac[s, 0] = T[a] # temps de début de nystagmus
            sac[s, 1] = T[b] # temps de fin de nystagmus

            if (abs(phi) <= 60) or (abs(phi) >= 135):
                sac[s, 2] = 0
                ampl = abs(delx) # amplitude si direction dominante horizontale
            else:
                sac[s, 2] = 1
                ampl = abs(dely) # amplitude si direction dominante verticale

            sac[s, 3] = ampl

            if ampl == 0:
                ampl = 0.00001 # Eviter les cas où on divise par 0

            sac[s, 4] = vpeak

            sac[s, 5] = vpeak/ampl # fréquence du nystagmus

        s = 0
        while s < nsac:
            if sac[s,2] == 0: # on supprime les cas où l'amplitude est nulle car il n'y a alors pas de déplacement oculaire
                sac = numpy.delete(sac, s, 0)
                nsac -=1
            s += 1


        return sac

    def launch(self, mode):
        sacG = self.Microsacc(self.OG, self.Vg, self.T, mode) # Microsacc sur les données de l'oeil gauche
        sacD = self.Microsacc(self.OD, self.Vd, self.T, mode) # Microsacc sur les données de l'oeil droit
        return  sacG, sacD






