# Reflect'o Bus
En cours de développement, ce projet a pour but de développer un mirroir intelligent basé sur une carte Raspberry Pi, qui donne accès aux horaires de bus du réseau de transport en commun de votre ville (ce projet étant actuellement basé sur la ville de Marseille), [l'API](https://github.com/augustin64/lepilote) pour les bouches du Rhône étant en cours de développement

## Installation
#### Installer Arch Linux sur une carte raspberry pi :
[guide](https://archlinuxarm.org/platforms/armv8/broadcom/raspberry-pi-4)  pour la raspberry Pi 4  
_libre à vous d'utiliser une autre distribution linux, il faudra alors ajuster le script d'installation en conséquence_  
### Lancer le script d'installation
 * Via ssh : `systemctl enable sshd` permettra d'activer la connexion ssh
 * Directement via un écran et clavier connectés sur la raspberry

Si vous vous connectez en ssh, vous ne pourrez pas forcément vous connecter en tant que `root`, connectez vous donc dans l'utilisateur `alarm` (utilisateur par défaut sous archlinux arm) et rentrez la commande suivante :  
`su root`  
Le mot de passe par défaut étant le nom d'utilisateur

Pour lancer le script d'installation, lancez la commande suivante :  
`cd ~ & curl -s https://raw.githubusercontent.com/augustin64/Reflect-o-Bus/main/scripts/installation-rpi-alarm.sh > script.sh & chmod +x ./script.sh & ./script.sh`  
Vous devrez ensuite patienter environ 1/2 heure le temps que le script s'exécute (cela pouvant varier selon le modèle que vous utilisez et votre connexion Internet)

Si vous souhaitez utiliser la raspberry via sa carte wifi (et non l'interface ethernet), éditez le fichier `/etc/netctl/wlan0`  
`nano /etc/netctl/wlan0`

Vous pouvez ensuite redémarrer le système :  
`reboot`  

Lors du priochain redémarrage, environ 3/4 minutes après le démarrage de la raspberry, des informations s'afficheront à l'écran, notamment son adresse IP.  
Utilisez un autre appareil connecté sur le même réseau local pour naviguer sur cette page (`http://xx.xx.xx.xx:5000/`), vous y trouverez de quoi configurer les horaires que vous souhaitez afficher  
Si vous ne parvenez pas à atteindre cette page, vérifiez les paramètres du pare-feu de votre box.

## WIP :
 - Configurer la connexion sans fil du coté serveur (l'interface étant déjà fonctionnelle du côté client)  
 - Mettre en forme à l'aide de CSS les pages `/` et `/config`  
 - Changer la structure des modules et rajouter une couche de compatibilité pour rendre l'application compatible avec des APIs de plusieurs réseaux de transport
