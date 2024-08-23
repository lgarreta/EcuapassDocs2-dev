from django.contrib import admin

# Register your models here.
from app_cartaporte.models_cpi import Cartaporte, CartaporteDoc
from app_manifiesto.models_mci import Manifiesto, ManifiestoDoc
from app_declaracion.models_dti import Declaracion, DeclaracionDoc
from .models_Entidades import Empresa, Conductor, Vehiculo

#admin.site.register(Empresa)
#admin.site.register(Conductor)
admin.site.register(Vehiculo)
#admin.site.register(Cartaporte)
#admin.site.register(Manifiesto)

# Define the admin class
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'id', 'direccion', 'ciudad', 'pais')

# Register the admin class with the associated model
admin.site.register(Empresa, EmpresaAdmin)

class ConductorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'documento', 'nacionalidad', 'licencia')

# Register the admin class with the associated model
admin.site.register(Conductor, ConductorAdmin)

class ManifiestosInline(admin.TabularInline):
    model = Manifiesto

class CartaporteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'remitente', 'documento', 'fecha_emision')
    inlines = [ManifiestosInline]

admin.site.register(Cartaporte, CartaporteAdmin)

class ManifiestoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'vehiculo', 'cartaporte', 'fecha_emision')

admin.site.register(Manifiesto, ManifiestoAdmin)

class DeclaracionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cartaporte', 'fecha_emision')

admin.site.register(Declaracion, DeclaracionAdmin)

