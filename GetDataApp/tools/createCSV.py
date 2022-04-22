import csv

col_sleep = ['date','minutesAwake','minutesAsleep','minutesToFallAsleep','timeInBed']
col_hr = ['date','time','value']
col_intra = ['date', 'value']

# Créer un fichier CSV pour les données de sommeil
# n-fic : nom du ficier
# rq : resultat obtenu apres la requete
# date : la date

def initCSV(n_fic, n_col):
    fichier = open(n_fic,'a')
    with fichier:    
        obj = csv.DictWriter(fichier, fieldnames=n_col)
        obj.writeheader()

def createCSV_Sleep (n_fic, rq):

    fichier = open(n_fic,'a')
    with fichier:    
        obj = csv.DictWriter(fichier, fieldnames=col_sleep)
        for v in rq:
            res = dict()
            res['date'] = v["dateOfSleep"]
            res['minutesAwake'] = v["minutesAwake"]
            res['minutesAsleep'] = v["minutesAsleep"]
            res['minutesToFallAsleep'] = v["minutesToFallAsleep"]
            res['timeInBed'] = v["timeInBed"]
            obj.writerow(res)

def createCSV_HR (n_fic, rq, date):

    fichier = open(n_fic,'a')
    with fichier:    
        obj = csv.DictWriter(fichier, fieldnames=col_hr)

        for v in rq:
            v['date'] = date
            obj.writerow(v)

def createCSV_INTRA(n_fic, rq):
    fichier = open(n_fic,'a')
    with fichier:    
        obj = csv.DictWriter(fichier, fieldnames=col_intra)
        for v in rq:
            res = dict()
            res['date'] = v["dateTime"]
            res['value'] = v["value"]
            obj.writerow(res)