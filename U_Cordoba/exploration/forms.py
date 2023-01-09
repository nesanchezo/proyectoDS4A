from django import forms
from exploration.models import filters,Institutions,Cods


compe_op_1 = (
        ("PUNT_GLOBAL",'Puntaje global'),
		("MOD_RAZONA_CUANTITAT_PUNT",'Modulo razonamiento cuantitativo'),
		("MOD_LECTURA_CRITICA_PUNT",'Modulo lectura crítica'),
		("MOD_COMPETEN_CIUDADA_PUNT",'Modulo competencia ciudadana'),
		("MOD_INGLES_PUNT",'Modulo ingles'),
		("MOD_COMUNI_ESCRITA_PUNT",'Modulo comunicación escrita'))
class CompeFormUno(forms.Form):
	Competencias = forms.ChoiceField(choices = compe_op_1)

facult_op = (
	('FACULTAD DE CIENCIAS DE LA SALUD' ,'FACULTAD DE CIENCIAS DE LA SALUD'),
		('FACULTAD DE EDUCACION Y CIENCIAS HUMANAS' ,'FACULTAD DE EDUCACION Y CIENCIAS HUMANAS'),
		('FACULTAD DE INGENIERIAS' ,'FACULTAD DE INGENIERIAS'),
		('FACULTAD DE CIENCIAS BASICAS' ,'FACULTAD DE CIENCIAS BASICAS'),
		('FAC DE MEDICINA VETERINARIA Y ZOOTECNIA' ,'FAC DE MEDICINA VETERINARIA Y ZOOTECNIA'),
		('FACULT CIENC ECON JURIDICAS Y ADMINISTR','FACULT CIENC ECON JURIDICAS Y ADMINISTR'),
		('FACULTAD DE CIENCIAS AGRICOLAS','FACULTAD DE CIENCIAS AGRICOLAS'))
class Facultades(forms.Form):
	Facultades = forms.ChoiceField(choices = facult_op)
	Competencia = forms.ChoiceField(choices = compe_op_1)


periodosSaber11_op = ((20132,20132),(20122,20122),(20142,20142),(20162,20162),(20152,20152))
periodosSaberPro_op = ((20182,20182),(20183,20183),(20195,20195),(20203,20203))
class periodosSaber(forms.Form):
	periodoSaber11 = forms.ChoiceField(choices = periodosSaber11_op)
	periodoSaberPro = forms.ChoiceField(choices = periodosSaberPro_op)

class periodosSaber11(forms.Form):
	periodo_Saber11 = forms.ChoiceField(choices = periodosSaber11_op)

class periodosSaberPro(forms.Form):
	periodo_SaberPro = forms.ChoiceField(choices = periodosSaberPro_op)


prueba_op = (('skills11','Saber 11'), ('skillsPro','Saber Pro'))
class pruebaSaber(forms.Form):
	Prueba_Saber = forms.ChoiceField(choices = prueba_op)

class periodosPruebaSaber(forms.Form):
	Prueba_Saber = forms.ChoiceField(choices = prueba_op)
	periodoSaber11 = forms.ChoiceField(choices = periodosSaber11_op)
	periodoSaberPro = forms.ChoiceField(choices = periodosSaberPro_op)

class InstitutionsForm(forms.Form):
	instituciones = forms.ModelMultipleChoiceField(queryset=Institutions.objects.all())

class InstitutionsForm11(forms.Form):
	instituciones = forms.ModelMultipleChoiceField(queryset=Institutions.objects.all())
	periodoSaber11 = forms.ChoiceField(choices = periodosSaber11_op)

class InstitutionsFormPro(forms.Form):
	instituciones = forms.ModelMultipleChoiceField(queryset=Institutions.objects.all())
	periodoSaberPro = forms.ChoiceField(choices = periodosSaberPro_op)

class CodsForm(forms.Form):
	codigos = forms.ModelMultipleChoiceField(queryset=Cods.objects.all())	

comp_years_op = (('FAMI_ESTRATOVIVIENDA_PRO','FAMI_ESTRATOVIVIENDA_PRO'),('ESTU_METODO_PRGM','ESTU_METODO_PRGM'),('YEARS_DIFF','YEARS_DIFF'))
class comp_yearsForm(forms.Form):
	comp_years = forms.ChoiceField(choices = comp_years_op)


estrato_op = (('1','1'),('2','2'),('3','3'),('4','4'),('5','5'))
programa_op =(('ACUICULTURA','ACUICULTURA'),('ADMINISTRACION EN FINANZAS Y NEGOCIOS INTERNACIONALES','ADMINISTRACION EN FINANZAS Y NEGOCIOS INTERNACIONALES'),
('ADMINISTRACION EN SALUD','ADMINISTRACION EN SALUD'),('BACTERIOLOGIA','BACTERIOLOGIA'),('BIOLOGIA','BIOLOGIA'),
('DERECHO','DERECHO'),('ENFERMERIA','ENFERMERIA'),('ESTADISTICA','ESTADISTICA'),('FISICA','FISICA'),
('GEOGRAFIA','GEOGRAFIA'),('INGENIERIA AGRONOMICA','INGENIERIA AGRONOMICA'),('INGENIERIA AMBIENTAL','INGENIERIA AMBIENTAL'),('INGENIERIA DE ALIMENTOS','INGENIERIA DE ALIMENTOS'),
('INGENIERIA DE SISTEMAS','INGENIERIA DE SISTEMAS'),('INGENIERIA INDUSTRIAL','INGENIERIA INDUSTRIAL'),
('INGENIERIA MECANICA','INGENIERIA MECANICA'),('LICENCIATURA EN CIENCIAS NATURALES Y EDUCACION AMBIENTAL','LICENCIATURA EN CIENCIAS NATURALES Y EDUCACION AMBIENTAL'),('LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN CIENCIAS SOCIALES','LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN CIENCIAS SOCIALES'),
('LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN EDUCACION ARTISTICAMUSICA','LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN EDUCACION ARTISTICAMUSICA'),('LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN HUMANIDADES   LENGUA CASTELLANA','LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN HUMANIDADES   LENGUA CASTELLANA'),
('LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN HUMANIDADESINGLES','LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN HUMANIDADESINGLES'),('LICENCIATURA EN EDUCACION FISICA RECREACION Y DEPORTES','LICENCIATURA EN EDUCACION FISICA RECREACION Y DEPORTES'),
('LICENCIATURA EN INFORMATICA Y MEDIOS AUDIOVISUALES','LICENCIATURA EN INFORMATICA Y MEDIOS AUDIOVISUALES'),
('MATEMATICAS','MATEMATICAS'),('MEDICINA VETERINARIA Y ZOOTECNIA','MEDICINA VETERINARIA Y ZOOTECNIA'),('QUIMICA','QUIMICA'))
area_op = (('AREA RURAL','AREA RURAL'),('CABECERA MUNICIPAL','CABECERA MUNICIPAL'),('NAN','NAN'))
class predictForm(forms.Form):
	PUNT_SOCIALES_CIUDADANAS = forms.IntegerField(min_value=1,max_value=100)
	PUNT_INGLES = forms.IntegerField(min_value=1,max_value=100)
	PUNT_LECTURA_CRITICA = forms.IntegerField(min_value=1,max_value=100)
	PUNT_MATEMATICAS = forms.IntegerField(min_value=1,max_value=100)
	PUNT_C_NATURALES = forms.IntegerField(min_value=1,max_value=100)
	Estrato = forms.ChoiceField(choices = estrato_op)
	Programa = forms.ChoiceField(choices = programa_op)
	AreaReside = forms.ChoiceField(choices = area_op)
'''

periodosSaberPro_op = ((20182,20183,20195,20203,20194,20184,20196,20202))
class periodosSaberPro(forms.Form):
	periodoSaberPro = forms.ChoiceField(choices = periodosSaberPro_op )
formulario pendiente para graphBoxplotCompareSaberSkills11 y graphBoxplotCompareSaberSkillsPro
singular_analysis = ["YEARS_DIFF","ESTU_METODO_PRGM","FAMI_ESTRATOVIVIENDA_11","FAMI_ESTRATOVIVIENDA_PRO"]


class FormFilters(forms.Form):
	class Meta:
		model = filters()
		fields = ['compe']

	def _ini_(self,*args,**kwargs):
		super()._ini_(*args,**kwargs)

		self.fields['compe'].widget.attrs.updste({
			'class': 'form-control'
			})


ACUICULTURA
ADMINISTRACION EN FINANZAS Y NEGOCIOS INTERNACIONALES
ADMINISTRACION EN SALUD
BACTERIOLOGIA
BIOLOGIA
DERECHO
ENFERMERIA
ESTADISTICA
FISICA
GEOGRAFIA
INGENIERIA AGRONOMICA
INGENIERIA AMBIENTAL
INGENIERIA DE ALIMENTOS
INGENIERIA DE SISTEMAS
INGENIERIA INDUSTRIAL
INGENIERIA MECANICA
LICENCIATURA EN CIENCIAS NATURALES Y EDUCACION AMBIENTAL
LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN CIENCIAS SOCIALES
LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN EDUCACION ARTISTICAMUSICA
LICENCIATU
LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN HUMANIDADES   LENGUA CASTELLANA
LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN HUMANIDADESINGLES
LICENCIATURA EN EDUCACION FISICA RECREACION Y DEPORTES
LICENCIATURA EN INFORMATICA Y MEDIOS AUDIOVISUALES
MATEMATICAS
MEDICINA VETERINARIA Y ZOOTECNIA
QUIMICA
'''
