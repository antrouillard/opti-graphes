import xml.etree.ElementTree as ET
from ortools.sat.python import cp_model
from datetime import datetime

# *** 1. Charger et extraire toutes les données ***

# Chemin vers le fichier .ros
filename = "Instances/Instance1.ros"  # A adapter si nécessaire
tree = ET.parse(filename)
root = tree.getroot()

# Dates
start_date_str = root.find("StartDate").text
end_date_str = root.find("EndDate").text
date_format = "%Y-%m-%d"
start_dt = datetime.strptime(start_date_str, date_format)
end_dt = datetime.strptime(end_date_str, date_format)
num_days = (end_dt - start_dt).days + 1

# Types de shifts (par exemple "D")
shift_types = {}
for shift in root.findall("ShiftTypes/Shift"):
    shift_id = shift.get("ID")
    start_time = shift.find("StartTime").text
    duration = int(shift.find("Duration").text)
    shift_types[shift_id] = {
        "start_time": start_time,
        "duration": duration
    }

# Liste d'employés
employees = [e.attrib['ID'] for e in root.findall("Employees/Employee")]
# Mapping employé -> index
emp_index = {e: i for i, e in enumerate(employees)}

# Affectations fixes
fixed_assignments = {}
for fa in root.findall("FixedAssignments/Employee"):
    emp_id = fa.find("EmployeeID").text
    day = int(fa.find("Assign/Day").text)
    shift_type = fa.find("Assign/Shift").text
    fixed_assignments[(emp_id, day)] = shift_type

# Demandes shift off
shift_off_requests = {}
for s_off in root.findall("ShiftOffRequests/ShiftOff"):
    emp_id = s_off.find("EmployeeID").text
    day = int(s_off.find("Day").text)
    weight = int(s_off.get("weight"))
    shift_type = s_off.find("Shift").text
    shift_off_requests[(emp_id, day)] = {"shift": shift_type, "weight": weight}

# Demandes shift on
shift_on_requests = {}
for s_on in root.findall("ShiftOnRequests/ShiftOn"):
    emp_id = s_on.find("EmployeeID").text
    day = int(s_on.find("Day").text)
    weight = int(s_on.get("weight"))
    shift_type = s_on.find("Shift").text
    shift_on_requests[(emp_id, day)] = {"shift": shift_type, "weight": weight}

# Exigences de couverture
cover_requirements = {}
for cov in root.findall("CoverRequirements/DateSpecificCover"):
    day = int(cov.find("Day").text)
    for cover in cov.findall("Cover"):
        shift_id = cover.find("Shift").text
        min_req = int(cover.find("Min").text)
        max_req = int(cover.find("Max").text)
        cover_requirements[(day, shift_id)] = (min_req, max_req)

# *** 2. Construction du modèle ***

model = cp_model.CpModel()

# Variables : affectation d'un employé à un shift un jour donné
x = {}
for e in employees:
    for d in range(num_days):
        for shift_id in shift_types:
            x[(e, d, shift_id)] = model.NewBoolVar(f"x_{e}_{d}_{shift_id}")

# Affectations fixes
for (emp_id, d), shift_type in fixed_assignments.items():
    for s in shift_types:
        if s == shift_type:
            model.Add(x[(emp_id, d, s)] == 1)
        else:
            model.Add(x[(emp_id, d, s)] == 0)

# 1. Chaque employé ne peut avoir qu'un seul shift par jour
for e in employees:
    for d in range(num_days):
        model.Add(sum(x[(e, d, s)] for s in shift_types) <= 1)

# 2. Contraintes liées aux séquences (ex: max 5 shifts consécutifs)
max_seq = 5  # à adapter si autres contraintes
for e in employees:
    for d in range(num_days - max_seq):
        model.Add(sum(x[(e, d + i, s)] for i in range(max_seq + 1) for s in shift_types) <= max_seq)

# 3. Contraintes de couverture
for d in range(num_days):
    for shift_id in shift_types:
        total = sum(x[(e, d, shift_id)] for e in employees)
        min_req, max_req = cover_requirements.get((d, shift_id), (0, len(employees)))
        model.Add(total >= min_req)
        model.Add(total <= max_req)

# Ajoutez ici d'autres contraintes selon votre besoin : pauses, séquences, repos, etc.

# 4. Fonction objectif : Penaliser les demandes et autres inconvénients
penalties = []

# Pénalités shift off
for (emp_id, d), info in shift_off_requests.items():
    weight = info['weight']
    shift_type = info['shift']
    penalties.append((1 - x[(emp_id, d, shift_type)]) * weight)

# Pénalités shift on
for (emp_id, d), info in shift_on_requests.items():
    weight = info['weight']
    shift_type = info['shift']
    penalties.append((1 - x[(emp_id, d, shift_type)]) * weight)

# Minimize total penalty
model.Minimize(sum(penalties))

# *** 3. Résolution ***
solver = cp_model.CpSolver()
status = solver.Solve(model)

# *** 4. Affichage de la planification ***
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for e in employees:
        planning = ""
        total_hours = 0
        penalites_totale = 0
        temps_travail = 0
        # Calcul des pénalités
        for (emp_id, d), info in shift_off_requests.items():
            if emp_id == e and solver.Value(x[(emp_id, d, info['shift'])]) == 0:
                penalites_totale += info['weight']
        for (emp_id, d), info in shift_on_requests.items():
            if emp_id == e and solver.Value(x[(emp_id, d, info['shift'])]) == 1:
                penalites_totale += info['weight']

        # Planning jour par jour
        for d in range(num_days):
            shift_char = "-"
            for s in shift_types:
                if solver.Value(x[(e, d, s)]) == 1:
                    shift_char = s
                    # Ajout temps travail
                    temps_travail += shift_types[s]['duration'] / 60
                    break
            planning += shift_char

        print(f"\nEmployé {e} :")
        print(f"Planning : {planning}")
        print(f"Total heures travaillées : {temps_travail:.2f} h")
        print(f"Penalités : {penalites_totale}")
else:
    print("Aucune solution trouvée.")