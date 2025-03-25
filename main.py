# Developped by Antoine Rouillard, Thomas Vauley, Adam Kaoukeb and Anthonin Pain
import classes
import os

def read_file(path : str):
    
    with open(path, "r", encoding="utf-8") as fichier:
        for ligne in fichier:
            print(ligne)




def main():
    instance1_txt_path="Instances/Instance1.txt"
    read_file(instance1_txt_path)
    
main()
