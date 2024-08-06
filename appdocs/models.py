from django.db import models

from django.urls import reverse  # To generate URLS by reversing URL patterns

from .models_EcuapassDoc  import EcuapassDoc
from app_cartaportes.models  import Cartaporte, CartaporteDoc
from .models_ManifiestoDoc  import Manifiesto, ManifiestoDoc
from .models_DeclaracionDoc import Declaracion, DeclaracionDoc
from .models_Entidades import Empresa, Conductor, Vehiculo

