import bleach
import re

def sanitize_html(html_content):
    """
    Sanitiza contenido HTML permitiendo solo etiquetas y atributos seguros.
    """
    allowed_tags = [
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li',
        'ol', 'p', 'strong', 'ul', 'br', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    ]
    
    allowed_attrs = {
        'a': ['href', 'title', 'rel'],
        'abbr': ['title'],
        'acronym': ['title'],
        '*': ['class']
    }
    
    # Sanitizar el HTML
    return bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

def sanitize_filename(filename):
    """
    Sanitiza un nombre de archivo para prevenir path traversal y caracteres inseguros.
    """
    # Eliminar caracteres peligrosos y path traversal
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'\.+', '.', filename)  # Evitar múltiples puntos
    
    # Asegurar que no comience con punto o guión
    filename = filename.lstrip('.-')
    
    return filename if filename else 'file'  # Default si queda vacío

def sanitize_input(text):
    """
    Sanitiza texto plano para prevenir inyecciones.
    """
    if not text:
        return ""
    
    # Eliminar caracteres potencialmente peligrosos
    text = re.sub(r'[<>]', '', text)
    
    return text