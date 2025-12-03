import pdfplumber
import yfinance as yf
import requests
from io import BytesIO
import pandas as pd
import sqlite3
from datetime import datetime
import time

def create_connection(db_file):
    """Crée une connexion à la base de données SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """Crée la table si elle n'existe pas"""
    create_table_cac40_composition = """
    CREATE TABLE IF NOT EXISTS cac40_composition (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_maj DATE NOT NULL,
        company TEXT NOT NULL,
        mnemonic TEXT NOT NULL,
        sector_icb TEXT NOT NULL,
        weight_percent REAL NOT NULL,
        ticker_yahoo TEXT NOT NULL,
        nom_indice TEXT NOT NULL,
        UNIQUE(date_maj, mnemonic,nom_indice)
    );
    """
    create_table_sql_actions = """
    CREATE TABLE actions (
    date           DATE,
    Open           REAL,
    High           REAL,
    Low            REAL,
    Close          REAL,
    Volume         INTEGER,
    Dividends      REAL,
    [Stock Splits] REAL,
    action         TEXT,
    UNIQUE(date, action)
    );
    """
    create_index="""
    CREATE INDEX IF NOT EXISTS idx_actions_date ON actions(date);
    CREATE INDEX IF NOT EXISTS idx_actions_action_date ON actions(action, date);
    CREATE INDEX IF NOT EXISTS idx_actions_year_month ON actions(
        strftime('%Y', date), 
        strftime('%m', date)
    );
    CREATE INDEX IF NOT EXISTS idx_cac40 ON cac40_composition(
        nom_indice, date_maj, ticker_yahoo
    );
    """

    try:
        cursor = conn.cursor()
        cursor.execute(create_table_cac40_composition)
        cursor.execute(create_table_sql_actions)
        cursor.executescript(create_index)
        conn.commit()   
    except sqlite3.Error as e:
        print(e)

def insert_composition_indice(conn, data):
    """Insère les données dans la table en évitant les doublons"""
    insert_sql = """
    INSERT OR IGNORE INTO cac40_composition 
    (date_maj, company, mnemonic, sector_icb, weight_percent, ticker_yahoo,nom_indice)
    VALUES (?, ?, ?, ?, ?, ?,?)
    """
    try:
        cursor = conn.cursor()
        cursor.executemany(insert_sql, data)
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion: {e}")
        return 0

def insert_actions(conn, data):
    """Insère les données dans la table en évitant les doublons"""
    insert_sql = """
    INSERT OR IGNORE INTO actions
    (date, Open, High, Low, Close, Volume, Dividends, [Stock Splits], action)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor = conn.cursor()
        cursor.executemany(insert_sql, data)
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion: {e}")
        return 0

def extract_euronext_from_pdf(url_pdf,conn):
    # Date du jour
    current_date = datetime.now().date()
    nom_indice = url_pdf.split("/")[-1].replace(".pdf", "").replace("_Index_Composition", "")

    try:
        cursor = conn.cursor()
        cursor.execute("select COUNT(*) from cac40_composition where date_maj=? and nom_indice=?", (current_date, nom_indice))
        count_existing = cursor.fetchone()[0]   
        if count_existing > 0:
            print(f"Données déjà présentes pour la date {current_date} et l'indice {nom_indice}, saut de l'insertion.")
            return 0    
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion: {e}")
        return 0    
        
    # Téléchargement et extraction PDF
    response = requests.get(url_pdf)
    pdf_file = BytesIO(response.content)
    rows = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            words = page.extract_words()
            lines = {}
            for w in words:
                y = round(w['top'])
                if y not in lines:
                    lines[y] = []
                lines[y].append(w)
            
            for y in sorted(lines.keys()):
                line = lines[y]
                line.sort(key=lambda w: w['x0'])
                columns = []
                current_col = []
                last_x1 = None
                
                for w in line:
                    if last_x1 is None or (w['x0'] - last_x1) < 15:
                        current_col.append(w['text'])
                    else:
                        columns.append(' '.join(current_col))
                        current_col = [w['text']]
                    last_x1 = w['x1']
                
                if current_col:
                    columns.append(' '.join(current_col))
                
                # Garde uniquement les lignes avec exactement 4 colonnes
                if len(columns) == 4:
                    rows.append(columns)
    
    # Préparer les données pour SQLite
    columns = ["Company", "MNEMO", "Sector (ICB)", "Weight (%)"]
    df_data = pd.DataFrame(rows, columns=columns)
    df_data['Weight (%)'] = df_data['Weight (%)'].str.replace(',', '.').str.replace('%', '').astype(float)

    # Corrections bug ticker Yahoo
    # 'APAM.PA' , 'SOLB.PA', 'TOUP.PA')
    # 'TOUP.PA'  -> 'ALTOU.PA'
    # 'SOLB.PA'  -> 'SOLB.BR'
    # 'APAM.PA'  -> 'APAM.AS'

    df_data['ticker_yahoo'] = df_data['MNEMO'] + ".PA"
    df_data['ticker_yahoo'] = df_data['ticker_yahoo'].replace('TOUP.PA', 'ALTOU.PA')
    df_data['MNEMO'] = df_data['MNEMO'].replace('TOUP', 'ALTOU')
    df_data['ticker_yahoo'] = df_data['ticker_yahoo'].replace('SOLB.PA', 'SOLB.BR')
    df_data['ticker_yahoo'] = df_data['ticker_yahoo'].replace('APAM.PA', 'APAM.AS')
    df_data['ticker_yahoo'] = df_data['ticker_yahoo'].replace('MT.PA', 'MT.AS')
    df_data['ticker_yahoo'] = df_data['ticker_yahoo'].replace('CGM.PA', 'ALCGM.PA')
    df_data['Nom Indice'] = nom_indice
       
    # Préparer les données pour l'insertion
    data_to_insert = []
    for _, row in df_data.iterrows():
        data_to_insert.append((
            current_date,
            row['Company'],
            row['MNEMO'],
            row['Sector (ICB)'],
            row['Weight (%)'],
            row['ticker_yahoo'],
            row['Nom Indice']
            ))
        
    # Insérer les données
    inserted_count = insert_composition_indice(conn, data_to_insert)
    print(f"{inserted_count} nouvelles lignes insérées pour la date {current_date}")
    
    # Sauvegarder en CSV
    # filename = url_pdf.split("/")[-1]
    # output_csv = filename.replace(".pdf", ".csv")
    # df_data.to_csv(output_csv, index=False, sep=';')
    # print(f"Données sauvegardées dans {output_csv}")

    time.sleep(2)  # Pause pour éviter les surcharges de requêtes et le blocage par Euronext

def extract_and_store_actions(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ticker_yahoo FROM cac40_composition where weight_percent>=0 group by ticker_yahoo order by ticker_yahoo")
        list_actions = cursor.fetchall()
        for action in list_actions:
            action_cherchee=action[0]
            ticker = yf.Ticker(action_cherchee)
            # ['1d', '5d', '7d', '60d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
            cursor.execute("SELECT max(date) FROM actions WHERE action=?", (action_cherchee,))
            last_date = cursor.fetchone()[0]
            if last_date is not None:
                ecart_jour_maj = datetime.now().date()-datetime.strptime(last_date, '%Y-%m-%d').date()
                if ecart_jour_maj.days == 1:
                    period="1d"
                elif ecart_jour_maj.days <=5:
                    period="5d"
                elif ecart_jour_maj.days <=7:
                    period="7d"
                elif ecart_jour_maj.days <=30:
                    period="1mo"
                elif ecart_jour_maj.days <=60:
                    period="60d"
                elif ecart_jour_maj.days <=180:
                    period="6mo"
                elif ecart_jour_maj.days <=365:
                    period="1y"
                else:
                    period="max"
            else:
                period="max"
                print(f"Aucune donnée existante pour {action_cherchee}, extraction complète.")
            historical_data = ticker.history(period=period, interval="1d")
            historical_data['action'] = action_cherchee
 
            # Préparer les données pour l'insertion
            data_to_insert = []
            for id, row in historical_data.iterrows():
                data_to_insert.append((
                    id.date(),
                    row['Open'],
                    row['High'],
                    row['Low'],
                    row['Close'],
                    row['Volume'],
                    row['Dividends'],
                    row['Stock Splits'],
                    row['action']
                    ))
            # Insérer les données
            inserted_count = insert_actions(conn, data_to_insert)
            print(f"{inserted_count} nouvelles lignes insérées pour l'action {action_cherchee}")
            time.sleep(2)       # Pause pour éviter les surcharges de requêtes
        
        # Supprimer les données du jour qui sont être incomplètes
        cursor.execute("DELETE FROM actions WHERE date >= date()")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion: {e}")    

db_file="cac40_data.db"
conn = create_connection(db_file)
if conn is not None:
    create_table(conn)

# 1️⃣ CAC 40
# Composition : 40 plus grandes entreprises françaises cotées à Paris, en termes de capitalisation flottante et de liquidité.
# Exemples : LVMH, TotalEnergies, Sanofi, Airbus, BNP Paribas…
# Utilité :
#   Baromètre principal de l’économie française.
#   Référence pour les investisseurs institutionnels.
# Sert de base à de nombreux ETF et produits dérivés.
# Type d’entreprises : Grandes capitalisations (large caps).
extract_euronext_from_pdf("https://live.euronext.com/sites/default/files/documentation/index-composition/CAC_40_Index_Composition.pdf",conn)

# 2️⃣ CAC Next 20
# Composition : 20 sociétés qui viennent juste après le CAC 40, souvent les "candidates" potentielles à y entrer.
# Exemples : Eurazeo, Euronext, Ubisoft, Ipsen…
# Utilité :
#   Indicateur des entreprises en forte croissance ou en voie d’entrer dans le CAC 40.
#   Sert à suivre les valeurs montantes du marché français.
# Type d’entreprises : Moyennes à grandes capitalisations (mid caps).
extract_euronext_from_pdf("https://live.euronext.com/sites/default/files/documentation/index-composition/CAC_Next_20_Index_Composition.pdf",conn)

# 3️⃣ CAC Mid 60
# Composition : 60 sociétés de taille intermédiaire.
# Exemples : Elis, Orpea, Soitec, Virbac…
# Utilité :
#   Reflète la performance des ETI (entreprises de taille intermédiaire) françaises.
#   Souvent plus dynamiques mais plus volatiles que les grandes entreprises.
# Type d’entreprises : Mid caps.
extract_euronext_from_pdf("https://live.euronext.com/sites/default/files/documentation/index-composition/CAC_Mid_60_Index_Composition.pdf",conn)

# 4️⃣ CAC Small
# Composition : Environ 80 à 100 petites capitalisations.
# Utilité :
#   Met en avant les PME cotées.
#   Sert aux investisseurs cherchant de la croissance à long terme, avec plus de risque.
# Type d’entreprises : Small caps.
extract_euronext_from_pdf("https://live.euronext.com/sites/default/files/documentation/index-composition/CAC_Small_Index_Composition.pdf",conn)

# 5️⃣ CAC Mid & Small
# Composition : Combine les entreprises du CAC Mid 60 et du CAC Small.
# Utilité :
#   Représente globalement le segment des valeurs moyennes et petites.
#   Référence utilisée par les fonds spécialisés dans les mid/small caps.
# Type d’entreprises : Mid & Small caps.
extract_euronext_from_pdf("https://live.euronext.com/sites/default/files/documentation/index-composition/CAC_Mid_and_Small_Index_Composition.pdf",conn)

# 6️⃣ SBF 120
# Composition : CAC 40 + CAC Next 20 + CAC Mid 60 (donc 120 valeurs).
# Utilité :
#   Indice de référence élargi pour le marché français.
#   Permet une vision plus complète de l’économie française cotée.
# Type d’entreprises : Large, mid et small caps.
extract_euronext_from_pdf("https://live.euronext.com/sites/default/files/documentation/index-composition/SBF_120_Index_Composition.pdf",conn)

# 7️⃣ CAC All-Tradable
# Composition : Toutes les entreprises éligibles à un indice CAC (plus de 300).
# Utilité :
#   Donne la vision globale de la performance du marché parisien.
#   Sert souvent à construire d’autres indices thématiques.
extract_euronext_from_pdf("https://live.euronext.com/sites/default/files/documentation/index-composition/CAC_All-Tradable_Index_Composition.pdf",conn)

# 8️⃣ CAC Large 60
# Composition : 60 plus grandes capitalisations parmi les entreprises éligibles au CAC.
# Utilité :
#   Benchmark, ETF, mesure de la tendance “grandes valeurs”
# Type d’entreprises : Grandes capitalisations (Large Caps)
extract_euronext_from_pdf("https://live.euronext.com/sites/default/files/documentation/index-composition/CAC_Large_60_Index_Composition.pdf",conn)

extract_and_store_actions(conn)

conn.close()
print(f"Extraction terminée")
