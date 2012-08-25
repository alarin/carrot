def slugify(x):
    from django.template.defaultfilters import slugify as django_slugify
    from unidecode import unidecode

    return django_slugify(unidecode(x))