from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count, Avg, F, Q
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views import View
import random
from tickets.models import Ticket
import datetime
import csv


def landing(request):
    return render(request, 'landing.html')


def report_issue(request):
    if request.user.is_authenticated:
        return redirect('tickets:create')
    return redirect(f"{reverse('users:login')}?next={reverse('tickets:create')}")


class StaffDashboardView(LoginRequiredMixin, View):
    template_name = 'reports/staff_dashboard.html'

    def get_queryset(self, request):
        return Ticket.objects.filter(Q(assigned_to=request.user) | Q(assigned_to__isnull=True))

    def get(self, request):
        if request.user.role == 'student':
            return redirect('reports:student_dashboard')

        tickets = self.get_queryset(request)
        query = request.GET.get('q', '').strip()
        if query:
            tickets = tickets.filter(
                Q(id__icontains=query) |
                Q(title__icontains=query) |
                Q(created_by__username__icontains=query)
            )

        my_open_tickets = Ticket.objects.filter(
            assigned_to=request.user,
            status__in=['open', 'in_progress']
        ).count()
        high_priority = tickets.filter(
            priority__in=['high', 'critical'],
            status__in=['open', 'in_progress']
        ).count()
        escalated = tickets.filter(is_escalated=True, status__in=['open', 'in_progress']).count()

        closed_tickets = Ticket.objects.filter(
            assigned_to=request.user,
            closed_at__isnull=False
        )
        avg_response_time = 0
        if closed_tickets.exists():
            times = [(t.closed_at - t.created_at).total_seconds() for t in closed_tickets]
            avg_response_time = sum(times) / len(times) / 3600

        now = timezone.now()
        for ticket in tickets:
            if ticket.priority in ['high', 'critical'] and ticket.status in ['open', 'in_progress']:
                hours = 2 if ticket.priority == 'critical' else 4
                due_at = ticket.created_at + datetime.timedelta(hours=hours)
                remaining = due_at - now
                if remaining.total_seconds() <= 0:
                    ticket.sla_due = 'Overdue'
                else:
                    hours_left = int(remaining.total_seconds() // 3600)
                    minutes_left = int((remaining.total_seconds() % 3600) // 60)
                    ticket.sla_due = f"Due in {hours_left}h {minutes_left}m"
            else:
                ticket.sla_due = None

        context = {
            'tickets': tickets.order_by('-created_at'),
            'query': query,
            'my_open_tickets': my_open_tickets,
            'high_priority': high_priority,
            'escalated': escalated,
            'avg_response_time': round(avg_response_time, 1),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        if request.user.role == 'student':
            return redirect('reports:student_dashboard')

        action = request.POST.get('action')
        ticket_id = request.POST.get('ticket_id')
        if action and ticket_id:
            ticket = get_object_or_404(Ticket, pk=ticket_id)
            if action == 'assign':
                ticket.assigned_to = request.user
                ticket.save()
                messages.success(request, 'Ticket assigned to you.')
            elif action == 'close':
                ticket.status = 'closed'
                ticket.save()
                messages.success(request, 'Ticket closed.')
            elif action == 'escalate':
                ticket.is_escalated = True
                ticket.save()
                messages.success(request, 'Ticket escalated.')

        bulk_action = request.POST.get('bulk_action')
        selected_ids = request.POST.getlist('selected_tickets')
        if bulk_action and selected_ids:
            selection = Ticket.objects.filter(id__in=selected_ids)
            if bulk_action == 'assign':
                selection.filter(assigned_to__isnull=True).update(assigned_to=request.user)
                messages.success(request, 'Selected tickets assigned to you.')
            elif bulk_action == 'close':
                selection.update(status='closed', closed_at=timezone.now())
                messages.success(request, 'Selected tickets closed.')

        return redirect('reports:dashboard')


class StudentDashboardView(LoginRequiredMixin, View):
    template_name = 'reports/student_dashboard.html'

    def get(self, request):
        if request.user.role != 'student':
            return redirect('reports:dashboard')

        tickets = Ticket.objects.filter(created_by=request.user).order_by('-created_at').prefetch_related('comments__user', 'category')
        open_tickets = tickets.filter(status__in=['open', 'in_progress']).count()
        resolved_tickets = tickets.filter(status__in=['resolved', 'closed']).count()

        pending_action = 0
        for ticket in tickets:
            last_comment = ticket.comments.order_by('-created_at').first()
            if last_comment and last_comment.user.role != 'student' and ticket.status in ['open', 'in_progress']:
                pending_action += 1

        tips = [
            'Forgot your password? You can reset it from the login page in minutes.',
            'Slow Wi-Fi? Try reconnecting to CUEA-Staff after forgetting the network.',
            'Printing issues often resolve after clearing the print queue.',
            'You can attach screenshots for faster support responses.',
        ]
        quick_tip = random.choice(tips)

        context = {
            'tickets': tickets,
            'open_tickets': open_tickets,
            'resolved_tickets': resolved_tickets,
            'pending_action': pending_action,
            'quick_tip': quick_tip,
        }
        return render(request, self.template_name, context)


@login_required
def dashboard_overview(request):
    if request.user.role == 'student':
        return redirect('tickets:list')

    # Stats
    total_tickets = Ticket.objects.count()
    resolved_tickets = Ticket.objects.filter(status='resolved').count()
    open_tickets = Ticket.objects.filter(status='open').count()
    
    # MTTR Calculation (approx)
    closed_tickets = Ticket.objects.filter(status='closed', closed_at__isnull=False)
    avg_resolution_time = 0
    if closed_tickets.exists():
        times = [(t.closed_at - t.created_at).total_seconds() for t in closed_tickets]
        avg_resolution_time = sum(times) / len(times) / 3600  # in hours

    context = {
        'total_tickets': total_tickets,
        'resolved_tickets': resolved_tickets,
        'open_tickets': open_tickets,
        'avg_resolution_time': round(avg_resolution_time, 1),
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
def chart_data(request):
    # Pie chart data: Status distribution
    status_data = list(Ticket.objects.values('status').annotate(count=Count('status')))
    
    # Line chart data: Tickets per day (last 7 days)
    today = datetime.date.today()
    last_7_days = today - datetime.timedelta(days=7)
    daily_data = list(Ticket.objects.filter(created_at__date__gte=last_7_days)
                      .extra(select={'day': 'date(created_at)'})
                      .values('day')
                      .annotate(count=Count('id'))
                      .order_by('day'))
    
    return JsonResponse({
        'status_dist': status_data,
        'daily_activity': daily_data
    })


@login_required
def export_tickets_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tickets_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Status', 'Priority', 'Category', 'Created By', 'Created At', 'Resolved At'])

    tickets = Ticket.objects.all().values_list(
        'id', 'title', 'status', 'priority', 'category__name', 'created_by__username', 'created_at', 'closed_at'
    )

    for ticket in tickets:
        writer.writerow(ticket)

    return response
