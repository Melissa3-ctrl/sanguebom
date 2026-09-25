from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


# =========================================================
# ROTAS PRINCIPAIS DO PROJETO
# =========================================================

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('membros.urls')),
]


# =========================================================
# MEDIA (uploads de arquivos — laudos médicos)
# Serve os arquivos em desenvolvimento (quando DEBUG=True)
# Em produção, o servidor (nginx, etc) serve esses arquivos
# =========================================================

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)