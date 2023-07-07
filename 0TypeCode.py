from qgis.core import (
    QgsProject, 
    QgsPointXY,
    QgsVectorLayer,
    QgsField,
    QgsGeometry,
    QgsFeature, 
    QgsCoordinateReferenceSystem
)

from qgis.PyQt.QtCore import QVariant
from qgis.utils import iface
import csv

# Specify the path to the CSV file
csv_file_path = "/Users/ismailsa/Downloads/0.AaaaGIS/SabahNew/dataCase/dummyCase1.csv"

# Create a new point vector layer
layer_name = "CSV Points"
crs = QgsCoordinateReferenceSystem("EPSG:4326")  # Assuming WGS84 coordinates

# Read the CSV file and add features to the layer
with open(csv_file_path, "r") as file:
    csv_data = csv.reader(file)
    header = next(csv_data)  # Read and store the header row

    # Create QgsField objects for the additional columns
    additional_fields = [QgsField(header[i], QVariant.String) for i in range(3, len(header))]

  # Create the layer with all necessary fields
    fields = [
        QgsField("ID", QVariant.Int),
        QgsField("X", QVariant.Double),
        QgsField("Y", QVariant.Double),
        QgsField("Gender", QVariant.String),
        QgsField("Year", QVariant.Int),
        QgsField("Week", QVariant.Int),
        QgsField("Child", QVariant.Int),
        QgsField("Income", QVariant.String),
        QgsField("House", QVariant.String),
        QgsField("Education", QVariant.String)
    ] + additional_fields

    layer = QgsVectorLayer("Point?crs={}".format(crs.toWkt()), layer_name, "memory")
    provider = layer.dataProvider()
    provider.addAttributes(fields)
    layer.updateFields()

    for row in csv_data:
        id = int(row[0])
        x, y = float(row[1]), float(row[2])
        gender = row[3]
        year = int(row[4])
        week = int(row[5])
        child = int(row[6])
        income = row[7]
        house = row[8]
        education = row[9]

        point = QgsPointXY(x, y)
        geom = QgsGeometry.fromPointXY(point)
        feature = QgsFeature()
        feature.setGeometry(geom)

        # Extract the additional column values and add them as attributes
        additional_values = [row[i] for i in range(3, len(row))]
        attributes = [id, x, y, gender, year, week, child, income, house, education] + additional_values
        feature.setAttributes(attributes)
        provider.addFeature(feature)

# Add the layer to the map
QgsProject.instance().addMapLayer(layer)

# Specify the path to save the Shapefile
shapefile_path = "/Users/ismailsa/Downloads/0.AaaaGIS/SabahNew/dataCase/dummyCase1.shp"

# Save the layer as a Shapefile
QgsVectorFileWriter.writeAsVectorFormat(layer, shapefile_path, "utf-8", layer.crs(), "ESRI Shapefile")

# Load the saved Shapefile as a vector layer
saved_layer = QgsVectorLayer(shapefile_path, "dummyCase1", "ogr")
if not saved_layer.isValid():
    print("Failed to load the Shapefile.")
else:
    # Add the saved layer to the map
    QgsProject.instance().addMapLayer(saved_layer)

    # Remove the temporary CSV Points layer
    QgsProject.instance().removeMapLayer(layer)
    
# Path to the shapefile
shapefilePoly_path = '/Users/ismailsa/Downloads/0.AaaaGIS/SabahNew/dataCase/sabahDummy.shp'
shapefilePoly_layer_name = 'Shapefile'
shapefilePoly_provider_type = 'ogr'

# Load the shapefile
shapefilePoly_layer = QgsVectorLayer(shapefilePoly_path, shapefilePoly_layer_name, shapefilePoly_provider_type)

# Check if the shapefile layer was loaded successfully
if not shapefilePoly_layer.isValid():
    print("Failed to load the shapefile layer!")
    exit()

# Add the shapefile layer to the QGIS workspace
iface.addVectorLayer(shapefilePoly_path, shapefilePoly_layer_name, shapefilePoly_provider_type)

# Set the active layer in the QGIS GUI to the shapefile layer
iface.setActiveLayer(shapefilePoly_layer)

# Zoom to the extent of the shapefile layer
iface.zoomToActiveLayer()

# Run the "Count Points in Polygon" algorithm
result = processing.run("qgis:countpointsinpolygon", {
    'POLYGONS': shapefilePoly_layer,
    'POINTS': saved_layer,
    'FIELD_PREFIX': 'count_',
    'OUTPUT': '/Users/ismailsa/Downloads/0.AaaaGIS/SabahNew/dataCase/caseFile.shp'
})

# Check if the algorithm ran successfully
if result['OUTPUT']:
    count_layer = QgsVectorLayer(result['OUTPUT'], "caseFile", "ogr")
    if not count_layer.isValid():
        print("Failed to load the count layer.")
    else:
        # Add the count layer to the QGIS workspace
        QgsProject.instance().addMapLayer(count_layer)
else:
    print("Failed to run the 'Count Points in Polygon' algorithm.")
    
    # Remove the 'Shapefile.shp' layer from the QGIS workspace
shapefile_layer = QgsProject.instance().mapLayersByName('Shapefile')
if len(shapefile_layer) > 0:
    QgsProject.instance().removeMapLayer(shapefile_layer[0])
