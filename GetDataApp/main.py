import platform
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
import os
import fitbit
from datetime import  timedelta


from tools.createCSV import createCSV, createCSV_Sleep, initCSV
from tools.string_date_module import isValidDate, date_to_string, string_to_date, deltaDay, isValidTime
from tools.showGraph import graphList, graphListSolo
import tools.gather_keys_oauth2 as Oauth2

class ConnectBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        global CURRENT_CLIENT
        self.parent = parent

    # LabelFrame
        self.labelframe = tk.LabelFrame(parent, text="Connexion")
    # Variables
        self.message = tk.StringVar()
        self.message.set("You are not connected")
    # Buttons
        self.button_CONNECT = tk.Button(self.labelframe, text = "CONNECT", command=self.connect_client)
    # Labels
        self.label_CLIENT_ID = tk.Label(self.labelframe, text="Client_ID : ")
        self.label_CLIENT_SECRET = tk.Label(self.labelframe, text="Client_SECRET : ")
        self.connect_message = tk.Label(self.labelframe, textvariable=self.message)
    # Entries
        self.entry_CLIENT_ID = tk.Entry(self.labelframe)
        self.entry_CLIENT_SECRET = tk.Entry(self.labelframe)

    # Pour les test a mettre en commentaire des la vrai publicataion de l'application
        self.entry_CLIENT_ID.insert(0,'238D8K')
        self.entry_CLIENT_SECRET.insert(0,'c1adab2e668a47f7123cba0da42a3319')

        self.placeComponent()
        
    def placeComponent(self):
    # Labels
        self.label_CLIENT_ID.grid(row = 0, column=0, ipadx = 5)
        self.label_CLIENT_SECRET.grid(row = 0,column=2, ipadx = 5)
    # Entries
        self.entry_CLIENT_ID.grid(row = 0,column=1, ipadx = 5)
        self.entry_CLIENT_SECRET.grid(row = 0,column=3, ipadx = 5)
    # Buttons
        self.button_CONNECT.grid(row = 0,column=4, ipadx = 5)
        self.connect_message.grid(row = 1, columnspan=5)
    # LabelFrame
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
    
    # LabelFrame
        self.labelFrame = tk.LabelFrame(parent, text="Get Data")
    # Labels
        self.label_DATE_START = tk.Label(self.labelFrame, text="Quel jour de debut ? ")
        self.label_DATE_END = tk.Label(self.labelFrame, text="Quel jour de fin ? ")
    # Buttons
        #self.button_SLEEP = tk.Button(self.labelFrame, text="SLEEP", command=lambda: self.action("sleep"))
        self.button_HR = tk.Button(self.labelFrame, text="HEART RATE", command=lambda: self.action("heart"))
        self.button_CAL = tk.Button(self.labelFrame, text="CALORIES", command=lambda: self.action("calories"))
        self.button_FLOORS = tk.Button(self.labelFrame, text="FLOORS", command=lambda: self.action("floors"))
        self.button_STEPS = tk.Button(self.labelFrame, text="STEPS", command=lambda: self.action("steps"))
        self.button_DIST = tk.Button(self.labelFrame, text="DISTANCE", command=lambda: self.action("distance"))
        self.button_ELEVATION = tk.Button(self.labelFrame, text="ELEVATION", command=lambda: self.action("elevation"))
    # Entries
        self.entry_DATE_START = tk.Entry(self.labelFrame)
        self.entry_DATE_END = tk.Entry(self.labelFrame)
        
        self.placeComponent()

    def placeComponent(self):
    # Labels
        self.label_DATE_START.grid(row=0, column=0, sticky="nsew")
        self.label_DATE_END.grid(row = 1, column= 0)
    # Entries
        self.entry_DATE_START.grid(row = 0, column = 1)
        self.entry_DATE_END.grid(row=1, column= 1)
    # Buttons
        #self.button_SLEEP.grid(row=0, column=2)
        self.button_FLOORS.grid(row=0, column=3)
        self.button_ELEVATION.grid(row=0, column=4)
        self.button_HR.grid(row=1, column=2)
        self.button_STEPS.grid(row=1, column=3)
        self.button_DIST.grid(row=1, column=4)
        #self.button_CAL.grid(row=2, column=2)
        self.button_CAL.grid(row = 0, column = 2)
    # LabelFrame
        self.labelFrame.grid()
        
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
        plt = platform.system()
        if(plt == "Windows"):
            sep = '\\'
        else:
            sep = '/'
        d = string_to_date(self.entry_DATE_START.get())
        if(action =="heart"):
            nom_fichier = 'data' + sep + 'data_heart_rate_' + self.entry_DATE_START.get() + '_to_'+ self.entry_DATE_END.get() + '.csv'
            initCSV(nom_fichier, "heart")
        else:
            nom_fichier = 'data/data_' + action + '_' + self.entry_DATE_START.get() + '_to_' + self.entry_DATE_END.get() + '.csv'
            initCSV(nom_fichier, action)  
        if(action == "sleep"):
            url = "https://api.fitbit.com/1.2/user/-/sleep/date/"+ self.entry_DATE_START.get() + "/" + self.entry_DATE_END.get() + ".json"
            fit_statsSleep = CURRENT_CLIENT.make_request(url)
            createCSV_Sleep(nom_fichier, fit_statsSleep['sleep'])
        else:
            for i in range(deltaDay(self.entry_DATE_END.get(), self.entry_DATE_START.get()) + 1):
                str_d = date_to_string(d)
                fit_statsHR = CURRENT_CLIENT.intraday_time_series('activities/' + action, base_date= str_d, detail_level='1min')
                createCSV(nom_fichier, fit_statsHR['activities-'+ action +'-intraday']['dataset'], str_d, action)
                d = d + timedelta(1)
        mb.showinfo("Succes", "Le fichier a été créer")

class Graph(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.filepathText = ""
        self.filepath = ""
        self.fileType = ""
        self.list_file = []

    # LabelFrame
        self.labelFrame = tk.LabelFrame(parent, text="Graphics", padx=20, pady=20)
        self.scopeframe = tk.LabelFrame(self.labelFrame, text="Scope : (Use only for Heartrate)")
    # Variables
        self.chkValue = tk.BooleanVar()
        self.text = tk.StringVar()
        self.text.set("file :")
    # Labels
        self.label_DATE_START = tk.Label(self.scopeframe, text="Quel jour de debut ? ")
        self.label_DATE_END = tk.Label(self.scopeframe, text="Quel jour de fin ? ")
        self.label_HOUR_START = tk.Label(self.scopeframe, text="Quel minute de debut ? ")
        self.label_HOUR_END = tk.Label(self.scopeframe, text="Quel minute de fin ? ")
        self.label_PATH = tk.Label(self.labelFrame, textvariable=self.text)
        self.label_MIN = tk.Label(self.scopeframe, text="Mean of time")
    # Buttons
        self.button_BROWSE = tk.Button(self.labelFrame, text="BROWSE", command=self.browseFile)
        self.button_SHOW = tk.Button(self.labelFrame, text="SHOW", command=self.show)
        self.button_REMOVE = tk.Button(self.labelFrame, text="REMOVE FILES", command=self.removeFiles)
    # Entries
        self.entry_DATE_START = tk.Entry(self.scopeframe)
        self.entry_DATE_END = tk.Entry(self.scopeframe)
        self.entry_HOUR_START = tk.Entry(self.scopeframe)
        self.entry_HOUR_END = tk.Entry(self.scopeframe)
        self.entry_MIN = tk.Entry(self.scopeframe)
    # CheckButtons
        self.checkbox = tk.Checkbutton(self.scopeframe, text="ensemle", variable = self.chkValue )

        self.placeComponent()
        
    def placeComponent(self):
    # Labels
        self.label_PATH.grid(row = 0, column= 0, sticky=tk.W)
        self.label_DATE_START.grid(row = 0, column=0)
        self.label_HOUR_START.grid(row = 1, column=0)
        self.label_DATE_END.grid(row = 0, column= 2)
        self.label_HOUR_END.grid(row = 1, column= 2)
        self.label_MIN.grid(row = 2, column= 0)
    # Buttons
        self.button_BROWSE.grid(row = 1, column= 0, sticky=tk.W)
        self.button_REMOVE.grid(row = 1, column = 1, sticky=tk.W , ipadx = 5)
        self.button_BROWSE.grid(row = 1, column= 0)
        self.button_SHOW.grid(row = 2, column=1, padx = 10,ipadx=10)
    # Entries       
        self.entry_DATE_START.grid(row = 0, column=1)
        self.entry_HOUR_START.grid(row=1, column=1)
        self.entry_DATE_END.grid(row = 0, column=3)
        self.entry_HOUR_END.grid(row=1, column=3)
        self.entry_MIN.grid(row = 2, column=1)
    # CheckButtons
        self.checkbox.grid(row = 2, column=3)
    # LabelFrame
        self.scopeframe.grid(row = 2)
        self.labelFrame.grid()

    # Pour les test a mettre en commentaire des la vrai publicataion de l'application
        self.entry_DATE_START.insert(0,'2022-04-05')
        self.entry_DATE_END.insert(0,'2022-04-05')
        self.entry_HOUR_START.insert(0,'06:00:00')
        self.entry_HOUR_END.insert(0,'15:00:00')
        self.entry_MIN.insert(0,'60')

    def browseFile(self):
        
        self.filepath = fd.askopenfilename(initialdir = os.getcwd(), title = "Select a File", filetypes = (("Text files", "*.csv*"), ("all files", "*.*")))
        if (self.filepath in self.list_file):
            mb.showerror("File", "Le fichier est deja ouvert")
            return
        self.filepathText = self.filepathText + self.filepath + '\n'
        self.setText(self.filepathText)
        self.list_file.append(self.filepath)
        filepathsplitted = self.filepath.split('/')
        namefile = filepathsplitted[len(filepathsplitted) - 1]
        self.fileType = namefile.split('_')[1] 
        
    def removeFiles(self):
        self.list_file = []
        self.filepathText = ""
        self.setText("file :")

    def setText(self, str):
        self.text.set(str)

    def isValidChamp(self):
        if ((self.entry_DATE_START.get() == "") | (self.entry_DATE_END.get() == "") | (self.entry_HOUR_START.get() == "") | (self.entry_HOUR_END.get() == "") | (self.entry_MIN.get() == "")):
            mb.showerror("Erreur", "Veuillez remplir tous les champs")
            return False
        if(not(isValidDate(self.entry_DATE_START.get()))):
            mb.showerror("Erreur", "Le champ date de debut n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
            return False
        if(not(isValidDate(self.entry_DATE_END.get()))):
            mb.showerror("Erreur", "Le champ date de fin n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
            return False
        if(not(isValidTime(self.entry_HOUR_START.get()))):
             mb.showerror("Erreur", "Le champ heure de fin n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
             return False
        if(not(isValidTime(self.entry_HOUR_END.get()))):
             mb.showerror("Erreur", "Le champ heure de fin n'est pas de la bonne forme ou la date n'existe pas\n Exemple 2022-04-21 (YYYY-MM-DD)")
             return False
        if(not(self.entry_MIN.get().isdigit())):
            mb.showerror("Erreur", "Le champ moyenne doit etre un nombre")
            return False
        return True
    
    def show(self):
        if(not(self.isValidChamp())):
            return
        if self.chkValue.get()  == True:
            graphList(self.list_file, int(self.entry_MIN.get()), self.entry_DATE_START.get(), self.entry_HOUR_START.get(), self.entry_DATE_END.get(), self.entry_HOUR_END.get())
        else :
            graphListSolo(self.list_file, int(self.entry_MIN.get()), self.entry_DATE_START.get(), self.entry_HOUR_START.get(), self.entry_DATE_END.get(), self.entry_HOUR_END.get())

    
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
