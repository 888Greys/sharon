from django.contrib import admin
from .models import Ticket, Category, Comment, Attachment, Feedback, InternalNote

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'priority', 'category', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_technician')

admin.site.register(Comment)
admin.site.register(Attachment)
admin.site.register(Feedback)
admin.site.register(InternalNote)
