import csv

list = ['heart', 'steps', 'floors', 'elevation', 'distance']

col_sleep = ['date','minutesAwake','minutesAsleep','minutesToFallAsleep','timeInBed']
col = ['date','time','value']
col_cal = ['date' , 'level', 'mets', 'time' ,'value']

# Créer un fichier CSV pour les données de sommeil
# n-fic : nom du ficier
# rq : resultat obtenu apres la requete
# date : la date

def initCSV(n_fic, type):
    fichier = open(n_fic,'a')
    with fichier:    
        if(type in list):
            obj = csv.DictWriter(fichier, fieldnames=col)
            obj.writeheader()
        elif(type == "calories"):
            obj = csv.DictWriter(fichier, fieldnames=col_cal)
            obj.writeheader()
        elif(type == "sleep"):
            pass


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

def createCSV (n_fic, rq, date, type):
    fichier = open(n_fic,'a')
    with fichier: 
        if(type in list):  
            obj = csv.DictWriter(fichier, fieldnames=col)
            for v in rq:
                v['date'] = date
                obj.writerow(v)
        elif(type == "calories"):
            obj = csv.DictWriter(fichier, fieldnames=col_cal)
            for v in rq:
                v['date'] = date
                obj.writerow(v)
        elif(type == "sleep"):
            pass
