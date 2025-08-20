from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def pode_ver(context, perm):
    """
    Verifica se o usuário tem a permissão passada.
    Uso no template: {% pode_ver 'app_label.permissao' %}
    """
    user = context['request'].user
    return user.has_perm(perm)

