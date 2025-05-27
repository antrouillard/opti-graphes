import xml.etree.ElementTree as ET

def charger_fichier_xml(path):
    return ET.parse(path).getroot()

def get_contracts_mmin_max_ax_shifts(xml_content):
    """
    Récupère tous les contrats du XML.
    Args:
        xml_content (Element): l'objet racine XML (déjà parsé)
    Returns:
        dict: {contratID: limite_MaxSeq}
    """
    contracts_max = {}
    contracts_min={}
    for contract in xml_content.findall('.//Contract'):
        maxseq = contract.find('MaxSeq')
        if maxseq is not None:
            shift_attr = maxseq.get('shift')
            if shift_attr == '$':
                value_str = maxseq.get('value')
                if value_str is not None:
                    contract_id = contract.get('ID')
                    contracts_max[contract_id] = int(value_str)
        maxseq = contract.find('MinSeq')
        if maxseq is not None:
            shift_attr = maxseq.get('shift')
            if shift_attr == '$':
                value_str = maxseq.get('value')
                if value_str is not None:
                    contract_id = contract.get('ID')
                    contracts_min[contract_id] = int(value_str)
    return contracts_max,contracts_min

def get_contracts_all_min_day_ff(xml_content):
    """
    Retourne un dict {contratID: [valeursMinSeq]} pour tous les contrats,
    où shift='-'.
    """
    contracts_DO = {}
    for contract in xml_content.findall('.//Contract'):
        contract_id = contract.get('ID')
        for minseq in contract.findall('MinSeq'):
            shift_attr = minseq.get('shift')
            if shift_attr == '-':
                value_str = minseq.get('value')
                if value_str is not None:
                    val = int(value_str)
                    contracts_DO[contract_id] = (val)
    return contracts_DO


def extraire_jours_travail(emp_element):
    days = []
    for assign in emp_element.findall('Assign'):
        day = int(assign.find('Day').text)
        shift = assign.find('Shift').text
        if shift == 'D':
            days.append(day)
    days.sort()
    print(days)
    return days


def plus_grande_sequence_jours(assignations):
    """
    Retourne la plus longue séquence de jours consécutifs dans la liste assignations.
    """
    if not assignations:
        return 0
    max_seq = 1
    current_seq = 1
    
    for i in range(1, len(assignations)):
        if assignations[i] == assignations[i-1] + 1:
            current_seq += 1
        else:
            if current_seq > max_seq:
                max_seq = current_seq
            current_seq = 1
    # Vérifier la dernière séquence
    if current_seq > max_seq:
        max_seq = current_seq
    return max_seq

def plus_petite_sequence_jours(assignations):
    """
    Retourne la plus longue séquence de jours consécutifs dans la liste assignations.
    """
    if not assignations:
        return 0
    min_seq = None
    current_seq = 1
    
    for i in range(1, len(assignations)):
        if assignations[i] == assignations[i-1] + 1:
            current_seq += 1
        else:
            if   min_seq == None:
                min_seq = current_seq

            elif current_seq < min_seq:
                min_seq = current_seq
            current_seq = 1
    # Vérifier la dernière séquence
    if current_seq < min_seq:
        min_seq = current_seq
    return min_seq

def extraire_max_sequences_par_employe(root):
    """
    Retourne un dict {ID_employé: max_sequence_de_jours_travailles}
    """
    max_sequences = {}
    for emp in root.findall('Employee'):
        emp_id = emp.get('ID')
        assignations = extraire_jours_travail(emp)
        max_seq_emp = plus_grande_sequence_jours(assignations)
        max_sequences[emp_id] = max_seq_emp
    return max_sequences

def extraire_min_sequences_par_employe(root):
    """
    Retourne un dict {ID_employé: max_sequence_de_jours_travailles}
    """
    max_sequences = {}
    for emp in root.findall('Employee'):
        emp_id = emp.get('ID')
        assignations = extraire_jours_travail(emp)
        max_seq_emp = plus_petite_sequence_jours(assignations)
        max_sequences[emp_id] = max_seq_emp
    return max_sequences

# Chargement
instance_path = 'Instances/Instance1.ros'
solution_path = 'solutions/Solution1.ros'
xml_instance = charger_fichier_xml(instance_path)
xml_solution = charger_fichier_xml(solution_path)

# Récupérer la limite max de séquence pour le shift "$" (pour référence)
max_seq_shift, min_seq_shift = get_contracts_mmin_max_ax_shifts(xml_instance)
# Extraire pour chaque employé : sa plus grande séquence de jours travaillés
max_seq_par_employe = extraire_max_sequences_par_employe(xml_solution)

# Vérification : Si la plus grande séquence d'un employé dépasse sa limite, c'est une violation
respecte = True
for emp, seq in max_seq_par_employe.items():
    limite_employe = max_seq_shift[emp]  # ou si chaque employé a une limite différente, tu peux adapter
    if seq > limite_employe:
        print(f"Erreur : {emp} a une séquence de {seq} jours, max autorisé {limite_employe}")
        respecte = False

if respecte:
    print("Tous les employés respectent leur plus longue séquence de jours.")
else:
    print("Certains employés dépassent leur limite de séquence.")


# Récupérer la limite max de séquence pour le shift "$" (pour référence)
max_seq_shift, min_seq_shift = get_contracts_mmin_max_ax_shifts(xml_instance)
# Extraire pour chaque employé : sa plus grande séquence de jours travaillés
min_seq_par_employe = extraire_min_sequences_par_employe(xml_solution)

# Vérification : Si la plus grande séquence d'un employé dépasse sa limite, c'est une violation
respecte = True
for emp, seq in min_seq_par_employe.items():
    limite_employe = min_seq_shift[emp]  # ou si chaque employé a une limite différente, tu peux adapter
    if seq < limite_employe:
        print(f"Erreur : {emp} a une séquence de {seq} jours, min autorisé {limite_employe}")
        respecte = False

if respecte:
    print("Tous les employés respectent leur plus courte séquence de jours.")
else:
    print("Certains employés dépassent leur limite de séquence.")


get_contracts_all_min_day_ff(xml_instance)

