from django.contrib import admin
from django.urls import path, include

from app_docs import views_docs

admin.site.site_header = "Creación/Almacenamiento de Documentos del ECUAPASS"
admin.site.site_title  = "Creación/Almacenamiento de Documentos del ECUAPASS"
admin.site.index_title = "Creación/Almacenamiento de Documentos del ECUAPASS Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("usuarios/", include("app_usuarios.urls_user")),
    path("documentos/", include("app_docs.urls_docs")),
    path("cartaporte/", include("app_cartaporte.urls_cpi")),
    path("manifiesto/", include("app_manifiesto.urls_mci")),
    path("declaracion/", include("app_declaracion.urls_dti")),
    path("reportes/", include("appreportes.urls")),

    #path('', views_docs.principal, name='principal'),
    #path ('index', views_docs.index, name='index'),
    #path ('reload_sidebar', views_docs.reload_sidebar, name='reload_sidebar'),


    path('', views_docs.index, name='index'),
    #path('profile/', views_main.profile, name='profile'),
    #path('login/', views_main.login_view,  name='login'),
    #path('logout/', views_main.logout_view, name='logout'),
    #path('admin_panel/', views_main.admin_panel, name='admin_panel'), 	
]

