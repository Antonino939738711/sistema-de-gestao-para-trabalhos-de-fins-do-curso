import os
import sys
from django.core.wsgi import get_wsgi_application

# Adiciona o diretório atual ao path para ajudar o importlib a achar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SGTFC.settings')

application = get_wsgi_application()
app = application