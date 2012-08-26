from carrot_tickets.core_forms import CoreFormMixin
from carrot_tickets.models import TicketComment
from django import forms

class CommentForm(CoreFormMixin, forms.ModelForm):
    class Meta:
        model = TicketComment
        exclude = ('ticket', 'author')



