"""
Gestionnaire de listing de répertoires (file browser)
"""

import os
from pathlib import Path
from urllib.parse import quote, unquote

def generate_directory_listing(path: str, request_path: str, document_root: str) -> bytes:
    """
    Génère une page HTML listant les fichiers et dossiers
    
    Args:
        path: Chemin absolu du répertoire
        request_path: Chemin de la requête HTTP
        document_root: Racine du serveur web
        
    Returns:
        HTML en bytes
    """
    
    if not os.path.isdir(path):
        return build_error_page("Not a directory")
    
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        return build_error_page("Permission denied")
    
    # Construire le HTML
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="fr">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'    <title>Index of {request_path}</title>',
        '    <style>',
        '        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }',
        '        h1 { color: #333; border-bottom: 2px solid #3498db; padding-bottom: 10px; }',
        '        .path { color: #7f8c8d; font-size: 14px; margin-bottom: 20px; }',
        '        table { width: 100%; background: white; border-collapse: collapse; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }',
        '        th { background: #3498db; color: white; text-align: left; padding: 12px; }',
        '        td { padding: 10px 12px; border-bottom: 1px solid #ecf0f1; }',
        '        tr:hover { background: #f8f9fa; }',
        '        a { text-decoration: none; color: #2980b9; }',
        '        a:hover { text-decoration: underline; }',
        '        .icon { margin-right: 8px; font-size: 18px; }',
        '        .folder { color: #f39c12; }',
        '        .file { color: #95a5a6; }',
        '        .size { color: #7f8c8d; text-align: right; }',
        '        .footer { margin-top: 30px; text-align: center; color: #95a5a6; font-size: 12px; }',
        '    </style>',
        '</head>',
        '<body>',
        f'    <h1>📂 Index of {request_path}</h1>',
        f'    <div class="path">Chemin complet: {path}</div>',
        '    <table>',
        '        <thead>',
        '            <tr>',
        '                <th>Nom</th>',
        '                <th style="text-align: right;">Taille</th>',
        '                <th>Type</th>',
        '            </tr>',
        '        </thead>',
        '        <tbody>',
    ]
    
    # Lien parent (sauf si on est à la racine)
    if request_path != '/' and request_path != '':
        parent_path = '/'.join(request_path.rstrip('/').split('/')[:-1]) or '/'
        html_parts.append(
            f'            <tr>'
            f'<td><span class="icon folder">📁</span><a href="{parent_path}">..</a></td>'
            f'<td class="size">-</td>'
            f'<td>Dossier parent</td>'
            f'</tr>'
        )
    
    # Lister les entrées (dossiers en premier)
    folders = []
    files = []
    
    for entry in entries:
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path):
            folders.append(entry)
        else:
            files.append(entry)
    
    # Afficher les dossiers
    for folder in folders:
        folder_url = os.path.join(request_path, folder).replace('\\', '/')
        if not folder_url.startswith('/'):
            folder_url = '/' + folder_url
        
        html_parts.append(
            f'            <tr>'
            f'<td><span class="icon folder">📁</span><a href="{quote(folder_url)}">{folder}/</a></td>'
            f'<td class="size">-</td>'
            f'<td>Dossier</td>'
            f'</tr>'
        )
    
    # Afficher les fichiers
    for file in files:
        file_path = os.path.join(path, file)
        file_url = os.path.join(request_path, file).replace('\\', '/')
        if not file_url.startswith('/'):
            file_url = '/' + file_url
        
        # Taille du fichier
        try:
            size = os.path.getsize(file_path)
            size_str = format_size(size)
        except:
            size_str = "?"
        
        # Type de fichier
        ext = os.path.splitext(file)[1].lower()
        file_type = get_file_type(ext)
        icon = get_file_icon(ext)
        
        html_parts.append(
            f'            <tr>'
            f'<td><span class="icon file">{icon}</span><a href="{quote(file_url)}">{file}</a></td>'
            f'<td class="size">{size_str}</td>'
            f'<td>{file_type}</td>'
            f'</tr>'
        )
    
    # Fermer le HTML
    html_parts.extend([
        '        </tbody>',
        '    </table>',
        f'    <div class="footer">',
        f'        {len(folders)} dossier(s), {len(files)} fichier(s) | Serveur HTTP Python | By Fiankinana, Sharon & Nia',
        f'    </div>',
        '</body>',
        '</html>',
    ])
    
    html = '\n'.join(html_parts)
    return html.encode('utf-8')


def format_size(size: int) -> str:
    """Formate la taille en unités lisibles"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def get_file_type(ext: str) -> str:
    """Retourne le type de fichier selon l'extension"""
    types = {
        '.html': 'HTML',
        '.htm': 'HTML',
        '.php': 'PHP',
        '.css': 'CSS',
        '.js': 'JavaScript',
        '.json': 'JSON',
        '.xml': 'XML',
        '.txt': 'Texte',
        '.md': 'Markdown',
        '.py': 'Python',
        '.jpg': 'Image JPEG',
        '.jpeg': 'Image JPEG',
        '.png': 'Image PNG',
        '.gif': 'Image GIF',
        '.svg': 'Image SVG',
        '.pdf': 'PDF',
        '.zip': 'Archive ZIP',
        '.tar': 'Archive TAR',
        '.gz': 'Archive GZIP',
    }
    return types.get(ext, 'Fichier')


def get_file_icon(ext: str) -> str:
    """Retourne une icône emoji selon le type de fichier"""
    icons = {
        '.html': '🌐',
        '.htm': '🌐',
        '.php': '🐘',
        '.css': '🎨',
        '.js': '⚡',
        '.json': '📋',
        '.xml': '📄',
        '.txt': '📝',
        '.md': '📝',
        '.py': '🐍',
        '.jpg': '🖼️',
        '.jpeg': '🖼️',
        '.png': '🖼️',
        '.gif': '🖼️',
        '.svg': '🎨',
        '.pdf': '📕',
        '.zip': '📦',
        '.tar': '📦',
        '.gz': '📦',
    }
    return icons.get(ext, '📄')


def build_error_page(message: str) -> bytes:
    """Page d'erreur simple"""
    html = f"""<!DOCTYPE html>
<html>
<head><title>Erreur</title></head>
<body>
    <h1>Erreur</h1>
    <p>{message}</p>
</body>
</html>"""
    return html.encode('utf-8')
