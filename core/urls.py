from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]

# URLs com suporte a internacionalização
urlpatterns += i18n_patterns(
    path('', include('linux.urls')),
    path('', include('support.urls')),
    prefix_default_language=False  # Isso garante que o idioma padrão (pt-br) não tenha o prefixo /pt-br
)

# Serve arquivos estáticos e de mídia no modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
