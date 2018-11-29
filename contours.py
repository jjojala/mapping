#!/usr/bin/env python

# Copyright (C) 2018 Jari Ojala (jari.ojala@iki.fi)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import sys
from osgeo import ogr

def get_driver_from_extension(filename):
	"""Return name of the OGR -driver based on file extension.
	
	:param filename: pathname of file being examined
	:type filename: str
	:returns: None, if no corresponding GDAL driver found, or the name of the driver.
	:rtype: str
	"""
	
    ext = os.path.splitext(filename)[-1].upper()
    if ext == 'SHP':
        return 'ESRI Shapefile'
    elif ext == 'GML':
        return 'GML'
    elif ext in ('JSON', "GEOJSON'):
        return 'GeoJSON'
    return None

def info(argv):
	"""Print summary and elevation distribution of the contours.
	
	:param argv: array of arguments so that argv[0] is expected to contain the filename
	             of the contour -file.
	:returns: 0 if things went smoothly, something else othervise
	:rtype:	int
	"""

	if len(argv) != 1:
		help()
		return 1

	distrib = get_contour_distrib(argv[0])
	keys = distrib.keys()
	keys.sort()
	max = keys[-1]
	min = keys[0]

	print "Elevation range: %0.2f - %0.2fm:\n" % (min, max)
	print "\tElevation | count "
	print "\t-----------------------"

	for k in keys:
		print "\t%5.2fm   | %4d" % (k, distrib[k])
		 
	return 0

def classify_contour(elev, contour_interval):
	"""Classify a contour by elevation.
	
	:param elev: elevation level
	:type elev: float
	:param contour_interval: contour interval to be used (usually 2.5 or 5.0)
	:type contour_interval: float
	:returns: Type of the contour
	:rtype: str
	"""

	if elev % (contour_interval * 5.0) == 0:
		return 'INDEX'
	elif elev % contour_interval == 0:
		return 'CONTOUR'
	elif contour_interval >= 5 and elev % (contour_interval / 2.0) == 0:
		return 'FORMLINE'
		
	return 'UTIL'

def get_contour_distrib(filename):
	"""Get dictionary of contour distribution in terms of elevation.
	
	:param filename: Filename of contours -file.
	:type filename: str
	:returns: dictionary of contour distribution so that key contains the elevation,
	          and the value contains the number of gemetry occurrences at the given elevation.
	:rtype: dict
	"""

	driver = ogr.GetDriverByName(get_driver_from_extension(filename))
	ds = driver.Open(filename, 0)
	layer = ds.GetLayer()

	distrib = {}
	for feature in layer:
		geometry = feature.GetGeometryRef()	
		z = geometry.GetZ()
		
		if z in distrib:
			count = distrib[z]
			distrib[z] = count + 1
		else:
			distrib[z] = 1

	layer = None
	ds = None
	driver = None

	return distrib

def define_index_elev(distrib, contour_interval):
	"""Define highest index contour elevation based on contour distribution.
	
	:param distrib: dictionary of contour distribution so, that key (float) is the
			elevation and the value (int) is the number of geometries in the
			particular elevation (as returned by get_contour_distrib())
	:type distrib:	dict
	:param contour_interval: contour interval (e.g. 2.5 or 5.0)
	:type contour_interval: float
	:returns: elevation of highest index contour
	:rtype: float
	"""

	keys = distrib.keys()
	keys.sort()
	
	min = keys[0]
	max = keys[-1]
	return max - (((max - min) % (contour_interval * 5)) / 2)

def tag(argv):
	"""Create new contour -file while tagging it with contour elevation ('ELEVATION') and
	   contour class ('CLASS') -attributes.

	:param argv: array of arguments so that:
		argv[0] is expected to contain 'auto' or elevation of highest index contour (float)
		argv[1] is expected to contain contour interval (usually 2.5 or 5.0)
		argv[2] is expected to contain source contour -filename
		argv[3] is expected to contain destination contour -filename
	:type argv: array
	:returns: 0 if things went smoothly or othervise something else
	:rtype:	int
	"""
	
	if len(argv) != 4:
		help()
		return 1
	
	contourInterval = float(argv[1])
	srcFileName = argv[2]
	dstFileName = argv[3]
	
	if argv[0] == 'auto':
		indexElev = define_index_elev(get_contour_distrib(srcFileName), contourInterval)
	else:
		indexElev = float(argv[0])

	srcDriver = ogr.GetDriverByName(get_driver_from_extension(srcFileName))
	srcDs = srcDriver.Open(srcFileName, 0)
	srcLayer = srcDs.GetLayer()

	if os.path.exists(dstFileName):
		dstDriver.DeleteDataSource(dstFileName)

	dstDriver = ogr.GetDriverByName(get_driver_from_extension(dstFileName))
	dstDs = dstDriver.CreateDataSource(dstFileName)
	geometryType = srcLayer.GetGeomType()
	dstLayer = dstDs.CreateLayer(srcLayer.GetName(), geom_type=geometryType)

	srcLayerDefn = srcLayer.GetLayerDefn()
	for i in range(0, srcLayerDefn.GetFieldCount()):
		srcFieldDfn = srcLayerDefn.GetFieldDefn(i)
		dstLayer.CreateField(srcFieldDefn)

	zFieldDefn = ogr.FieldDefn("ELEVATION", ogr.OFTReal)
	classFieldDefn = ogr.FieldDefn("CLASS", ogr.OFTString)
	dstLayer.CreateField(zFieldDefn)
	dstLayer.CreateField(classFieldDefn)

	dstLayerDefn = dstLayer.GetLayerDefn()

	for srcFeature in srcLayer:
		srcPolyline = srcFeature.GetGeometryRef().Clone()	
		dstFeature = ogr.Feature(dstLayerDefn)
	
		dstFeature.SetGeometry(srcPolyline)
		for i in range(0, srcLayerDefn.GetFieldCount()):
			fieldDefn = srcLayerDefn.GetFieldDefn(i)
			dstFeature.SetField(fieldDefn.GetNameRef(),
				srcFeature.GetField(i).Clone())
		
		z = srcPolyline.GetZ()
		dstFeature.SetField(zFieldDefn.GetNameRef(), z)
		dstFeature.SetField(classFieldDefn.GetNameRef(), classify_contour(z-indexElev, contourInterval))

		dstLayer.CreateFeature(dstFeature)
	
	dstLayer = None
	srcLayer = None
	dstDs = None
	srcDs = None
	dstDriver = None
	srcDriver = None

	return 0

def help():
	"""Print usage. """
	app = sys.argv[0]
	print "Usage: %s -help" % app
	print "       %s -info <shp-file>" % app
	print "       %s -tag <indexElev> <contourInterval> <shp-sourcefile> <gml-target-file>" % app
	print "       %s -tag auto <contourInterval> <shp-sourcefile> <gml-target-file>" % app
	
def main():
	"""Main app. See help() for usage."""

	if len(sys.argv) > 1:
		if sys.argv[1] == '-info':
			sys.exit(info(sys.argv[2:]))
		elif sys.argv[1] == '-tag':
			sys.exit(tag(sys.argv[2:]))
	else:
		help()

	sys.exit(1)
	
if __name__ == "__main__":
	main()
