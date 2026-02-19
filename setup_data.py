import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from tickets.models import Category, Ticket

User = get_user_model()

def create_initial_data():
    # Create Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='admin')
        print("Superuser created: admin/admin123")
    else:
        print("Superuser already exists")

    # Create Categories
    categories = [
        {'name': 'Network', 'description': 'Wifi, Internet, LAN issues'},
        {'name': 'Hardware', 'description': 'Printers, Laptops, Desktops'},
        {'name': 'Software', 'description': 'OS, Applications, Antivirus'},
    ]
    
    for cat_data in categories:
        cat, created = Category.objects.get_or_create(name=cat_data['name'], defaults={'description': cat_data['description']})
        if created:
            print(f"Created Category: {cat.name}")

    # Create a Technician User for auto-assignment test
    if not User.objects.filter(username='tech_net').exists():
        tech = User.objects.create_user('tech_net', 'tech@example.com', 'password123', role='technician', first_name='Network', last_name='Tech')
        print("Created Technician: tech_net")
        
        # Link to Network Category
        cat_net = Category.objects.get(name='Network')
        cat_net.default_technician = tech
        cat_net.save()
        print("Linked Network Tech to Network Category")
        
    print("Initial data setup complete.")

if __name__ == '__main__':
    create_initial_data()
