from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    default_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_categories'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Ticket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    is_escalated = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new:
            # 1. Auto-Categorization (The "AI" feature)
            description_lower = self.description.lower()
            if not self.category:
                if 'wifi' in description_lower or 'internet' in description_lower:
                    try:
                        self.category = Category.objects.get(name='Network')
                    except Category.DoesNotExist:
                        pass
                elif 'printer' in description_lower:
                    try:
                        self.category = Category.objects.get(name='Hardware')
                    except Category.DoesNotExist:
                        pass

            # 2. Auto-Assignment (Speed feature)
            if self.category and self.category.default_technician and not self.assigned_to:
                self.assigned_to = self.category.default_technician

        if self.status in ['resolved', 'closed'] and not self.closed_at:
            self.closed_at = timezone.now()
            
        super().save(*args, **kwargs)

        # 3. Automated Emails (Communication Feature)
        if is_new:
            send_mail(
                subject=f'Ticket Created: {self.title}',
                message=f'Ticket #{self.id} has been created.\n\nDescription: {self.description}',
                from_email='system@helpdesk.local',
                recipient_list=[self.created_by.email] if self.created_by.email else [],
                fail_silently=True,
            )

    def suggested_solution(self):
        """Knowledge Base "AI" Suggestion"""
        desc = self.description.lower()
        if 'wifi' in desc or 'internet' in desc:
            return "Try restarting your router or checking if the cable is plugged in."
        elif 'printer' in desc:
            return "Check if the printer has paper and toner."
        elif 'password' in desc:
            return "You can reset your password at the login page."
        return None

    def __str__(self):
        return f"#{self.id} - {self.title}"


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on #{self.ticket.id}"


class InternalNote(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='internal_notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Internal note by {self.user} on #{self.ticket.id}"


class Attachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for #{self.ticket.id}"


class Feedback(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for #{self.ticket.id} - {self.rating} Stars"
