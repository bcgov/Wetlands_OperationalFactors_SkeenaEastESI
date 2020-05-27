'''

	Wetlands Office Tier 2 Operation Factors
	Created By: Jesse Fraser
	May 25th 2020
	
	Goal:
Create a simpler way for data to be consistent between internal to BC Gov and Sync infrastructure
	
'''


import sys, string, os, time, win32com.client, datetime, win32api, arcpy, arcpy.mapping , csv
#import  wml_library_arcpy_v3 as wml_library
from arcpy import env

#Make sure that the overwrite is allowed
arcpy.env.overwriteOutput = True

#make sure the spatial extension is working
try:
    arcpy.CheckOutExtension("Spatial")
    from arcpy.sa import *
    from arcpy.da import *
except:
    arcpy.AddError("Spatial Extension could not be checked out")
    os.sys.exit(0)

#Set the time stamp
time = time.strftime("%Y%m%d")

#Input Wetland Complex dataset
wetland_complex_input = arcpy.GetParameterAsText(0)

#Save Location Folder
output_save = arcpy.GetParameterAsText(1)

#Wetland Complex Unique ID Field
wet_ID = arcpy.GetParameterAsText(2)

#create geodatabase to work out of
save_gdb = "Wetlands_OperationFactors_Desktop_" + time
work_gdb = arcpy.CreateFileGDB_management(output_save, save_gdb)

#work Wetland Complex features 
wet_comp = work_gdb + r"\Wetland_Complex_OF_DesktopAssessment_" + time

#Create the Output Wetland Complex that will have all the OF features
arcpy.CopyFeatures_management(wetland_complex_input, wet_comp)

#create Wetland layer to query
arcpy.MakeFeatureLayer_management(wet_comp,"wet_lyr")
lyr_wet = arcpy.mapping.Layer("wet_lyr")

'''Buffer the Wetland Complexs to different needs'''

#Output
wetbuff_100m = work_gdb + r"\Wetland_Complex_100m_buff_" + time 
wetbuff_500m = work_gdb + r"\Wetland_Complex_500m_buff_" + time 
wetbuff_1km = work_gdb + r"\Wetland_Complex_1km_buff_" + time 
wetbuff_2km = work_gdb + r"\Wetland_Complex_2km_buff_" + time 
wetbuff_5km = work_gdb + r"\Wetland_Complex_5km_buff_" + time 
wetbuff_10km = work_gdb + r"\Wetland_Complex_10km_buff_" + time 

#Buffers 
arcpy.Buffer_analysis(lyr_wet, wetbuff_100m, "100 Meters")
arcpy.Buffer_analysis(lyr_wet, wetbuff_500m, "500 Meters")
arcpy.Buffer_analysis(lyr_wet, wetbuff_1km, "1000 Meters")
arcpy.Buffer_analysis(lyr_wet, wetbuff_2km, "2000 Meters")
arcpy.Buffer_analysis(lyr_wet, wetbuff_5km, "5000 Meters")
arcpy.Buffer_analysis(lyr_wet, wetbuff_10km, "10000 Meters")

#centroid output
wet_centroid = work_gdb + r"\Wetland_Complex_Centroid_" + time
#Centroid of Wetland Complex
arcpy.FeatureToPoint_management(lyr_wet, wet_centroid, "INSIDE")

#Buffer Centroids Outputs
cent_buff_10m = work_gdb + r"\Wetland_Complex_Centroid_10m_buff_" + time 
cent_buff_25m = work_gdb + r"\Wetland_Complex_Centroid_25m_buff_" + time 
cent_buff_50m = work_gdb + r"\Wetland_Complex_Centroid_5m_buff_" + time
cent_buff_100m = work_gdb + r"\Wetland_Complex_Centroid_100m_buff_" + time
cent_buff_500m = work_gdb + r"\Wetland_Complex_Centroid_500m_buff_" + time

#Buffer Centroids
arcpy.Buffer_analysis(wet_centroid, cent_buff_10m, "10 Meters")
arcpy.Buffer_analysis(wet_centroid, cent_buff_25m, "25 Meters")
arcpy.Buffer_analysis(wet_centroid, cent_buff_100m, "100 Meters")
arcpy.Buffer_analysis(wet_centroid, cent_buff_500m, "500 Meters")

''' End of Buffering '''

'''OF1 - Process to Calculate Distance to Human Settlement'''
#Human Settlement Feature

''' Make Changes Here To Human Settlement Feature - HARD CODE'''
HMN_Settle = r"\\spatialfiles.bcgov\work\srm\smt\Workarea\ArcProj\P17_Skeena_ESI\Data\ESI_Data.gdb\Hmn_Structure_Density_ESI_ExtendedAUarea_191001"

#Human Settlement Query Layer
arcpy.MakeFeatureLayer_management(HMN_Settle,"hmn_lyr")
lyr_hmn = arcpy.mapping.Layer("hmn_lyr")

#Query for what is defined as a settlement
lyr_hmn.definitionQuery = r"gridcode > 2"
#First add the field (Settlement w/i) to the copied Wetland Complex
hmn_field = "OF1_Dist_HMN"
arcpy.AddField_management(wet_comp, hmn_field, "DOUBLE")

#Create the spatial join outputs
hmn_join_100m = work_gdb + r"\Wet_HmnWet_100m_buff_" + time 
hmn_join_500m = work_gdb + r"\Wet_HmnWet_500m_buff_" + time 
hmn_join_1km = work_gdb + r"\Wet_HmnWet_1km_buff_" + time 
hmn_join_2km = work_gdb + r"\Wet_HmnWet_2km_buff_" + time 
hmn_join_5km = work_gdb + r"\Wet_HmnWet_5km_buff_" + time 
hmn_join_10km = work_gdb + r"\Wet_HmnWet_10km_buff_" + time 


#At 10km

#Spatial Join
arcpy.SpatialJoin(wetbuff_10km, lyr_hmn, hmn_join_10km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_10km, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_settlement)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "10000")


#At 5km

#Spatial Join
arcpy.SpatialJoin(wetbuff_5km, lyr_hmn, hmn_join_5km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 5km Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_5km, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_settlement)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "5000")

#At 2km

#Spatial Join
arcpy.SpatialJoin(wetbuff_2km, lyr_hmn, hmn_join_2km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 2km Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_2km, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_settlement)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "2000")

#At 1km

#Spatial Join
arcpy.SpatialJoin(wetbuff_1km, lyr_hmn, hmn_join_1km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 1km Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_1km, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_settlement)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "1000")

#At 500m

#Spatial Join
arcpy.SpatialJoin(wetbuff_500m, lyr_hmn, hmn_join_500m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 100m Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_500m, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_settlement)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "500")

#At 100m

#Spatial Join
arcpy.SpatialJoin(wetbuff_100m, lyr_hmn, hmn_join_100m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 100m Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_100m, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_settlement)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "100")

''' OF2 - Distance to Nearest Road '''

''' Make Changes Here To Road Feature - HARD CODE'''
Rds = r"\\spatialfiles.bcgov\work\srm\smt\Workarea\ArcProj\P17_Skeena_ESI\Data\ESI_Data.gdb\Data\CEF_ConsRd_KispBulkTSAs_Removed_190918"

#First add the field (Road w/i) to the copied Wetland Complex
rd_field = "OF2_Dist_Rds"

#Add OF 2 Field
arcpy.AddField_management(wet_comp, rd_field, "DOUBLE")

#Create the spatial join outputs
rd_join_10m = work_gdb + r"\Wet_RdCentroid_10m_buff_" + time 
rd_join_25m = work_gdb + r"\Wet_RdCentroid_25m_buff_" + time 
rd_join_50m = work_gdb + r"\Wet_RdCentroid_50m_buff_" + time 
rd_join_100m = work_gdb + r"\Wet_RdCentroid_100m_buff_" + time 
rd_join_500m = work_gdb + r"\Wet_RdCentroid_500m_buff_" + time 

#At 500m

#Spatial Join
arcpy.SpatialJoin(cent_buff_500m, Rds, rd_join_500m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_rd = [row[0] for row in arcpy.da.SearchCursor(rd_join_500m, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_rd)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, rd_field, "500")

#At 100m

#Spatial Join
arcpy.SpatialJoin(cent_buff_100m, Rds, rd_join_100m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_rd = [row[0] for row in arcpy.da.SearchCursor(rd_join_100m, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_rd)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, rd_field, "100")

#At 50m

#Spatial Join
arcpy.SpatialJoin(cent_buff_50m, Rds, rd_join_50m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_rd = [row[0] for row in arcpy.da.SearchCursor(rd_join_50m, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_rd)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, rd_field, "50")

#At 25m

#Spatial Join
arcpy.SpatialJoin(cent_buff_25m, Rds, rd_join_25m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_rd = [row[0] for row in arcpy.da.SearchCursor(rd_join_25m, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_rd)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, rd_field, "25")

#At 10m

#Spatial Join
arcpy.SpatialJoin(cent_buff_25m, Rds, rd_join_10m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_rd = [row[0] for row in arcpy.da.SearchCursor(rd_join_10m, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_rd)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, rd_field, "10")


''' End OF2 '''

''' OF4 Distance to Large Ponded Water'''

Lakes = \\spatialfiles.bcgov\work\srm\smt\Workarea\ArcProj\P17_Skeena_ESI\Data\ESI_Data.gdb\Data\FWA_Lakes
''' Change here for different body of water - HARD CODE'''

#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
desc = arcpy.Describe(Lakes)
geomField = desc.shapeFieldName
areaFieldName = str(geomField) + "_Area"

#Water Body Query Layer
arcpy.MakeFeatureLayer_management(Lakes,"lakes_layer")
lyr_lakes = arcpy.mapping.Layer("lakes_layer")

#Query for what is defined as a settlement
lyr_lakes.definitionQuery = areaFieldName "> 80000"

#First add the field (Settlement w/i) to the copied Wetland Complex
lakes_field = "OF4_Lakes_Dist"
arcpy.AddField_management(wet_comp, lakes_field, "DOUBLE")

#Create the spatial join outputs
lakes_join_100m = work_gdb + r"\Wet_lakes_100m_buff_" + time 
lakes_join_500m = work_gdb + r"\Wet_lakes_500m_buff_" + time 
lakes_join_1km = work_gdb + r"\Wet_lakes_1km_buff_" + time 
lakes_join_2km = work_gdb + r"\Wet_lakes_2km_buff_" + time 
lakes_join_5km = work_gdb + r"\Wet_lakes_5km_buff_" + time 
lakes_join_10km = work_gdb + r"\Wet_lakes_10km_buff_" + time 

#At 10km

#Spatial Join
arcpy.SpatialJoin(wetbuff_10km, lyr_lakes, lakes_join_10km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_lakes = [row[0] for row in arcpy.da.SearchCursor(lakes_join_10km, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_lakes)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, "10000")


#At 5km

#Spatial Join
arcpy.SpatialJoin(wetbuff_5km, lyr_lakes, lakes_join_5km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 5km Buffer
overlap_lakes = [row[0] for row in arcpy.da.SearchCursor(lakes_join_10km, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_lakes)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, "5000")

#At 2km

#Spatial Join
arcpy.SpatialJoin(wetbuff_2km, lyr_lakes, lakes_join_2km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 2km Buffer
overlap_lakes = [row[0] for row in arcpy.da.SearchCursor(lakes_join_10km, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_lakes)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, "2000")

#At 1km

#Spatial Join
arcpy.SpatialJoin(wetbuff_1km, lyr_lakes, lakes_join_1km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 1km Buffer
overlap_lakes = [row[0] for row in arcpy.da.SearchCursor(lakes_join_1km, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_lakes)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, "1000")

#At 500m

#Spatial Join
arcpy.SpatialJoin(wetbuff_500m, lyr_lakes, lakes_join_500m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 100m Buffer
overlap_lakes = [row[0] for row in arcpy.da.SearchCursor(lakes_join_500m, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_lakes)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, "500")

#At 100m

#Spatial Join
arcpy.SpatialJoin(wetbuff_100m, lyr_hmn, lakes_join_100m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 100m Buffer
overlap_lakes = [row[0] for row in arcpy.da.SearchCursor(lakes_join_100m, wet_ID)]
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + " IN " + str(overlap_lakes)
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, "100")


''' End of OF4 '''

''' OF5 Relative Elevation in Watershed '''








