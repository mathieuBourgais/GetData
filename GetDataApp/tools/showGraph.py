import csv
from distutils import file_util
import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox as mb


"""
Input : file : url of the file
         day_start, day_end : respectively the start day and the end day of the window to observe
                               in the form "YYYY-MM-DD 
         hour_start, hour_end : espectively the start and end time of the window to observe
                                in the form "HH:MM:SS"
    
Output : A list of the data to observe in the given window
"""
def getListFenetre(file, day_start, hour_start, day_end, hour_end):
    temp = []
    temp2 = []
    filetype = file.split('_')[1]
    with open(file, 'r') as f:
        obj = csv.reader(f)
        next(obj)
        for row in obj:
            
            if(filetype == "calories"):
                temp.append(row)
                if((row[0] == day_end) & (row[3] == hour_end)):
                    break
            else:
                temp.append(row)
                if((row[0] == day_end) & (row[1] == hour_end)):
                    break
        for row in reversed(temp):
            if(filetype == "calories"):
                    temp2.append(row)
                    if((row[0] == day_start) & (row[3] == hour_start)):
                        break
            else:
                    temp2.append(row)
                    if((row[0] == day_start) & (row[1] == hour_start)):
                        break
        DataWindow = list(reversed(temp2))
        temp = []
        for data in DataWindow:
            if(filetype == "calories"):
                temp.append(data[0] + '|' + data[3])
            else:
                temp.append(data[0] +'|'+ data[1])
        if(not(day_start + '|' + hour_start in temp)):
            return False
        if(not(day_end + '|' + hour_end in temp)):
            return False
        return DataWindow

"""
Additional Function for a next Update
"""

def graphSleepByDay(file):
    list_mAwake = []
    list_mAsleep = []
    list_mFallAsleep = []
    list_timeIn = []
    list_x = []
    list_date = []
    with open(file, 'r') as f:
        obj = csv.reader(f)
        for ligne in obj:
            if(ligne[0] != 'date'):
                list_date.append(ligne[0])
            if(ligne[1] != "minutesAwake"):
                list_mAwake.append(int(ligne[1]))
            if(ligne[2] != "minutesAsleep"):
                list_mAsleep.append(int(ligne[2]))
            if(ligne[3] != "minutesToFallAsleep"):
                list_mFallAsleep.append(int(ligne[3]))
            if(ligne[4] != "timeInBed"):
                list_timeIn.append(int(ligne[4]))
    
    for i in range(len(list_mAwake)):
        list_x.append(i)

    list_date.reverse()

    x = np.array(list_x)
    y_Awake = np.array(list_mAwake)
    y_Asleep = np.array(list_mAsleep)
    y_FallAsleep = np.array(list_mFallAsleep)
    y_TimeIn = np.array(list_timeIn)

    plt.plot(x,y_Awake, label="Minutes Awake") 
    plt.plot(x,y_Asleep, label="Minutes Asleep")
    plt.plot(x,y_FallAsleep, label="Minutes To Fall Asleep")
    plt.plot(x,y_TimeIn, label="Time In Bed")

    plt.xticks(list_x, list_date, color='r', rotation="vertical")
    plt.title("SleepData / Days")
    plt.legend()
    plt.show()

"""
Input : file_list : a list of file url
        mean : The spacing between each value, all values are calculated from the average of all spacing values
        day_start, day_end : respectively the start day and the end day of the window to observe
                               in the form "YYYY-MM-DD 
        hour_start, hour_end : espectively the start and end time of the window to observe
                                in the form "HH:MM:SS"

Output : A graph with the number of curves as elements in the list passed in parameter on the same graph
"""
def graphList(file_list, mean, day_start, hour_start, day_end, hour_end):
    fenetre_list = []
    for file in file_list:
        fen = getListFenetre(file,day_start, hour_start, day_end, hour_end)
        if(fen == False):
            mb.showerror("ERREUR", "Revoyez votre fenetre, il n'a a pas toutes les donnée dans cette fenetre")
            return
        fenetre_list.append(fen)
            
    if(not(TestWindow(fenetre_list))):
        mb.showerror("Erreur", "Le graphe n'a pas pus etre créer car vous n'avez pas le meme nombre de valeurs sur cette fenetre de temps")
        return
    for i in range(0,len(file_list)):
        x = []
        y = []
        for row in fenetre_list[i]:
            x.append(row[0] + " " + row[1])
            y.append(int(row[2]))
        GraphLegend = file_list[i].split('_')[1]
        plt.plot(x,y, label= GraphLegend)
    a = []
    b = []
    for i in range(1,len(x)):
        if (i % mean == 0):
            a.append(i)
            b.append(x[i])
    plt.xticks(a,b, rotation="vertical")
    plt.legend()
    plt.show()
    
"""
Input : file_list : a list of file url
        mean : The spacing between each value, all values are calculated from the average of all spacing values
        day_start, day_end : respectively the start day and the end day of the window to observe
                               in the form "YYYY-MM-DD 
        hour_start, hour_end : espectively the start and end time of the window to observe
                                in the form "HH:MM:SS"

Output : A graph for each file in the list passed in parameter
"""
def graphListSolo(file_list, MIN, day_start, hour_start, day_end, hour_end):
    fenetre_list = []
    for file in file_list:
        fen = getListFenetre(file,day_start, hour_start, day_end, hour_end)
        if(fen == False):
            mb.showerror("ERREUR", "Revoyez votre fenetre, il n'a a pas toutes les donnée dans cette fenetre")
            return
        fenetre_list.append(fen)
            
    
    for i in range(0,len(file_list)):
        x = []
        y = []
        for row in fenetre_list[i]:
            x.append(row[0] + " " + row[1])
            y.append(int(row[2]))
        plt.figure(i)
        GraphLegend = file_list[i].split('_')[1]
        plt.title(GraphLegend + " / min")
        a = []
        b = []
        for i in range(1,len(x)):
            if (i % MIN == 0):
                a.append(i)
                b.append(x[i])
        plt.xticks(a,b, rotation="vertical")
        plt.plot(x,y)
    plt.show()

def TestWindow(win):
    value = len(win[0])
    for i in range(1,len(win)):
        if (len(win[i]) != value):
            return False
    return True
