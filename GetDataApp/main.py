import fitbit
from numpy import column_stack
import tools.gather_keys_oauth2 as Oauth2
from datetime import  timedelta
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
import os

from tools.createCSV import createCSV_HR, createCSV_Sleep, initCSV, createCSV_INTRA, col_sleep, col_hr, col_intra
from tools.string_date_module import isValidDate, date_to_string, string_to_date, deltaDay
from tools.showGraph import grapheHRbyFen, graphIntraByDay



# Action a effectué quand l'evenement quitter la fenetre est fait
def on_closing(): 
    global app
    app.destroy()

# Place les composant dans la fenetre main principale
def placeComponentApp():
    label_CLIENT_ID.grid(row = 0)
    label_CLIENT_SECRET.grid(row = 1)
    entry_CLIENT_ID.grid(row = 0, column = 1)
    entry_CLIENT_SECRET.grid(row = 1, column = 1)
    button_CONNECT.grid(row = 2, column=0, columnspan= 2)
    button_SHOW.grid(row = 3,columnspan= 2)

# Place les composant dans la fenetre apres la connexion
def placeComponentConnexion():
    label_BIENVENUE.grid(row = 0)
    button_HR.grid(row = 1, column= 0)
    button_SLEEP.grid(row = 1, column = 1)
    button_INTRADAY.grid(row = 1, column = 2)
    button_RETURN.grid(row = 1, column = 3)

# Place les composant dans la fenetre pour recupérer les données du coeur
def placeComponentHR():
    label_INFO_HR.grid(row = 0, columnspan=2, sticky=tk.E+tk.W)
    label_DATE.grid(row = 1, column = 0)
    entry_DATE_START.grid(row = 1, column = 1)
    label_TIME.grid(row=2, column=0)
    entry_DATE_END.grid(row = 2, column= 1)
    button_GETHR.grid(row = 3, column= 0)
    button_RETURN.grid(row = 3, column= 1)

# Place les composant dans la fenetre pour recupérer les donnée de sommeil
def placeComponentSleep():
    label_INFO_HR.grid(row = 0, columnspan=2, sticky=tk.E+tk.W)
    label_DATE.grid(row = 1, column = 0)
    entry_DATE_START.grid(row = 1, column = 1)
    label_TIME.grid(row=2, column=0)
    entry_DATE_END.grid(row = 2, column= 1)
    button_GETSLEEP.grid(row = 3, column= 0)
    button_RETURN.grid(row = 3, column= 1)

def placeComponentIntraday():
    label_INFO_HR.grid(row = 0, columnspan=2, sticky=tk.E+tk.W)
    label_DATE.grid(row = 1, column = 0)
    entry_DATE_START.grid(row = 1, column = 1)
    label_TIME.grid(row=2, column=0)
    entry_DATE_END.grid(row = 2, column= 1)
    button_STEPS.grid(row = 3, column= 0)
    button_FLOORS.grid(row = 3, column= 1)
    button_CALORIES.grid(row = 3, column= 2)
    button_DISTANCE.grid(row = 3, column= 3)
    button_ELEVATION.grid(row = 3, column= 4)
    button_RETURN.grid(row = 3, column= 5)

def placeComponentGraph():
    button_FILE.pack()
# Action de retour a la 1ere fenetre
def quit_app_connexion():
    app_CONNEXION.destroy()
    app.deiconify()

# Action de retour a la 2eme fenetre
def quit_data():
    appDATA.destroy()
    app_CONNEXION.deiconify()

def isValidChamp():
    if ((entry_DATE_START.get() == "") | (entry_DATE_END.get() == "")):
        mb.showerror("Erreur", "Veuillez remplir tous les champs")
        return False
    if(not(isValidDate(entry_DATE_START.get()))):
        mb.showerror("Erreur", "Le champ date de debut n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
        return False
    if(not(isValidDate(entry_DATE_END.get()))):
        mb.showerror("Erreur", "Le champ date de fin n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
        return False
    return True

def action(action):
    if(not(isValidChamp())):
      return
    d = string_to_date(entry_DATE_START.get())
    if(action == "sleep"):
        nom_fichier = 'data/data_sleep_' + entry_DATE_START.get() + '_to_'+ entry_DATE_END.get() + '.csv'
        initCSV(nom_fichier, col_sleep)
    elif(action =="hr"):
        nom_fichier = 'data/data_heart_rate_' + entry_DATE_START.get() + '_to_'+ entry_DATE_END.get() + '.csv'
        initCSV(nom_fichier, col_hr)
    else:
        nom_fichier = 'data/data_' + action + '_' + entry_DATE_START.get() + '_to_' + entry_DATE_END.get() + '.csv'
        initCSV(nom_fichier, col_intra)  
    if(action == "sleep"):
        url = "https://api.fitbit.com/1.2/user/-/sleep/date/"+ entry_DATE_START.get() + "/" + entry_DATE_END.get() + ".json"
        fit_statsSleep = client.make_request(url)
        createCSV_Sleep(nom_fichier, fit_statsSleep['sleep'])
    elif(action == "hr"):
        
        for i in range(deltaDay(entry_DATE_END.get(), entry_DATE_START.get()) + 1):
            str_d = date_to_string(d)
            fit_statsHR = client.intraday_time_series('activities/heart', base_date= str_d, detail_level='1min')
            createCSV_HR(nom_fichier, fit_statsHR['activities-heart-intraday']['dataset'], str_d)
            d = d + timedelta(1)
    else:
        fit_statsSteps = client.time_series('activities/' + action , base_date= entry_DATE_START.get(), end_date=entry_DATE_END.get())
        createCSV_INTRA(nom_fichier, fit_statsSteps['activities-' + action])
    
    mb.showinfo("Succes", "Le fichier a été créer")


def getSleep():
    global appDATA, button_GETSLEEP, label_INFO_HR, label_DATE, entry_DATE_START, button_RETURN, entry_DATE_END, label_TIME
    appDATA = tk.Toplevel(app_CONNEXION)
    app_CONNEXION.withdraw()
    label_INFO_HR = tk.Label(appDATA, text="Vous pouve récupérer les données de sommeil a partir d'un date donnée et un nombre de jour")
    label_DATE = tk.Label(appDATA, text="Quel jour de debut ?")
    entry_DATE_START = tk.Entry(appDATA)
    label_TIME = tk.Label(appDATA, text="Quel jour de fin ?")
    entry_DATE_END = tk.Entry(appDATA)
    button_GETSLEEP = tk.Button(appDATA, text="GET SLEEP", command=lambda: action("sleep"))
    button_RETURN = tk.Button(appDATA, text="RETURN", command=quit_data)

    placeComponentSleep()
    appDATA.protocol("WM_DELETE_WINDOW", on_closing)

def getHR():
    global appDATA, button_GETHR, label_INFO_HR, label_DATE, entry_DATE_START, button_RETURN, entry_DATE_END, label_TIME
    appDATA = tk.Toplevel(app_CONNEXION)
    app_CONNEXION.withdraw()
    label_INFO_HR = tk.Label(appDATA, text="Vous pouve récupérer le HR a partir d'un date donnée et un nombre de jour")
    label_DATE = tk.Label(appDATA, text="Quel jour de debut ?")
    entry_DATE_START = tk.Entry(appDATA)
    label_TIME = tk.Label(appDATA, text="Quel jour de fin ?")
    entry_DATE_END = tk.Entry(appDATA)
    button_GETHR = tk.Button(appDATA, text="GET HEARTRATE", command=lambda: action("hr"))
    button_RETURN = tk.Button(appDATA, text="RETURN", command=quit_data)

    placeComponentHR()
    appDATA.protocol("WM_DELETE_WINDOW", on_closing)

def getIntraday():
    global appDATA
    global button_STEPS, button_FLOORS, button_CALORIES, button_DISTANCE, button_ELEVATION, button_RETURN
    global label_INFO_HR, label_DATE, label_TIME
    global entry_DATE_START, entry_DATE_END

    appDATA = tk.Toplevel(app_CONNEXION)
    app_CONNEXION.withdraw()
    label_INFO_HR = tk.Label(appDATA, text="Vous pouve récupérer un bon nombre de donnée si dessous")
    label_DATE = tk.Label(appDATA, text="Quel jour de debut ?")
    entry_DATE_START = tk.Entry(appDATA)
    label_TIME = tk.Label(appDATA, text="Quel jour de fin ?")
    entry_DATE_END = tk.Entry(appDATA)
    button_STEPS = tk.Button(appDATA, text="GET STEPS", command=lambda: action("steps"))
    button_FLOORS = tk.Button(appDATA, text="GET FLOORS", command=lambda: action("floors"))
    button_CALORIES = tk.Button(appDATA, text="GET CALORIES", command=lambda: action("calories"))
    button_DISTANCE = tk.Button(appDATA, text="GET DISTANCE", command=lambda: action("distance"))
    button_ELEVATION = tk.Button(appDATA, text="GET ELEVATION", command=lambda: action("elevation"))
    button_RETURN = tk.Button(appDATA, text="RETURN", command=quit_data)

    placeComponentIntraday()
    appDATA.protocol("WM_DELETE_WINDOW", on_closing)

def connect_client():
    global client, server, app_CONNEXION, label_BIENVENUE, button_HR, button_RETURN, button_SLEEP, button_INTRADAY
    if ((entry_CLIENT_ID.get() == "") | (entry_CLIENT_SECRET.get() == "")):
            mb.showerror("Erreur", "Veuillez remplir tous les champs")
            return
    CLIENT_ID = entry_CLIENT_ID.get()
    CLIENT_SECRET = entry_CLIENT_SECRET.get()
    server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    server.browser_authorize()
    ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
    print(ACCESS_TOKEN)
    REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
    print(REFRESH_TOKEN)
    client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)
    nom = client.user_profile_get()['user']['fullName']

    app_CONNEXION = tk.Toplevel(app)
    app_CONNEXION.lift()

    label_BIENVENUE = tk.Label(app_CONNEXION, text= "Bienvenue, " + nom + "\nQuelles données voulez vous récupérer ?")
    button_HR = tk.Button(app_CONNEXION, text = "Heart Rate", command= getHR)
    button_SLEEP = tk.Button(app_CONNEXION, text='Sleep', command=getSleep)
    button_INTRADAY = tk.Button(app_CONNEXION, text="INTRADAY", command= getIntraday)
    button_RETURN = tk.Button(app_CONNEXION, text="Retour", command= quit_app_connexion)
    placeComponentConnexion()
    
    app.withdraw()
    app_CONNEXION.protocol("WM_DELETE_WINDOW", on_closing)

# A FINIR -------------------------------------------------------------
# TESTER LE NOM DU FICHIER POUR FAIRE APPEL A LA BONNE FONCTION
def browseFiles(): 
    filename = fd.askopenfilename(initialdir = os.getcwd(), 
                                  title = "Select a File", 
                                  filetypes = (("Text files", "*.csv*"), 
                                               ("all files", "*.*"))) 
    graphIntraByDay(filename, "floors")
# -------------------------------------------------------------
    

def show_graph():
    global app_graph
    global button_FILE

    app_graph = tk.Toplevel(app)
    button_FILE = tk.Button(app_graph,  
                        text = "Browse Files", 
                        command = browseFiles)  

    placeComponentGraph()
    app.withdraw()
    app_graph.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == "__main__":

    global app
    
    app = tk.Tk()
    app.geometry("500x500")
    label_CLIENT_ID = tk.Label(app, text="Client_ID")
    label_CLIENT_SECRET = tk.Label(app, text="Client_SECRET")
    entry_CLIENT_ID = tk.Entry(app)
    entry_CLIENT_ID.insert(0, "238D8K")
    entry_CLIENT_SECRET = tk.Entry(app)
    entry_CLIENT_SECRET.insert(0, "c1adab2e668a47f7123cba0da42a3319")
    button_CONNECT = tk.Button(app, text = "CONNECT", command=connect_client, width= 20)
    button_SHOW = tk.Button(app, text= "GRAPHIQUES", command=show_graph, width= 20)

    placeComponentApp()
    app.mainloop()