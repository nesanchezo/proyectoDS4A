from django.db import models
from django.forms import ModelForm

# Create your models here.

compe_op = [
        ("PUNT_GLOBAL",'Puntaje global'),
		("MOD_RAZONA_CUANTITAT_PUNT",'Modulo razonamiento cuantitativo'),
		("MOD_LECTURA_CRITICA_PUNT",'Modulo lectura crítica'),
		("MOD_COMPETEN_CIUDADA_PUNT",'Modulo competencia ciudadana'),
		("MOD_INGLES_PUNT",'Modulo ingles'),
		("MOD_COMUNI_ESCRITA_PUNT",'Modulo comunicación escrita')
    ]
class filters(models.Model):
	compe = models.CharField(max_length=255,
		null= False, blank=False,
		choices=compe_op, default="PUNT_GLOBAL"
	)

	def _str_(self):
		return self.compe

class Institutions(models.Model):
    instituciones = models.CharField(max_length=20,default='UNIVERSIDAD FRANCISCO DE PAULA SANTANDER-CUCUTA')
  
    def __str__(self):
        return f"{self.instituciones}"

class InstitutionsForm(ModelForm):
    class Meta:
        model = Institutions
        fields = ['instituciones']

class Cods(models.Model):
    codigos = models.CharField(max_length=20)
  
    def __str__(self):
        return f"{self.codigos}"

class CodsForm(ModelForm):
    class Meta:
        model = Cods
        fields = ['codigos']