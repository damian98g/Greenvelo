import processing

# Aktualne warstwy i usuniecie ich
actual_layer = QgsProject.instance().mapLayers().values()

for lay in actual_layer:
    QgsProject.instance().removeMapLayer(lay)
    
# Ustawienie systepu odniesienia na EPSG: 2180
QgsProject().instance().setCrs(QgsCoordinateReferenceSystem(2180))

# Zaladowanie danych
tracks_final_short_agr_single = iface.addVectorLayer('GIS_COURSES/tracks_final_short_agr_single.shp', 'tracks_final_short_agr_single', 'ogr')
tracks_monuments_snap = iface.addVectorLayer('GIS_COURSES/tracks_monuments_snap.shp', 'tracks_monuments_snap', 'ogr')
tracks_beginning = iface.addVectorLayer('GIS_COURSES/tracks_beginning.shp', 'tracks_beginning', 'ogr')

#processing.run("native:buffer", {'INPUT': tracks_monuments_snap, 'DISTANCE': 1, 'END_CAP_STYLE': 0, 'OUTPUT': 'GIS_COURSES/tracks_monuments_snap_buffor.shp'})
tracks_monuments_snap_buffor = QgsVectorLayer('GIS_COURSES/tracks_monuments_snap_buffor.shp', 'tracks_monuments_snap_buffor', 'ogr')

#processing.run("qgis:difference", {'INPUT': tracks_final_short_agr_single, 'OVERLAY': tracks_monuments_snap_buffor, 'OUTPUT': 'GIS_COURSES/tracks_monuments_difference.shp'})
tracks_monuments_difference = QgsVectorLayer('GIS_COURSES/tracks_monuments_difference.shp', 'tracks_monuments_difference', 'ogr')

# Zamiana z multiline na singleline
#processing.run("native:multiparttosingleparts", {'INPUT': tracks_monuments_difference, 'OUTPUT': 'GIS_COURSES/tracks_monuments_difference_single.shp'})
tracks_monuments_difference_single = QgsVectorLayer('GIS_COURSES/tracks_monuments_difference_single.shp', 'tracks_monuments_difference_single', 'ogr')

# Dodanie kolumny i policzenie dlugosci
if 'track_len' not in tracks_monuments_difference_single.fields().names():
    sum_dist = 0
    it = 1
    tracks_monuments_difference_single.startEditing()
    layer_provider = tracks_monuments_difference_single.dataProvider()
    layer_provider.addAttributes([QgsField('track_len', QVariant.Double)])
    
    tracks_monuments_difference_single.updateFields()
    
    expression = QgsExpression('$length')
    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(pomniki_linie))
    
    for f in tracks_monuments_difference_single.getFeatures():
        context.setFeature(f)
        if it == 1 or it == len(list(tracks_monuments_difference_single.getFeatures())):
            sum_dist = sum_dist + expression.evaluate(context) + 1
        else:
            sum_dist = sum_dist + expression.evaluate(context) + 2
        it+=1
        f['track_len'] = sum_dist
        tracks_monuments_difference_single.updateFeature(f)
    
    tracks_monuments_difference_single.commitChanges()



















