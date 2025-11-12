**Objet de l'Étude :** Évaluer la performance et le risque d'une stratégie d'investissement systématique (DCA) sur les actions du CAC 40
et déterminer la durée de détention optimale.

**Période d'Analyse :**
    Début : 1er janvier 2015
    Fin   : 10 novembre 2025

**Stratégie d'Investissement (DCA) :**
    Fréquence    : Un investissement mensuel.
    Date         : Chaque premier jour ouvré du mois.
    Montant      : 100 € investis sur chaque action du CAC 40 individuellement.
    Portefeuille : L'analyse est conduite action par action. Chaque ligne d'action est gérée indépendamment.

**Stratégie de Désinvestissement (Vente) :**
    Scénarios testés : Chaque achat est revendu systématiquement après une durée de détention prédéfinie.
    Durées de détention testées : 6, 12, 18, 24, 30, 36, 42 et 60 (buy and hold) mois.

**Conditions de Transaction (Frais) :**
    Frais d'Achat : 1 € par ordre d'achat.
    Frais de Vente : 1 € par ordre de vente.

**Objectifs de l'Analyse :**
    Évaluer le Risque : Mesurer le taux de réussite, l'amplitude des pertes et la volatilité.
    Déterminer la Durée Idéale : Identifier la durée offrant le meilleur compromis rentabilité/taux de réussite.

============================================================================

**Biais et Limites de la Méthode d'Analyse**

**Biais de Survie (Survivorship Bias)**
    Le biais : L'analyse se concentre sur la composition actuelle du CAC 40. Elle ignore les entreprises qui ont été cotées
              dans l'indice entre 2015 et aujourd'hui mais qui en sont sorties (faillites, rachats, réorganisations).
    L'impact : La performance réelle était probablement moins bonne. Les actions les plus performantes ont tendance à rester dans l'indice, 
              tandis que les moins bonnes en sortent. En ignorant les "mauvais élèves", les résultats surestiment la rentabilité et sous-estiment le risque.

**Biais de Période (Period Bias)**
    Le biais : La période 2015-2025 est très spécifique. Elle inclut une longue phase de marché haussier, la crise du COVID-19 
              (chute brutale puis rebond vigoureux) et une période de fortes turbulences inflationnistes et géopolitiques.

**Biais de Cohérence du CAC 40**
    Le biais : La composition du CAC 40 change plusieurs fois par an. Votre rétrotest suppose que vous pouviez acheter une action en 2015 qui n'est entrée dans l'indice qu'en 2020
              ce qui est impossible en réalité.
    L'impact : Cela introduit une distortion historique. Pour être parfaitement exact, l'analyse devrait recréer la composition de l'indice à chaque date d'achat, 
              ce qui est beaucoup plus complexe.

**Biais de Frais Sous-estimés**
    Le biais : Des frais de 1€ sur un investissement de 100€ représentent un coût d'entrée de 1%. C'est réaliste pour un PEA
    L'impact : Cela pénalise disproportionnellement les durées courtes. Sur un trade de 6 mois, les 2€ de frais totaux pèsent 
              bien plus lourd sur la rentabilité potentielle que sur un trade de 5 ans. L'impact des frais de transaction est donc amplifié.

**Biais de Réinvestissement**
    Le biais : Le modèle suppose que l'argent issu des ventes (le capital et les gains) reste "stérile" et n'est pas réinvesti.
    L'impact : Dans la réalité, un investisseur réinvestirait probablement les produits des ventes. En ne le modélisant pas, 
              on sous-estime l'effet cumulatif des gains (intérêts composés), surtout pour les durées de détention courtes
              qui libèrent du capital plus fréquemment.

**Biais Fiscal Ignoré**
    Le biais : Le modèle ne tient pas compte de la fiscalité (Flat Tax à 30% en France sur les plus-values).
    L'impact : Cela fausse la comparaison des durées. Les trades fréquents (durées courtes) génèrent des impôts à payer chaque année,
               ce qui réduit le capital disponible pour les intérêts composés. Les durées longues, 
               en différant l'impôt, pourraient être plus efficaces fiscalement

**Utilisation:**
    Lancer maj_cours_euronext.py avant de lancer ce script
    modifier à votre guise:
        date_debut
        date_fin
        duree_investissement
        montant_mensuel
        frais_acquisition
        frais_cession
