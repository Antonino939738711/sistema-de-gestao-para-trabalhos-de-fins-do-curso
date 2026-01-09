import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SGTFC.settings')

app = get_wsgi_application()  # Vercel usa este nome
