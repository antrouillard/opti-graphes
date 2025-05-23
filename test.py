import xml.etree.ElementTree as ET
from ortools.sat.python import cp_model

# Charger le fichier XML
tree = ET.parse("Instances/Instance1.ros")  # Remplace par ton chemin
root = tree.getroot()

# Récupérer la période
start_day = 0
num_days = (lambda s, e: (int(e[-2:]) - int(s[-2:]) + 1))(root.find("StartDate").text, root.find("EndDate").text)

# Extraire les employés
employees = [e.attrib['ID'] for e in root.find("Employees")]
num_employees = len(employees)
emp_index = {e: i for i, e in enumerate(employees)}

# Extraire les demandes OFF/ON
shift_off = {(emp_index[e.find("EmployeeID").text], int(e.find("Day").text)): int(e.attrib["weight"])
             for e in root.findall(".//ShiftOff")}
shift_on = {(emp_index[e.find("EmployeeID").text], int(e.find("Day").text)): int(e.attrib["weight"])
            for e in root.findall(".//ShiftOn")}

# Extraire les jours de repos fixes
fixed_days_off = {(emp_index[e.find("EmployeeID").text], int(e.find("Assign/Day").text))
                  for e in root.findall(".//FixedAssignments/Employee")}

# Initialiser le modèle
model = cp_model.CpModel()

# Variables de décision : 1 si l'employé e travaille le jour d, sinon 0
work = {}
for e in range(num_employees):
    for d in range(num_days):
        work[e, d] = model.NewBoolVar(f"work_{e}_{d}")

# Contraintes : jour de repos fixes
for (e, d) in fixed_days_off:
    model.Add(work[e, d] == 0)

# Contraintes : Max 5 jours consécutifs de travail
for e in range(num_employees):
    for d in range(num_days - 5):
        model.Add(sum(work[e, d + i] for i in range(6)) <= 5)

# Fonction objectif : satisfaire un max de souhaits (ON), éviter les refus (OFF)
objective_terms = []

for (e, d), w in shift_off.items():
    objective_terms.append(work[e, d] * w)  # pénalité

for (e, d), w in shift_on.items():
    objective_terms.append((1 - work[e, d]) * w)  # pénalité si non attribué

model.Minimize(sum(objective_terms))

# Résolution
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Affichage des résultats
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("\nPlanning généré :\n")
    for e in range(num_employees):
        schedule = ''.join("D" if solver.Value(work[e, d]) else "-" for d in range(num_days))
        print(f"{employees[e]} : {schedule}")
else:
    print("Aucune solution trouvée.")
