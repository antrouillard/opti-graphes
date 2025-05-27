from ortools.sat.python import cp_model


model = cp_model.CpModel()

def load_my_format(filename):
    data = {
        'horizon': None,
        'shifts': {},             # ID -> { 'length': int }
        'staff': {},              # ID -> { 'max_shifts': int, 'max_total': int, 'min_total': int, 'max_cseq': int, 'min_cseq': int, 'min_rest': int, 'max_wend': int }
        'days_off': {},           # EmployeeID -> list de jours
        'shift_on_requests': [],  # list de dicts
        'shift_off_requests': [],
        'cover': []
    }

    section = None
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Ignorer les commentaires ou lignes vides
            if line.startswith('#') or not line:
                continue

            # Détecter la section
            if line.startswith('SECTION_'):
                section = line
                continue

            # Traitement selon la section
            if section == 'SECTION_HORIZON':
                data['horizon'] = int(line)
            elif section == 'SECTION_SHIFTS':
                parts = line.split(',')
                shift_id = parts[0]
                length = int(parts[1])
                last = parts[2]
                no_follow = last.split('|') # liste de shifts qui ne peuvent pas suivre
                data['shifts'][shift_id] = {'length': length, 'no_follow': no_follow}
            elif section == 'SECTION_STAFF':
                # Ligne exemple : A,D=14,4320,3360,5,2,2,1
                parts = line.split(',')  # ['A', 'D=14', '4320', '3360', '5', '2', '2', '1']
                emp_id = parts[0]

                valeurs= parts[2:]
                attr_part = parts[1]  # 'D=14'
                # Séparer la partie après le '='
                max_shifts = attr_part.split('|')
                '''
                if len(key_value) != 2:
                    print("Format inattendu dans ligne:", line)
                    continue


                if len(valeurs) != 6:
                    print("Nombre de valeurs inattendu dans ligne:", line)
                    print("il y a", len(valeurs), "éléments :", valeurs)
                    continue
                '''
                #max_shifts = key_value[1]
                max_total_minutes = int(valeurs[0])
                min_total_minutes = int(valeurs[1])
                max_cseq = int(valeurs[2])
                min_cseq = int(valeurs[3])
                min_rest = int(valeurs[4])
                max_wend = int(valeurs[5])

                data['staff'][emp_id] = {
                    'max_shifts': max_shifts,
                    'max_total': max_total_minutes,
                    'min_total': min_total_minutes,
                    'max_cseq': max_cseq,
                    'min_cseq': min_cseq,
                    'min_rest': min_rest,
                    'max_wend': max_wend
                }
            elif section == 'SECTION_DAYS_OFF':
                parts = line.split(',')
                emp_id = parts[0]
                days_off_list = [int(d) for d in parts[1:]]
                data['days_off'][emp_id] = days_off_list
            elif section == 'SECTION_SHIFT_ON_REQUESTS':
                parts = line.split(',')
                emp_id = parts[0]
                day = int(parts[1])
                shift_id = parts[2]
                weight = int(parts[3])
                data['shift_on_requests'].append({'empID': emp_id, 'day': day, 'shiftID': shift_id, 'weight': weight})
            elif section == 'SECTION_SHIFT_OFF_REQUESTS':
                parts = line.split(',')
                emp_id = parts[0]
                day = int(parts[1])
                shift_id = parts[2]
                weight = int(parts[3])
                data['shift_off_requests'].append({'empID': emp_id, 'day': day, 'shiftID': shift_id, 'weight': weight})
            elif section == 'SECTION_COVER':
                parts = line.split(',')
                day = int(parts[0])
                shiftID = parts[1]
                requirement = int(parts[2])
                weight_under = int(parts[3])
                weight_over = int(parts[4])
                data['cover'].append({'day': day, 'shiftID': shiftID, 'requirement': requirement, 'weight_under': weight_under, 'weight_over': weight_over})
    return data

# initialisation après chargement de data
data = load_my_format('Instances/Instance2.txt')
print(data)
# Nombre total de jours dans l'horizon
h = data['horizon']
# Ensemble des jours (commençant à 1)
J = list(range(1, h + 1))

# Ensemble des week-ends (si h=14, W=1,2,...)
W = list(range(1, (h // 7) + 1))

# Ensemble des employés (liste des clés dans 'staff')
E = list(data['staff'].keys())

# Ensemble des types de postes (d'après 'shifts' IDs)
P = list(data['shifts'].keys())

# Dictionnaires pour les paramètres par poste
dp = {}     # durée en minutes
Ip = {}     # ensemble des postes qui ne peuvent pas suivre p
ujp = {}   # le besoin en personnel par jour pour chaque p

for p in P:
    dp[p] = data['shifts'][p]['length']
    # Si 'no_follow' est en place, le récupérer, sinon vide
    Ip[p] = data['shifts'][p].get('no_follow', [])
    # Si vous voulez remplir ujp pour tous j dans J, faire :
    for j in J:
        # Ex: supposer que pour tous j c'est le même besoin, ou si dans data par exemple
        # vous avez un dict, adaptez ici.
        # exemple: ujp[(p,j)] = valeur définie selon votre fichier ou règle
        pass

# Dictionnaires pour les employés, initialisés à partir des données
Re = {}     # jours de repos
tmin_e = {} # tps min total
tmax_e = {} # tps max total
cmin_e = {} # la longueur minimale de posts consécutifs
cmax_e = {} # la longueur maximale
rmin_e = {} # repos consécutifs minimaux
wmax_e = {} # max week-ends travaillé
mmax_ep = {} # max jours par poste p pour chaque employé e

for e in E:
    staff_info = data['staff'][e]
    # Exemple d'extraire chaque paramètre
    tmax_e[e] = staff_info['max_total']
    tmin_e[e] = staff_info['min_total']
    cmax_e[e] = staff_info['max_cseq']
    cmin_e[e] = staff_info['min_cseq']
    rmin_e[e] = staff_info['min_rest']
    wmax_e[e] = staff_info['max_wend']
    # Pour les jours de repos, si dans data['days_off'] e est présent
    Re[e] = data['days_off'].get(e, [])
    # Pour mmax_ep, il faut que dans tes données tu aies cette info
    # Si tu l'as dans `data['mmax_ep']`, l'utiliser directement.
    # Sinon, si tu ne l'as pas, tu peux le fixer par exemple à une valeur par défaut
    # (ex: 14)
    # Exemple :
    # mmax_ep[(e,p)] = valeur
    # Si pas dans data, tu peux faire :
    # mmax_ep[(e,p)] = valeur_par_defaut


### DEFINITION DES VARIABLES DE DECISION

# Variables d'affectation : employé e, jour j, poste p
x_ejp = {}
for e in E:
    for j in J:
        for p in P:
            x_ejp[(e, j, p)] = model.NewBoolVar(f"x_{e}_{j}_{p}")

# Variables pour week-ends (si besoin)
wmax = max(W)
w_end = {}
for e in E:
    for w in W:
        w_end[(e, w)] = model.NewBoolVar(f"w_{e}_{w}")

# Variables pour écarts de personnel
y_missing = {}
y_excess = {}
for p in P:
    for j in J:
        y_missing[(p, j)] = model.NewIntVar(0, 10000, f"miss_{p}_{j}")
        y_excess[(p, j)] = model.NewIntVar(0, 10000, f"excess_{p}_{j}")

#Pour la contrainte 1 OK
for e in E:
    for d in J:
        model.Add(sum(x_ejp[(e, d, p)] for p in P) <= 1)

#Pour la contrainte 2
'''for e in E:
    for d in J[:-1]:
        for p in P:
            # Vérifiez si Ip[p] existe et n'est pas vide
            if p in Ip and Ip[p]:
                model.AddImplication(
                    x_ejp[(e, d, p)] == 1,
                    sum(x_ejp[(e, d+1, p_prime)] for p_prime in Ip[p]) == 0
                )'''
#Pour la contrainte 3 OK
total = model.NewIntVar(0, len(J), f"total_{e}_{p}")

limite_generale = 10 * len(J)  # ajuste cette valeur selon la taille de ton problème

for e in E:
    for p in P:
        limite_p = mmax_ep.get((e,p), limite_generale)  # limite max fixée ou valeur par défaut
        # Si la limite est infinie, on la remplace par limite_generale
        if limite_p == float('inf'):
            limite_p = limite_generale
        # ajouter la contrainte
        model.Add(cp_model.LinearExpr.Sum([x_ejp[(e, d, p)] for d in J]) <= limite_p)
#Pour la contrainte 4 OK
# Dictionnaire des durées
shift_durations = {}
for p in P:
    shift_durations[p] = data['shifts'][p]['length']
for e in E:
    for d in J:
        total_duree = sum(x_ejp[(e, d, p)] * shift_durations[p] for p in P)
        model.Add(total_duree >= tmin_e[e])
        model.Add(total_duree <= tmax_e[e])
#Pour la contrainte 5
startSeq = {}
for e in E:
    for d in J:
        startSeq[(e, d)] = model.NewBoolVar(f"startSeq_{e}_{d}")

for e in E:
    for d in J:
        # Si d>0, appliquer la contrainte
        if d > 0:
            # La contrainte pour d>0
            model.AddImplication(
                startSeq[(e, d)],
                1 - cp_model.LinearExpr.Sum([x_ejp[(e, d-1, p)] for p in P])
            )
        else:
            # Pour d=0, tu peux fixer startSeq[(e, 0)] = 1 si tu veux que l’employé
            # commence une séquence de travail à la première journée
            model.Add(startSeq[(e, 0)] == 1)
#Pour la contrainte 6
# La série de jours travaillés suivants doit faire au moins cmin_e[e]
'''for e in E:
    for d in J:
        for d2 in J:
            if d2 >= d and d2 < d + cmin_e[e]:
                # Si startSeq[e,d] = 1, alors e doit travailler tous ces jours
                model.AddImplication(
                    startSeq[(e, d)],
                    sum(x_ejp[(e, day, p)] for day in range(d, d + cmin_e[e]) for p in P if day in J) == cmin_e[e]
                )'''
#Pour la contrainte 7
'''rest_day = {}
for e in E:
    for d in J:
        rest_day[(e, d)] = model.NewBoolVar(f"rest_{e}_{d}")
for e in E:
    for d in J:
        # Si l'employé e ne travaille pas ce jour-là (toutes mes variables p)
        model.Add(sum(x_ejp[(e, d, p)] for p in P) == 0).OnlyEnforceIf(rest_day[(e, d)])
        # Si l'employé travaille ce jour-là
        model.Add(sum(x_ejp[(e, d, p)] for p in P) >= 1).OnlyEnforceIf(1 - rest_day[(e, d)])'''
#Pour la contrainte 8

wmax_e = {...}  # dictionnaire avec limite de week-ends par employé
W = range(1, (h // 7)+1)

# Dictionnaire pour variables week-end
worked_weekend = {}
for e in E:
    for w in W:
        worked_weekend[(e, w)] = model.NewBoolVar(f"worked_weekend_{e}_{w}")

# Ajout des contraintes pour chaque week-end
for e in E:
    for w in W:
        samedi = (w-1)*7 + 5
        dimanche = (w-1)*7 + 6
        # Vérifier si l'employé travaille samedi ou dimanche
        travail_samedi = model.NewBoolVar(f"work_sat_{e}_{w}")
        travail_dimanche = model.NewBoolVar(f"work_sun_{e}_{w}")
        # Si dans votre dict `J`, jour 0 = lundi, alors samedi= jour 5, dimanche= jour 6
        if samedi in J:
            model.AddMaxEquality(travail_samedi, [x_ejp[(e, samedi, p)] for p in P])
        else:
            model.Add(travail_samedi == 0)
        if dimanche in J:
            model.AddMaxEquality(travail_dimanche, [x_ejp[(e, dimanche, p)] for p in P])
        else:
            model.Add(travail_dimanche == 0)
        # Si l’un ou l’autre est vrai, alors week-end travaillé
        model.AddBoolOr([travail_samedi, travail_dimanche]).OnlyEnforceIf(worked_weekend[(e, w)])
        model.AddImplication(worked_weekend[(e, w)], 1 - travail_samedi + 1 - travail_dimanche >= 1)
        # Ou ça peut aussi être : [ travaillant samedi ou dimanche ] => week-end travaillé
        model.Add(worked_weekend[(e, w)] == 1).OnlyEnforceIf([travail_samedi, travail_dimanche])
        model.Add(worked_weekend[(e, w)] <= 1)

    # Limite W
    model.Add(sum(worked_weekend[(e, w)] for w in W) <= wmax_e[e])
#Pour la contrainte 9
for e in E:
    for d in data['days_off'].get(e, []):
        for p in P:
            model.Add(x_ejp[(e, d, p)] == 0)
#Pour la contrainte 10

def contraint1(solver, x, E, J, P):
    """
    Vérifie que pour chaque employé e et jour j, il y a au plus une affectation (un seul poste).
    Retourne True si la contrainte est respectée dans la solution, False sinon.
    """
    for e in E:
        for d in J:
            affectations = [solver.Value(x[(e, d, p)]) for p in P]
            somme_affects = sum(affectations)
            if somme_affects > 1:
                print(f"Violation : Employé {e} le jour {d+1} a {somme_affects} affectations.")
                return False
    return True


def constraint2(solver, x, E, J, P, Ip):
    """
    Vérifie que dans la solution, pour chaque employé e,
    le poste p à jour d, et le poste p' interdit à suivre,
    si on travaille p à d, alors on ne travaille pas p' à d+1.
    Retourne True si la contrainte est respectée, sinon False.
    """
    for e in E:
        for d in J[:-1]:  # jusqu'à penultième jour pour d+1
            d_next = d + 1
            for p in P:
                if solver.Value(x[(e, d, p)]) == 1:
                    # si ce poste p est travaillé ce jour-là
                    for p_prime in Ip.get(p, []):
                        # alors, p' ne doit pas être travaillé le lendemain
                        if solver.Value(x[(e, d_next, p_prime)]) == 1:
                            print(f"Violation : Employé {e} travaille {p} le jour {d+1} et {p_prime} le jour {d+2}")
                            return False
    return True

def constraint3(solver, x, E, J, P, mmax_e_p):
    """
    Vérifie qu’un employé e n’est pas affecté plus que mmax_e_p fois au poste p dans la solution.
    Retourne True si respecté, sinon False.
    """
    for e in E:
        for p in P:
            count = 0
            for d in J:
                if solver.Value(x[(e, d, p)]) == 1:
                    count += 1
            if count > mmax_e_p.get((e, p), float('inf')):
                print(f"Violation : Employé {e} est affecté {count} fois au poste {p} (limite {mmax_e_p.get((e,p), 'inf')})")
                return False
    return True

def constraint4(solver, x, E, J, P, shift_types, tmin_e, tmax_e):
    """
    Vérifie que pour chaque employé, la durée totale de travail est dans [tmin_e[e], tmax_e[e]].
    Retourne True si respecté, sinon False.
    """
    for e in E:
        total_duree = 0
        for d in J:
            for p in P:
                if solver.Value(x[(e, d, p)]) == 1:
                    total_duree += shift_types[p].duration
        # Vérifier la limite inférieure si définie
        if e in tmin_e and total_duree < tmin_e[e]:
            print(f"Violation : Employé {e} travaille seulement {total_duree} min (< {tmin_e[e]})")
            return False
        # Vérifier la limite supérieure si définie
        if e in tmax_e and total_duree > tmax_e[e]:
            print(f"Violation : Employé {e} travaille {total_duree} min (> {tmax_e[e]})")
            return False
    return True

def constraint5(solver, x, E, J, cmax_e):
    """
    Vérifie que pour chaque employé e, il n'a pas de séquence de jours travaillés (1) > cmax_e[e].
    Retourne True si respecté, sinon False.
    """
    for e in E:
        max_consecutif = 0
        count = 0
        for d in J:
            # Vérifie si e travaille ce jour
            travaille = any(solver.Value(x[(e, d, p)]) == 1 for p in P)
            if travaille:
                count += 1
                if count > max_consecutif:
                    max_consecutif = count
            else:
                count = 0
        # Vérification contre cmax_e
        if e in cmax_e and max_consecutif > cmax_e[e]:
            print(f"Violation : Employé {e} a une séquence de {max_consecutif} jours travaillés consécutifs (> {cmax_e[e]})")
            return False
    return True

def constraint6(solver, x, E, J, cmin_e):
    """
    Vérifie que pour chaque employé e, toute séquence de jours travaillés
    a une longueur >= cmin_e[e].
    Retourne True si respecté, sinon False.
    """
    for e in E:
        count = 0
        for d in J:
            # Vérifie si e travaille ce jour
            travaille = any(solver.Value(x[(e, d, p)]) == 1 for p in P)
            if travaille:
                count += 1
            else:
                # Si on a fini une séquence, on vérifie sa longueur
                if count > 0 and count < cmin_e.get(e, 0):
                    print(f"Violation : Employé {e} a une séquence de {count} jours travaillés (< {cmin_e[e]})")
                    return False
                count = 0
        # Vérification en fin de boucle pour la dernière séquence
        if count > 0 and count < cmin_e.get(e, 0):
            print(f"Violation : Employé {e} a une séquence finale de {count} jours travaillés (< {cmin_e[e]})")
            return False
    return True

def constraint7(solver, x, E, J, rmin_e):
    """
    Vérifie que pour chaque employé e, toute séquence de jours de repos
    a une longueur >= rmin_e[e].
    Retourne True si respecté, sinon False.
    """
    for e in E:
        count = 0
        for d in J:
            # Vérifie si e est en repos ce jour-là
            en_repos = all(solver.Value(x[(e, d, p)]) == 0 for p in P)
            if en_repos:
                count += 1
            else:
                # Si on a fini une séquence, on vérifie sa longueur
                if 0 < count < rmin_e.get(e, 0):
                    print(f"Violation : Employé {e} a une séquence de {count} jours de repos (< {rmin_e[e]})")
                    return False
                count = 0
        # Vérification en fin de boucle pour la dernière séquence
        if 0 < count < rmin_e.get(e, 0):
            print(f"Violation : Employé {e} a une séquence finale de {count} jours de repos (< {rmin_e[e]})")
            return False
    return True

def constraint8(solver, x, E, W, week_end_info, wmax_e):
    """
    Vérifie que pour chaque employé e, le nombre de week-ends travaillés ne dépasse pas wmax_e[e].
    - week_end_info : dict avec clé (e,w) = bool, indique si e a travaillé ce week-end.
    Retourne True si OK, sinon False.
    """
    for e in E:
        count_wend = 0
        for w in W:
            # Définir les jours du week-end w
            samedi = w*7 + 5   # jour 5 dans la semaine (si 0 = lundi)
            dimanche = w*7 + 6 # jour 6
            travail_weekend = False
            if samedi < len(J):
                travail_weekend = travail_weekend or (any(solver.Value(x[(e, samedi, p)]) == 1 for p in P))
            if dimanche < len(J):
                travail_weekend = travail_weekend or (any(solver.Value(x[(e, dimanche, p)]) == 1 for p in P))
            if travail_weekend:
                count_wend += 1
        if count_wend > wmax_e.get(e, float('inf')):
            print(f"Violation : Employé {e} travaille {count_wend} week-ends (> {wmax_e[e]})")
            return False
    return True

def constraint9(solver, x, days_off, E, P):
    """
    Vérifie que pour chaque employé e dans days_off,
    si un jour d est interdit, alors e n’est affecté à aucun poste ce jour-là.
    Retourne True si respecté, sinon False.
    """
    for e in days_off:
        jours_interdits = days_off[e]
        for d in jours_interdits:
            for p in P:
                if solver.Value(x[(e, d, p)]) == 1:
                    print(f"Violation : Employé {e} travaille le jour {d} alors que c’est interdit.")
                    return False
    return True

solver = cp_model.CpSolver()
status = solver.Solve(model)
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("et ben niquel")
else:
    print("Aucune solution trouvée.")

def construire_planning(solver, x, E, J, P):
    """
    Construit un planning à partir de la solution, sous forme d'un dict
    ou d'une liste par employé et jour, en respectant toutes les contraintes dures.
    """
    planning = {}
    for e in E:
        planning[e] = []
        for d in J:
            poste_trouve = '-'
            for p in P:
                if solver.Value(x[(e, d, p)]) == 1:
                    poste_trouve = p
                    break
            planning[e].append(poste_trouve)
    return planning

planning = construire_planning(solver, x_ejp, E, J, P)
print(planning)
