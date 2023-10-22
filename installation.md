# Installation

## Windows 10

### Installation de Python

Aller sur le site de Python: https://www.python.org et télécharger le module d'installation pour Windows. Prendre la version stable et lancer l'installation avec les options par défaut.

### Installation des fichiers de l'appli

Dézipper l'archive de l'appli dans votre dossier personnel et renommer le dossier créé mybudget.

### Création d'un environnement virtuel

(Source: https://docs.djangoproject.com/en/4.1/howto/windows/)

Ouvrir une fenêtre de commande en tapant cmd dans la barre de commande de windows,
puis lancer les commandes suivantes:

```
py -m venv mybudget
mybudget\Scripts\activate.bat
```

### Installation des modules nécessaires

Lancer l'installation des modules:

```
cd mybudget
py -m pip install -r requirements.txt
```

### Initialisation de la base de données

Créer le dossier data et initialiser la base de données:

```
mkdir data
py app/manage.py migrate
py app/manage.py loaddata init
```

Fermer la fenêtre de commandes.

### Installation du script de lancement

Créer un raccourci sur le fichier mybudget.bat et le déplacer sur le bureau.

### Lancement

* Lancer le raccourci mybudget
* Lancer un navigateur web et se connecter sur la page: http://localhost:8000/budget
* créer éventuellement un favori sur cette page pour simplifier l'accès

Si votre navigateur affiche cette page, tout est prêt !

![Capture d'écran de la page d'entrée de l'appli](/assets/mybudget.png)
