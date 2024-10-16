import os
import processing

# System odniesienia EPSG: 4326
QgsProject().instance().setCrs(QgsCoordinateReferenceSystem(4326))

# Aktualne warstwy i usuniecie ich
actual_layer = QgsProject.instance().mapLayers().values()

for lay in actual_layer:
    QgsProject.instance().removeMapLayer(lay)

names = ["track_points", "tracks"]

# Dodanie pliku gpx i zamiana na plik shp
for name in names:
    layer = iface.addVectorLayer(f'GIS_COURSES/szlak-green-velo.gpx|layername={name}', name, "ogr")
    _writer = QgsVectorFileWriter.writeAsVectorFormat(layer, f'GIS_COURSES/{name}.shp', 'UTF-8', driverName='ESRI Shapefile')

# Usuniecie wsyzstkich warstw
actual_layers2 = QgsProject.instance().mapLayers().values()

for lay in actual_layers2:
    QgsProject.instance().removeMapLayer(lay)

# Dodanie warstwa i usuniecie atrybutów
for file in os.listdir('GIS_COURSES'):
    if file.endswith('shp'):
        name_shp_layer = file.split('.')[0]
        if name_shp_layer == 'track_points':
            shp_layer = QgsVectorLayer(f'GIS_COURSES/{file}', name_shp_layer, 'ogr')
            column_names = shp_layer.fields().names()
            index_to_del = list(range(4, len(column_names)))
            
            shp_layer.startEditing()
            shp_prov_to_del = shp_layer.dataProvider()
            shp_prov_to_del.deleteAttributes(index_to_del)
            shp_layer.commitChanges()
        if name_shp_layer == 'tracks':
            shp_layer = iface.addVectorLayer(f'GIS_COURSES/{file}', name_shp_layer, 'ogr')
            column_names = shp_layer.fields().names()
            index_to_del = list(range(0, len(column_names)))
            
            shp_layer.startEditing()
            shp_prov_to_del = shp_layer.dataProvider()
            shp_prov_to_del.deleteAttributes(index_to_del)
            shp_layer.commitChanges()

# Stworzenie zakresu zorientowanego
#processing.run('native:orientedminimumboundingbox', {'INPUT': 'GIS_COURSES/tracks.shp', 'OUTPUT': 'GIS_COURSES/Zakres.shp'})
zakres = QgsVectorLayer('GIS_COURSES/Zakres.shp', 'Zakres', 'ogr')

# Ustawienie koloru
zakres.renderer().symbol().setColor(QColor(QColor("Transparent")))
zakres.triggerRepaint()

# Stworzenie zakresu niezorientowanego
processing.run('qgis:minimumboundinggeometry', {'INPUT': 'GIS_COURSES/tracks.shp', 'TYPE': 0, 'OUTPUT': 'GIS_COURSES/Zakres_envelope.shp'})
zakres_envelope = QgsVectorLayer('GIS_COURSES/Zakres_envelope.shp', 'Zakres Envelope', 'ogr')

# Ustawienie koloru i ramki
props = zakres_envelope.renderer().symbol().symbolLayer(0).properties()
props['outline_color']='255,0,0,255'
props['style']='no'
zakres_envelope.renderer().setSymbol(QgsFillSymbol.createSimple(props))
zakres_envelope.triggerRepaint()

srtm_list = [f'GIS_COURSES/SRTM/{name}' for name in os.listdir('GIS_COURSES/SRTM')]

# Stworzenie skorowidza
processing.run('gdal:tileindex', {'LAYERS': srtm_list, 'OUTPUT': 'GIS_COURSES/Skorowidz.shp'})
skorowidz = QgsVectorLayer('GIS_COURSES/Skorowidz.shp', 'Skorowidz', 'ogr')

# Ustawienia labeli oraz format tekstu
layer_setting = QgsPalLayerSettings()
layer_setting.isExpression = True
layer_setting.fieldName = '''substr("location", 18, 8)'''
layer_setting.enabled = True
layer_setting.multilineAlign = 1

text_format = QgsTextFormat()
text_format.setFont(QFont("Arial Black", 6))
text_format.setSize(6)
layer_setting.setFormat(text_format)

labeling = QgsVectorLayerSimpleLabeling(layer_setting)

skorowidz.setLabelsEnabled(True)
skorowidz.setLabeling(labeling)
skorowidz.triggerRepaint()

# Polaczenie plikow
#processing.run('gdal:merge', {'INPUT': srtm_list, 'DATA_TYPE': 1, 'OUTPUT': 'GIS_COURSES/MergeTif.tif'})
merge_tif = QgsRasterLayer('GIS_COURSES/MergeTif.tif', 'Merge tif')

# Przyciecie plikow
#processing.run("gdal:cliprasterbymasklayer", {'INPUT': 'GIS_COURSES/MergeTif.tif', 'MASK': 'GIS_COURSES/Zakres_envelope.shp', 'OUTPUT': 'GIS_COURSES/ClipTif.tif'})
clip_tif = iface.addRasterLayer('GIS_COURSES/ClipTif.tif', 'Clip tif')

# Ustawienie systepu odniesienia na EPSG: 2180
#QgsProject().instance().setCrs(QgsCoordinateReferenceSystem(2180))




