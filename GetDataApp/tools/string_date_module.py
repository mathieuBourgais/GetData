import datetime

MAX_YEAR = 2022
MIN_YEAR = 2000


# Renvoie True si la chaine str est au format valide False sinon
# Format : 2022-01-04 avec uniquement des chiffre et des tirets
def isValid(str):
    t = str.split('-')
    if (len(t) != 3):
        return False
    elif((len(t[0]) != 4) | (len(t[1]) != 2) | (len(t[2]) != 2)):
        return False
    else:
        for i in range(3):
            for j in t[i]:
                try:
                    v = int(j)
                except:
                    return False
        return True

# Renvoie True si l'année passée en paramètre est Bissextile, False sinon 
def isBissextile(a):
    if(a % 4 == 0 & (a % 100 != 0 | a % 400 == 0)):
        return True
    else:
        return False

# Renvoie True si le couple (Mois,Jour) est valable, False sinon
# (2022,04,07) renvoie True alors que (2022,04,32) renvoi False car le 32/04/2022 n'existe pas
def isValidMounthDay(a,m,d):
    if(isBissextile(a)):
        if((m == 2) & ((d < 1) | (d > 29))):
            return False
    else:
        if((m == 2) & ((d < 1) | (d > 28))):
            return False

    if (((m == 1) | (m == 3) | (m == 5) | (m == 7) | (m == 8) | (m == 10) | (m == 12)) & ((d < 1) | (d > 31))):
        return False
    elif (((m == 4) | (m == 6) | (m == 9) | (m == 11)) & ((d < 1) | (d > 30))):
        return False
    else:
        return True

# Prend une chaine de caractere type "2022-01-04" et renvoi True si elle est valide, False sinon
def isValidDate(str):
    if (not(isValid(str))):
        return False
    t = str.split('-')
    year = int(t[0])
    mounth = int(t[1])
    day = int(t[2])
    if ((year > MAX_YEAR) | (year < MIN_YEAR)):
        return False
    elif (not(isValidMounthDay(year,mounth,day))):
        return False
    else:
        return True

def isValidFormatTime(str):
    t = str.split(':')
    if (len(t) != 3):
        return False
    elif((len(t[0]) != 2) | (len(t[1]) != 2) | (len(t[2]) != 2)):
        return False
    else:
        for i in range(3):
            for j in t[i]:
                try:
                    v = int(j)
                except:
                    return False
        return True

def isValidTime(str):
    if (not(isValidFormatTime(str))):
        return False
    t = str.split(':')
    h = int(t[0])
    m = int(t[1])
    s = int(t[1])
    if((h > 23) | (m > 59) | (s > 59)):
        return False
    return True

# Converti un objet de type Date en une chaine de caractere de type "YYYY-MM-DD"
def date_to_string(date):

    str_month = str(date.month)
    str_day = str(date.day)
    if(date.month < 10):
        str_month = '0' + str(date.month)
    if(date.day < 10):
        str_day = '0' + str(date.day)
    return (str(date.year) + '-' + str_month + '-' + str_day)

# Converti une chaine de caractere de type "YYYY-MM-DD" en un objet de type Date
def string_to_date(s):
    date = s.split('-')
    y = int(date[0])
    m = int(date[1])
    d = int(date[2])
    return datetime.date(y,m,d)

def deltaDay(d1,d2):
    r1 = string_to_date(d1)
    r2 = string_to_date(d2)
    res = r1 - r2
    return res.days
