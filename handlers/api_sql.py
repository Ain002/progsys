"""
API pour exécuter des requêtes SQL depuis HTTP
"""
import json
from handlers import database as db


async def handle_api_sql(method: str, path: str, body: bytes, query_string: str) -> tuple:
    """
    API pour exécuter des requêtes SQL
    POST /api/sql
    Body: {"sql": "SELECT * FROM users", "params": []}
    """
    
    if method != 'POST':
        return (405, json.dumps({'error': 'Seul POST est autorisé'}).encode(), 'application/json')
    
    try:
        data = json.loads(body.decode())
        sql = data.get('sql', '').strip()
        params = tuple(data.get('params', []))
        
        if not sql:
            return (400, json.dumps({'error': 'SQL requis'}).encode(), 'application/json')
        
        # Exécuter la requête
        result = await db.execute_query(sql, params)
        
        response = {
            'success': True,
            'sql': sql,
            'result': result
        }
        
        return (200, json.dumps(response, ensure_ascii=False).encode(), 'application/json')
    
    except json.JSONDecodeError as e:
        return (400, json.dumps({'error': 'JSON invalide'}).encode(), 'application/json')
    except Exception as e:
        return (500, json.dumps({'error': str(e), 'success': False}).encode(), 'application/json')
