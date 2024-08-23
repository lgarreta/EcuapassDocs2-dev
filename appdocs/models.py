from django.db import models

from django.urls import reverse  # To generate URLS by reversing URL patterns

from .models_EcuapassDoc  import EcuapassDoc
from app_cartaporte.models_cpi  import Cartaporte, CartaporteDoc
from app_manifiesto.models_mci  import Manifiesto, ManifiestoDoc
from app_declaracion.models_dti import Declaracion, DeclaracionDoc
from .models_Entidades import Empresa, Conductor, Vehiculo

