from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Ticket
from .forms import TicketCreateForm, TicketUpdateForm, CommentForm, FeedbackForm, InternalNoteForm


@login_required
def ticket_list(request):
    tickets = Ticket.objects.all()
    # Simple search
    query = request.GET.get('q')
    if query:
        tickets = tickets.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(id__icontains=query)
        )
    
    # Filter by user role
    if request.user.role == 'student':
        tickets = tickets.filter(created_by=request.user)
    elif request.user.role == 'technician':
        # Technicians see all, or only assigned? Usually all but highlighted assigned.
        pass 
    
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Permission check (simple)
    if request.user.role == 'student' and ticket.created_by != request.user:
        messages.error(request, "You do not have permission to view this ticket.")
        return redirect('tickets:list')

    is_staff_user = request.user.role in ['technician', 'staff', 'admin']

    comment_form = CommentForm()
    feedback_form = FeedbackForm()
    internal_note_form = InternalNoteForm()

    if request.method == 'POST':
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.user = request.user
                comment.save()
                messages.success(request, 'Comment added.')
                return redirect('tickets:detail', pk=pk)
        elif 'feedback_submit' in request.POST:
            feedback_form = FeedbackForm(request.POST)
            if feedback_form.is_valid():
                feedback = feedback_form.save(commit=False)
                feedback.ticket = ticket
                feedback.save()
                messages.success(request, 'Thank you for your feedback!')
                return redirect('tickets:detail', pk=pk)
        elif 'internal_note_submit' in request.POST and is_staff_user:
            internal_note_form = InternalNoteForm(request.POST)
            if internal_note_form.is_valid():
                note = internal_note_form.save(commit=False)
                note.ticket = ticket
                note.user = request.user
                note.save()
                messages.success(request, 'Internal note saved.')
                return redirect('tickets:detail', pk=pk)
        elif 'status_submit' in request.POST and is_staff_user:
            new_status = request.POST.get('status')
            if new_status in dict(Ticket.STATUS_CHOICES):
                ticket.status = new_status
                ticket.save()
                messages.success(request, 'Ticket status updated.')
                return redirect('tickets:detail', pk=pk)
        elif 'assign_to_me' in request.POST and is_staff_user:
            ticket.assigned_to = request.user
            ticket.save()
            messages.success(request, 'Ticket assigned to you.')
            return redirect('tickets:detail', pk=pk)
        elif 'close_ticket' in request.POST and is_staff_user:
            ticket.status = 'closed'
            ticket.save()
            messages.success(request, 'Ticket closed.')
            return redirect('tickets:detail', pk=pk)
        elif 'escalate_ticket' in request.POST and is_staff_user:
            ticket.is_escalated = True
            ticket.save()
            messages.success(request, 'Ticket escalated.')
            return redirect('tickets:detail', pk=pk)
        elif 'reopen_ticket' in request.POST and request.user == ticket.created_by:
            ticket.status = 'open'
            ticket.is_escalated = False
            ticket.save()
            messages.success(request, 'Ticket reopened.')
            return redirect('tickets:detail', pk=pk)

    feedback = getattr(ticket, 'feedback', None)
    internal_notes = ticket.internal_notes.select_related('user').order_by('-created_at')
    recommended_solutions = []
    suggestion = ticket.suggested_solution()
    if suggestion:
        recommended_solutions.append(suggestion)
    if not recommended_solutions:
        recommended_solutions = [
            'Check known outage notices in the ICT updates.',
            'Restart the affected device and confirm network access.',
            'Verify account permissions and retry the action.',
        ]

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'comment_form': comment_form,
        'feedback_form': feedback_form,
        'feedback': feedback,
        'internal_note_form': internal_note_form,
        'internal_notes': internal_notes,
        'recommended_solutions': recommended_solutions,
        'is_staff_user': is_staff_user,
        'status_choices': Ticket.STATUS_CHOICES,
    })


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            
            # Check for AI suggestion
            suggestion = ticket.suggested_solution()
            if suggestion:
                messages.info(request, f"AI Suggestion: {suggestion}")

            messages.success(request, 'Ticket created successfully.')
            return redirect('tickets:detail', pk=ticket.pk)
    else:
        form = TicketCreateForm()
    return render(request, 'tickets/ticket_form.html', {'form': form, 'title': 'Create Ticket'})


@login_required
def ticket_update(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket updated.')
            return redirect('tickets:detail', pk=pk)
    else:
        form = TicketUpdateForm(instance=ticket)
    return render(request, 'tickets/ticket_form.html', {'form': form, 'title': 'Update Ticket'})


@login_required
def kanban_board(request):
    # Only for technicians/staff/admin
    if request.user.role == 'student':
         messages.error(request, "Access denied.")
         return redirect('tickets:list')

    tickets = Ticket.objects.all()
    return render(request, 'tickets/kanban.html', {
        'open_tickets': tickets.filter(status='open'),
        'in_progress_tickets': tickets.filter(status='in_progress'),
        'resolved_tickets': tickets.filter(status='resolved'),
        'closed_tickets': tickets.filter(status='closed'),
    })
