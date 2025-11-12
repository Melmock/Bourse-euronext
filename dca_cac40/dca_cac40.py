#
# Objet de l'Étude : Évaluer la performance et le risque d'une stratégie d'investissement systématique (DCA) sur les actions du CAC 40
# et déterminer la durée de détention optimale.
#
# Période d'Analyse :
#     Début : 1er janvier 2015
#     Fin   : 10 novembre 2025
#
# Stratégie d'Investissement (DCA) :
#     Fréquence    : Un investissement mensuel.
#     Date         : Chaque premier jour ouvré du mois.
#     Montant      : 100 € investis sur chaque action du CAC 40 individuellement.
#     Portefeuille : L'analyse est conduite action par action. Chaque ligne d'action est gérée indépendamment.
#
# Stratégie de Désinvestissement (Vente) :
#     Scénarios testés : Chaque achat est revendu systématiquement après une durée de détention prédéfinie.
#     Durées de détention testées : 6, 12, 18, 24, 30, 36, 42 et 60 (buy and hold) mois.
#
# Conditions de Transaction (Frais) :
#     Frais d'Achat : 1 € par ordre d'achat.
#     Frais de Vente : 1 € par ordre de vente.
#
# Objectifs de l'Analyse :
#     Évaluer le Risque : Mesurer le taux de réussite, l'amplitude des pertes et la volatilité.
#     Déterminer la Durée Idéale : Identifier la durée offrant le meilleur compromis rentabilité/taux de réussite.
# Biais et Limites de la Méthode d'Analyse
#
#   ========================================================================================================================
#
# 1. Biais de Survie (Survivorship Bias)
#     Le biais : L'analyse se concentre sur la composition actuelle du CAC 40. Elle ignore les entreprises qui ont été cotées
#               dans l'indice entre 2015 et aujourd'hui mais qui en sont sorties (faillites, rachats, réorganisations).
#     L'impact : La performance réelle était probablement moins bonne. Les actions les plus performantes ont tendance à rester dans l'indice, 
#               tandis que les moins bonnes en sortent. En ignorant les "mauvais élèves", les résultats surestiment la rentabilité et sous-estiment le risque.
#
# 2. Biais de Période (Period Bias)
#     Le biais : La période 2015-2025 est très spécifique. Elle inclut une longue phase de marché haussier, la crise du COVID-19 
#               (chute brutale puis rebond vigoureux) et une période de fortes turbulences inflationnistes et géopolitiques.
#
# 3. Biais de Cohérence du CAC 40
#     Le biais : La composition du CAC 40 change plusieurs fois par an. Votre rétrotest suppose que vous pouviez acheter une action en 2015 qui n'est entrée dans l'indice qu'en 2020
#               ce qui est impossible en réalité.
#     L'impact : Cela introduit une distortion historique. Pour être parfaitement exact, l'analyse devrait recréer la composition de l'indice à chaque date d'achat, 
#               ce qui est beaucoup plus complexe.
#
# 4. Biais de Frais Sous-estimés
#     Le biais : Des frais de 1€ sur un investissement de 100€ représentent un coût d'entrée de 1%. C'est réaliste pour un PEA
#     L'impact : Cela pénalise disproportionnellement les durées courtes. Sur un trade de 6 mois, les 2€ de frais totaux pèsent 
#               bien plus lourd sur la rentabilité potentielle que sur un trade de 5 ans. L'impact des frais de transaction est donc amplifié.

# 5. Biais de Réinvestissement
#     Le biais : Le modèle suppose que l'argent issu des ventes (le capital et les gains) reste "stérile" et n'est pas réinvesti.
#     L'impact : Dans la réalité, un investisseur réinvestirait probablement les produits des ventes. En ne le modélisant pas, 
#               on sous-estime l'effet cumulatif des gains (intérêts composés), surtout pour les durées de détention courtes
#               qui libèrent du capital plus fréquemment.
#
# 6. Biais Fiscal Ignoré
#     Le biais : Le modèle ne tient pas compte de la fiscalité (Flat Tax à 30% en France sur les plus-values).
#     L'impact : Cela fausse la comparaison des durées. Les trades fréquents (durées courtes) génèrent des impôts à payer chaque année,
#                ce qui réduit le capital disponible pour les intérêts composés. Les durées longues, 
#                en différant l'impôt, pourraient être plus efficaces fiscalement

#
# Utilisation:
# lancer maj_cours_euronext.py avant de lancer ce script
# modifier à votre guise:
# date_debut, date_fin, duree_investissement, montant_mensuel, frais_acquisition, frais_cession
#

import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

pd.set_option('display.max_rows', 1000) 
pd.set_option('display.max_columns', 500) 
pd.set_option('display.width', 1000) 

# Connexion à la base de données
conn = sqlite3.connect('cac40_data.db')
cursor = conn.cursor()

# Dates de début et fin de l'analyse
date_debut = datetime(2020, 1, 1)
date_fin   = datetime(2025, 10, 31)
duree_investissement = 12   # en mois

# Montant d'investissement mensuel par action
montant_mensuel = 100.0

# Frais de transaction (en euros)
frais_acquisition = 1.0  # Frais par transaction d'achat quelque soit le montant
frais_cession     = 1.0  # Frais par transaction de vente quelque soit le montant

# Structure pour le portefeuille
portefeuille = pd.DataFrame(columns=['action', 'date_acquisition', 'prix_unitaire_achat', 'quantite_actions','frais_acquisition','cout_acquisition_brut','cout_acquisition_net'])

# Fonction pour trouver le premier jour disponible du mois et retourner le cours moyen (Open+Close)/2 avec la date de l'opération
def cours_action_asap(annee, mois, action,decalage=0):
    """Trouve le premier jour disponible dans la table pour un mois donné"""
    premier_jour  = datetime(annee, mois, 1)+timedelta(days=decalage)
    nb_jours_mois = (premier_jour + relativedelta(months=1) - timedelta(days=1)).day    

    # Vérifie si la date demandée est après la dernière date disponible
    cursor.execute("""
        SELECT max(date)
        FROM actions
        WHERE action = ?
    """, (action,))
    result = cursor.fetchone()
    if result:
        date_max = datetime.strptime(result[0], '%Y-%m-%d')
        if premier_jour >= date_max:
            cursor.execute("""
                SELECT date, Open, Close 
                FROM actions 
                WHERE date = ? AND action = ?
            """, (result[0], action))
            result = cursor.fetchone()
            if result:
                date_str, prix_open, prix_close = result
                prix = (prix_open+prix_close)/2  # Prix moyen entre Open et Close
                return (date_str, prix) 

    # Vérifie si la date demandée est avant la première date disponible
    cursor.execute("""
        SELECT min(date)
        FROM actions 
        WHERE action = ?
    """, (action,))
    result = cursor.fetchone()
    if result:
        date_min = datetime.strptime(result[0], '%Y-%m-%d')
        if premier_jour < date_min:
            return 0,0

    # Cherche jusqu'au dernier jours du mois après le 1er du mois
    for i in range(nb_jours_mois):
        date_test = premier_jour + timedelta(days=i)
        
        cursor.execute("""
            SELECT date, Open, Close 
            FROM actions 
            WHERE date = ? AND action = ?
        """, (date_test.strftime('%Y-%m-%d'), action))
        result = cursor.fetchone()
        if result:
            date_str, prix_open, prix_close = result
            prix = (prix_open+prix_close)/2  # Prix moyen entre Open et Close
            return (date_str, prix) 
    return None

def vente_des_actions(portefeuille):
    # Vente des actions après duree_investissement mois
    for index in portefeuille.index:
        action           = portefeuille.at[index, 'action']
        date_acquisition = datetime.strptime(portefeuille.at[index, 'date_acquisition'], '%Y-%m-%d')
        quantite_actions = portefeuille.at[index, 'quantite_actions']

        # Date de vente après x mois
        date_cession_demandee    = date_acquisition + relativedelta(months=duree_investissement)
        date_cession, prix_unitaire_vente = cours_action_asap(date_cession_demandee.year, date_cession_demandee.month, action,decalage=0)

        if date_cession:
            portefeuille.at[index, 'date_cession']         = date_cession
            portefeuille.at[index, 'prix_unitaire_vente']  = prix_unitaire_vente
            portefeuille.at[index, 'frais_cession']        = frais_cession
            portefeuille.at[index, 'produit_cession_brut'] = prix_unitaire_vente * quantite_actions
            portefeuille.at[index, 'produit_cession_net']  = prix_unitaire_vente * quantite_actions- frais_cession
            portefeuille.at[index, 'plus_value_brute']     = portefeuille.at[index, 'produit_cession_brut'] - portefeuille.at[index, 'cout_acquisition_brut']
            portefeuille.at[index, 'plus_value_nette']     = portefeuille.at[index, 'produit_cession_net']  - portefeuille.at[index, 'cout_acquisition_net'] 
            portefeuille.at[index, 'duree_detention_mois'] = duree_investissement
            portefeuille.at[index, 'performance_brute_%']  = (portefeuille.at[index, 'plus_value_brute'] / portefeuille.at[index, 'cout_acquisition_brut']) * 100
            portefeuille.at[index, 'performance_net_%']    = (portefeuille.at[index, 'plus_value_nette'] / portefeuille.at[index, 'cout_acquisition_net']) * 100
            print(f"Vente {action} le {date_cession} au prix de {prix_unitaire_vente:.2f}€ | Gain/Perte: {portefeuille.at[index, 'plus_value_nette']:.2f}€")
        else:
            print(f"  ⚠ {action}: Pas de cours disponible pour la vente après {duree_investissement} mois.")    
    return portefeuille

def calculer_rendements_annualises(portefeuille):
    """Calcule les rendements annualisés pour chaque ligne"""
    
    # Durée en années pour chaque ligne
    portefeuille['duree_annees'] = portefeuille['duree_detention_mois'] / 12
    
    # Rendement annualisé brut par ligne
    portefeuille['rendement_annualise_brut_%'] = (
        ((portefeuille['produit_cession_brut'] / portefeuille['cout_acquisition_brut']) 
         ** (1 / portefeuille['duree_annees']) - 1) * 100
    )
    
    # Rendement annualisé net par ligne
    portefeuille['rendement_annualise_net_%'] = (
        ((portefeuille['produit_cession_net'] / portefeuille['cout_acquisition_net']) 
         ** (1 / portefeuille['duree_annees']) - 1) * 100
    )
    
    return portefeuille

def analyse_resultats(portefeuille,action):
    resultats = []

    portefeuille = calculer_rendements_annualises(portefeuille)
    print(f"\n=== 📊 MÉTRIQUES GLOBALES ===")
    total_investi_brut = portefeuille['cout_acquisition_brut'].sum()
    total_investi      = portefeuille['cout_acquisition_net'].sum()
    total_vente_brut   = portefeuille['produit_cession_brut'].sum()
    total_vente        = portefeuille['produit_cession_net'].sum()
    total_gain_net     = total_vente - total_investi
    total_gain_brut    = total_vente_brut - total_investi_brut
    total_frais        = portefeuille['frais_acquisition'].sum() + portefeuille['frais_cession'].sum()

    performance_globale_brute = (total_gain_brut / total_investi_brut) * 100
    performance_globale_nette = (total_gain_net / total_investi) * 100

    print(f"Total investi (net)        : {total_investi:.2f}€")
    print(f"Total vendu (net)          : {total_vente:.2f}€")
    print(f"Gain/Perte net             : {total_gain_net:.2f}€")
    print(f"Total frais                : {total_frais:.2f}€")
    print(f"Performance globale BRUTE  : {performance_globale_brute:.2f}%")
    print(f"Performance globale NETTE  : {performance_globale_nette:.2f}%")

    print(f"\nDurée de détention: {duree_investissement} mois")
    print(f"Nombre de transactions: {len(portefeuille)}")

    # Impact des frais
    impact_frais_sur_performance = performance_globale_brute - performance_globale_nette
    ratio_frais_gains = (total_frais / abs(total_gain_brut)) * 100 if total_gain_brut != 0 else 0
    taux_frais = (total_frais / total_investi) * 100
    
    print(f"\n--- IMPACT DES FRAIS ---")
    # Impact sur performance : Si vous avez -2.5 points, cela signifie que les frais vous ont fait perdre 2.5% de rendement
    print(f"Impact des frais sur la performance: -{impact_frais_sur_performance:.2f}%")

    #Frais/Gains bruts : Si = 15%, cela signifie que 15% de vos gains bruts partent en frais
    print(f"Ratio frais/gains bruts: {ratio_frais_gains:.2f}%")

    if ratio_frais_gains<0:
        print("\tGain négatif : 🚨 Les frais amplifient les pertes")
    elif ratio_frais_gains<5:
        print("\t< 5%   : ✅ Très bon (frais optimisés)")
    elif ratio_frais_gains<10:
        print("\t5-10%  : ⚠️ Acceptable  ")
    elif ratio_frais_gains<15:
        print("\t10-15% : ❌ Élevé (revoir la stratégie)")
    else:
        print("\t> 15%  : 🚨 Très élevé (frais trop importants)")

    # Taux de frais : Représente le coût fixe des frais par rapport à votre investissement total
    print(f"Taux de frais sur le total investi: {taux_frais:.2f}%")

    print(f"\n=== 📈 MÉTRIQUES DE RENDEMENT ===")
    Rendement_annualise_moyen = portefeuille['performance_net_%'].mean()

    rendement_annualise_brut_moyen = ( (portefeuille['rendement_annualise_brut_%'] * portefeuille['cout_acquisition_brut']).sum() / total_investi_brut)
    rendement_annualise_net_moyen  = ( (portefeuille['rendement_annualise_net_%']  * portefeuille['cout_acquisition_net']).sum()  / total_investi)

    print(f"\n--- RENDEMENTS ANNUALISÉS MOYENS ---")
    print(f"Rendement annualisé BRUT moyen   : {rendement_annualise_brut_moyen:+.2f}% par an")
    print(f"Rendement annualisé NET moyen    : {rendement_annualise_net_moyen:+.2f}% par an")

    # ==========================================================

    # Volatilité des performances nettes (en points de %)
    volativite_des_performances=portefeuille['performance_net_%'].std()
    print(f"Volatilité des performances nettes par transaction: {volativite_des_performances:.2f}%")

    # Volatilité des rendements annualisés nets
    volatilite_rendement_annualise = portefeuille['rendement_annualise_net_%'].std()
    # print(f"Volatilité des rendement annualise: {volatilite_rendement_annualise:.2f}%")

    # Taux sans risque (ex: Livret A à 1.7% annuel)
    taux_sans_risque = 1.7

    # Ratio de Sharpe
    ratio_sharpe = (rendement_annualise_net_moyen - taux_sans_risque) / volatilite_rendement_annualise

    print(f"Ratio de Sharpe  avec rf={taux_sans_risque}: {ratio_sharpe:.2f}")
    if ratio_sharpe < 0:
        print("\t< 0 : 🚨 Mauvais (le rendement est en dessous du taux sans risque)"    )
    elif ratio_sharpe < 1:
        print("\t0 - 1 : ⚠️ Rendement insuffisant pour le risque pris" )   
    elif ratio_sharpe < 2:
        print("\t1 - 2 : ✅ Bon compromis rendement/risque" )
    elif ratio_sharpe < 3:
        print("\t2 : 👍 Très bon" )
    else:
        print("\t3 : 🌟 Excellent rendement ajusté du risque" )

    # Taux frais effectif pour l'efficacité opérationnelle
    taux_frais_effectif = (total_frais / total_investi) * 100
    print(f"Taux de frais effectif sur le total investi: {taux_frais_effectif:.2f}%")
    if taux_frais_effectif < 0.5:
        print("🎯 < 0,5%   : EXCELLENT (Professionnel)")
    elif taux_frais_effectif < 1.0:
        print("✅ 0,5-1%   : TRÈS BON (Compétitif)")
    elif taux_frais_effectif < 2.0:
        print("⚠️  1-2%     : ACCEPTABLE (Standard)")
    elif taux_frais_effectif < 3.0:
        print("❌ 2-3%     : ÉLEVÉ (Pénalisant)")
    else:
        print("🚨 > 3%     : TRÈS ÉLEVÉ (À éviter)")

    print("=======================")
    meilleur_performance=portefeuille['performance_net_%'].max()
    print(f"Meilleure performance nette sur une transaction: {meilleur_performance:.2f}%")
    pire_performance=portefeuille['performance_net_%'].min()
    print(f"Pire performance nette sur une transaction (Max Drawdown): {pire_performance:.2f}%")
    print("=" * 40)

    performance_moyenne_par_transaction=portefeuille['performance_net_%'].mean()
    print(f"Performance nette moyenne par transaction: {performance_moyenne_par_transaction:.2f}%")
    performance_median_par_transaction=portefeuille['performance_net_%'].median()
    print(f"Performance nette médiane par transaction: {performance_median_par_transaction:.2f}%")
    print("=" * 40)
    # print(f"Coût_opportunite_moyen_par_transaction {(Rendement_annualise_moyen - rf) * (duree_investissement / 12):.2f}%")
    # print(f"Coût_opportunite_moyen_en_euros {(Rendement_annualise_moyen - rf) * (duree_investissement / 12) * total_investi / 100:.2f}€")

    print("\n=== 🎯 MÉTRIQUES DE RÉUSSITE DES TRANSACTIONS ===")
    if portefeuille.shape[0]>0:
        taux_de_reussite=(portefeuille[portefeuille['performance_net_%'] > 0].shape[0] / portefeuille.shape[0]) * 100
    else:
        taux_de_reussite=0
    print(f"Taux de réussite des transactions: {taux_de_reussite:.2f}%")
    nombre_de_transactions_gagnantes=portefeuille[portefeuille['performance_net_%'] > 0].shape[0]
    print(f"Nombre de transactions gagnantes: {nombre_de_transactions_gagnantes}")
    nombre_de_transactions_perdantes=portefeuille[portefeuille['performance_net_%'] <= 0].shape[0]
    print(f"Nombre de transactions perdantes: {nombre_de_transactions_perdantes}")
    gain_moyen_par_transaction_gagnante=portefeuille[portefeuille['performance_net_%'] > 0]['performance_net_%'].mean()
    print(f"Gain moyen par transaction gagnante: {gain_moyen_par_transaction_gagnante:.2f}%")
    perte_moyenne_par_transaction_perdante=portefeuille[portefeuille['performance_net_%'] <= 0]['performance_net_%'].mean()
    print(f"Perte moyenne par transaction perdante: {perte_moyenne_par_transaction_perdante:.2f}%")
    ratio_gain_perte= - gain_moyen_par_transaction_gagnante / perte_moyenne_par_transaction_perdante if perte_moyenne_par_transaction_perdante !=0 else float('inf')
    print(f"Ratio gain/perte: {ratio_gain_perte:.2f}")
    print("=" * 40)

    print(f"\n=== 📈 MÉTRIQUES DE RENDEMENT POUR 6 MOIS ===")

    print('=' * 40)
    portefeuille['date_dt'] = pd.to_datetime(portefeuille['date_acquisition'])
    portefeuille = portefeuille.sort_values(['action', 'date_dt'])

    intervals = []
    for action in portefeuille['action'].unique():
        action_dates = portefeuille[portefeuille['action'] == action]['date_dt']
        if len(action_dates) > 1:
            action_intervals = action_dates.diff().dropna()
            intervals.extend([delta.days for delta in action_intervals])

    if intervals:
        intervals_series = pd.Series(intervals)

        resultats.append(["Intervalle MIN", f"{intervals_series.min():.0f} jours", ""])
        resultats.append(["Intervalle MAX", f"{intervals_series.max():.0f} jours", ""])
        resultats.append(["Intervalle MOYEN", f"{intervals_series.mean():.1f} jours", ""])
        resultats.append(["Intervalle MÉDIAN", f"{intervals_series.median():.1f} jours", ""])
        resultats.append(["Écart-type", f"{intervals_series.std():.1f} jours", ""])

        print(f"Intervalle MIN: {intervals_series.min():.0f} jours")
        print(f"Intervalle MAX: {intervals_series.max():.0f} jours") 
        print(f"Intervalle MOYEN: {intervals_series.mean():.1f} jours")
        print(f"Intervalle MÉDIAN: {intervals_series.median():.1f} jours")
        print(f"Écart-type: {intervals_series.std():.1f} jours")
        
        # Analyse de la régularité
        ecart_type = intervals_series.std()
        if ecart_type < 5:
            regularite = "✅ TRÈS RÉGULIER"
        elif ecart_type < 10:
            regularite = "✅ RÉGULIER" 
        elif ecart_type < 20:
            regularite = "⚠️  ASSEZ RÉGULIER"
        else:
            regularite = "❌ PEU RÉGULIER"
        print(f"Régularité: {regularite}")
    else:
        print("Données insuffisantes pour l'analyse des intervalles")

    resultats.append(["MÉTRIQUES GLOBALES", "", ""])
    resultats.append(["Action", action, ""])
    resultats.append(["Date acquisition début", portefeuille['date_acquisition'].min(), ""])
    resultats.append(["Date acquisition fin",   portefeuille['date_acquisition'].max(), ""])
    
    resultats.append(["Total investi (net)", f"{total_investi:.2f}€", ""])
    resultats.append(["Total vendu (net)", f"{total_vente:.2f}€", ""])
    resultats.append(["Gain/Perte net", f"{total_gain_net:.2f}€", ""])
    resultats.append(["Total frais", f"{total_frais:.2f}€", ""])
    resultats.append(["Performance globale BRUTE", f"{performance_globale_brute:.2f}%", ""])
    resultats.append(["Performance globale NETTE", f"{performance_globale_nette:.2f}%", ""])
    resultats.append(["Durée de détention", f"{duree_investissement} mois", ""])
    resultats.append(["Nombre de transactions", f"{len(portefeuille)}", ""])

    resultats.append(["", "", ""])
    resultats.append(["IMPACT DES FRAIS", "", ""])
    resultats.append(["Impact des frais sur la performance", f"-{impact_frais_sur_performance:.2f}%", ""])
    resultats.append(["Ratio frais/gains bruts", f"{ratio_frais_gains:.2f}%", ""])
    resultats.append(["Taux de frais sur le total investi", f"{taux_frais:.2f}%", ""])

    resultats.append(["", "", ""])
    resultats.append(["PERFORMANCES INDIVIDUELLES", "", ""])
    resultats.append(["Meilleure performance nette sur une transaction", f"{meilleur_performance:.2f}%", ""])
    resultats.append(["Pire performance nette sur une transaction (Max Drawdown)", f"{pire_performance:.2f}%", ""])
    resultats.append(["Performance nette moyenne par transaction", f"{performance_moyenne_par_transaction:.2f}%", ""])
    resultats.append(["Performance nette médiane par transaction", f"{performance_median_par_transaction:.2f}%", ""])
    resultats.append(["", "", ""])

    resultats.append(["", "", ""])
    resultats.append(["MÉTRIQUES DE RENDEMENT", "", ""])
    resultats.append(["RENDEMENTS ANNUALISÉS MOYENS", "", ""])
    resultats.append(["Rendement annualisé BRUT moyen", f"{rendement_annualise_brut_moyen:+.2f}% par an", ""])
    resultats.append(["Rendement annualisé NET moyen", f"{rendement_annualise_net_moyen:+.2f}% par an", ""])

    resultats.append(["Volatilité des performances nettes par transaction", f"{volativite_des_performances:.2f}%", ""])
    resultats.append(["Ratio de Sharpe", f"{ratio_sharpe:.2f}", f"rf={taux_sans_risque}%"])

    resultats.append(["MÉTRIQUES DE RÉUSSITE DES TRANSACTIONS", "", ""])
    resultats.append(["Taux de réussite des transactions", f"{taux_de_reussite:.2f}%", ""])
    resultats.append(["Nombre de transactions gagnantes", f"{nombre_de_transactions_gagnantes}", ""])
    resultats.append(["Nombre de transactions perdantes", f"{nombre_de_transactions_perdantes}", ""])
    resultats.append(["Gain moyen par transaction gagnante", f"{gain_moyen_par_transaction_gagnante:.2f}%", ""])
    resultats.append(["Perte moyenne par transaction perdante", f"{perte_moyenne_par_transaction_perdante:.2f}%", ""])
    resultats.append(["Ratio gain/perte", f"{ratio_gain_perte:.2f}", ""])
    
    # Sauvegarder tous les résultats dans un fichier CSV
    # df_resultats = pd.DataFrame(resultats, columns=["Métrique", "Valeur", "Commentaire"])
    # df_resultats.to_csv("resultat_"+action+".csv", index=True, encoding='utf-8-sig')
    return resultats

# Récupérer la liste des actions disponibles
cursor.execute("SELECT DISTINCT action FROM actions where action in (SELECT ticker_yahoo FROM cac40_composition where nom_indice='CAC_40' and date_maj=(select max(date_maj) from cac40_composition) limit 300) ORDER BY action")
actions_list = [row[0] for row in cursor.fetchall()]

print(f"Actions trouvées: {actions_list}")
print(f"\n=== SIMULATION DCA ===")
print(f"Période: {date_debut.strftime('%Y-%m-%d')} à {date_fin.strftime('%Y-%m-%d')}")
print(f"Investissement mensuel par action: {montant_mensuel}€")
print(f"Durée de détention: {duree_investissement} mois\n")

# Parcourir chaque mois
date_courante = date_debut
achats_en_cours = []

while date_courante <= date_fin:
    annee = date_courante.year
    mois  = date_courante.month

    # Pour chaque action, effectuer un achat
    for action in actions_list:
        date_acquisition,prix_unitaire_achat = cours_action_asap(annee, mois, action)

        # Calculer le nombre d'actions entières achetées
        # Montant disponible après frais d'achat
        montant_disponible = montant_mensuel - frais_acquisition
        if prix_unitaire_achat == 0:
            quantite_actions = 0
            print(f"  ⚠ {action}: Pas de cours disponible pour l'achat en {annee}-{mois:02d}.")
        else:
            quantite_actions = int(montant_disponible / prix_unitaire_achat)  # Nombre entier d'actions

        # Si on ne peut pas acheter au moins 1 action, on saute
        if quantite_actions >= 1:
            print(f"Achat {action} le {date_acquisition} au prix de {prix_unitaire_achat:.2f}€")
            portefeuille.loc[len(portefeuille)] = [
                action, 
                date_acquisition, 
                prix_unitaire_achat, 
                quantite_actions,
                frais_acquisition,
                quantite_actions * prix_unitaire_achat,
                quantite_actions * prix_unitaire_achat+frais_acquisition
                ]
        else:
            print(f"  ⚠ {action}: Montant insuffisant (prix: {prix_unitaire_achat:.2f}€)")

    date_courante = date_courante + relativedelta(months=1)

portefeuille = vente_des_actions(portefeuille)

print(portefeuille.head(10))
portefeuille.to_csv(r'portefeuille.csv',sep=';',index=True,encoding='utf-8',decimal=",", float_format='%.2f', mode='w', header=True)

resultat = pd.DataFrame()
for action in actions_list:
    portefeuille_indiv = portefeuille[portefeuille['action'] == action].copy()
    resultats_list = analyse_resultats(portefeuille_indiv, action)

    valeurs_dict = {}
    for item in resultats_list:
        if len(item) >= 2:
            metrique = item[0]
            valeur = item[1]
            valeurs_dict[metrique] = valeur
    resultat[action] = pd.Series(valeurs_dict)

resultat.to_csv("resultat_valeurs_seules.csv", encoding='utf-8-sig')

conn.close()
