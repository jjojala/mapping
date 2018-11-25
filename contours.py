#!/usr/bin/env python

import os
import sys
from osgeo import ogr

def info(argv):
	if len(argv) != 1:
		help()
		return
		
	srcFileName = argv[0]
	srcDriver = ogr.GetDriverByName("ESRI Shapefile")
	srcDs = srcDriver.Open(srcFileName, 0)
	srcLayer = srcDs.GetLayer()

	max = -10000.0
	min = 10000.0
	elevDistrib = {}
	for srcFeature in srcLayer:
		srcPolyline = srcFeature.GetGeometryRef()	
		z = srcPolyline.GetZ()
		if z > max:
			max = z
	
		if z < min:
			min = z
		
		if z in elevDistrib:
			count = elevDistrib[z]
			elevDistrib[z] = count + 1
		else:
			elevDistrib[z] = 1

	keys = elevDistrib.keys()
	keys.sort()

	print "Elevation range: %0.2f - %0.2fm:\n" % (min, max)
	print "\tElevation | count "
	print "\t-----------------------"

	for k in keys:
		print "\t%5.2fm   | %4d" % (k, elevDistrib[k])

def classify(norm_z, contourInterval):
	if norm_z % (5*contourInterval) == 0:
		return 'INDEX'
	elif norm_z % contourInterval == 0:
		return 'CONTOUR'
	elif contourInterval >= 5 and norm_z % (contourInterval / 2.0) == 0:
		return 'FORMLINE'
		
	return 'UTIL'

def tag(argv):
	if len(argv) != 4:
		help()
		return
		
	indexElev = float(argv[0])
	contourInterval = int(argv[1])
	srcFileName = argv[2]
	dstFileName = argv[3]

	srcDriver = ogr.GetDriverByName("ESRI Shapefile")
	srcDs = srcDriver.Open(srcFileName, 0)
	srcLayer = srcDs.GetLayer()

	dstDriver = ogr.GetDriverByName("GML")
	
	if os.path.exists(dstFileName):
		dstDriver.DeleteDataSource(dstFileName)

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
		dstFeature.SetField(classFieldDefn.GetNameRef(), classify(z-indexElev, contourInterval))

		dstLayer.CreateFeature(dstFeature)
	
	dstLayer.SyncToDisk()

def help():
	app = sys.argv[0]
	print "Usage: %s -help" % app
	print "       %s -info <shp-file>" % app
	print "       %s -tag <indexElev> <contourInterval> <shp-sourcefile> <gml-target-file>" % app
	
def main():
	if len(sys.argv) > 1:
		if sys.argv[1] == '-info':
			info(sys.argv[2:])
		elif sys.argv[1] == '-tag':
			tag(sys.argv[2:])
	
	else:
		help()
	
if __name__ == "__main__":
	main()