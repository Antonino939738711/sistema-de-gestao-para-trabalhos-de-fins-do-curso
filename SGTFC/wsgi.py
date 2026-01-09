import os
from django.core.wsgi import get_wsgi_application

# Certifique-se de que o nome aqui corresponde à sua pasta de configurações
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SGTFC.settings')

# Na Vercel, definimos como 'app' para facilitar a exportação
app = get_wsgi_application()