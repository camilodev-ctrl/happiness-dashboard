from flask import Flask, render_template, request
import pandas as pd
import glob
import folium

app = Flask(__name__)

# Cargar los archivos CSV
archivos_csv = glob.glob("*.csv")
datos =[]

for archivo in archivos_csv:
    año = archivo.split('.')[0] #extraer el año del nombre del archivo
    df = pd.read_csv(archivo) 
    #Renombrar columnas para estandarizar
    renombres ={
        'Country or region': 'Country',
        'Country Region': 'Country',
        'Happiness score': 'Score',
        'Happiness.Score': 'Score',
    }
    df.rename(columns={k: v for k, v in renombres.items() if k in df.columns}, inplace=True)
    
    if{'Country', 'Score'}.issubset(df.columns):
        df['Año'] = int(año)
        datos.append(df)

#Unir todos los DataFrames en uno solo
datos = pd.concat(datos, ignore_index=True)
datos = datos.dropna(subset=['Score'])

@app.route('/', methods=["GET"])
def index():
    año = request.args.get('año', '2019')
    datos_filtrados =  datos[datos['Año'] == int(año)]

    columna_valor = 'Score'
    titulo_leyenda = 'Puntuación de felicidad'

    #Crear mapa base
    m = folium.Map(location=[20, 0], zoom_start=2)

    choropleth = folium.Choropleth(
        geo_data='world-countries.geojson',
        name='choropleth',
        data=datos_filtrados,
        columns=['Country', columna_valor],
        key_on='feature.properties.name',
        fill_color='RdYlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color="lightgray",
        nan_fill_opacity=0.4,
        legend_name=titulo_leyenda
    ).add_to(m)

    #Etiquetas emergentes con nombres del país
    folium.GeoJson(
        'world-countries.geojson',
        name='Labels',
        tooltip = folium.GeoJsonTooltip(
            fields=["name"],
            aliases=["País:"],
            sticky=False
        )
    ).add_to(m)
    
    #Obtener el HTML del mapa
    map_html = m._repr_html_()
    return render_template('index.html', map=map_html, año=año)


if __name__ == '__main__':
    app.run(debug=True)