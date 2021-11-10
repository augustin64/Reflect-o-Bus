#!/usr/bin/python3
"""
Vérifie la validité de la configuration actuelle
en fonction d'un template minimal
"""
import configparser


def check(configpath, templatepath):
    """
    Vérifie la validité de la configuration actuelle
    en fonction d'un template minimal
    """
    config = configparser.ConfigParser()
    config.read(configpath)

    template = configparser.ConfigParser()
    template.read(templatepath)

    modified = False

    for field in template:
        if not field in config.keys():
            config[field] = template[field]
            print(f"{configpath} : pas d'entrée pour '{field}'")
        for option in template[field]:
            if not option in config[field].keys():
                config[field][option] = template[field][option]
                print(f"{configpath} : pas d'entrée pour '{option}'")
                modified = True

    if modified:
        with open(configpath, "w") as configfile:
            config.write(configfile)
        print(f"{configpath} : Ajout des champs manquants")
