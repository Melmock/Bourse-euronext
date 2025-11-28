# Bourse-euronext
Analyse des cours de la bourse de Paris (Euronext)  

Script en python qui récupère la composition des indices officiels directement sur le site euronext, puis télécharge les cours de ces actions pour les intégrer dans une base SQLITE facile d'accès  

## Installation:  
pip install yfinance  
pip install pdfplumber  
pip install pandas  

## Utilisation:  
python maj_cours_euronext.py

## Résultat:  
Base SQLITE cac40_data.db avec les données des actions à jour

## Récupération des pdf depuis euronext:  
1️⃣ **CAC 40** (Baromètre principal de l’économie française)  
2️⃣ **CAC Next 20** (Indicateur des entreprises en forte croissance ou en voie d’entrer dans le CAC 40)  
3️⃣ **CAC Mid 60** (Reflète la performance des ETI françaises  
4️⃣ **CAC Small** (Met en avant les PME cotées)  
5️⃣ **CAC Mid & Small** (Combine les entreprises du CAC Mid 60 et du CAC Small)  
6️⃣ **SBF 120** (CAC 40 + CAC Next 20 + CAC Mid 60)  
7️⃣ **CAC All-Tradable** (Donne la vision globale de la performance du marché parisien)  
8️⃣ **CAC Large 60** (Benchmark, ETF, mesure de la tendance “grandes valeurs”)  

---
Méthode 1 - Achat de toutes les actions du CAC40 ! [Lien](/dca_cac40/dca_cac40.md)  
Méthode 2 - Achat d'une action du CAC40 basé sur le volume [Lien](/dca_v0.1/dca_v0.1.md)  
---
Les Performances passées ne préjuge pas des résultats futurs* ceci n'est pas un conseil en investissement.
