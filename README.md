# PokemonBattle

**PokemonBattle** est un projet permettant de créer et de simuler un tournoi entre Pokémon. Le programme récupère les données des Pokémon depuis l'API [PokeAPI](https://pokeapi.co/api/v2/pokemon/{id}) et les intègre dans une base de données SQLite. Un tournoi est ensuite généré avec 16 Pokémon, qui s'affrontent jusqu'à ce qu'il ne reste qu'un seul vainqueur. Ce projet utilise Python et des bibliothèques courantes pour afficher les combats dans le terminal.

## Auteurs

Le projet a été créé par HEM Patrick et Anthony Vallad.

## Table des matières

- [Installation](#installation)
- [Utilisation](#utilisation)
- [Fonctionnalités](#fonctionnalités)

## Installation

Pour installer le projet : 

```bash
# Cloner le dépôt
git clone https://github.com/TheSmartisen/PokemonBattle.git

# Aller dans le répertoire du projet
cd votre-projet

# Installer les dépendances
pip install -r requirements.txt
```

Les dépendances nécessaires au projet sont listées dans `requirements.txt` :

```
certifi==2024.8.30
charset-normalizer==3.3.2
idna==3.10
requests==2.32.3
urllib3==2.2.3
windows-curses==2.3.3
```

## Utilisation

Pour utiliser l'application, lancez le fichier `do_tournament.py` en **plein écran** pour une meilleure expérience :

```bash
python do_tournament.py
```

## Fonctionnalités

- Récupération des données des Pokémon depuis l'API [PokeAPI](https://pokeapi.co/api/v2/pokemon/{id}) et intégration dans une base de données SQLite.
- Création d'un tournoi avec 16 Pokémon, qui s'affrontent jusqu'à ce qu'il ne reste qu'un vainqueur.
