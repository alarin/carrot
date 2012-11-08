#encoding: utf-8
from carrot_tickets.core_forms import CoreFormMixin
from carrot_tickets.models import TicketComment, Ticket
from django import forms

class CommentForm(CoreFormMixin, forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ('content',)


class TicketForm(CoreFormMixin, forms.ModelForm):
    estimate = forms.IntegerField(required=False, label=u"Оценка")
    file = forms.FileField(required=False)

    class Meta:
        model = Ticket
        exclude = ('reporter',)



