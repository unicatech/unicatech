from django import template

register = template.Library()

def _to_number(x):
    if x is None:
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    # remove pontos de milhares e troca vírgula decimal por ponto
    s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0

@register.filter
def multiply(value, arg):
    """Multiplica dois valores, tratando strings com vírgula/ponto"""
    try:
        return _to_number(value) * _to_number(arg)
    except Exception:
        return 0.0