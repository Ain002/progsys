"""
Connecteur MySQL simple pour exécuter des requêtes SQL
"""
import aiomysql
from typing import Optional, List, Dict, Any

# Pool de connexions
pool: Optional[aiomysql.Pool] = None

# Configuration XAMPP MySQL/MariaDB (à adapter selon votre setup)
DB_CONFIG = {
    'host': 'localhost',  # ou '127.0.0.1'
    'port': 3306,         # Port par défaut XAMPP
    'user': 'root',       # Utilisateur par défaut XAMPP
    'password': '',       # Pas de mot de passe par défaut XAMPP
    'db': 'serveur_db',   # Nom de votre base de données
    'charset': 'utf8mb4'
}


async def init_db() -> None:
    """Initialise la connexion à MySQL"""
    global pool
    try:
        pool = await aiomysql.create_pool(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['db'],
            charset=DB_CONFIG['charset'],
            minsize=1,
            maxsize=10
        )
        print("✅ Connexion MySQL établie")
    except Exception as e:
        print(f"❌ Erreur connexion MySQL: {e}")
        raise


async def close_db() -> None:
    """Ferme la connexion"""
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()
        print("✅ Connexion MySQL fermée")


async def execute_query(sql: str, params: tuple = None) -> Dict[str, Any]:
    """
    Exécute une requête SQL (SELECT, INSERT, UPDATE, DELETE, ALTER, etc.)
    
    Args:
        sql: La requête SQL à exécuter
        params: Les paramètres (optionnel) pour requêtes préparées
        
    Returns:
        Dict avec 'rows' (résultats SELECT) et 'rowcount' (lignes affectées)
    """
    # Convertir les ? en %s pour MySQL (aiomysql utilise le format Python)
    sql = sql.replace('?', '%s')
    
    async with pool.acquire() as conn:
        # Activer autocommit pour éviter les deadlocks
        await conn.autocommit(True)
        
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Exécuter avec ou sans paramètres
            if params:
                await cursor.execute(sql, params)
            else:
                await cursor.execute(sql)
            
            # Si c'est un SELECT, récupérer les résultats
            if sql.strip().upper().startswith('SELECT'):
                rows = await cursor.fetchall()
                # Convertir datetime en string pour JSON
                for row in rows:
                    for key, value in row.items():
                        if hasattr(value, 'isoformat'):
                            row[key] = str(value)
                return {
                    'rows': rows,
                    'rowcount': len(rows)
                }
            else:
                # INSERT, UPDATE, DELETE, ALTER, etc.
                return {
                    'rows': [],
                    'rowcount': cursor.rowcount,
                    'lastrowid': cursor.lastrowid if cursor.lastrowid else None
                }
