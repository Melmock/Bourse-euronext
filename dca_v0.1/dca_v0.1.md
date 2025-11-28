# Stratégie DCA (Dollar Cost Averaging) - CAC 40 - V0.1

## 📊 Vue d'ensemble

Cette stratégie d'investissement combine un investissement mensuel régulier avec une gestion active des sorties basée sur des objectifs de rendement.

---

## 💰 Méthode d'Achat

### Principe
Investissement mensuel régulier et automatique sur les actions du CAC 40.

### Paramètres d'achat

| Paramètre | Valeur |
|-----------|--------|
| **Montant mensuel** | 100€ par action |
| **Période** | Janvier 2015 - Octobre 2025 |
| **Frais d'acquisition** | 1€ par transaction |
| **Sélection de l'action** | Action CAC 40 avec le plus fort volume le 1er jour du mois |
| **Date d'achat** | Premier jour de bourse disponible |
| **Prix d'achat** | Moyenne (Ouverture + Clôture) / 2 |

### Calcul du nombre d'actions
```
Montant disponible = 100€ - 1€ (frais) = 99€
Quantité achetée = arrondi de (99€ / prix_unitaire)
```

> ⚠️ Si le prix est trop élevé pour acheter au moins 1 action, la transaction est annulée.

---

## 📈 Méthode de Vente

### Stratégie de sortie conditionnelle

La vente s'effectue selon une logique à trois niveaux :

#### 1️⃣ Vente optimale (après 12 mois)
- **Durée minimale de détention** : 12 mois (duree_investissement_min)
- **Condition** : Rendement brut ≥ +10% (rendement_min)
- **Vérification** : Quotidienne à partir du 12ème mois 
- **Action** : Vente dès que l'objectif est atteint

#### 2️⃣ Vente forcée (après 18 mois)
- **Durée maximale de détention** : 18 mois (12 mois + 6 mois) (duree_investissement_max)
- **Condition** : Vente automatique même en perte
- **Motif** : Éviter l'immobilisation prolongée du capital

#### 3️⃣ Vente de clôture
- **Date butoir** : 31 octobre 2025
- **Condition** : Liquidation de toutes les positions restantes
- **Motif** : Fin de la simulation

### Frais de vente
- **Coût** : 1€ par transaction de vente

---

## 📊 Métriques Calculées

### Performance Globale
- Total investi (net)
- Total vendu (net)
- Gain/Perte net
- Performance globale brute et nette (%)

### Impact des Frais
- Impact sur la performance (points %)
- Ratio frais/gains bruts (%)
- Taux de frais sur investissement total (%)

### Rendements Annualisés
- Rendement annualisé brut moyen
- Rendement annualisé net moyen
- Volatilité des performances
- Ratio de Sharpe (avec taux sans risque = 1,7%)

### Métriques de Réussite
- Taux de réussite des transactions (%)
- Nombre de transactions gagnantes/perdantes
- Gain moyen par transaction gagnante
- Perte moyenne par transaction perdante
- Ratio gain/perte

### Analyse des Durées
- Intervalle de détention : min, max, moyen, médian
- Écart-type (régularité des sorties)

---

## 🎯 Avantages de la Stratégie

✅ **Lissage du risque** : Investissement régulier indépendant des cycles de marché  
✅ **Discipline** : Automatisation des achats et ventes  
✅ **Objectif clair** : Vente à +10% de rendement brut  
✅ **Protection** : Vente forcée à 18 mois limite les pertes prolongées  
✅ **Liquidité** : Focus sur les actions les plus liquides du CAC 40

---

## ⚠️ Limites et Risques

❌ **Frais proportionnels** : Impact significatif sur petits montants (100€)  
❌ **Vente forcée** : Possibilité de sortir en perte après 18 mois  
❌ **Objectif unique** : +10% peut être trop rigide selon les conditions de marché  
❌ **Pas de stop-loss** : Aucune protection avant 18 mois en cas de forte baisse  
❌ **Coût d'opportunité** : Capital immobilisé 12-18 mois minimum

---

## 🔧 Paramètres Configurables

```python
montant_mensuel = 100.0              # Investissement mensuel
frais_acquisition = 1.0               # Frais d'achat
frais_cession = 1.0                   # Frais de vente
duree_investissement_min = 12         # Durée min (mois)
duree_investissement_max = 18         # Durée max (mois)
rendement_min = 10.0                  # Objectif de rendement (%)
```

---

## 📝 Notes Techniques

- **Base de données** : SQLite (`cac40_data.db`)
- **Source des données** : Actions du CAC 40 avec données OHLCV
- **Gestion des jours fériés** : Recherche automatique du prochain jour de bourse disponible
- **Exports** : 
  - `portefeuille.csv` : Détail de toutes les transactions
  - `resultats.csv` : Synthèse des métriques calculées

---

# 📊 Analyse Optimisation Stratégie DCA V0.1

## 🎯 Résultats de l'Analyse Comparative

### Méthodologie
- **Période** : 01/01/2015 - 31/10/2025
- **Investissement mensuel** : 100€
- **Seuils de gain testés** : 2% à 40%
- **Durées de détention** : 6 à 72 mois
- **Frais fixes** : 2€ par transaction (1€ acquisition + 1€ cession)

---

## 🏆 Top 5 des Stratégies Optimales

| Rang | Seuil | Durée | Gain Net | Perf. Nette | Perf. Annualisée | Sharpe | Succès |
|------|-------|-------|----------|-------------|------------------|---------|---------|
| 🥇 **1** | **40%** | **72 mois** | **7 544,34 €** | **63,51%** | **12,60%** | **0,63** | 90,00% |
| 🥈 **2** | 30% | 72 mois | 7 457,30 € | 62,78% | 12,53% | 0,62 | 90,00% |
| 🥉 **3** | 40% | 66 mois | 6 898,67 € | 58,07% | 12,24% | 0,60 | 88,46% |
| 4 | 20% | 72 mois | 7 387,34 € | 62,19% | 12,48% | 0,62 | 91,54% |
| 5 | 30% | 66 mois | 6 717,76 € | 56,55% | 12,06% | 0,59 | 88,46% |

---

## 📈 Analyse par Paramètre

### Impact du Seuil de Vente
| Seuil | Meilleur Gain Net | Durée Optimale | Perf. Nette |
|-------|------------------|----------------|-------------|
| 2% | 7 186,21 € | 72 mois | 60,49% |
| 5% | 7 220,96 € | 72 mois | 60,79% |
| 10% | 7 302,17 € | 72 mois | 61,47% |
| 20% | 7 387,34 € | 72 mois | 62,19% |
| 30% | 7 457,30 € | 72 mois | 62,78% |
| **40%** | **7 544,34 €** | **72 mois** | **63,51%** |

### Impact de la Durée de Détention (Seuil 40%)
| Durée | Gain Net | Perf. Nette | Volatilité |
|-------|----------|-------------|------------|
| 6 mois | 2 178,70 € | 18,34% | 24,87% |
| 12 mois | 2 638,74 € | 22,21% | 32,48% |
| 24 mois | 3 566,13 € | 30,02% | 37,81% |
| 36 mois | 4 344,38 € | 36,57% | 42,58% |
| 48 mois | 5 376,80 € | 45,26% | 45,28% |
| 60 mois | 6 315,57 € | 53,17% | 48,22% |
| **72 mois** | **7 544,34 €** | **63,51%** | **53,07%** |

---

## ⚖️ Métriques de Risque-Rendement

### Ratio de Sharpe par Stratégie
- **Meilleur** : 0,63 (40%/72m)
- **Moyen** : 0,55-0,60
- **Plus faible** : 0,45 (2%/12m)

### Volatilité des Performances
- **Plus stable** : 15,87% (2%/6m)
- **Plus volatile** : 55,17% (2%/72m)
- **Optimal** : 53,07% (40%/72m)

### Taux de Réussite
- **Maximum** : 93,85% (5-6%/72m)
- **Minimum** : 76,92% (30%/36m)
- **Stratégie optimale** : 90,00%

---

## 💰 Impact Financier Détaillé

### Comparaison Stratégies
| Métrique | Stratégie N°1 | Stratégie N°10 | Écart |
|----------|---------------|----------------|-------|
| Gain Net | 7 544,34 € | 5 179,70 € | +2 365 € |
| Performance | 63,51% | 43,59% | +19,92% |
| Performance Annualisée | 12,60% | 11,35% | +1,25% |

### Impact des Frais
- **Frais totaux** : 260€ (constant)
- **Impact sur performance** : -2,31% à -2,92%
- **Ratio frais/gains bruts** : 3,33% à 24,21%

---

## 🎯 Recommandations par Profil

### 🚀 Profil Maximisateur
**Stratégie N°1 : Seuil 40% / Durée 72 mois**
- ✅ Gain net maximum
- ✅ Meilleur ratio Sharpe
- ✅ Performance annualisée optimale

### 🛡️ Profil Prudent  
**Stratégie N°2 : Seuil 30% / Durée 72 mois**
- ✅ Gain presque identique (-87€)
- ✅ Seuil plus réaliste
- ✅ Même stabilité

### 💧 Profil Liquidité
**Stratégie N°3 : Seuil 40% / Durée 66 mois**
- ✅ Liquidités 6 mois plus tôt
- ✅ Performance maintenue
- ✅ Bon compromis temporal

### 📊 Profil Conservateur
**Stratégie N°4 : Seuil 20% / Durée 72 mois**
- ✅ Taux de réussite maximal (91,54%)
- ✅ Performance élevée
- ✅ Risque maîtrisé

---

## ✅ Conclusion Stratégique

### Stratégie Optimale Validée
**"Seuil de vente à 40% avec durée minimale de détention de 6 ans"**

### Avantages Clés
1. **Rendement maximal** : +7 544€ de gain net
2. **Efficacité** : Performance annualisée de 12,60%
3. **Équilibre** : Meilleur ratio risque/rendement (Sharpe 0,63)
4. **Fiabilité** : 90% de transactions gagnantes

### Mise en Œuvre
- Investissement mensuel maintenu à 100€
- Patience requise (détention longue)
- Seuil ambitieux mais réaliste sur 6 ans
- Acceptation d'une volatilité modérée

---

*Analyse réalisée sur données 2015-2025 - Performance passée ne préjuge pas des résultats futurs* ceci n'est pas un conseil en investissement.
