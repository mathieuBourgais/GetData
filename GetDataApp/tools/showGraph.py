import csv
import numpy as np
import matplotlib.pyplot as plt

file = "/home/bdombry/Documents/GetDataApp/data/data_steps_2022-04-01_to_2022-04-30.csv"
file2 = "/home/bdombry/Documents/GetDataApp/data/data_distance_2022-04-01_to_2022-04-30.csv"
file3 = "/home/bdombry/Documents/GetDataApp/data/data_heart_rate_2022-04-05_to_2022-04-07.csv"

def graphIntraByDay(fic, str):
    list_y = []
    list_x = []
    list_date = []
    with open(fic, 'r') as f:
        obj = csv.reader(f)
        for ligne in obj:
            if(ligne[0] != 'date'):
                list_date.append(ligne[0])
            if(ligne[1] != "value"):
                if(str == "distance"):
                    list_y.append(float(ligne[1]) * 1.515)
                else:
                    list_y.append(int(ligne[1]))
    
    for i in range(len(list_y)):
        list_x.append(i)

    x = np.array(list_x)
    y = np.array(list_y)

    plt.plot(x, y)
    plt.xticks(list_x, list_date, color='r', rotation="vertical")
    plt.title(str +" / Days")
    plt.show()

def getListFenetre(fic, jour_debut, min_debut, jour_fin, min_fin):
    temp = []
    temp2 = []
    with open(fic, 'r') as f:
        obj = csv.reader(f)
        for row in obj:
            temp.append(row)
            if((row[0] == jour_fin) & (row[1] == min_fin)):
                break
        for row in reversed(temp):
            temp2.append(row)
            if((row[0] == jour_debut) & (row[1] == min_debut)):
                break
        final = list(reversed(temp2))
        return final

def grapheHRbyFen(fic, MIN, jour_debut, min_debut, jour_fin, min_fin):
    
    list_y = []
    list_y_moy = []
    list_x = []
    list_x_moy = []
    list_min= []
    list_min_moy = []
    fenetre = getListFenetre(fic, jour_debut, min_debut, jour_fin, min_fin) 
    for ligne in fenetre:
        if(ligne[1] != 'time'):
            list_min.append(ligne[1])
        if(ligne[2] != 'value'):
            list_y.append(int(ligne[2]))
    sum = 0
    for i in range(len(list_y)):
        list_x.append(i)

    for i in range(1,len(list_y)):
        if (i % MIN == 0):
            list_y_moy.append(sum/MIN)
            list_x_moy.append(list_x[i])
            list_min_moy.append(list_min[i])
            sum = 0
        else:
            sum += list_y[i]
        

    x = np.array(list_x_moy)
    y = np.array(list_y_moy)

    plt.plot(x, y)
    plt.xticks(list_x_moy, list_min_moy, color='r', rotation="vertical")
    plt.title("HR / Min")
    plt.show()


