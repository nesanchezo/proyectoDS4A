import pandas as pd
import numpy as np

import plotly.express as px
import json
from plotly.offline import download_plotlyjs, plot
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.figure_factory as ff

import pingouin as pg
import statsmodels as sm
import pickle5 as pickle

from django.http import HttpResponse
from django.shortcuts import render

from exploration.models import filters,Institutions,Cods
from . import forms


'''
------------------------------------------------------------------------------
--Cargar archivos de entrada y parametros que se van a usar en la aplicación--
------------------------------------------------------------------------------
'''
def read_data():
    AllUMergeSaber = pd.read_csv('data/AllU_SaberMerged_plus.csv')
    saberUniCordoba = AllUMergeSaber[AllUMergeSaber["INST_COD_INSTITUCION"] == 1113].copy(deep=True)#pd.read_csv('data/Unicordoba_SaberMerged_Faculties.csv')
    saberUniCordoba.rename(columns = {'GHOST_FACULTY':'FACULTAD'}, inplace = True)
    df_sabermerged_powercampus = pd.read_csv('data/Unicordoba_PowerCampusWithSaberProFull_clean.csv')
    powerCampusGrades = pd.read_csv('data/powerCampusGradesFiltered.csv')
    return AllUMergeSaber, saberUniCordoba, df_sabermerged_powercampus, powerCampusGrades

AllUMergeSaber, saberUniCordoba, df_sabermerged_powercampus, powerCampusGrades = read_data()
skills11 = [ "PUNT_SOCIALES_CIUDADANAS","PUNT_INGLES","PUNT_LECTURA_CRITICA","PUNT_MATEMATICAS","PUNT_C_NATURALES"]
skillsPro = ["MOD_RAZONA_CUANTITAT_PUNT","MOD_LECTURA_CRITICA_PUNT","MOD_COMPETEN_CIUDADA_PUNT","MOD_INGLES_PUNT","MOD_COMUNI_ESCRITA_PUNT"]
replace_compe = {"PUNT_GLOBAL":'Puntaje global',"MOD_RAZONA_CUANTITAT_PUNT":'Modulo razonamiento cuantitativo',
         "MOD_LECTURA_CRITICA_PUNT":'Modulo lectura crítica',"MOD_COMPETEN_CIUDADA_PUNT":'Modulo competencia ciudadana',
         "MOD_INGLES_PUNT":'Modulo ingles',"MOD_COMUNI_ESCRITA_PUNT":'Modulo comunicación escrita'}
aggregation_levels = ["UNIVERSIDAD","FACULTAD","CARRERA"]
color_green_UCordoba = "rgb(64,142,54)"
color_blue_UCordoba = "rgb(84,119,173)"
color_lightgray_UCordoba = "rgb(233,233,233)"
color_orange_UCordoba =  "rgb(240,154,68)"
color_red_UCordoba =  "rgb(142,64,54)"
color_discrete_sequence_Ucordoba = [color_green_UCordoba,color_blue_UCordoba, color_orange_UCordoba, color_red_UCordoba]
color_discrete_sequence_Auto = px.colors.qualitative.Prism
all_terms_saber11 = AllUMergeSaber["PERIODO_11"].unique()
all_terms_saberPro = AllUMergeSaber["PERIODO_PRO"].unique()

with open('data/models/pred_model_skill1.pickle', 'rb') as f:
    pred_model_skill1 = pickle.load(f)
with open('data/models/pred_model_skill2.pickle', 'rb') as f:
    pred_model_skill2 = pickle.load(f)
with open('data/models/pred_model_skill3.pickle', 'rb') as f:
    pred_model_skill3 = pickle.load(f)
with open('data/models/pred_model_skill4.pickle', 'rb') as f:
    pred_model_skill4 = pickle.load(f)
with open('data/models/pred_model_skill5.pickle', 'rb') as f:
    pred_model_skill5 = pickle.load(f)
# Create your views here.
'''
------------------------------------------------------------------
----------Vizualización de la página de inicio--------------------
------------------------------------------------------------------
'''

def index(request):
	return render(request,'index.html')

'''
------------------------------------------------------------------
------------------Visualizaciones de los mapas--------------------
------------------------------------------------------------------
'''
def mapaSaber11(request):
    formUno = forms.periodosSaber11()
    period_saber11_select = 20152
    if request.method=='POST':
        formUno = forms.periodosSaber11(request.POST)
        if formUno.is_valid():
            period_saber11_select = formUno.cleaned_data["periodo_Saber11"]
        else:
            period_saber11_select = 20152
    graphs = mapSaber11SkillsForTerm(saberUniCordoba, skills11 , int(period_saber11_select))
    plot_div = plot({'data': graphs}, output_type='div')
    resultados = {'plot_div': plot_div,'formUno':formUno}
    return render(request,'mapa_saber11.html',resultados)

def mapaSaberPro(request):
    formUno = forms.periodosSaberPro()
    period_saberPro_select = 20203
    if request.method=='POST':
        formUno = forms.periodosSaberPro(request.POST)
        if formUno.is_valid():
            period_saberPro_select = formUno.cleaned_data["periodo_SaberPro"]
        else:
            period_saberPro_select = 20203
    graphs = mapSaberProSkillsForTerm(saberUniCordoba, skillsPro , int(period_saberPro_select))
    plot_div = plot({'data': graphs}, output_type='div')
    resultados = {'plot_div': plot_div,'formUno':formUno}
    return render(request,'mapa_saberPro.html',resultados)

#---Funciones

def mapSaber11SkillsForTerm(df, skills, requiredTerm):
    df_filtered = df[df["PERIODO_11"] == requiredTerm] 
    fig = mapSaberSkillsForTerm(df_filtered, skills)
    return fig

def mapSaberProSkillsForTerm(df, skills, requiredTerm):
    df_filtered = df[df["PERIODO_PRO"] == requiredTerm] 
    fig = mapSaberSkillsForTerm(df_filtered, skills)
    return fig

def mapSaberSkillsForTerm(df_filtered, skills):
    f = open('data/colombia.geo.json')
    ColombianMap = json.load(f)
    columns_used = np.append(skills,"ESTU_DEPTO_RESIDE_PRO")
    df_grouped = df_filtered[columns_used].groupby("ESTU_DEPTO_RESIDE_PRO").mean().reset_index()

    visiblebyDefault = True
    graph_data = []
    buttonLayout = []
    i = 0
    for skill in skills:
        graph_data.append(go.Choroplethmapbox(geojson=ColombianMap,locations=df_grouped["ESTU_DEPTO_RESIDE_PRO"], featureidkey="properties.NOMBRE_DPT",z=df_grouped[skill],colorscale='RdYlGn',colorbar_title="Average Score Value",visible = visiblebyDefault))
        visiblebyDefault = False
        visibleArray = [False]*len(skills)
        visibleArray[i] = True
        buttonLayout.append(dict(
                        args=['visible', visibleArray],
                        label=skill,
                        method='restyle'
                    ))
        i = i+1

    layout = go.Layout(mapbox = dict(style="carto-positron",
                                    center= {"lat": 8, "lon": -73.1198},
                                    zoom=5.5,
                                    ))#accesstoken=mapbox_accesstoken))

    layout.update(updatemenus=list([
            dict(
                x=-0.05,
                y=1,
                yanchor='top',
                buttons=buttonLayout,
            )]))
    layout.update(
    autosize=False,
    width=1500,
    height=800,
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ),)
    fig=go.Figure(data=graph_data, layout =layout)
    return fig

'''
------------------------------------------------------------------
------------------Visualizacion prediciones-----------------------
------------------------------------------------------------------
'''
def predict(request):
    formUno = forms.CodsForm()
    cod = "P000058813"
    if request.method=='POST':
        formUno = forms.CodsForm(request.POST)
        if formUno.is_valid():
            cod = formUno.cleaned_data["codigos"]
            cod=str(cod[0])
        else:
            cod = "P000058813"
    print(cod)
    #cod=str(cod[0])
    graphs_1 = graphStudentRadarSaberSkills(df_sabermerged_powercampus,cod,skills11,skillsPro,color_lightgray_UCordoba)
    plot_div = plot({'data': graphs_1}, output_type='div')
    powerCampusStudentId="P000096280"
    print(powerCampusStudentId)
    graphs_2 = graphBarsStudentScores(powerCampusGrades, powerCampusStudentId)
    plot_div_2 = plot({'data': graphs_2}, output_type='div')
    resultados = {'plot_div': plot_div,'plot_div_2': plot_div_2,'formUno':formUno}
    return render(request,'predict.html',resultados)


#---Funciones

def graphStudentRadarSaberSkills(df,powerCampusId,skills11,skillsPro,color_lightgray_UCordoba):
    specificStudent = df[df["people_code_id"]  == powerCampusId]
    saber11Data = specificStudent[skills11].values.flatten()
    saberProData = specificStudent[skillsPro].values.flatten()
    
    nrows = 1
    ncols = 2
    fig = make_subplots(rows=nrows, cols=ncols, subplot_titles=["Saber11","SaberPro"], specs=[[{'type': 'polar'}]*2])
    
    fig.add_trace(go.Scatterpolar(
          name = "Saber11 Skills",
          r = np.append(saber11Data,saber11Data[0]),
          theta = np.append(skills11,skills11[0]),
          line_color = 'green',
          fill = 'toself'
        ), 1, 1)
    fig.add_trace(go.Scatterpolar(
          name = "SaberPro Skills",
          r = np.append(saberProData,saberProData[0]),
          theta = np.append(skillsPro,skillsPro[0]),
          thetaunit = "radians",
          line_color = 'green',
          fill = 'toself'
        ), 1, 2)
    
    #fig.update_layout(title_text="Skills")
    fig.update_polars(bgcolor=color_lightgray_UCordoba)
    fig.update_layout(title_text='Id: ' +powerCampusId)
    return fig

def getStudentGradesAndUniversityAverage(df, powerCampusStudentId):
    df_clean = df.copy(deep=True)
    df_clean["NotaFinal"].replace(["PE","NP"], "NaN", inplace=True)
    df_clean["NotaFinal"] = df_clean["NotaFinal"].astype(float)
    studentGrades = df_clean[df_clean["people_code_id"]== powerCampusStudentId]
    studentGradesFiltered = studentGrades.dropna(subset=['Nota1', 'Nota2', 'Nota3'])
    studentTerm = studentGradesFiltered["Periodo"].unique()
    studentSemesters = studentGradesFiltered["Semestre"].unique()
    studentCareer = studentGradesFiltered["ProgramaEstudiante"].unique()
    careerdata = df_clean[(df_clean["ProgramaEstudiante"] == studentCareer[0])]

    career_means = careerdata[["Periodo","Semestre","NotaFinal"]].groupby(['Periodo','Semestre']).mean().reset_index()

    semester = 0
    career_grades = [0]*len(studentTerm)
    for studentT in studentTerm:
        career_grades[semester] = career_means[(career_means["Periodo"] == studentT) & (career_means["Semestre"] == studentSemesters[semester] )]["NotaFinal"].iloc[0]
        semester = semester + 1

    studentAverage = studentGradesFiltered[["Semestre","NotaFinal"]].groupby(by=["Semestre"]).mean().reset_index()
    return studentAverage, career_grades

def graphBarsStudentScores(df, powerCampusStudentId):
    studentAverage, career_grades = getStudentGradesAndUniversityAverage(df, powerCampusStudentId)
    fig = go.Figure(
        data=[
            go.Bar(name='Student average', x=studentAverage["Semestre"], y=studentAverage["NotaFinal"], offsetgroup=1, marker=dict(color=color_blue_UCordoba)),
            go.Bar(name='Career average', x=studentAverage["Semestre"], y=career_grades, offsetgroup=2, marker=dict(color=color_green_UCordoba)),
        ],
        layout={
            'yaxis': {'title': 'Score average'},
            'xaxis': {'title': 'Semester'}
        }
    )

    # Change the bar mode
    fig.update_layout(barmode='group',plot_bgcolor=color_lightgray_UCordoba)
    fig.update_layout(title_text='Id: ' +powerCampusStudentId)
    return fig

'''
------------------------------------------------------------------
----------------Visualizaciones Hypothesis------------------------
------------------------------------------------------------------
'''
def hypothesis(request):
    graphs_1 = plotHistograms(saberUniCordoba, df_sabermerged_powercampus, "MOD_COMPETEN_CIUDADA_PUNT", "MOD_COMUNI_ESCRITA_PUNT",color_lightgray_UCordoba,color_green_UCordoba,color_orange_UCordoba)
    plot_div_1 = plot({'data': graphs_1}, output_type='div')
    graphs_2 = CompareDistributions(saberUniCordoba, df_sabermerged_powercampus, "MOD_COMPETEN_CIUDADA_PUNT", "MOD_COMUNI_ESCRITA_PUNT",color_lightgray_UCordoba,color_green_UCordoba,color_orange_UCordoba)
    plot_div_2 = plot({'data': graphs_2}, output_type='div')
    graphs_3 = CompareDistributions(saberUniCordoba, df_sabermerged_powercampus, "MOD_COMPETEN_CIUDADA_PUNT", "MOD_COMUNI_ESCRITA_PUNT",color_lightgray_UCordoba,color_green_UCordoba,color_orange_UCordoba)
    plot_div_3 = plot({'data': graphs_3}, output_type='div')
    data_1 = pValue(skillsPro).reset_index().to_html()
    data_2 = pValue(skills11).reset_index().to_html()
    resultados = {'data_1':data_1,'data_2':data_2,'plot_div_1': plot_div_1,'plot_div_2': plot_div_2,'plot_div_3': plot_div_3}
    return render(request,'hypothesis.html',resultados)

#----Funciones

def pValue(skillsSaber):
    df_pro = pd.DataFrame(columns=['Skill','P-Value'])
    for skill in skillsSaber:
        dff = pd.DataFrame([[skill,pg.ttest(saberUniCordoba[skill],df_sabermerged_powercampus[skill])['p-val'][0]]],columns=['Skill','P-Value'])
        df_pro = pd.concat([df_pro, dff],ignore_index=True)
    df_pro = df_pro.replace(replace_compe)
    df_pro = df_pro.set_index('Skill')
    return df_pro

def plotHistograms(df_full, df_subset, skill1, skill2,color_lightgray_UCordoba,color_green_UCordoba,color_orange_UCordoba):
    fig = make_subplots(rows=1, cols=2, subplot_titles=[skill1, skill2],x_title = "Score")
    fig.add_trace(go.Histogram(name='Dataset', x=df_full[skill1], offsetgroup=1,nbinsx = 25, opacity = 0.5, marker=dict(color=color_green_UCordoba))
                  , 1, 1)
    fig.add_trace(go.Histogram(name='Subset', x=df_subset[skill1], offsetgroup=1,nbinsx = 25, opacity = 0.5, marker=dict(color=color_orange_UCordoba))
                  , 1, 1)
    fig.add_trace(go.Histogram(name='Dataset', x=df_full[skill2], offsetgroup=1,nbinsx = 25, opacity = 0.5, marker=dict(color=color_green_UCordoba))
                  , 1, 2)
    fig.add_trace(go.Histogram(name='Subset', x=df_subset[skill2], offsetgroup=1,nbinsx = 25, opacity = 0.5, marker=dict(color=color_orange_UCordoba))
                  , 1, 2)
    fig.update_layout(plot_bgcolor=color_lightgray_UCordoba,title_text = "Histogram comparisson of dataset and merged-subset")
    return fig

def CompareDistributions(df_full, df_subset, skill1, skill2,color_lightgray_UCordoba,color_green_UCordoba,color_orange_UCordoba):
    fig = make_subplots(rows=1, cols=2, subplot_titles=[skill1,skill2],x_title = "Score")

    df_full = df_full.dropna(subset=[skill1, skill2])
    df_subset = df_subset.dropna(subset=[skill1, skill2])

    hist_data1 = [df_full[skill1], df_subset[skill1]]
    group_labels = ['Dataset', 'Subset']

    fig1 = ff.create_distplot(
        hist_data1, group_labels, show_hist = False)

    hist_data2 = [df_full[skill2], df_subset[skill2]]
    group_labels = ['Dataset', 'Subset']

    fig2 = ff.create_distplot(
        hist_data2, group_labels, show_hist = False)


    fig.add_trace(go.Scatter(fig1['data'][0],
                             line=dict(color=color_green_UCordoba)
                            ), row=1, col=1)

    fig.add_trace(go.Scatter(fig1['data'][1],
                             line=dict(color=color_orange_UCordoba)
                            ), row=1, col=1)

    fig.add_trace(go.Scatter(fig2['data'][0],
                             line=dict(color=color_green_UCordoba)
                            ), row=1, col=2)

    fig.add_trace(go.Scatter(fig2['data'][1],
                             line=dict(color=color_orange_UCordoba)
                            ), row=1, col=2)

    fig.update_layout(plot_bgcolor=color_lightgray_UCordoba, title_text = "Probability densities of dataset and merged-subset")
    return fig

'''
------------------------------------------------------------------
---------Visualizaciones predicción--------------------
------------------------------------------------------------------
'''
def prediction(request):
    formUno = forms.predictForm()
    SOCIALES_CIUDADANAS =1
    INGLES =1
    LECTURA_CRITICA =1
    MATEMATICAS =1
    C_NATURALES =1
    Estra =1
    Program ='ADMINISTRACION EN FINANZAS Y NEGOCIOS INTERNACIONALES'
    AreaResid ='AREA RURAL'
    if request.method=='POST':
        formUno = forms.predictForm(request.POST)
        if formUno.is_valid():
            SOCIALES_CIUDADANAS = formUno.cleaned_data["PUNT_SOCIALES_CIUDADANAS"]
            INGLES = formUno.cleaned_data["PUNT_INGLES"]
            LECTURA_CRITICA = formUno.cleaned_data["PUNT_LECTURA_CRITICA"]
            MATEMATICAS = formUno.cleaned_data["PUNT_MATEMATICAS"]
            C_NATURALES = formUno.cleaned_data["PUNT_C_NATURALES"]
            Estra = formUno.cleaned_data["Estrato"]
            Program = formUno.cleaned_data["Programa"]
            AreaResid = formUno.cleaned_data["AreaReside"]
        else:
            SOCIALES_CIUDADANAS =1
            INGLES =1
            LECTURA_CRITICA =1
            MATEMATICAS =1
            C_NATURALES =1
            Estra =1
            Program ='ADMINISTRACION EN FINANZAS Y NEGOCIOS INTERNACIONALES'
            AreaResid ='AREA RURAL'
    data = predictSaberPro(SOCIALES_CIUDADANAS,INGLES,LECTURA_CRITICA,MATEMATICAS,C_NATURALES,Estra,Program,AreaResid)
    data_1 = data.to_html()
    graphs_1 = graphStudentRadarSaberSkillsPredicted(SOCIALES_CIUDADANAS,INGLES,LECTURA_CRITICA,MATEMATICAS,C_NATURALES,data)
    plot_div_1 = plot({'data': graphs_1}, output_type='div')
    resultados = {'plot_div_1': plot_div_1,'data_1':data_1,'formUno':formUno}
    return render(request,'prediction.html',resultados)

def predictSaberPro(PUNT_SOCIALES_CIUDADANAS, PUNT_INGLES, PUNT_LECTURA_CRITICA, PUNT_MATEMATICAS, PUNT_C_NATURALES,
                    Estrato, Programa:str, AreaReside:str):
    
    input_data = {'PUNT_SOCIALES_CIUDADANAS': 0,
    'PUNT_INGLES': 0,
    'PUNT_LECTURA_CRITICA': 0,
    'PUNT_MATEMATICAS': 0,
    'PUNT_C_NATURALES': 0,
    'FAMI_ESTRATOVIVIENDA_11_Estrato 1': 0,
    'FAMI_ESTRATOVIVIENDA_11_Estrato 2': 0,
    'FAMI_ESTRATOVIVIENDA_11_Estrato 3': 0,
    'FAMI_ESTRATOVIVIENDA_11_Estrato 5': 0,
    'FAMI_ESTRATOVIVIENDA_11_Estrato 4': 0,
    'ProgramaEstudiante_ADMINISTRACION EN FINANZAS Y NEGOCIOS INTERNACIONALES': 0,
    'ProgramaEstudiante_ADMINISTRACION EN SALUD': 0,
    'ProgramaEstudiante_INGENIERIA DE ALIMENTOS': 0,
    'ProgramaEstudiante_MEDICINA VETERINARIA Y ZOOTECNIA': 0,
    'ProgramaEstudiante_INGENIERIA DE SISTEMAS': 0,
    'ProgramaEstudiante_LICENCIATURA EN CIENCIAS NATURALES Y EDUCACION AMBIENTAL': 0,
    'ProgramaEstudiante_ACUICULTURA': 0,
    'ProgramaEstudiante_BACTERIOLOGIA': 0,
    'ProgramaEstudiante_BIOLOGIA': 0,
    'ProgramaEstudiante_DERECHO': 0,
    'ProgramaEstudiante_ENFERMERIA': 0,
    'ProgramaEstudiante_ESTADISTICA': 0,
    'ProgramaEstudiante_FISICA': 0,
    'ProgramaEstudiante_GEOGRAFIA': 0,
    'ProgramaEstudiante_INGENIERIA AGRONOMICA': 0,
    'ProgramaEstudiante_INGENIERIA AMBIENTAL': 0,
    'ProgramaEstudiante_INGENIERIA INDUSTRIAL': 0,
    'ProgramaEstudiante_INGENIERIA MECANICA': 0,
    'ProgramaEstudiante_LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN CIENCIAS SOCIALES': 0,
    'ProgramaEstudiante_LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN HUMANIDADESINGLES': 0,
    'ProgramaEstudiante_LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN HUMANIDADES   LENGUA CASTELLANA': 0,
    'ProgramaEstudiante_LICENCIATURA EN EDUCACION BASICA CON ENFASIS EN EDUCACION ARTISTICAMUSICA': 0,
    'ProgramaEstudiante_LICENCIATURA EN EDUCACION FISICA RECREACION Y DEPORTES': 0,
    'ProgramaEstudiante_LICENCIATURA EN INFORMATICA Y MEDIOS AUDIOVISUALES': 0,
    'ProgramaEstudiante_MATEMATICAS': 0,
    'ProgramaEstudiante_QUIMICA': 0,
    'ESTU_AREARESIDE_CABECERA MUNICIPAL': 0,
    'ESTU_AREARESIDE_AREA RURAL': 0,
    'ESTU_AREARESIDE_NAN': 0
    }

    Estrato_key = 'FAMI_ESTRATOVIVIENDA_11_Estrato ' + str(Estrato)
    Programa_key = 'ProgramaEstudiante_' + Programa
    AreaReside_key = 'ESTU_AREARESIDE_' + AreaReside

    input_data["PUNT_SOCIALES_CIUDADANAS"] = PUNT_SOCIALES_CIUDADANAS,
    input_data["PUNT_INGLES"] = PUNT_INGLES
    input_data["PUNT_LECTURA_CRITICA"] = PUNT_LECTURA_CRITICA,
    input_data["PUNT_MATEMATICAS"] = PUNT_MATEMATICAS,
    input_data["PUNT_C_NATURALES"] = PUNT_C_NATURALES
    input_data[Estrato_key] = 1
    input_data[Programa_key] = 1
    input_data[AreaReside_key] = 1

    input_df = pd.DataFrame(input_data)

    output_data = {
    pred_model_skill1.model.endog_names: pred_model_skill1.predict(input_df),
    pred_model_skill2.model.endog_names: pred_model_skill2.predict(input_df),
    pred_model_skill3.model.endog_names: pred_model_skill3.predict(input_df),
    pred_model_skill4.model.endog_names: pred_model_skill4.predict(input_df),
    pred_model_skill5.model.endog_names: pred_model_skill5.predict(input_df)
    }

    output_df = pd.DataFrame(output_data)
    
    return output_df

def graphStudentRadarSaberSkillsPredicted(PUNT_SOCIALES_CIUDADANAS, PUNT_INGLES, 
                         PUNT_LECTURA_CRITICA, PUNT_MATEMATICAS, 
                         PUNT_C_NATURALES, prediction_df):
    
    saber11_data = {'PUNT_SOCIALES_CIUDADANAS': [PUNT_SOCIALES_CIUDADANAS],
      'PUNT_INGLES': [PUNT_INGLES],
      'PUNT_LECTURA_CRITICA': [PUNT_LECTURA_CRITICA],
      'PUNT_MATEMATICAS': [PUNT_MATEMATICAS],
      'PUNT_C_NATURALES': [PUNT_C_NATURALES]
    }

    saber11_df = pd.DataFrame(saber11_data)
    saber11Data = saber11_df.values.flatten()
    
    saberProData = prediction_df.values.flatten()
    
    nrows = 1
    ncols = 2
    fig = make_subplots(rows=nrows, cols=ncols, subplot_titles=["Saber11","SaberPro Prediction"], specs=[[{'type': 'polar'}]*2])
    
    fig.add_trace(go.Scatterpolar(
          name = "Saber11 Skills",
          r = np.append(saber11Data,saber11Data[0]),
          theta = np.append(skills11,skills11[0]),
          line_color = 'green',
          fill = 'toself'
        ), 1, 1)
    fig.add_trace(go.Scatterpolar(
          name = "SaberPro Skills",
          r = np.append(saberProData,saberProData[0]),
          theta = np.append(skillsPro,skillsPro[0]),
          thetaunit = "radians",
          line_color = 'green',
          fill = 'toself'
        ), 1, 2)
    
    fig.update_layout(title_text="Skills")
    fig.update_polars(bgcolor=color_lightgray_UCordoba)
    return fig


'''
------------------------------------------------------------------
---------Visualizaciones analisis exploratorio--------------------
------------------------------------------------------------------
'''

def visualizations(request):
    formUno = forms.CompeFormUno()
    compe = "PUNT_GLOBAL"
    if request.method=='POST':
        formUno = forms.CompeFormUno(request.POST)
        if formUno.is_valid():
            compe = formUno.cleaned_data["Competencias"]
        else:
            compe = "PUNT_GLOBAL"
    graphs_1 = graphbubbleskillbyfaculty(saberUniCordoba,compe,color_discrete_sequence_Auto,color_lightgray_UCordoba)
    plot_div = plot({'data': graphs_1}, output_type='div')
    facult_select = "FACULTAD DE INGENIERIAS"
    compe2 = "PUNT_GLOBAL"
    formDos = forms.Facultades()
    if request.method=='POST':
        formDos = forms.Facultades(request.POST)
        if formDos.is_valid():
            facult_select = formDos.cleaned_data["Facultades"]
            compe2 = formDos.cleaned_data["Competencia"]
        else:
            facult_select = "FACULTAD DE INGENIERIAS"
            compe2 = "PUNT_GLOBAL"
    graphs_2 = plotbubbleprogramsbyfaculty(saberUniCordoba,facult_select,compe2,color_discrete_sequence_Auto,color_lightgray_UCordoba)
    plot_div_2 = plot({'data': graphs_2}, output_type='div')
    formTres = forms.periodosSaber()
    period_saber11_select = 20152
    period_saberPro_select = 20203
    if request.method=='POST':
        formTres = forms.periodosSaber(request.POST)
        if formTres.is_valid():
            period_saber11_select = formTres.cleaned_data["periodoSaber11"]
            period_saberPro_select = formTres.cleaned_data["periodoSaberPro"]
        else:
            period_saber11_select = 20152
            period_saberPro_select = 20203
    graphs_3 = graphScatter(AllUMergeSaber,int(period_saber11_select),int(period_saberPro_select))
    plot_div_3 = plot({'data': graphs_3}, output_type='div')
    formDos2 = forms.periodosSaberPro()
    period_saberPro_select = 20203
    if request.method=='POST':
        formDos2 = forms.periodosSaberPro(request.POST)
        if formDos2.is_valid():
            period_saberPro_select = formDos2.cleaned_data["periodo_SaberPro"]
        else:
            period_saberPro_select = 20203
    graphs_2_5 = graphBoxplotCompareSaberSkillsPro(skillsPro, int(period_saberPro_select),AllUMergeSaber,color_discrete_sequence_Auto,color_lightgray_UCordoba,"YEARS_DIFF")
    plot_div2_5 = plot({'data': graphs_2_5}, output_type='div')
    
    formCuatro = forms.comp_yearsForm()
    comp = 'FAMI_ESTRATOVIVIENDA_PRO'
    if request.method=='POST':
        formCuatro = forms.comp_yearsForm(request.POST)
        if formCuatro.is_valid():
            comp = formCuatro.cleaned_data["comp_years"]
        else:
            comp = 'FAMI_ESTRATOVIVIENDA_PRO'
    graphs_2_6 = graphBoxplotCompareSaberProGradeForVariable(comp)
    plot_div2_6 = plot({'data': graphs_2_6}, output_type='div')
    data_1 = updateRanking(comp).to_html()        
    resultados = {'data_1':data_1,'plot_div': plot_div,'plot_div_2': plot_div_2,'plot_div_3': plot_div_3,'formUno':formUno,'formDos':formDos,'formDos2':formDos2,'formTres':formTres,'formCuatro':formCuatro,'plot_div2_5': plot_div2_5,'plot_div2_6': plot_div2_6}
    return render(request,'visualizations.html', resultados)


#---Funciones

def isLocalData(universityCode):
    if (universityCode == 1113):
        result = "U de Cordoba"
    else:
        result= "National Total Score"
    return result

def graphbubbleskillbyfaculty(saberUniCordoba,skillPro,color_discrete_sequence_Auto,color_lightgray_UCordoba):
    general=saberUniCordoba.groupby(['FACULTAD','PERIODO_PRO']).agg({'PERIODO_PRO':'size', \
                                                                       'MOD_RAZONA_CUANTITAT_PUNT':'mean', 'MOD_COMPETEN_CIUDADA_PUNT':'mean', 'MOD_COMUNI_ESCRITA_PUNT':'mean',
                                                                        'MOD_LECTURA_CRITICA_PUNT':'mean','MOD_INGLES_PUNT':'mean',
                                                                        'PUNT_GLOBAL':'mean'}).rename(columns={'PERIODO_PRO':'STUDENTS'}).reset_index()
    periodos=[20183,20195,20203,20212]
    general = general[general['PERIODO_PRO'].isin(periodos)]
    print(len(general["PERIODO_PRO"]))
    fig = px.scatter(general, x="PERIODO_PRO", y=skillPro, color='FACULTAD',
                     size="STUDENTS", size_max=30,  color_discrete_sequence = color_discrete_sequence_Auto)
    fig.update_xaxes(type='category')
    fig.update_xaxes(title_text='Period')
    fig.update_yaxes(title_text='Score')
    fig.update_layout(plot_bgcolor=color_lightgray_UCordoba,title_text=skillPro)
    return fig

def plotbubbleprogramsbyfaculty(saberUniCordoba,faculty,skillPro,color_discrete_sequence_Auto,color_lightgray_UCordoba):
    # PLOT THE RESULTS by programs for a selected faculty and a selected skill    
    general=saberUniCordoba.groupby(['FACULTAD','PERIODO_PRO','ESTU_PRGM_ACADEMICO']).agg({'PERIODO_PRO':'size', \
                                                                                              'MOD_RAZONA_CUANTITAT_PUNT':'mean', 'MOD_COMPETEN_CIUDADA_PUNT':'mean', 'MOD_COMUNI_ESCRITA_PUNT':'mean',
                                                                                           'MOD_LECTURA_CRITICA_PUNT':'mean','MOD_INGLES_PUNT':'mean', 'PUNT_GLOBAL':'mean'})\
    .rename(columns={'PERIODO_PRO':'STUDENTS'}).reset_index()
    periodos=[20183,20195,20203,20212]
    general = general[general['PERIODO_PRO'].isin(periodos)]
    general = general[general['FACULTAD']==faculty]
    fig = px.scatter(general, x="PERIODO_PRO", y=skillPro, color='ESTU_PRGM_ACADEMICO',size="STUDENTS", size_max=20, color_discrete_sequence = color_discrete_sequence_Auto)
    fig.update_xaxes(type='category')
    fig.update_xaxes(title_text='Period')
    fig.update_yaxes(title_text='Score')
    fig.update_layout(legend=dict(yanchor="top",y=0.99,xanchor="right",x=1.21,font=dict(size=9,color="black"))
                      ,title_text=faculty + ' - ' + skillPro, plot_bgcolor=color_lightgray_UCordoba)
    return fig

def graphScatter(df, termSaber11, termSaberPro):
    dfFiltered = df[(df["PERIODO_11"] == termSaber11) & (df["PERIODO_PRO"] == termSaberPro)].copy(deep=True)
    #if dfFiltered.empty:

    dfFiltered["PUNT_TOTAL_11"] = dfFiltered[skills11].mean(axis = 1)
    dfUcordoba = dfFiltered[dfFiltered["INST_COD_INSTITUCION"] == 1113]
    
    saber11_mean = dfFiltered["PUNT_TOTAL_11"].mean()
    saberPro_mean = dfFiltered["PUNT_GLOBAL"].mean()
    color_coding = [0]*len( dfUcordoba["PUNT_TOTAL_11"])
    i=0
    for index, row in dfUcordoba[["PUNT_TOTAL_11","PUNT_GLOBAL"]].iterrows():
        if ((row["PUNT_TOTAL_11"] < saber11_mean) & (row["PUNT_GLOBAL"] < saberPro_mean)):
            color_coding[i] = 3
        elif (row["PUNT_GLOBAL"] < saberPro_mean):
            color_coding[i] = 2
        elif (row["PUNT_TOTAL_11"] < saber11_mean):
            color_coding[i] = 1
        else:
            color_coding[i] = 0
        i = i+1

    fig = go.Figure()

    fig = px.scatter(dfUcordoba, x="PUNT_TOTAL_11", y="PUNT_GLOBAL", marginal_x="histogram", marginal_y="histogram"
                     , color=color_coding, color_continuous_scale  = color_discrete_sequence_Ucordoba
                     ,labels = {"PUNT_TOTAL_11":"Saber 11 scores","PUNT_GLOBAL":"Saber Pro scores"})

    fig.add_vline(x=saber11_mean, col = 1, row = 1, line_width=3, line_dash="dot", annotation_text="National mean of Saber 11", line_color=color_orange_UCordoba)
    fig.add_hline(y=saberPro_mean, col = 1, row = 1, line_width=3, line_dash="dot", annotation_text="National mean of Saber Pro", line_color=color_orange_UCordoba)

    fig.update_traces(marker=dict(opacity=0.5),
                      selector=dict(mode='markers'))
    fig.update_layout(plot_bgcolor=color_lightgray_UCordoba)
    return fig

def PlainGraph():
    fig = make_subplots(rows=1, cols=1,x_title = "Score",y_title="Saber Pro Score")
    return fig
# graphfscatter, se hacen 2 filtros fecha saber pro y fecha saber 11
#-----------NUEVA GRAFICA--------------------
def read_saberUniCordoba():
    saberUniCordoba = AllUMergeSaber[AllUMergeSaber["INST_COD_INSTITUCION"] == 1113].copy(deep=True)
    return saberUniCordoba

def graphBoxplotCompareSaberProGradeForVariable(variabletoCheck):
    saberCordoba = read_saberUniCordoba()
    df = saberCordoba[["PERIODO_PRO", "PUNT_GLOBAL", variabletoCheck]].copy(deep = True)
    del saberCordoba
    #get the data of the the university and the term to compare
    df.dropna(inplace = True)
    df.sort_values(by=[variabletoCheck, "PERIODO_PRO"],inplace = True)
    fig = px.box(df, x= "PERIODO_PRO", y="PUNT_GLOBAL", color = variabletoCheck, color_discrete_sequence=color_discrete_sequence_Auto)
    fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
    fig.update_layout(plot_bgcolor=color_lightgray_UCordoba)
    fig.update_xaxes(type='category')
    return fig

def showNewClassification20203(variable):
    saberUniCordoba = pd.read_csv('data/1113.csv')
    new_classification_df =  pd.read_csv('data/Classifications2020.csv')
    new_classification_df.drop([180], inplace = True)   
    saberUniCordoba20203 = saberUniCordoba[saberUniCordoba["PERIODO_PRO"]==20203].dropna(subset=["PERIODO_PRO"]).copy(deep=True)
    del saberUniCordoba
    if(variable == "ESTU_METODO_PRGM"):
        group_cordoba20203_mean = saberUniCordoba20203[saberUniCordoba20203["ESTU_METODO_PRGM"] == "PRESENCIAL"]["PUNT_GLOBAL"].mean()
    elif(variable == "YEARS_DIFF"):
        group_cordoba20203_mean = saberUniCordoba20203[saberUniCordoba20203["YEARS_DIFF"] < 7]["PUNT_GLOBAL"].mean()
    else:
        group_cordoba20203_mean = saberUniCordoba20203[saberUniCordoba20203["FAMI_ESTRATOVIVIENDA_PRO"] != "Estrato 1"]["PUNT_GLOBAL"].mean()
    new_classification_df.loc[len(new_classification_df.index)] = ['UNIVERSIDAD DE CORDOBA-MONTERIA', group_cordoba20203_mean] 
    new_classification_df = new_classification_df.sort_values(['PUNT_GLOBAL'], ascending=False,ignore_index = True)
    
    new_position = new_classification_df[new_classification_df["INST_NOMBRE_INSTITUCION"] == "UNIVERSIDAD DE CORDOBA-MONTERIA"]["PUNT_GLOBAL"].index.values.astype(int)[0]
    return new_position

def updateRanking(variable):
    new_value = showNewClassification20203(variable)
    universityTable = {'Institucion Educativa': ["UNIVERSIDAD DE CORDOBA-MONTERIA"], 'Ranking Actual': [181], 'Ranking Recalculado':[new_value]}
    universityRanking = pd.DataFrame(data=universityTable)
    return universityRanking
'''
------------------------------------------------------------------
---------------Visualizaciones Analisis comparativo---------------
------------------------------------------------------------------
'''

def comparativo(request):   
    formUno = forms.periodosPruebaSaber()
    prueba = 'skills11'
    period_saber11_select_1 = 20152
    period_saberPro_select_1 = 20203
    if request.method=='POST':
        formUno = forms.periodosPruebaSaber(request.POST)
        if formUno.is_valid():
            prueba = formUno.cleaned_data["Prueba_Saber"]
            period_saber11_select_1 = formTres.cleaned_data["periodoSaber11"]
            period_saberPro_select_1 = formTres.cleaned_data["periodoSaberPro"]
        else:
            prueba = 'skills11'
            period_saber11_select_1 = 20152
            period_saberPro_select_1 = 20203
    if prueba == 'skills11':
        skills = skills11
    else:
        skills = skillsPro

    graphs_2_1 = graphBoxplotWithFilters(AllUMergeSaber,[int(period_saber11_select_1)], [int(period_saberPro_select_1)], skills, "", "", "",color_discrete_sequence_Ucordoba,color_lightgray_UCordoba)
    plot_div2_1 = plot({'data': graphs_2_1}, output_type='div')

    #institutions = forms.FormInstitutions()
    formCuatro = forms.InstitutionsForm11()
    Uni = 'UNIVERSIDAD FRANCISCO DE PAULA SANTANDER-CUCUTA'
    period_saber11_select_1 = 20152
    if request.method=='POST':
        formCuatro = forms.InstitutionsForm11(request.POST)
        if formCuatro.is_valid():
            Uni = formCuatro.cleaned_data["instituciones"]
            period_saber11_select_1 = formCuatro.cleaned_data["periodoSaber11"]
        else:
            Uni = 'UNIVERSIDAD FRANCISCO DE PAULA SANTANDER-CUCUTA'
            period_saber11_select_1 = 20152
    targetUniversityName = str(Uni[0])#AllUMergeSaber[AllUMergeSaber.INST_NOMBRE_INSTITUCION == Uni]["INST_NOMBRE_INSTITUCION"].iloc[0]
    graphs_2_2 = graphBoxplotWithFilters(AllUMergeSaber,[int(period_saber11_select_1)],all_terms_saberPro,skills11, targetUniversityName,"","",color_discrete_sequence_Ucordoba,color_lightgray_UCordoba)
    plot_div2_2 = plot({'data': graphs_2_2}, output_type='div')

    formCinco = forms.InstitutionsFormPro()
    Uni = 'UNIVERSIDAD FRANCISCO DE PAULA SANTANDER-CUCUTA'
    period_saberPro_select = 20203
    if request.method=='POST':
        formCinco = forms.InstitutionsFormPro(request.POST)
        if formCinco.is_valid():
            Uni = formCinco.cleaned_data["instituciones"]
            period_saberPro_select = formCinco.cleaned_data["periodoSaberPro"]
        else:
            Uni = 'UNIVERSIDAD FRANCISCO DE PAULA SANTANDER-CUCUTA'
            period_saberPro_select = 20203
    targetUniversityNamepro = str(Uni[0])
    graphs_2_3 = graphBoxplotWithFilters(AllUMergeSaber,all_terms_saber11,[int(period_saberPro_select)],skillsPro, targetUniversityNamepro,"","",color_discrete_sequence_Ucordoba,color_lightgray_UCordoba)
    plot_div2_3 = plot({'data': graphs_2_3}, output_type='div')

    

    resultados = {'plot_div2_1': plot_div2_1,'plot_div2_2': plot_div2_2,'plot_div2_3': plot_div2_3,'formUno':formUno,'formCuatro':formCuatro,'formCinco':formCinco}
    return render(request,'comparativo.html',resultados)

#---Funciones

def configureBoxPlotGraph(df, color_variable,color_discrete_sequence_Ucordoba,color_lightgray_UCordoba):
    fig = px.box(df, x="variable", y="value", color=color_variable, color_discrete_sequence=color_discrete_sequence_Ucordoba)
    fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
    fig.update_layout(plot_bgcolor=color_lightgray_UCordoba)
    return fig

def aggregateDataFrame(df, university_filter, faculty_filter, career_filter):
    if(len(university_filter) > 0): 
        df_aggregated = df[(df["INST_NOMBRE_INSTITUCION"] == university_filter) | (df["INST_COD_INSTITUCION"] == 1113)]
    else:
        df_aggregated = df.copy(deep=True)
    if(len(career_filter) > 0):
        df_aggregated = df_aggregated[(df_aggregated["ESTU_PRGM_ACADEMICO"] == career_filter)]
    elif(len(faculty_filter) > 0):
        df_aggregated = df_aggregated[(df_aggregated["GHOST_FACULTY"] == faculty_filter)]
    
    return df_aggregated

def graphBoxplotWithFilters(df,required_saber11_terms, required_saberPro_terms, required_skills
                                      , university_filter, faculty_filter, career_filter,color_discrete_sequence_Ucordoba,color_lightgray_UCordoba):
    #get data by aggregation level requested
    df_aggregated = aggregateDataFrame(df, university_filter, faculty_filter, career_filter)
    #fuse all other universities in a single unit by creating a new variable called DATA_SOURCE
    filteredData = df_aggregated[(df_aggregated["PERIODO_11"].isin(required_saber11_terms)) 
                      & df_aggregated["PERIODO_PRO"].isin(required_saberPro_terms)]
    #check from smallest to biggest level which to use to melt
    if(len(university_filter) > 0):
        aggregation_column = "INST_NOMBRE_INSTITUCION" 
    elif(len(faculty_filter) > 0):
        if(len(career_filter) > 0):
            aggregation_column = "GHOST_FACULTY"
        else:
            aggregation_column = "DATA_SOURCE"
            filteredData['DATA_SOURCE'] = filteredData['INST_COD_INSTITUCION'].apply(isLocalData)        
    elif(len(career_filter) > 0):
        aggregation_column = "DATA_SOURCE"       
        filteredData['DATA_SOURCE'] = filteredData['INST_COD_INSTITUCION'].apply(isLocalData)     
    else:
        aggregation_column = "DATA_SOURCE"       
        filteredData['DATA_SOURCE'] = filteredData['INST_COD_INSTITUCION'].apply(isLocalData)        
    
    filteredData_slim = filteredData.melt(id_vars=aggregation_column, value_vars=required_skills)
    
    fig = configureBoxPlotGraph(filteredData_slim, aggregation_column,color_discrete_sequence_Ucordoba,color_lightgray_UCordoba)
    return fig

def graphBoxplotCompareSaberSkills11(termSkills, referenceTerm,AllUMergeSaber,color_discrete_sequence_Auto,color_lightgray_UCordoba,variabletoCheck):
    #get the data of the the university and the term to compare
    UniversityData = AllUMergeSaber[(AllUMergeSaber["INST_COD_INSTITUCION"] == 1113) & (AllUMergeSaber["PERIODO_11"] == referenceTerm)]
    
    df = UniversityData.melt(id_vars=variabletoCheck, value_vars=termSkills).sort_values(variabletoCheck)

    fig = px.box(df, x="variable", y="value", color=variabletoCheck, color_discrete_sequence=color_discrete_sequence_Auto)
    fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
    fig.update_layout(plot_bgcolor=color_lightgray_UCordoba)
    return fig
    
def graphBoxplotCompareSaberSkillsPro(termSkills, referenceTerm,AllUMergeSaber,color_discrete_sequence_Auto,color_lightgray_UCordoba,variabletoCheck):
    #get the data of the the university and the term to compare
    UniversityData = AllUMergeSaber[(AllUMergeSaber["INST_COD_INSTITUCION"] == 1113) & (AllUMergeSaber["PERIODO_PRO"] == referenceTerm)]
    
    df = UniversityData.melt(id_vars=variabletoCheck, value_vars=termSkills).sort_values(variabletoCheck)

    fig = px.box(df, x="variable", y="value", color=variabletoCheck, color_discrete_sequence=color_discrete_sequence_Auto)
    fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
    fig.update_layout(plot_bgcolor=color_lightgray_UCordoba)
    return fig


'''
institutions = Institutions.objects.all()
    Uni = 'UNIVERSIDAD FRANCISCO DE PAULA SANTANDER-CUCUTA'
    if request.method=='POST':
        institutions = forms.FormInstitutions(request.POST)
        if institutions.is_valid():
            Uni_display = institutions.cleaned_data['Institutions']
            Uni_display = dict(form.fields['Institutions'].choices)[Institutions]
            #Uni = institutions.get_instituciones_display()
        else:
            Uni = 'UNIVERSIDAD FRANCISCO DE PAULA SANTANDER-CUCUTA'



<div class="container">
  <h2>Seleccione la universidad</h2>
  <form method = "POST">
<input type="text" id="tags">
{%csrf_token%}
    <script>
  $( function() {
    var availableTags = [
        {% for institution in institutions %}
            "{{institution.instituciones}}",
        {% endfor %}
    ];
    $( "#tags" ).autocomplete({
      source: availableTags
    });
  } );
  </script>
  <input type = "submit" value = "Submit">
  </form>
</div>
'''