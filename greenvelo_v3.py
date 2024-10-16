import processing
import mmqgis.mmqgis_library as mmqgis

# Aktualne warstwy i usuniecie ich
actual_layer = QgsProject.instance().mapLayers().values()

for lay in actual_layer:
    QgsProject.instance().removeMapLayer(lay)
    
# Ustawienie systepu odniesienia na EPSG: 2180
QgsProject().instance().setCrs(QgsCoordinateReferenceSystem(2180))

## Zaladowanie danych
#zakres = iface.addVectorLayer('GIS_COURSES/Zakres_envelope92.shp', 'Zakres_envelope92', "ogr")
#
## Zmiana stylu zakresu
#style = zakres.renderer().symbol().symbolLayer(0).properties()
#style['style'] = 'no'
#style['outline_color'] = 'red'
#zakres.renderer().setSymbol(QgsFillSymbol.createSimple(style))
#zakres.triggerRepaint()


# Zmien typ geometrii
#processing.run("native:polygonize", {'INPUT': 'GIS_COURSES/tracks_snapagr_clean92.shp','OUTPUT': 'GIS_COURSES/tracks_polygon.shp'})
tracks_polygon = QgsVectorLayer('GIS_COURSES/tracks_polygon.shp', 'tracks_polygon', 'ogr')

# Dodanie kolumny i policzenie powierzchni
if 'area' not in tracks_polygon.fields().names():
    tracks_polygon.startEditing()
    layer_provider = tracks_polygon.dataProvider()
    layer_provider.addAttributes([QgsField("area", QVariant.Double)])
    
    tracks_polygon.updateFields()
    
    expression = QgsExpression('area($geometry)')
    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(tracks_polygon))
    
    for f in tracks_polygon.getFeatures():
        context.setFeature(f)
        f['area'] = expression.evaluate(context)
        tracks_polygon.updateFeature(f)
    
    tracks_polygon.commitChanges()

# Zaznaczenie pol o okreslonym polu
tracks_polygon.selectByExpression('"area" < 100000000')

# Usuniecie zaznaczonych obiektow
#processing.run("qgis:eliminateselectedpolygons", {'INPUT': 'GIS_COURSES/tracks_polygon.shp', 'MODE': 0, 'OUTPUT': 'GIS_COURSES/tracks_polygon_eliminate.shp'})
tracks_polygon_eliminate = QgsVectorLayer('GIS_COURSES/tracks_polygon_eliminate.shp', 'tracks_polygon_eliminate', 'ogr')

# Usuniece zaznaczenia
tracks_polygon.removeSelection()

# Zaznaczenie pol o okreslonym polu
tracks_polygon_eliminate.selectByExpression('"area" > 100000000')

# Zapisanie tylko zaznaczonych pol
#writer = QgsVectorFileWriter.writeAsVectorFormat(tracks_polygon_eliminate, 'GIS_COURSES/tracks_polygon_final.shp', 'utf-8', driverName='ESRI Shapefile', onlySelected=True)
tracks_polygon_final = QgsVectorLayer('GIS_COURSES/tracks_polygon_final.shp', 'tracks_polygon_final', 'ogr')

# Usuniece zaznaczenia
tracks_polygon_eliminate.removeSelection()

# Zmiana typu geometrii
#processing.run("qgis:convertgeometrytype", {'INPUT': tracks_polygon_final, 'TYPE': 2, 'OUTPUT': 'GIS_COURSES/tracks_linestring.shp'})
tracks_linestring = QgsVectorLayer('GIS_COURSES/tracks_linestring.shp', 'tracks_linestring', 'ogr')

# Dodanie warstwy
tracks_snapagr_single = QgsVectorLayer('GIS_COURSES/tracks_snapagr_single92.shp', 'tracks_snapagr_single', 'ogr')

# Zaznaczenie przez lokalizacje
processing.run("qgis:selectbylocation", {'INPUT': tracks_snapagr_single, 'PREDICATE': 6, 'INTERSECT': tracks_linestring})

# Zapisanie tylko zaznaczonych pol
#writer_tracks_final = QgsVectorFileWriter.writeAsVectorFormat(tracks_snapagr_single , 'GIS_COURSES/tracks_final.shp', 'utf-8', driverName='ESRI Shapefile', onlySelected=True)
tracks_final = QgsVectorLayer('GIS_COURSES/tracks_final.shp', 'tracks_final', 'ogr')

# Usuniece zaznaczenia
tracks_snapagr_single.removeSelection()

# Agregacja linii
#processing.run("native:dissolve", {'INPUT': tracks_final, 'OUTPUT': 'GIS_COURSES/tracks_final_agr.shp'})
tracks_final_agr = QgsVectorLayer('GIS_COURSES/tracks_final_agr.shp', 'tracks_final_agr', 'ogr')

# Zamiana z multiline na singleline
processing.run("native:multiparttosingleparts", {'INPUT': tracks_final_agr, 'OUTPUT': 'GIS_COURSES/tracks_final_single.shp'})
tracks_final_single = QgsVectorLayer('GIS_COURSES/tracks_final_single.shp', 'tracks_final_single', 'ogr')

# Dodanie kolumny i policzenie dlugosci
if 'length' not in tracks_final_single.fields().names():
    tracks_final_single.startEditing()
    layer_provider = tracks_final_single.dataProvider()
    layer_provider.addAttributes([QgsField('length', QVariant.Double)])
    
    tracks_final_single.updateFields()
    
    expression = QgsExpression('$length')
    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(tracks_final_single))
    
    for f in tracks_final_single.getFeatures():
        context.setFeature(f)
        f['length'] = expression.evaluate(context)
        tracks_final_single.updateFeature(f)
    
    tracks_final_single.commitChanges()

# Lista dlugosci tras
tracks_final_length = []
for fe in tracks_final_single.getFeatures():
    tracks_final_length.append(fe['length'])
    
# Zaznaczenie pol o okreslonym polu
sorted_length = sorted(tracks_final_length)
tracks_final_single.selectByExpression(f'"length" != {sorted_length[0]}')

# Zapisanie tylko zaznaczonych pol
#writer_tracks_final_short = QgsVectorFileWriter.writeAsVectorFormat(tracks_final_single , 'GIS_COURSES/tracks_final_short.shp', 'utf-8', driverName='ESRI Shapefile', onlySelected=True)
tracks_final_short = QgsVectorLayer('GIS_COURSES/tracks_final_short.shp', 'tracks_final_short', 'ogr')

# Usuniece zaznaczenia
tracks_final_single.removeSelection()

# Agregacja linii
#processing.run("native:dissolve", {'INPUT': tracks_final_short, 'OUTPUT': 'GIS_COURSES/tracks_final_short_agr.shp'})
tracks_final_short_agr = QgsVectorLayer('GIS_COURSES/tracks_final_short_agr.shp', 'tracks_final_short_agr', 'ogr')

# Zamiana z multiline na singleline
#processing.run("native:multiparttosingleparts", {'INPUT': tracks_final_short_agr, 'OUTPUT': 'GIS_COURSES/tracks_final_short_agr_single.shp'})
tracks_final_short_agr_single = iface.addVectorLayer('GIS_COURSES/tracks_final_short_agr_single.shp', 'tracks_final_short_agr_single', 'ogr')

# Dodanie warstwy tekstowej z csv
uri = 'file:GIS_COURSES/ZESTAWIENIE_PH_7Tf4hrW.csv?delimiter=;&crs=epsg:4326&xField=E&yField=N'
pomniki_historii =  QgsVectorLayer(uri, 'pomniki historii', 'delimitedtext')

# Zapisanie warstwy csv
#writer_pomniki_historii = QgsVectorFileWriter.writeAsVectorFormat(pomniki_historii, 'GIS_COURSES/pomniki_historii.shp', 'utf-8', driverName='ESRI Shapefile', destCRS=QgsCoordinateReferenceSystem(2180))
pomniki_historii_warstwa = QgsVectorLayer('GIS_COURSES/pomniki_historii.shp', 'pomniki_historii', 'ogr')

# Usuniecie niepotrzebnych atrybutow
column_names_pomniki_historii = pomniki_historii_warstwa.fields().names()
column_names_pomniki_historii_to_save = ['INSPIRE_ID', 'NAZWA', 'RODZAJ_POM']
index = 0
for names in column_names_pomniki_historii:
    if names not in column_names_pomniki_historii_to_save:
        pomniki_historii_warstwa.startEditing()
        layer_prov_to_del = pomniki_historii_warstwa.dataProvider()
        layer_prov_to_del.deleteAttributes([index])
        pomniki_historii_warstwa.commitChanges()
    else:
        index +=1

#processing.run("native:buffer", {'INPUT': tracks_final_short_agr_single, 'DISTANCE': 20000, 'END_CAP_STYLE': 1, 'OUTPUT': 'GIS_COURSES/tracks_final_short_buffor.shp'})
tracks_final_short_buffor = QgsVectorLayer('GIS_COURSES/tracks_final_short_buffor.shp', 'tracks_final_short_buffor', 'ogr')

#processing.run("qgis:extractbylocation", {'INPUT': pomniki_historii_warstwa, 'PREDICATE': 0, 'INTERSECT': tracks_final_short_buffor, 'OUTPUT': 'GIS_COURSES/tracks_monuments.shp'})
tracks_monuments = QgsVectorLayer('GIS_COURSES/tracks_monuments.shp', 'tracks_monuments', 'ogr')

# Dodanie kolumny i dodanie wartosci id
if 'numer' not in tracks_monuments.fields().names():
    tracks_monuments.startEditing()
    layer_provider = tracks_monuments.dataProvider()
    layer_provider.addAttributes([QgsField('numer', QVariant.Int)])
    
    tracks_monuments.updateFields()
    
    expression = QgsExpression('$id+1')
    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(tracks_monuments))
    
    for f in tracks_monuments.getFeatures():
        context.setFeature(f)
        f['numer'] = expression.evaluate(context)
        tracks_monuments.updateFeature(f)
    
    tracks_monuments.commitChanges()
    
# Polaczenie geometrii do warstwy
#processing.run("native:snapgeometries", {'INPUT': tracks_monuments, 'REFERENCE_LAYER': tracks_final_short_agr_single, 'TOLERANCE': 20000, 'BEHAVIOR': 3, 'OUTPUT': 'GIS_COURSES/tracks_monuments_snap.shp'})
tracks_monuments_snap = iface.addVectorLayer('GIS_COURSES/tracks_monuments_snap.shp', 'tracks_monuments_snap', 'ogr')

## Suma dwoch warstw
#processing.run("qgis:union", {'INPUT': tracks_monuments, 'OVERLAY': tracks_monuments_snap, 'OUTPUT': 'GIS_COURSES/tracks_monuments_union.shp'})
#tracks_monuments_union = iface.addVectorLayer('GIS_COURSES/tracks_monuments_union.shp', 'tracks_monuments_union', 'ogr')

## Edycja wartosci tabeli numer
#tracks_monuments_union.startEditing()
#expression = QgsExpression('if("numer" > 0, "numer", "numer_2")')
#context = QgsExpressionContext()
#scope = QgsExpressionContextScope()
#scope.setFields(tracks_monuments_union.fields())
#context.appendScope(scope)
#expression.prepare(context)
#    
#for f in tracks_monuments_union.getFeatures():
#    context.setFeature(f)
#    value = expression.evaluate(context)
#    atts = {3: value}
#    tracks_monuments_union.changeAttributeValues(f.id(), atts)
#    
#tracks_monuments_union.commitChanges()

mmqgis.mmqgis_merge([tracks_monuments, tracks_monuments_snap], 'GIS_COURSES/tracks_monuments_merge.shp', status_callback=None)
tracks_monuments_merge = QgsVectorLayer('GIS_COURSES/tracks_monuments_merge.shp', 'tracks_monuments_merge', 'ogr')

# Linie miedzy punktami
pomniki_linie = QgsVectorLayer('GIS_COURSES/pomniki_linie.shp', 'pomniki_linie', 'ogr')

# Dodanie kolumny i policzenie dlugosci
if 'length' not in pomniki_linie.fields().names():
    pomniki_linie.startEditing()
    layer_provider = pomniki_linie.dataProvider()
    layer_provider.addAttributes([QgsField('length', QVariant.Double())])
    
    pomniki_linie.updateFields()
    
    expression = QgsExpression('$length')
    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(pomniki_linie))
    
    for f in pomniki_linie.getFeatures():
        context.setFeature(f)
        f['length'] = expression.evaluate(context)
        pomniki_linie.updateFeature(f)
    
    pomniki_linie.commitChanges()


#processing.run("native:joinattributestable", {'INPUT': tracks_monuments, 'FIELD': 'numer', 'INPUT_2': pomniki_linie, 'FIELD_2': 'numer', 'OUTPUT': 'GIS_COURSES/pomniki_length.shp'})
pomniki_length = QgsVectorLayer('GIS_COURSES/pomniki_length.shp', 'pomniki_length', 'ogr')

processing.run("native:interpolatepoint", {'INPUT': tracks_final_short_agr_single, 'OUTPUT': 'GIS_COURSES/tracks_beginning.shp'})
tracks_beginning = iface.addVectorLayer('GIS_COURSES/tracks_beginning.shp', 'tracks_beginning', 'ogr')




























    
