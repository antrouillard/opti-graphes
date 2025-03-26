# Developped by Antoine Rouillard, Thomas Vauley, Adam Kaoukeb and Anthonin Pain
import classes
import os
import xml.etree.ElementTree as ET

tree = ET.parse("Instances/Instance1.ros")
root = tree.getroot()



print(f"Racine : {root.tag}")
""" for element in root.iter():
    print(f"{element.tag} : {element.text}")"""

#exemple de recupération d'un élément, ici Contract 

contracts = {}
for contract in root.find("Contracts"):
    contract_id = contract.get("ID")
    contracts[contract_id] = {
        "MinRestTime": contract.find("MinRestTime").text if contract.find("MinRestTime") is not None else None,
        "MaxSeq": [seq.attrib for seq in contract.findall("MaxSeq")],
        "MinSeq": [seq.attrib for seq in contract.findall("MinSeq")],
        "Workload": {
            "Max": contract.find("Workload/TimeUnits/Max/Count").text if contract.find("Workload/TimeUnits/Max/Count") is not None else None,
            "Min": contract.find("Workload/TimeUnits/Min/Count").text if contract.find("Workload/TimeUnits/Min/Count") is not None else None,
        },
        "ValidShifts": contract.find("ValidShifts").get("shift") if contract.find("ValidShifts") is not None else None
    }

# Affichage des contrats
for contract_id, details in contracts.items():
    print(f"Contract ID: {contract_id}")
    print(details)
    print("-" * 30)

