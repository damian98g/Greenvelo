import processing
import mmqgis.mmqgis_library as mmqgis
import os

# Aktualne warstwy i usuniecie ich
actual_layer = QgsProject.instance().mapLayers().values()

for lay in actual_layer:
    QgsProject.instance().removeMapLayer(lay)
    
# Ustawienie systepu odniesienia na EPSG: 2180
QgsProject().instance().setCrs(QgsCoordinateReferenceSystem(2180))

files_to_merge = []
for file in os.listdir('GIS_COURSES/'):
    if file.startswith('model_wyniki') and file.endswith('shp'):
        files_to_merge.append(QgsVectorLayer(f'GIS_COURSES/{file}'))

# Polaczenie warstw
#mmqgis.mmqgis_merge(files_to_merge, 'GIS_COURSES/model_wyniki_merge.shp', status_callback=None)
model_wyniki_merge = QgsVectorLayer('GIS_COURSES/model_wyniki_merge.shp', 'model_wyniki_merge', 'ogr')

tracks_final_short_agr_single = QgsVectorLayer('GIS_COURSES/tracks_final_short_agr_single.shp', 'tracks_final_short_agr_single', 'ogr')

## Ustaiwenia labeli
#layer_settings  = QgsPalLayerSettings()
#text_format = QgsTextFormat()
#
#text_format.setFont(QFont("Arial", 8))
#text_format.setSize(8)
#
#text_format.setBuffer(buffer_settings)
#layer_settings.setFormat(text_format)
#
#layer_settings.fieldName = "dlugosc"
#
#
#layer_settings.enabled = True
#
#layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
#model_wyniki_merge.setLabelsEnabled(True)
#model_wyniki_merge.setLabeling(layer_settings)
#model_wyniki_merge.triggerRepaint()

# Unterpolacja punktu co 100 km
#processing.run("native:pointsalonglines", {'INPUT': tracks_final_short_agr_single, 'DISTANCE': 100000, 'START_OFFSET': 100000, 'OUTPUT': 'GIS_COURSES/tracks_interpolate.shp'})
tracks_interpolate = iface.addVectorLayer('GIS_COURSES/tracks_interpolate.shp', 'tracks_interpolate', 'ogr')

# Narysowanie buforu
#processing.run("native:buffer", {'INPUT': tracks_interpolate, 'DISTANCE': 1, 'END_CAP_STYLE': 0, 'OUTPUT': 'GIS_COURSES/tracks_interpolate_bufor.shp'})
tracks_interpolate_bufor = QgsVectorLayer('GIS_COURSES/tracks_interpolate_bufor.shp', 'tracks_interpolate_bufor', 'ogr')

# Obliczenie roznucy
#processing.run("qgis:difference", {'INPUT': tracks_final_short_agr_single, 'OVERLAY': tracks_interpolate_bufor, 'OUTPUT': 'GIS_COURSES/tracks_interpolate_diff.shp'})
tracks_interpolate_diff = QgsVectorLayer('GIS_COURSES/tracks_interpolate_diff.shp', 'tracks_interpolate_diff', 'ogr')

# Zamiana z multiline na singleline
#processing.run("native:multiparttosingleparts", {'INPUT': tracks_interpolate_diff, 'OUTPUT': 'GIS_COURSES/tracks_interpolate_single.shp'})
tracks_interpolate_single = QgsVectorLayer('GIS_COURSES/tracks_interpolate_single.shp', 'tracks_interpolate_single', 'ogr')

# Polaczenie geometrii do warstwy
#processing.run("native:snapgeometries", {'INPUT': tracks_interpolate_single, 'REFERENCE_LAYER': tracks_interpolate, 'TOLERANCE': 1, 'BEHAVIOR': 3, 'OUTPUT': 'GIS_COURSES/tracks_interpolate_single_snap.shp'})
tracks_interpolate_single_snap = iface.addVectorLayer('GIS_COURSES/tracks_interpolate_single_snap.shp', 'tracks_interpolate_single_snap', 'ogr')

# Dodanie kolumny i policzenie id
if 'id' not in tracks_interpolate_single_snap.fields().names():
    tracks_interpolate_single_snap.startEditing()
    layer_provider = tracks_interpolate_single_snap.dataProvider()
    layer_provider.addAttributes([QgsField('id', QVariant.Int)])
    
    tracks_interpolate_single_snap.updateFields()
    
    expression = QgsExpression('$id')
    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(tracks_interpolate_single_snap))
    
    for f in tracks_interpolate_single_snap.getFeatures():
        context.setFeature(f)
        f['id'] = expression.evaluate(context)+1
        tracks_interpolate_single_snap.updateFeature(f)
    
    tracks_interpolate_single_snap.commitChanges()
    
# Dodanie kolumny i policzenie id
if 'id' not in tracks_interpolate.fields().names():
    tracks_interpolate.startEditing()
    layer_provider = tracks_interpolate.dataProvider()
    layer_provider.addAttributes([QgsField('id', QVariant.Int)])
    
    tracks_interpolate.updateFields()
    
    expression = QgsExpression('$id')
    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(tracks_interpolate))
    
    for f in tracks_interpolate.getFeatures():
        context.setFeature(f)
        f['id'] = expression.evaluate(context)+1
        tracks_interpolate.updateFeature(f)
    
    tracks_interpolate.commitChanges()


# Dodanie kolumny i policzenie id
if 'dzien' not in tracks_interpolate_single_snap.fields().names():
    tracks_interpolate_single_snap.startEditing()
    layer_provider = tracks_interpolate_single_snap.dataProvider()
    layer_provider.addAttributes([QgsField('dzien', QVariant.String)])
    
    tracks_interpolate_single_snap.updateFields()
    
    expression = QgsExpression('''concat('dzien ', $id+1)''')
    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(tracks_interpolate_single_snap))
    
    for f in tracks_interpolate_single_snap.getFeatures():
        context.setFeature(f)
        f['dzien'] = expression.evaluate(context)
        tracks_interpolate_single_snap.updateFeature(f)
    
    tracks_interpolate_single_snap.commitChanges()


# Ustawienia labeli oraz format tekstu
layer_settingg = QgsPalLayerSettings()
layer_settingg.isExpression = True
layer_settingg.fieldName = "dzien"
layer_settingg.enabled = True

text_formatt = QgsTextFormat()
text_formatt.setFont(QFont("Arial Black", 12))
text_formatt.setSize(12)
layer_settingg.setFormat(text_format)

labelingg = QgsVectorLayerSimpleLabeling(layer_settingg)

tracks_interpolate_single_snap.setLabelsEnabled(True)
tracks_interpolate_single_snap.setLabeling(labelingg)
tracks_interpolate_single_snap.triggerRepaint()
























