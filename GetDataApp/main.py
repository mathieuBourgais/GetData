from ast import Return
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
import os
import fitbit
from datetime import  timedelta

from numpy import column_stack

from tools.createCSV import createCSV_HR, createCSV_Sleep, initCSV, createCSV_INTRA, col_sleep, col_hr, col_intra
from tools.string_date_module import isValidDate, date_to_string, string_to_date, deltaDay
from tools.showGraph import graphSleepByDay, grapheHRbyFen, graphIntraByDay
import tools.gather_keys_oauth2 as Oauth2

class ConnectBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        global CURRENT_CLIENT
        self.parent = parent

        self.labelframe = tk.LabelFrame(parent, text="Connexion")
        self.message = tk.StringVar()
        self.message.set("You are not connected")
        self.connect_message = tk.Label(self.labelframe, textvariable=self.message)
        self.label_CLIENT_ID = tk.Label(self.labelframe, text="Client_ID : ")
        self.label_CLIENT_SECRET = tk.Label(self.labelframe, text="Client_SECRET : ")
        self.entry_CLIENT_ID = tk.Entry(self.labelframe)
        self.entry_CLIENT_SECRET = tk.Entry(self.labelframe)
        self.button_CONNECT = tk.Button(self.labelframe, text = "CONNECT", command=self.connect_client)

        self.label_CLIENT_ID.grid(row = 0, column=0, ipadx = 5)
        self.entry_CLIENT_ID.grid(row = 0,column=1, ipadx = 5)
        self.label_CLIENT_SECRET.grid(row = 0,column=2, ipadx = 5)
        self.entry_CLIENT_SECRET.grid(row = 0,column=3, ipadx = 5)
        self.button_CONNECT.grid(row = 0,column=4, ipadx = 5)
        self.connect_message.grid(row = 1, columnspan=4)
        self.labelframe.grid(ipadx = 5, ipady = 5)
    
    def connect_client(self):
        global CURRENT_CLIENT
        if ((self.entry_CLIENT_ID.get() == "") | (self.entry_CLIENT_SECRET.get() == "")):
            mb.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        CLIENT_ID = self.entry_CLIENT_ID.get().strip()
        CLIENT_SECRET = self.entry_CLIENT_SECRET.get().strip()
        server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
        server.browser_authorize()
        ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
        REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
        CURRENT_CLIENT = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)
        self.message.set("You are connected now")
        
class getData(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.labelFrame = tk.LabelFrame(parent, text="Get Data")
        

        self.label_DATE_START = tk.Label(self.labelFrame, text="Quel jour de debut ? ")
        self.entry_DATE_START = tk.Entry(self.labelFrame)
        self.label_DATE_END = tk.Label(self.labelFrame, text="Quel jour de fin ? ")
        self.entry_DATE_END = tk.Entry(self.labelFrame)
        self.button_SLEEP = tk.Button(self.labelFrame, text="SLEEP", command=lambda: self.action("sleep"))
        self.button_HR = tk.Button(self.labelFrame, text="HEART RATE", command=lambda: self.action("hr"))
        self.button_CAL = tk.Button(self.labelFrame, text="CALORIES", command=lambda: self.action("calories"))
        self.button_FLOORS = tk.Button(self.labelFrame, text="FLOORS", command=lambda: self.action("floors"))
        self.button_STEPS = tk.Button(self.labelFrame, text="STEPS", command=lambda: self.action("steps"))
        self.button_DIST = tk.Button(self.labelFrame, text="DISTANCE", command=lambda: self.action("distance"))
        self.button_ELEVATION = tk.Button(self.labelFrame, text="ELEVATION", command=self.test)

        
        self.label_DATE_START.grid(row=0, column=0, sticky="nsew")
        self.label_DATE_END.grid(row = 1, column= 0)
        self.entry_DATE_START.grid(row = 0, column = 1)
        self.entry_DATE_END.grid(row=1, column= 1)
        self.button_SLEEP.grid(row=0, column=2)
        self.button_FLOORS.grid(row=0, column=3)
        self.button_ELEVATION.grid(row=0, column=4)
        self.button_HR.grid(row=1, column=2)
        self.button_STEPS.grid(row=1, column=3)
        self.button_DIST.grid(row=1, column=4)
        self.button_CAL.grid(row=2, column=2)

        self.labelFrame.grid()
    def test(self):
        print(CURRENT_CLIENT.user_profile_get()['user']['fullName'])
    def isValidChamp(self):
        if ((self.entry_DATE_START.get() == "") | (self.entry_DATE_END.get() == "")):
            mb.showerror("Erreur", "Veuillez remplir tous les champs")
            return False
        if(not(isValidDate(self.entry_DATE_START.get()))):
            mb.showerror("Erreur", "Le champ date de debut n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
            return False
        if(not(isValidDate(self.entry_DATE_END.get()))):
            mb.showerror("Erreur", "Le champ date de fin n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
            return False
        return True

    def isValidChamp(self):
        if ((self.entry_DATE_START.get() == "") | (self.entry_DATE_END.get() == "")):
            mb.showerror("Erreur", "Veuillez remplir tous les champs")
            return False
        if(not(isValidDate(self.entry_DATE_START.get()))):
            mb.showerror("Erreur", "Le champ date de debut n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
            return False
        if(not(isValidDate(self.entry_DATE_END.get()))):
            mb.showerror("Erreur", "Le champ date de fin n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
            return False
        return True

    def action(self, action):
        if(not(self.isValidChamp())):
            return
        d = string_to_date(self.entry_DATE_START.get())
        if(action == "sleep"):
            nom_fichier = 'data/data_sleep_' + self.entry_DATE_START.get() + '_to_'+ self.entry_DATE_END.get() + '.csv'
            initCSV(nom_fichier, col_sleep)
        elif(action =="hr"):
            nom_fichier = 'data/data_heart_rate_' + self.entry_DATE_START.get() + '_to_'+ self.entry_DATE_END.get() + '.csv'
            initCSV(nom_fichier, col_hr)
        else:
            nom_fichier = 'data/data_' + action + '_' + self.entry_DATE_START.get() + '_to_' + self.entry_DATE_END.get() + '.csv'
            initCSV(nom_fichier, col_intra)  
        if(action == "sleep"):
            url = "https://api.fitbit.com/1.2/user/-/sleep/date/"+ self.entry_DATE_START.get() + "/" + self.entry_DATE_END.get() + ".json"
            fit_statsSleep = CURRENT_CLIENT.make_request(url)
            createCSV_Sleep(nom_fichier, fit_statsSleep['sleep'])
        elif(action == "hr"):
            
            for i in range(deltaDay(self.entry_DATE_END.get(), self.entry_DATE_START.get()) + 1):
                str_d = date_to_string(d)
                fit_statsHR = CURRENT_CLIENT.intraday_time_series('activities/heart', base_date= str_d, detail_level='1min')
                createCSV_HR(nom_fichier, fit_statsHR['activities-heart-intraday']['dataset'], str_d)
                d = d + timedelta(1)
        else:
            fit_statsSteps = CURRENT_CLIENT.time_series('activities/' + action , base_date= self.entry_DATE_START.get(), end_date=self.entry_DATE_END.get())
            createCSV_INTRA(nom_fichier, fit_statsSteps['activities-' + action])
        
        mb.showinfo("Succes", "Le fichier a été créer")

class Graph(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.filepath = ""
        self.fileType = ""

        self.labelFrame = tk.LabelFrame(parent, text="Graphics", padx=20, pady=20)
        self.scopeframe = tk.LabelFrame(self.labelFrame, text="Scope : (Use only for Heartrate)")

        self.label_DATE_START = tk.Label(self.scopeframe, text="Quel jour de debut ? ")
        self.entry_DATE_START = tk.Entry(self.scopeframe)
        self.label_DATE_END = tk.Label(self.scopeframe, text="Quel jour de fin ? ")
        self.entry_DATE_END = tk.Entry(self.scopeframe)
        self.label_HOUR_START = tk.Label(self.scopeframe, text="Quel minute de debut ? ")
        self.entry_HOUR_START = tk.Entry(self.scopeframe)
        self.label_HOUR_END = tk.Label(self.scopeframe, text="Quel minute de fin ? ")
        self.entry_HOUR_END = tk.Entry(self.scopeframe)
        self.button_BROWSE = tk.Button(self.labelFrame, text="BROWSE", command=self.browseFile)
        self.button_SHOW = tk.Button(self.labelFrame, text="SHOW", command=self.show)
        self.text = tk.StringVar()
        self.text.set("file :")
        self.label_PATH = tk.Label(self.labelFrame, textvariable=self.text)
        self.label_MIN = tk.Label(self.scopeframe, text="Mean of time")
        self.entry_MIN = tk.Entry(self.scopeframe)

        self.label_PATH.grid(row = 0, column= 0, sticky=tk.W)
        self.button_BROWSE.grid(row = 1, column= 0, sticky=tk.W)

        self.label_DATE_START.grid(row = 0, column=0)
        self.label_HOUR_START.grid(row = 1, column=0)
        self.entry_DATE_START.grid(row = 0, column=1)
        self.entry_HOUR_START.grid(row=1, column=1)

        self.label_DATE_END.grid(row = 0, column= 2)
        self.label_HOUR_END.grid(row = 1, column= 2)
        
        self.entry_DATE_END.grid(row = 0, column=3)
        self.entry_HOUR_END.grid(row=1, column=3)

        self.label_MIN.grid(row = 2, column= 0)
        self.entry_MIN.grid(row = 2, column=1)

        self.button_BROWSE.grid(row = 1, column= 0)

        self.scopeframe.grid(row = 2)
        self.button_SHOW.grid(row = 2, column=1, padx = 10,ipadx=10)
        self.labelFrame.grid()

    def browseFile(self):
        
        self.filepath = fd.askopenfilename(initialdir = os.getcwd(), title = "Select a File", filetypes = (("Text files", "*.csv*"), ("all files", "*.*")))
        self.setText(self.filepath)
        filepathsplitted = self.filepath.split('/')
        namefile = filepathsplitted[len(filepathsplitted) - 1]
        self.fileType = namefile.split('_')[1]
        

    def setText(self, str):
        self.text.set(str)

    def isValidChamp(self):
        if ((self.entry_DATE_START.get() == "") | (self.entry_DATE_END.get() == "") | (self.entry_MIN_START.get() == "") | (self.entry_MIN_END.get() == "") | (self.entry_MIN.get() == "")):
            mb.showerror("Erreur", "Veuillez remplir tous les champs")
            return False
        if(not(isValidDate(self.entry_DATE_START.get()))):
            mb.showerror("Erreur", "Le champ date de debut n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
            return False
        if(not(isValidDate(self.entry_DATE_END.get()))):
            mb.showerror("Erreur", "Le champ date de fin n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
            return False
        if(not(self.isValidTime(self.entry_HOUR_START.get()))):
             mb.showerror("Erreur", "Le champ heure de fin n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
             return False
        if(not(self.isValidTime(self.entry_HOUR_END.get()))):
             mb.showerror("Erreur", "Le champ heure de fin n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
             return False
        if(not(self.entry_MIN.get().isdigit())):
            mb.showerror("Erreur", "Le champ moyenne doit etre un nombre")
            return False
        return True
    
    def show(self):
        if(self.fileType == "heart"):
            grapheHRbyFen(self.filepath, int(self.entry_MIN.get()), self.entry_DATE_START.get(), self.entry_HOUR_START.get(), self.entry_DATE_END.get(), self.entry_HOUR_END.get())
        elif(self.fileType == "sleep"):
            graphSleepByDay(self.filepath)
        else:
            graphIntraByDay(self.filepath, self.fileType)


class MainApplication(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.connectbar = ConnectBar(self.parent)
        self.getData = getData(self.parent)
        self.Graph = Graph(self.parent)




if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).grid()
    root.mainloop()
