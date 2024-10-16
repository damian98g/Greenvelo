import processing

# Aktualne warstwy i usuniecie ich
actual_layer = QgsProject.instance().mapLayers().values()

for lay in actual_layer:
    QgsProject.instance().removeMapLayer(lay)
    
# Ustawienie systepu odniesienia na EPSG: 2180
QgsProject().instance().setCrs(QgsCoordinateReferenceSystem(2180))

# Zaladowanie danych
track = QgsVectorLayer('GIS_COURSES/tracks92.shp', 'tracks92', "ogr")
zakres = iface.addVectorLayer('GIS_COURSES/Zakres_envelope92.shp', 'Zakres_envelope92', "ogr")

# Zmiana stylu zakresu
style = zakres.renderer().symbol().symbolLayer(0).properties()
style['style'] = 'no'
style['outline_color'] = 'red'
zakres.renderer().setSymbol(QgsFillSymbol.createSimple(style))
zakres.triggerRepaint()

# Zmiana systemu odniesienia 
#processing.run("gdal:warpreproject", {'INPUT': 'GIS_COURSES/MergeTif.tif', 'SOURCE_CRS': 'EPSG:4326', 'TARGET_CRS': 'EPSG:2180', 'OUTPUT': 'GIS_COURSES/MergeTif92.tif'})

# Stworzenie zakresu niezorientowanego
processing.run('qgis:minimumboundinggeometry', {'INPUT': 'GIS_COURSES/tracks92.shp', 'TYPE': 0, 'OUTPUT': 'GIS_COURSES/Zakres_envelope92.shp'})

# Przyciecie plikow
#processing.run("gdal:cliprasterbymasklayer", {'INPUT': 'GIS_COURSES/MergeTif92.tif', 'MASK': 'GIS_COURSES/Zakres_envelope92.shp', 'OUTPUT': 'GIS_COURSES/ClipTif92.tif'})
clip_tif = QgsVectorLayer('GIS_COURSES/ClipTif92.tif', 'Clip tif92')

# Cieniowanie 
#processing.run("gdal:hillshade", {'INPUT': 'GIS_COURSES/ClipTif92.tif', 'BAND': 1, 'Z_FACTOR': 5, 'OUTPUT': 'GIS_COURSES/hillshade.tif'})
hill_tif = QgsVectorLayer('GIS_COURSES/hillshade.tif', 'Cieniowanie')

## Ustawianie przezroczystosci dla cieniowania
#hill_tif.renderer().setOpacity(0.4)
#hill_tif.triggerRepaint()

# Ustawianie koloru mapy rastowej
#stats = clip_tif.dataProvider().bandStatistics(1, QgsRasterBandStats.All)
#
#min = stats.minimumValue
#max = stats.maximumValue
#
#fnc = QgsColorRampShader()
#fnc.setColorRampType(QgsColorRampShader.Interpolated)
#
#lst = [QgsColorRampShader.ColorRampItem(min, QColor('#1a9641')), QgsColorRampShader.ColorRampItem((max-min)/2, QColor('#ffffc0')), QgsColorRampShader.ColorRampItem(max, QColor('#a05204'))]
#fnc.setColorRampItemList(lst)
#
#shader = QgsRasterShader()
#shader.setRasterShaderFunction(fnc)
#
#renderer = QgsSingleBandPseudoColorRenderer(clip_tif.dataProvider(), 1, shader)
#clip_tif.setRenderer(renderer)

# Zamiana z multiline na singleline
#processing.run("native:multiparttosingleparts", {'INPUT': 'GIS_COURSES/tracks92.shp', 'OUTPUT': 'GIS_COURSES/tracks_singleparts92.shp'})
tracks_singleparts92 = QgsVectorLayer('GIS_COURSES/tracks_singleparts92.shp', 'tracks_singleparts92', 'ogr')

# Agregacja linii
#processing.run("native:dissolve", {'INPUT': 'GIS_COURSES/tracks_singleparts92.shp', 'OUTPUT': 'GIS_COURSES/tracks_singleparts_agregate92.shp'})
tracks_singleparts_agregate92 = QgsVectorLayer('GIS_COURSES/tracks_singleparts_agregate92.shp', 'tracks_singleparts_agregate92', 'ogr')

# Zamiana z multiline na singleline
#processing.run("native:multiparttosingleparts", {'INPUT': 'GIS_COURSES/tracks_singleparts_agregate92.shp', 'OUTPUT': 'GIS_COURSES/tracks_singleparts2_92.shp'})
tracks_singleparts2_92 = QgsVectorLayer('GIS_COURSES/tracks_singleparts2_92.shp', 'tracks_singleparts2_92', 'ogr')

# Zmiana stylu linii
style_track = tracks_singleparts2_92.renderer().symbol().symbolLayer(0).properties()
style_track['line_width'] = 0.4
tracks_singleparts2_92.renderer().setSymbol(QgsLineSymbol.createSimple(style_track))
tracks_singleparts2_92.triggerRepaint()

# Polaczenie geometrii do warstwy
#processing.run("native:snapgeometries", {'INPUT': 'GIS_COURSES/tracks_singleparts2_92.shp', 'REFERENCE_LAYER': 'GIS_COURSES/tracks_singleparts2_92.shp', 'TOLERANCE': 20, 'BEHAVIOR': 0, 'OUTPUT': 'GIS_COURSES/tracks_snap92.shp'})
tracks_snap92 = QgsVectorLayer('GIS_COURSES/tracks_snap92.shp', 'tracks_snap92', 'ogr')

# Naprawa geometrii
#processing.run("native:fixgeometries", {'INPUT': 'GIS_COURSES/tracks_snap92.shp', 'OUTPUT': 'GIS_COURSES/tracks_snap_fix92.shp'})

# Agregacja linii
#processing.run("native:dissolve", {'INPUT': 'GIS_COURSES/tracks_snap_fix92.shp', 'OUTPUT': 'GIS_COURSES/tracks_snapagr92.shp'})
tracks_snapagr92 = QgsVectorLayer('GIS_COURSES/tracks_snapagr92.shp', 'tracks_snapagr92', 'ogr')

# Zamiana z multiline na singleline
#processing.run("native:multiparttosingleparts", {'INPUT': 'GIS_COURSES/tracks_snapagr92.shp', 'OUTPUT': 'GIS_COURSES/tracks_snapagr_single92.shp'})
tracks_singleparts2_92 = QgsVectorLayer('GIS_COURSES/tracks_snapagr_single92.shp', 'tracks_snapagr_single92', 'ogr')

# Laczenie linii za pomoca grass v.clean
#processing.run('grass7:v.clean', {'input': 'GIS_COURSES/tracks_snapagr92.shp','output': 'GIS_COURSES/tracks_snapagr_clean92.shp', 'tool': 0, 'error': 'GIS_COURSES/clean_error.shp'})
tracks_snapagr_clean92 = iface.addVectorLayer('GIS_COURSES/tracks_snapagr_clean92.shp', 'tracks_snapagr_clean92', 'ogr')

# Ustawianie snappingu
snap_config = QgsSnappingConfig()
snap_config.setEnabled(True)
snap_config.setType(QgsSnappingConfig.Vertex)
snap_config.setUnits(QgsTolerance.Pixels)
snap_config.setTolerance(12)
snap_config.setIntersectionSnapping(True)
snap_config.setMode(QgsSnappingConfig.SnappingMode.AdvancedConfiguration)
lyr_settings = QgsSnappingConfig.IndividualLayerSettings(True, QgsSnappingConfig.SnappingType.Vertex, 12, QgsTolerance.Pixels)
snap_config.setIndividualLayerSettings(tracks_snapagr_clean92, lyr_settings)
QgsProject.instance().setSnappingConfig(snap_config)

## Dodanie jednej kolumny do danych
column_names = tracks_snapagr_clean92.fields().names()

if 'Nr' not in column_names:
    tracks_snapagr_clean92.startEditing()
    layer_provider = tracks_snapagr_clean92.dataProvider()
    layer_provider.addAttributes([QgsField("Nr", QVariant.Int)])

    features = tracks_snapagr_clean92.getFeatures()
    nr = 0
    for f in features:
        id = f.id()
        nr = nr+1
        attr_value = {2: nr}
        layer_provider.changeAttributeValues({id:attr_value})
        

    tracks_snapagr_clean92.commitChanges()




