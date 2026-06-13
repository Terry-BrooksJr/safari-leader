from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def querystring_replace(context, key, value):
    query = context["request"].GET.copy()
    query[key] = value
    return query.urlencode()
