# Reflect'o Bus
En cours de développement, ce projet a pour but de développer un mirroir intelligent basé sur une carte Raspberry Pi, qui donne accès aux horaires de bus du réseau de transport en commun de votre ville (ce projet étant actuellement basé sur la ville de Marseille), [l'API](https://github.com/augustin64/lepilote) pour les bouches du Rhône étant en cours de développement

## Aperçus

##### Aperçu de la page web :  
![](https://augustin64.github.io/reflect-o-bus/screenshot.png)  

##### Aperçu sur une raspberry pi (l'image ayant été retouchée afin de mieux voir l'écran) :  
![](https://augustin64.github.io/reflect-o-bus/raspberry-pi-edited.png)  


## Installation
[Page du wiki](https://github.com/augustin64/Reflect-o-Bus/wiki/Installation)

## WIP :
 - Configurer la connexion sans fil du coté serveur (l'interface étant déjà fonctionnelle du côté client)  
 - Mettre en forme à l'aide de CSS les pages `/` et `/config`  

## TODO :
 - Ajouter une option permettant d'afficher les horaires en temps relatif/ absolu (18:15/15min)
 - Ajouter une option permettant d'afficher l'heure sur l'écran
 - Changer la structure des modules et rajouter une couche de compatibilité pour rendre l'application compatible avec des APIs de plusieurs réseaux de transport
 - Basculer la récupération des horaires sur une requête JSON et une mise en forme JavaScript plut
