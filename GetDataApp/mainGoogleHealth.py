import csv
import os
import platform
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import filedialog as fd
from tkinter import messagebox as mb

import requests
from google.auth.exceptions import GoogleAuthError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession
from oauthlib.oauth2.rfc6749.errors import OAuth2Error

from GraphFile import GraphFile, ListGrapheFile


API_ROOT = "https://health.googleapis.com/v4/users/me/dataTypes"
SCOPES = [
    "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly",
    "https://www.googleapis.com/auth/googlehealth.health_metrics_and_measurements.readonly",
]
DATA_TYPES = {
    "heart": ("heart-rate", "sample_time.civil_time"),
    "calories": ("total-calories", "interval.civil_start_time"),
    "floors": ("floors-climbed", "interval.civil_start_time"),
    "steps": ("steps", "interval.civil_start_time"),
    "distance": ("distance", "interval.civil_start_time"),
    "elevation": ("elevation-gain", "interval.civil_start_time"),
}
VALUE_KEYS = {
    "heart": ("beatsPerMinute", "bpm", "value"),
    "calories": ("kilocalories", "calories", "value"),
    "floors": ("count", "floors", "value"),
    "steps": ("count", "value"),
    "distance": ("meters", "distanceMeters", "value"),
    "elevation": ("millimeters", "meters", "value"),
}


class GoogleHealthClient:
    def __init__(self, credentials):
        self.session = AuthorizedSession(credentials)

    def data_points(self, action, start_date, end_date):
        data_type, time_field = DATA_TYPES[action]
        filter_type = data_type.replace("-", "_")
        start = start_date.isoformat() + "T00:00:00"
        end = (end_date + timedelta(days=1)).isoformat() + "T00:00:00"
        filter_expression = (
            f'{filter_type}.{time_field} >= "{start}" AND '
            f'{filter_type}.{time_field} < "{end}"'
        )
        url = f"{API_ROOT}/{data_type}/dataPoints"
        page_token = None
        points = []

        while True:
            params = {"filter": filter_expression, "page_size": 1000}
            if page_token:
                params["page_token"] = page_token
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            points.extend(result.get("dataPoints", []))
            page_token = result.get("nextPageToken")
            if not page_token:
                return points


def _camel_case(value):
    first, *rest = value.split("-")
    return first + "".join(part.capitalize() for part in rest)


def _find_value(value, candidates):
    if isinstance(value, dict):
        for candidate in candidates:
            if candidate in value and not isinstance(value[candidate], (dict, list)):
                return value[candidate], candidate
        for child in value.values():
            found = _find_value(child, candidates)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_value(child, candidates)
            if found is not None:
                return found
    return None


def _civil_datetime(value):
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.astimezone().replace(tzinfo=None) if parsed.tzinfo else parsed
        except ValueError:
            return None
    if not isinstance(value, dict):
        return None

    if isinstance(value.get("date"), dict):
        day = value["date"]
        parts = value.get("time", {})
        try:
            return datetime(
                day["year"],
                day["month"],
                day["day"],
                parts.get("hours", 0),
                parts.get("minutes", 0),
                parts.get("seconds", 0),
            )
        except (KeyError, TypeError, ValueError):
            return None
    return None


def _point_datetime(point, record):
    for container in (record, point):
        if not isinstance(container, dict):
            continue
        for field in ("civilStartTime", "civilTime", "startTime", "time", "physicalTime"):
            if field in container:
                parsed = _civil_datetime(container[field])
                if parsed is not None:
                    return parsed
        for field in ("interval", "sampleTime", "sample_time"):
            nested = container.get(field)
            if isinstance(nested, dict):
                parsed = _point_datetime({}, nested)
                if parsed is not None:
                    return parsed
    return None


def _csv_rows(action, points, start_date, end_date):
    data_type = DATA_TYPES[action][0]
    record_key = _camel_case(data_type)
    rows = []
    for point in points:
        record = point.get(record_key, point)
        timestamp = _point_datetime(point, record)
        if timestamp is None:
            raise ValueError(
                f"Impossible de lire l'heure d'un point de données « {data_type} »."
            )
        if not (start_date <= timestamp.date() <= end_date):
            continue
        found = _find_value(record, VALUE_KEYS[action])
        if found is None:
            raise ValueError(
                f"Impossible de lire la valeur d'un point de données « {data_type} »."
            )

        value, value_key = found
        if action == "distance" and value_key in ("meters", "distanceMeters"):
            value = float(value) / 1609.34
        elif action == "elevation" and value_key == "millimeters":
            value = float(value) / 1000

        if action == "calories":
            rows.append(
                {
                    "date": timestamp.date().isoformat(),
                    "level": "",
                    "mets": "",
                    "time": timestamp.strftime("%H:%M:%S"),
                    "value": value,
                }
            )
        else:
            rows.append(
                {
                    "date": timestamp.date().isoformat(),
                    "time": timestamp.strftime("%H:%M:%S"),
                    "value": value,
                }
            )
    return rows


def _write_csv(path, action, rows):
    if action == "calories":
        columns = ("date", "level", "mets", "time", "value")
    else:
        columns = ("date", "time", "value")
    with open(path, "w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


class ConnectBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.client = None
        self.label_frame = tk.LabelFrame(parent, text="Connexion Google Health")
        self.message = tk.StringVar(value="Vous n'êtes pas connecté")
        self.client_id = tk.Entry(self.label_frame, width=38)
        self.client_secret = tk.Entry(self.label_frame, width=38, show="*")

        tk.Label(self.label_frame, text="Client ID :").grid(row=0, column=0, padx=5)
        self.client_id.grid(row=0, column=1, padx=5)
        tk.Label(self.label_frame, text="Client Secret :").grid(row=0, column=2, padx=5)
        self.client_secret.grid(row=0, column=3, padx=5)
        tk.Button(
            self.label_frame, text="CONNECT", command=self.connect_client
        ).grid(row=0, column=4, padx=5)
        tk.Label(self.label_frame, textvariable=self.message).grid(
            row=1, column=0, columnspan=5
        )
        self.label_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    def connect_client(self):
        client_id = self.client_id.get().strip()
        client_secret = self.client_secret.get().strip()
        if not client_id or not client_secret:
            mb.showerror("Erreur", "Veuillez renseigner le Client ID et le Client Secret.")
            return

        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }
        try:
            flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
            credentials = flow.run_local_server(port=0, open_browser=True)
            self.client = GoogleHealthClient(credentials)
            self.message.set("Vous êtes connecté à Google Health")
        except (
            GoogleAuthError,
            OAuth2Error,
            requests.RequestException,
            OSError,
            ValueError,
        ) as error:
            self.client = None
            self.message.set("Connexion impossible")
            mb.showerror(
                "Erreur de connexion",
                "La connexion à Google Health a échoué.\n"
                "Vérifiez le Client ID, le Client Secret, la configuration OAuth "
                "et l'accès à l'API.\n\n"
                f"{error}",
            )


class GetData(tk.Frame):
    def __init__(self, parent, connect_bar):
        super().__init__(parent)
        self.client = connect_bar
        self.label_frame = tk.LabelFrame(parent, text="Télécharger les données")
        self.start_date = tk.Entry(self.label_frame)
        self.end_date = tk.Entry(self.label_frame)
        tk.Label(self.label_frame, text="Date de début (AAAA-MM-JJ) :").grid(
            row=0, column=0, sticky="w"
        )
        self.start_date.grid(row=0, column=1)
        tk.Label(self.label_frame, text="Date de fin (AAAA-MM-JJ) :").grid(
            row=1, column=0, sticky="w"
        )
        self.end_date.grid(row=1, column=1)

        actions = (
            ("HEART RATE", "heart"),
            ("CALORIES", "calories"),
            ("FLOORS", "floors"),
            ("STEPS", "steps"),
            ("DISTANCE", "distance"),
            ("ELEVATION", "elevation"),
        )
        for index, (label, action) in enumerate(actions):
            tk.Button(
                self.label_frame,
                text=label,
                command=lambda selected=action: self.download(selected),
            ).grid(row=index // 3, column=index % 3 + 2, padx=3, pady=3)
        self.label_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    def download(self, action):
        if self.client.client is None:
            mb.showerror("Erreur", "Connectez-vous d'abord à Google Health.")
            return

        try:
            start_date = date.fromisoformat(self.start_date.get().strip())
            end_date = date.fromisoformat(self.end_date.get().strip())
            if end_date < start_date:
                raise ValueError("La date de fin doit être postérieure à la date de début.")
        except ValueError as error:
            mb.showerror(
                "Dates invalides",
                f"{error}\nUtilisez le format AAAA-MM-JJ, par exemple 2022-04-21.",
            )
            return

        if platform.system() == "Windows":
            output_dir = "."
        else:
            output_dir = "data"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(
            output_dir,
            f"data_{'heart_rate' if action == 'heart' else action}_"
            f"{start_date.isoformat()}_to_{end_date.isoformat()}.csv",
        )

        try:
            points = self.client.client.data_points(action, start_date, end_date)
            rows = _csv_rows(action, points, start_date, end_date)
            _write_csv(filename, action, rows)
        except (requests.RequestException, OSError, ValueError, KeyError, TypeError) as error:
            mb.showerror("Erreur de téléchargement", str(error))
            return

        mb.showinfo(
            "Succès",
            f"{len(rows)} enregistrement(s) exporté(s) dans :\n{filename}",
        )


class Graph(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.files = []
        self.filepath = ""
        self.label_frame = tk.LabelFrame(parent, text="Graphiques", padx=10, pady=10)
        self.status = tk.StringVar(value="Aucun fichier sélectionné")
        self.start_date = tk.Entry(self.label_frame, width=24)
        self.end_date = tk.Entry(self.label_frame, width=24)
        self.mean = tk.Entry(self.label_frame, width=8)
        self.start_date.insert(0, "AAAA-MM-JJ_HH:MM:SS")
        self.end_date.insert(0, "AAAA-MM-JJ_HH:MM:SS")
        self.mean.insert(0, "60")

        tk.Button(self.label_frame, text="PARCOURIR", command=self.browse).grid(
            row=0, column=0, padx=3
        )
        tk.Label(self.label_frame, textvariable=self.status).grid(
            row=0, column=1, columnspan=3, sticky="w"
        )
        tk.Label(self.label_frame, text="Début :").grid(row=1, column=0, sticky="e")
        self.start_date.grid(row=1, column=1, padx=3)
        tk.Label(self.label_frame, text="Fin :").grid(row=2, column=0, sticky="e")
        self.end_date.grid(row=2, column=1, padx=3)
        tk.Label(self.label_frame, text="Moyenne de temps :").grid(
            row=3, column=0, sticky="e"
        )
        self.mean.grid(row=3, column=1, sticky="w", padx=3)
        tk.Button(self.label_frame, text="AJOUTER", command=self.add_file).grid(
            row=3, column=2, padx=3
        )
        tk.Button(self.label_frame, text="AFFICHER", command=self.show).grid(
            row=4, column=1, padx=3, pady=3
        )
        tk.Button(self.label_frame, text="EFFACER", command=self.clear).grid(
            row=4, column=2, padx=3, pady=3
        )
        self.label_frame.grid(row=2, column=0, padx=5, pady=5, sticky="w")

    def browse(self):
        self.filepath = fd.askopenfilename(
            initialdir=os.getcwd(),
            title="Choisir un fichier CSV",
            filetypes=(("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")),
        )
        if not self.filepath:
            return
        self.status.set(self.filepath)
        basename = os.path.basename(self.filepath)
        parts = basename.split("_")
        if len(parts) >= 6:
            self.start_date.delete(0, tk.END)
            self.end_date.delete(0, tk.END)
            self.start_date.insert(0, parts[-3] + "_00:00:00")
            self.end_date.insert(0, parts[-1].rsplit(".", 1)[0] + "_23:59:00")

    def add_file(self):
        if not self.filepath:
            mb.showerror("Erreur", "Sélectionnez d'abord un fichier CSV.")
            return
        try:
            start = datetime.strptime(self.start_date.get(), "%Y-%m-%d_%H:%M:%S")
            end = datetime.strptime(self.end_date.get(), "%Y-%m-%d_%H:%M:%S")
            mean = int(self.mean.get())
            if end < start or mean < 1:
                raise ValueError
        except ValueError:
            mb.showerror(
                "Erreur",
                "Vérifiez les dates (AAAA-MM-JJ_HH:MM:SS) et la moyenne (entier positif).",
            )
            return
        self.files.append(
            GraphFile(
                self.filepath,
                start.strftime("%Y-%m-%d_%H:%M:%S"),
                end.strftime("%Y-%m-%d_%H:%M:%S"),
                mean,
            )
        )
        self.filepath = ""
        self.status.set(f"{len(self.files)} fichier(s) ajouté(s)")

    def show(self):
        if not self.files:
            mb.showerror("Erreur", "Ajoutez au moins un fichier CSV.")
            return
        try:
            ListGrapheFile(self.files).show()
        except (OSError, ValueError, IndexError) as error:
            mb.showerror("Erreur de graphique", str(error))

    def clear(self):
        self.files.clear()
        self.filepath = ""
        self.status.set("Aucun fichier sélectionné")


class MainApplication:
    def __init__(self, parent):
        self.connect_bar = ConnectBar(parent)
        GetData(parent, self.connect_bar)
        Graph(parent)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("GetData - Google Health")
    MainApplication(root)
    root.mainloop()
