from django import forms
from .models import Ticket, Comment, Feedback, InternalNote


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category']


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category', 'status', 'assigned_to', 'is_escalated']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow assigning to technicians/staff/admins ideally, but for now allow all users or filter if needed
        # self.fields['assigned_to'].queryset = User.objects.filter(role=User.Role.TECHNICIAN)
        pass


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any other feedback?'}),
            'rating': forms.RadioSelect(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]),
        }


class InternalNoteForm(forms.ModelForm):
    class Meta:
        model = InternalNote
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a private note for staff...'}),
        }
