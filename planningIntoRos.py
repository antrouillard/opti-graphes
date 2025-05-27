import xml.etree.ElementTree as ET

# Enregistre une solution dans un fichier .ros XML, compatible avec les visualiseurs.
# Paramètres : 
# planning (dict): planning[employee] = [shift_id_j0, shift_id_j1, ..., shift_id_jN]
# output_file (str): chemin du fichier de sortie (.ros)
# original_file_ref (str): chemin relatif vers le fichier d'origine (Instance.ros), affiché dans <SchedulingPeriodFile>

def save_solution_to_ros(planning, output_file, original_file_ref="../../Instance1.ros"):
    # Création de la racine avec les attributs nécessaires (<Roster xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="Roster.xsd"> dans l'exemple)
    root = ET.Element("Roster", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:noNamespaceSchemaLocation": "Roster.xsd"
    })

    # Lien vers le fichier de période de planification (<SchedulingPeriodFile>../../Instance1.ros</SchedulingPeriodFile> dans l'exemple)
    fichier_planning = ET.SubElement(root, "SchedulingPeriodFile")
    fichier_planning.text = original_file_ref

    # Remplir les employés et leurs assignations
    for emp_id, shift_list in planning.items():
        # Ajoute les employés (<Employee ID="A">...</Employee> dans l'exemple)
        emp_elem = ET.SubElement(root, "Employee", {"ID": emp_id})
        for day, shift_id in enumerate(shift_list):
            if shift_id and shift_id != "-":
                # Ajoute le jour et le shift (<Assign><Day>3</Day><Shift>D</Shift></Assign> dans l'exemple)
                assign_elem = ET.SubElement(emp_elem, "Assign")
                day_elem = ET.SubElement(assign_elem, "Day")
                day_elem.text = str(day)
                shift_elem = ET.SubElement(assign_elem, "Shift")
                shift_elem.text = shift_id

    # Écriture dans le fichier XML avec déclaration
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ Solution exportée au format .ros dans : {output_file}")