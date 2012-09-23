from django.dispatch import Signal
#called in cases caused by concrete user
ticket_will_update = Signal(providing_args=['ticket', 'changer'])
