import mapnik
from BorderGeoJSONWriter import BorderGeoJSONWriter
from BorderFactory import BorderFactory
from histToContour import Contours
from generateTiles import render_tiles
from shutil import rmtree
from addLabelsXml import Labels
import Constants

fullFeatureList = []


# ===== Generate JSON Data ==========
def generatePolygonFile():
    clusterList = BorderFactory.from_file().build().values()
    BorderGeoJSONWriter(clusterList).writeToFile(Constants.FILE_NAME_COUNTRIES)
    global fullFeatureList
    fullFeatureList = clusterList


# ===== Generate Map File =====
def generateCountryPolygonStyle(filename, opacity):
    colorWheel = ["#795548", "#FF5722", "#FFC107", "#CDDC39", "#4CAF50", "#009688", "#00BCD4", "#2196F3", "#3F51B5", "#673AB7"]
    s = mapnik.Style()
    for i in range(len(fullFeatureList)):
        r = mapnik.Rule()
        symbolizer = mapnik.PolygonSymbolizer()
        symbolizer.fill = mapnik.Color(colorWheel[i])
        symbolizer.fill_opacity = opacity
        r.symbols.append(symbolizer)
        r.filter = mapnik.Expression('[clusterNum].match("' + str(i) + '")')
        s.rules.append(r)

    return s


def generateSinglePolygonStyle(filename, opacity, color, gamma=1):
    s = mapnik.Style()
    r = mapnik.Rule()
    symbolizer = mapnik.PolygonSymbolizer()
    symbolizer.fill = mapnik.Color('steelblue')
    symbolizer.fill_opacity = opacity
    symbolizer.gamma = gamma
    r.symbols.append(symbolizer)
    s.rules.append(r)
    return s


def generateLineStyle(color, opacity):
    s = mapnik.Style()
    r = mapnik.Rule()
    symbolizer = mapnik.LineSymbolizer()
    symbolizer.stroke = mapnik.Color(color)
    symbolizer.stroke_opacity = opacity
    r.symbols.append(symbolizer)
    s.rules.append(r)
    return s


def generateLayer(jsonFile, name, styleName):
    ds = mapnik.GeoJSON(file=jsonFile)
    layer = mapnik.Layer(name)
    layer.datasource = ds
    layer.styles.append(styleName)
    return layer


def makeMap():
    m = mapnik.Map(1200, 600)
    m.background = mapnik.Color('white')


# ======== Make Contour Layer =========
    m.append_style("contour", generateSinglePolygonStyle(Constants.FILE_NAME_CONTOUR_DATA, 0, 1))
    m.layers.append(generateLayer(Constants.FILE_NAME_CONTOUR_DATA,
                                  "contour", "contour"))

    m.append_style("outline", generateLineStyle("darkblue", 0))
    m.layers.append(generateLayer(Constants.FILE_NAME_CONTOUR_DATA,
                                  "outline", "outline"))

    m.append_style("countries", generateCountryPolygonStyle(Constants.FILE_NAME_COUNTRIES, 1.0))
    m.layers.append(generateLayer(Constants.FILE_NAME_COUNTRIES, "countries", "countries"))
    m.zoom_all()

    mapnik.save_map(m, Constants.FILE_NAME_MAP)

    label = Labels()
    label.writeLabelsXml('[labels]', 'interior', Constants.FILE_NAME_COUNTRIES)

    mapnik.load_map(m, Constants.FILE_NAME_MAP)


    mapnik.render_to_file(m, Constants.FILE_NAME_IMGNAME + ".png")
    mapnik.render_to_file(m, Constants.FILE_NAME_IMGNAME + ".svg")
    print "rendered image to", Constants.FILE_NAME_IMGNAME

if __name__ == "__main__":
    print "Generating Polygons"
    generatePolygonFile()

    print "Generating Contours"
    contour = Contours(Constants.FILE_NAME_COORDS_AND_CLUSTERS, Constants.FILE_NAME_CONTOUR_DATA)
    contour.makeContourFeatureCollection()

    print "Making Map XML"
    makeMap()

    mapfile = Constants.FILE_NAME_MAP
    tile_dir = Constants.DIRECTORY_NAME_TILES

    bbox = (-180.0, -90.0, 180.0, 90.0)
    rmtree(tile_dir)
    render_tiles(bbox, mapfile, tile_dir, 0, 2, "World")
