from django.db import models

from django.urls import reverse  # To generate URLS by reversing URL patterns

from .models_EcuapassDoc  import EcuapassDoc
from app_cartaportes.models_cpi  import Cartaporte, CartaporteDoc
from app_manifiestos.models_mci  import Manifiesto, ManifiestoDoc
from app_declaraciones.models_dti import Declaracion, DeclaracionDoc
from .models_Entidades import Empresa, Conductor, Vehiculo

