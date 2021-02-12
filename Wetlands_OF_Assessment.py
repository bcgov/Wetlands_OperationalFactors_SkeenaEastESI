'''

	Wetlands Office Tier 2 Operation Factors
	Created By: Jesse Fraser
	June 1st 2020

	Goal:
Create a tool that automatically calculates the Operational Factors for any given wetlands

'''
#Possibly needed imports
#import win32com.client, win32api
import sys, string, os, time, win32com.client, datetime, win32api, arcpy, arcpy.mapping , csv
#import  wml_library_arcpy_v3 as wml_library
from arcpy import env

env.overwriteOutput = True
import sys, string, os, time , datetime, arcpy, arcpy.mapping , csv


#make sure the spatial extension is working
try:
    arcpy.CheckOutExtension("Spatial")
    from arcpy.sa import *
    from arcpy.da import *
except:
    arcpy.AddError("Spatial Extension could not be checked out")
    os.sys.exit(0)

#Set the time stamp
time = time.strftime("%y%m%d")

#Input Wetland Complex dataset
wetland_complex_input = arcpy.GetParameterAsText(0)

#Save Location Folder
output_save = arcpy.GetParameterAsText(1)


#Wetland Complex Unique ID Field
wet_ID = arcpy.GetParameterAsText(2)


#create geodatabase to work out of
save_gdb = "Wet_OF_" + time
arcpy.CreateFileGDB_management(output_save, save_gdb)
output_gdb = output_save + r"\Wet_OF_" + time + r".gdb"

#work Wetland Complex features
wet_comp = output_gdb + r"\WetComp_OF_" + time

#Create the Output Wetland Complex that will have all the OF features
arcpy.CopyFeatures_management(wetland_complex_input, wet_comp)

#create Wetland layer to query
arcpy.MakeFeatureLayer_management(wet_comp,"wet_lyr")
lyr_wet = arcpy.mapping.Layer("wet_lyr")

#VRI
vri = r"\\spatialfiles.bcgov\work\srm\smt\Workarea\ArcProj\P17_Skeena_ESI\Data\ESI_Data.gdb\Data\SSAF_VRI_R1_Intersect_200512"
'''Hardcode VRI - Change'''

'''Buffer the Wetland Complexs to different needs'''

#Output
wetbuff_100m = output_gdb + r"\Wetland_Complex_100m_buff_" + time
wetbuff_500m = output_gdb + r"\Wetland_Complex_500m_buff_" + time
wetbuff_1km = output_gdb + r"\Wetland_Complex_1km_buff_" + time
wetbuff_2km = output_gdb + r"\Wetland_Complex_2km_buff_" + time
wetbuff_5km = output_gdb + r"\Wetland_Complex_5km_buff_" + time
wetbuff_10km = output_gdb + r"\Wetland_Complex_10km_buff_" + time

#Buffers
arcpy.Buffer_analysis(lyr_wet, wetbuff_100m, "100 Meters")
arcpy.Buffer_analysis(lyr_wet, wetbuff_500m, "500 Meters")
arcpy.Buffer_analysis(lyr_wet, wetbuff_1km, "1000 Meters")
arcpy.Buffer_analysis(lyr_wet, wetbuff_2km, "2000 Meters")
arcpy.Buffer_analysis(lyr_wet, wetbuff_5km, "5000 Meters")
arcpy.Buffer_analysis(lyr_wet, wetbuff_10km, "10000 Meters")

#centroid output
wet_centroid = output_gdb + r"\Wetland_Complex_Centroid_" + time
#Centroid of Wetland Complex
arcpy.FeatureToPoint_management(lyr_wet, wet_centroid, "INSIDE")

#Centroid w/Elev
wet_centroid_elev = output_gdb + r"\Wetland_Complex_Centroid_elev_" + time
#DEM
''' Hard code of DEM - Change if you want to the DEM'''
DEM = r"\\spatialfiles.bcgov\work\srm\bcce\shared\data_library\DEM\BC_Elevation_Mosaic_20161125.gdb\BC_elevation_mosaic"
#Centroid w/ Elevation
ExtractValuesToPoints(wet_centroid, DEM, wet_centroid_elev)

#Buffer Centroids Outputs
cent_buff_10m = output_gdb + r"\Wetland_Complex_Centroid_10m_buff_" + time
cent_buff_25m = output_gdb + r"\Wetland_Complex_Centroid_25m_buff_" + time
cent_buff_50m = output_gdb + r"\Wetland_Complex_Centroid_50m_buff_" + time
cent_buff_100m = output_gdb + r"\Wetland_Complex_Centroid_100m_buff_" + time
cent_buff_500m = output_gdb + r"\Wetland_Complex_Centroid_500m_buff_" + time

#Buffer Centroids
arcpy.Buffer_analysis(wet_centroid, cent_buff_10m, "10 Meters")
arcpy.Buffer_analysis(wet_centroid, cent_buff_25m, "25 Meters")
arcpy.Buffer_analysis(wet_centroid, cent_buff_50m, "50 Meters")
arcpy.Buffer_analysis(wet_centroid, cent_buff_100m, "100 Meters")
arcpy.Buffer_analysis(wet_centroid, cent_buff_500m, "500 Meters")

''' End of Buffering '''


###OF1 - Process to Calculate Distance to Human Settlement###
#Human Settlement Feature

### Make Changes Here To Human Settlement Feature - HARD CODE ###
HMN_Settle = r"\\spatialfiles.bcgov\work\srm\smt\Workarea\ArcProj\P17_Skeena_ESI\Data\ESI_Data.gdb\Data\ExtendedSSAF_fwaAU_Hmn_Structure_Density_191001"

#Human Settlement Query Layer
arcpy.MakeFeatureLayer_management(HMN_Settle,"hmn_lyr")
lyr_hmn = arcpy.mapping.Layer("hmn_lyr")

#Query for what is defined as a settlement
lyr_hmn.definitionQuery = r"gridcode > 2"
#First add the field (Settlement w/i) to the copied Wetland Complex
hmn_field = "OF1_Dist_HMN"
arcpy.AddField_management(wet_comp, hmn_field, "DOUBLE")

#Create the spatial join outputs
hmn_join_100m = output_gdb + r"\Wet_HmnWet_100m_buff_" + time
hmn_join_500m = output_gdb + r"\Wet_HmnWet_500m_buff_" + time
hmn_join_1km = output_gdb + r"\Wet_HmnWet_1km_buff_" + time
hmn_join_2km = output_gdb + r"\Wet_HmnWet_2km_buff_" + time
hmn_join_5km = output_gdb + r"\Wet_HmnWet_5km_buff_" + time
hmn_join_10km = output_gdb + r"\Wet_HmnWet_10km_buff_" + time


#At 10km

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_10km, lyr_hmn, hmn_join_10km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_10km, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_settlement]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_settlement = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_settlement + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "10000", r"PYTHON")

# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "Wet_HmnWet_10km_buff_200911"

#At 5km

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_5km, lyr_hmn, hmn_join_5km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 5km Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_5km, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_settlement]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_settlement = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_settlement + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "5000", r"PYTHON")

#At 2km

#Spatial Join
arcpy.arcpy.SpatialJoin_analysis(wetbuff_2km, lyr_hmn, hmn_join_2km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 2km Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_2km, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_settlement]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_settlement = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_settlement + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "2000", r"PYTHON")

#At 1km

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_1km, lyr_hmn, hmn_join_1km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 1km Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_1km, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_settlement]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_settlement = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_settlement + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "1000", r"PYTHON")

#At 500m

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_500m, lyr_hmn, hmn_join_500m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 100m Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_500m, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_settlement]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_settlement = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_settlement + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "500", r"PYTHON")

#At 100m

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_100m, lyr_hmn, hmn_join_100m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 100m Buffer
overlap_settlement = [row[0] for row in arcpy.da.SearchCursor(hmn_join_100m, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_settlement]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_settlement = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_settlement + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, hmn_field, "100", r"PYTHON")

lyr_wet.definitionQuery = ""

### End OF1 ###


### OF2 - Distance to Nearest Road ###

### Make Changes Here To Road Feature - HARD CODE###
Rds = r"\\spatialfiles.bcgov\work\srm\smt\Workarea\ArcProj\P17_Skeena_ESI\Data\ESI_Data.gdb\Roads\SSAF_Ext_Clip_ConsRd_inclKispBulk_DSS_190918"

#First add the field (Road w/i) to the copied Wetland Complex
rd_field = "OF2_Dist_Rds"

#Add OF 2 Field
arcpy.AddField_management(wet_comp, rd_field, "DOUBLE")

#Create the spatial join outputs
rd_join_10m = output_gdb + r"\Wet_RdCentroid_10m_buff_" + time
rd_join_25m = output_gdb + r"\Wet_RdCentroid_25m_buff_" + time
rd_join_50m = output_gdb + r"\Wet_RdCentroid_50m_buff_" + time
rd_join_100m = output_gdb + r"\Wet_RdCentroid_100m_buff_" + time
rd_join_500m = output_gdb + r"\Wet_RdCentroid_500m_buff_" + time

#At 500m

#Spatial Join
arcpy.SpatialJoin_analysis(cent_buff_500m, Rds, rd_join_500m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_rd = [row[0] for row in arcpy.da.SearchCursor(rd_join_500m, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_rd]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_rd = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_rd + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, rd_field, "500", r"PYTHON")

#At 100m

#Spatial Join
arcpy.SpatialJoin_analysis(cent_buff_100m, Rds, rd_join_100m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_rd = [row[0] for row in arcpy.da.SearchCursor(rd_join_100m, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_rd]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_rd = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_rd + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, rd_field, "100", r"PYTHON")

#At 50m

#Spatial Join
arcpy.SpatialJoin_analysis(cent_buff_50m, Rds, rd_join_50m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_rd = [row[0] for row in arcpy.da.SearchCursor(rd_join_50m, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_rd]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_rd = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_rd + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, rd_field, "50", r"PYTHON")

#At 25m

#Spatial Join
arcpy.SpatialJoin_analysis(cent_buff_25m, Rds, rd_join_25m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_rd = [row[0] for row in arcpy.da.SearchCursor(rd_join_25m, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_rd]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_rd = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_rd + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, rd_field, "25", r"PYTHON")

#At 10m

#Spatial Join
arcpy.SpatialJoin_analysis(cent_buff_10m, Rds, rd_join_10m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_rd = [row[0] for row in arcpy.da.SearchCursor(rd_join_10m, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_rd]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_rd = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_rd + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, rd_field, "10", r"PYTHON")

lyr_wet.definitionQuery = ""
### End OF2 ###


### OF4 Distance to Large Ponded Water###

Lakes = r"\\spatialfiles.bcgov\work\srm\smt\Workarea\ArcProj\P17_Skeena_ESI\Data\ESI_Data.gdb\Data\SSAF_fwaAU_FWA_Lakes_200605"
### Change here for different body of water - HARD CODE###

#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
desc = arcpy.Describe(Lakes)
geomField = desc.shapeFieldName
areaFieldName = str(geomField) + "_Area"


#Water Body Query Layer
arcpy.MakeFeatureLayer_management(Lakes,"lakes_layer")
lyr_lakes = arcpy.mapping.Layer("lakes_layer")



#Query for what is defined as a large body of water
lyr_lakes.definitionQuery = areaFieldName + "> 80000"

#First add the field Lakes to the copied Wetland Complex
lakes_field = "OF4_Lakes_Dist"
arcpy.AddField_management(wet_comp, lakes_field, "DOUBLE")

#Create the spatial join outputs
lakes_join_100m = output_gdb + r"\Wet_lakes_100m_buff_" + time
lakes_join_500m = output_gdb + r"\Wet_lakes_500m_buff_" + time
lakes_join_1km = output_gdb + r"\Wet_lakes_1km_buff_" + time
lakes_join_2km = output_gdb + r"\Wet_lakes_2km_buff_" + time
lakes_join_5km = output_gdb + r"\Wet_lakes_5km_buff_" + time
lakes_join_10km = output_gdb + r"\Wet_lakes_10km_buff_" + time

#At 10km

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_10km, lyr_lakes, lakes_join_10km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_lakes = [row[0] for row in arcpy.da.SearchCursor(lakes_join_10km, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_lakes]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_lakes = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_lakes + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, '10000', r"PYTHON")


#At 5km

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_5km, lyr_lakes, lakes_join_5km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 5km Buffer
overlap_lakes = [row[0] for row in arcpy.da.SearchCursor(lakes_join_5km, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_lakes]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_lakes = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_lakes + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, '5000', r"PYTHON")

#At 2km

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_2km, lyr_lakes, lakes_join_2km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 2km Buffer
overlap_lakes = [row[0] for row in arcpy.da.SearchCursor(lakes_join_2km, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_lakes]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_lakes = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_lakes + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, '2000', r"PYTHON")

#At 1km

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_1km, lyr_lakes, lakes_join_1km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 1km Buffer
overlap_lakes = [row[0] for row in arcpy.da.SearchCursor(lakes_join_1km, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_lakes]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_lakes = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_lakes + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, r'1000',  r"PYTHON")

#At 500m

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_500m, lyr_lakes, lakes_join_500m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 100m Buffer
overlap_lakes = [row[0] for row in arcpy.da.SearchCursor(lakes_join_500m, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_lakes]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_lakes = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_lakes + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, r'500', r"PYTHON")

#At 100m

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_100m, lyr_hmn, lakes_join_100m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 100m Buffer
overlap_lakes = (row[0] for row in arcpy.da.SearchCursor(lakes_join_100m, wet_ID))

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_lakes]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_lakes = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_lakes + r")"

#Apply the Distance
arcpy.CalculateField_management (lyr_wet, lakes_field, r'100', r"PYTHON")

lyr_wet.definitionQuery = ""
lyr_lakes.definitionQuery = ""

### End of OF4 ###



### OF5 Relative Elevation in Watershed ###

#Watershed Elevation Relief Extraction from CEF Aquatics AUs
elev_relief = r"\\spatialfiles.bcgov\work\srm\smt\Workarea\ArcProj\P17_Skeena_ESI\Data\ESI_Data.gdb\CEF_2015\CEF_SSAF_AquaticCE_AU_190404"
### Change here for different body of water - HARD CODE ###

#Output of Spatial Join
wet_relief = output_gdb + r"\WetCent_CEF_FWA_au_" + time

#But first add the field in the Wetland to the copied Wetland Complex
relief = "Elev_Relief"
arcpy.AddField_management(wet_comp, relief, "DOUBLE")
minimum = "MinElev"
arcpy.AddField_management(wet_comp, minimum, "DOUBLE")
wet_elev = "CentroidElev"
arcpy.AddField_management(wet_comp, wet_elev, "DOUBLE")
elev_field = "OF5_RelativeElev"
arcpy.AddField_management(wet_comp, elev_field, "DOUBLE")

#SpatialJoin with centroid
arcpy.SpatialJoin_analysis(wet_centroid_elev, elev_relief, wet_relief, "JOIN_ONE_TO_MANY", "KEEP_COMMON")

#add OF field to SJ
elev_CE= "RelativeElev"
arcpy.AddField_management(wet_relief, elev_CE, "DOUBLE")

#Calculate the value
value = r"(!RASTERVALU! - !MinElev!) / !Elev_Relief!"

#Populate the field in SJ 
arcpy.CalculateField_management(wet_relief, elev_CE, value, "PYTHON")

#create layer to definition query
arcpy.MakeFeatureLayer_management(wet_relief,"relief_lyr")
lyr_relief = arcpy.mapping.Layer("relief_lyr")



#iterate through the features in wetland relief to populate the relief field
##### Need to change the relief field if different data  #####

with arcpy.da.UpdateCursor(lyr_wet, [wet_ID,"Elev_Relief", "MinElev", "CentroidElev",elev_field	]) as cursor:
	for test in cursor:
		
		#put a definition query on the lyr_wet
		lyr_wet.definitionQuery = wet_ID + " = " + str(test[0])[:-2]
		lyr_relief.definitionQuery = wet_ID + " = " + str(test[0])[:-2]
		cursor2 = arcpy.SearchCursor(lyr_relief) 
		for test2 in cursor2:
			feat1 = test2.getValue("Elev_Relief")
			feat2 = test2.getValue("MinElev")
			feat3 = test2.getValue("RASTERVALU")
			feat4 = test2.getValue(elev_CE)
		
		test[1] = feat1
		test[2] = feat2
		test[3] = feat3
		test[4] = feat4
		cursor.updateRow(test)
lyr_wet.definitionQuery = ""
#Populate the field  

### End of OF5 ###



### OF7 Aspect - Haven't done take average aspect?###
### End of OF7 ###



### OF19 Karst Geology ####

### Make Changes Here To Karst Feature - HARD CODE###
karst = r"\\spatialfiles.bcgov\work\srm\smt\Workarea\ArcProj\P17_Skeena_ESI\Data\ESI_Data.gdb\Data\SSAF_fwaAU_Karst_20200507"

#First add the field to the copied Wetland Complex
karst_field = "OF19_Karst"
arcpy.AddField_management(wet_comp, karst_field, "TEXT")

#Karst and Wetland spatial join Output
karst_join = output_gdb + r"\Wetland_Karst_" + time
#Spatial Join
arcpy.SpatialJoin_analysis(wet_comp, karst, karst_join, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_karst = [row[0] for row in arcpy.da.SearchCursor(karst_join, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_karst]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_karst = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_karst + r")"


# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "WetComp_OF_200623"
arcpy.CalculateField_management(lyr_wet, karst_field, r'"Yes"', r"VB")

lyr_wet.definitionQuery = ""
### End OF19 ###


### OF20 Geologic Faults ###

### Change here for different body of water - HARD CODE###
faults = r"\\spatialfiles.bcgov\work\srm\smt\Workarea\ArcProj\P17_Skeena_ESI\Data\ESI_Data.gdb\Data\SSAF_fwaAU_Geologic_Fault_Lines_20200507"

#First add the field to the copied Wetland Complex
fault_field = "OF20_GeogFault"
arcpy.AddField_management(wet_comp, fault_field, "TEXT")

#Karst and Wetland spatial join Output
fault_join = output_gdb + r"\Wetland_GeogFault_" + time
#Spatial Join
arcpy.SpatialJoin_analysis(wet_comp, faults, fault_join, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
overlap_fault = [row[0] for row in arcpy.da.SearchCursor(fault_join, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_fault]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_fault = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_fault + r")"

# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "WetComp_OF_200623"
arcpy.CalculateField_management(lyr_wet, fault_field, r'"Yes"', r"VB")

lyr_wet.definitionQuery = ""

### End OF20 ###

# Create a 2km Buffer feature layer for the next 2 OFs
arcpy.MakeFeatureLayer_management(wetbuff_2km,"Buffwet2km_lyr")
lyr_Buffwet2km = arcpy.mapping.Layer("Buffwet2km_lyr")

#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
desc = arcpy.Describe(lyr_Buffwet2km)
geomField = desc.shapeFieldName
Buffwet2km_areaFieldName = str(geomField) + "_Area"

###OF21 Percentage of Area lakes w/i 2km of Wetland###

#First add the field to the copied Wetland Complex
areabuffer_field = "TotalArea_wi2km"
arcpy.AddField_management(wet_comp, areabuffer_field, "DOUBLE")

areaLakes_field = "Arealakes_wi2km"
arcpy.AddField_management(wet_comp, areaLakes_field, "DOUBLE")

percentLakes_field = "OF21_Percentlakes_wi2km"
arcpy.AddField_management(wet_comp, percentLakes_field, "DOUBLE")


#output clip
area_lakes_wi2km = output_gdb + r"\lakes_clip_2km_" + time

#clip
arcpy.Clip_analysis(wetbuff_2km, lyr_lakes, area_lakes_wi2km)

#create a query layer
arcpy.MakeFeatureLayer_management(area_lakes_wi2km,"wet2km_lyr")
lyr_wet2km = arcpy.mapping.Layer("wet2km_lyr")



#iterate through wetlands 
with arcpy.da.UpdateCursor(lyr_wet, [wet_ID, areabuffer_field, areaLakes_field]) as cursor:
	for test in cursor:
		#Set up variable
		denominator = 0
		numerator = 0
		querTest = str(test[0])[:-2]
		#put a definition query on the lyr_wet and 2km Buffer
		lyr_wet2km.definitionQuery = wet_ID + " = " + querTest
		lyr_Buffwet2km.definitionQuery = wet_ID + " = " + querTest
		lyr_wet.definitionQuery = wet_ID + " = " + querTest
		
		#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
		desc = arcpy.Describe(lyr_wet2km)
		geomField = desc.shapeFieldName
		wet2km_areaFieldName = str(geomField) + "_Area"
		
		#iterate through wetland 2km 
		cursor2 = arcpy.SearchCursor(lyr_wet2km) 
		for test2 in cursor2:
			numerator = test2.getValue(wet2km_areaFieldName) + numerator
		
		#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
		desc = arcpy.Describe(lyr_Buffwet2km)
		geomField = desc.shapeFieldName
		Buff_wet2km_areaFieldName = str(geomField) + "_Area"
		
		#iterate through layer with Bu		
		cursor3 = arcpy.SearchCursor(lyr_Buffwet2km) 
		for test3 in cursor3:
			denominator = test3.getValue(Buff_wet2km_areaFieldName) + denominator
		
		#populate Wetland stuff
		test[1] = denominator
		test[2] = numerator

		cursor.updateRow(test)

lyr_wet.definitionQuery = ""
#Calculate Amount Lakes Percent
calc_lakesPerc = r"(!Arealakes_wi2km!/!TotalArea_wi2km!)"
arcpy.CalculateField_management(lyr_wet, percentLakes_field, calc_lakesPerc, "PYTHON")


### End OF21 ###
#Script has run to at least here
### OF22 Percentage of Area wetland and lakes w/i 2km of Wetland###


#First add the field to the copied Wetland Complex

areaWater_field = "AreaWetlakes_wi2km"
arcpy.AddField_management(wet_comp, areaWater_field, "DOUBLE")

percentWater_field = "OF22_wetANDlakes_wi2km"
arcpy.AddField_management(wet_comp, percentWater_field, "DOUBLE")

#Lakes feature - make sure no query on it
lyr_lakes.definitionQuery = ""

#union output
water_union = output_gdb + r"\Wet_Lakes_union_" + time

#union wetland and lakes
arcpy.Union_analysis([lyr_lakes, wet_comp], water_union)

#output clip
area_water_wi2km = output_gdb + r"\water_clip_2km_" + time

#clip
arcpy.Clip_analysis(wetbuff_2km, water_union, area_water_wi2km)

#create a query layer
arcpy.MakeFeatureLayer_management(area_water_wi2km,"water2km_lyr")
lyr_water2km = arcpy.mapping.Layer("water2km_lyr")

with arcpy.da.UpdateCursor(lyr_wet, [wet_ID, areabuffer_field, areaWater_field]) as cursor:
	for test in cursor:
		#Set up variable
		denominator = 0
		numerator = 0
		querTest = str(test[0])[:-2]
		#put a definition query on the lyr_wet and 2km Buffer
		lyr_water2km.definitionQuery = wet_ID + " = " + querTest
		lyr_wet.definitionQuery = wet_ID + " = " + querTest
		
		#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
		desc = arcpy.Describe(lyr_water2km)
		geomField = desc.shapeFieldName
		Buff_water2km_areaFieldName = str(geomField) + "_Area"
		
		#iterate through layer with Bu		
		cursor4 = arcpy.SearchCursor(lyr_water2km) 
		for test4 in cursor4:
		#Iterate through the total area of Wetlands and Lakes
			numerator = test4.getValue(Buff_water2km_areaFieldName) + numerator
		

		#Populate Fields
		test[2] = numerator
		cursor.updateRow(test)
		
lyr_wet.definitionQuery = ""
#Calculate Amount Lakes Percent
calc_lakesPerc2 = r"(!AreaWetlakes_wi2km!/!TotalArea_wi2km!)"
arcpy.CalculateField_management(lyr_wet, percentWater_field, calc_lakesPerc2, "PYTHON")

### End OF22 ###


### OF28 Species of Conservation Concer###

#yes/no for plants/communites inside 100m buffer
#yes/no for waterbird inside 100m buffer
#yes/no for other bird inside 100m buffer

### End OF28 ###


### OF32 Soil Nutrients based on Site Index ###

#First add the field to the copied Wetland Complex
siteIndex_field = "OF32_SiteIndex"
arcpy.AddField_management(wet_comp, siteIndex_field, "DOUBLE")

#VRI and Wetland spatial join Output
site_Index = output_gdb + r"\Wetland_VRI_" + time
#Spatial Join
arcpy.SpatialJoin_analysis(wet_centroid, vri, site_Index, "JOIN_ONE_TO_MANY", "KEEP_COMMON")
#Get the wet_ID that overlap with the 10km Buffer
with arcpy.da.UpdateCursor(site_Index, [wet_ID, "SITE_INDEX"]) as cursor:
	for test in cursor:
		#Definition Query for Wetlands
		lyr_wet.definitionQuery = wet_ID + " = " + str(test[0])[:-2]
		
		
		#iterate through layer with Bu		
		
		cursor5 = arcpy.UpdateCursor(lyr_wet) 
		for test5 in cursor5:
		#Iterate through the total area of Wetlands and Lakes
			test5.setValue(siteIndex_field, test[1])
			cursor5.updateRow(test5)
lyr_wet.definitionQuery = ""

##3 End OF32 ###

### OF33 Position in Landscape ###

#Not sure how this differs from OF5 in terms of relative position?

### End OF32 ###



'''Hard Code for BCLCS Stuff'''
#Output Land Class Feature
BCLCS = output_gdb + r"\BCLCS_VRI_Dissolve_" + time

BCLCS_Interest = "BCLCS_LEVEL_1", "BCLCS_LEVEL_2", "BCLCS_LEVEL_3", "BCLCS_LEVEL_4"
#dissolve VRI into landcover type codes
arcpy.Dissolve_management(vri, BCLCS, BCLCS_Interest)

#Add BCLCS Level 1 to 4 Concatonated field
BCLCS_con = "BCLCS_Lev1to4"
arcpy.AddField_management(BCLCS, BCLCS_con, "TEXT")

#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
desc = arcpy.Describe(BCLCS)
geomField = desc.shapeFieldName
BCLCS_areaFieldName = str(geomField) + "_Area"

#Calculate Concatonated field for BCLCS
arcpy.CalculateField_management(BCLCS,BCLCS_con, r"!BCLCS_LEVEL_1! + ' ' +  !BCLCS_LEVEL_2! + ' ' + !BCLCS_LEVEL_3! + ' ' + !BCLCS_LEVEL_4!", "PYTHON")

#BCLCS Frequency Output
freq_BCLCS = output_gdb + r"\BCLCS_Freq_" + time
#Get a summary of each 1-4 Level amount using frequency field
arcpy.Frequency_analysis(BCLCS, freq_BCLCS, BCLCS_con, BCLCS_areaFieldName)

#create a query layer
arcpy.MakeFeatureLayer_management(BCLCS,"BCLCS_lyr")
lyr_BCLCS = arcpy.mapping.Layer("BCLCS_lyr")


###OF39 VRI Class Unquieness - Using BCLCS Classes 1-4

#First add the field to the copied Wetland Complex
uniqueClass_field = "OF39_UniqueClass_Dist"
arcpy.AddField_management(wet_comp, uniqueClass_field, "DOUBLE")


#Add percent field to query
BCLCS_PCNT = r"BCLCS_PCNT"
arcpy.AddField_management(freq_BCLCS, BCLCS_PCNT, "DOUBLE")
ESI_FWAau_area = 0
#calc percent
with arcpy.da.UpdateCursor(BCLCS, [BCLCS_areaFieldName]) as cursor:
	for test in cursor:
		ESI_FWAau_area = ESI_FWAau_area + test[0]

print ESI_FWAau_area

ESI_Area = "ESI_Area"

arcpy.AddField_management(freq_BCLCS, ESI_Area, "DOUBLE")

arcpy.CalculateField_management(freq_BCLCS, ESI_Area, ESI_FWAau_area, "PYTHON")


calc = "!GEOMETRY_Area! / !ESI_Area!"
arcpy.CalculateField_management(freq_BCLCS, BCLCS_PCNT, calc, "PYTHON")


#with arcpy.da.UpdateCursor(freq_BCLCS, ["Shape_Area", BCLCS_PCNT]) as cursor:
#	for test in cursor:
		#Populate Fields
#		test[1] = test[0]/ESI_FWAau_area
#		cursor.updateRow(test)
	

#create a query layer for the freq table
arcpy.MakeTableView_management(freq_BCLCS,"freq_BCLCS_lyr")
lyr_freq_BCLCS = arcpy.mapping.TableView("freq_BCLCS_lyr")

# Def Query freq table to only keep the areas with less than 1% across the ESI area
lyr_freq_BCLCS.definitionQuery = BCLCS_PCNT + " < 0.01"

#Populate a field of the BCLCS areas that are 'unique'
BCLCS_rare_defquer = [row[0] for row in arcpy.da.SearchCursor(lyr_freq_BCLCS, BCLCS_con)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i) for i in BCLCS_rare_defquer]
#remove the square brackets
str_baseNoSquare = str(str_NolastTwo)[1:-1]
print str_NoSquare

#No need to do all the fancy footwork for string data
lyr_BCLCS.definitionQuery = BCLCS_con + r" IN (" + str_baseNoSquare + r")"

#At 5km

#BCLCS Join Output
BCLCS_5km = output_gdb + r"\BCLCS_Wet_5km_" + time
#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_5km, lyr_BCLCS, BCLCS_5km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")

#create a query layer for 5km
arcpy.MakeFeatureLayer_management(BCLCS_5km,"BCLCS5km_lyr")
lyr_5kmBCLCS = arcpy.mapping.Layer("BCLCS5km_lyr")

#Only have rare overlap
lyr_5kmBCLCS.definitionQuery = BCLCS_con + r" IN (" + str_baseNoSquare + r")"

#Get the wet_ID that overlap with the 2km Buffer
overlap_BCLCS_rare = [row[0] for row in arcpy.da.SearchCursor(lyr_5kmBCLCS, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_BCLCS_rare]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_BCLCS_rare = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_BCLCS_rare + r")"

calc5000 = 5000 
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, uniqueClass_field, calc5000)

#remove def quer
lyr_wet.definitionQuery = ""

#At 1km

#BCLCS Join Output
BCLCS_1km = output_gdb + r"\BCLCS_Wet_1km_" + time
#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_1km, lyr_BCLCS, BCLCS_1km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")

#create a query layer for 5km
arcpy.MakeFeatureLayer_management(BCLCS_1km,"BCLCS1km_lyr")
lyr_1kmBCLCS = arcpy.mapping.Layer("BCLCS1km_lyr")

#Only have rare overlap
lyr_1kmBCLCS.definitionQuery = BCLCS_con + r" IN (" + str_baseNoSquare + r")"

#Get the wet_ID that overlap with the 2km Buffer
overlap_BCLCS_rare = [row[0] for row in arcpy.da.SearchCursor(lyr_1kmBCLCS, wet_ID)]

#building for the def query just right
#iterate through list to convert to string w/o .0 at the endswith
str_NolastTwo = [str(i)[:-2] for i in overlap_BCLCS_rare]
#remove the square brackets
str_NoSquare = str_NolastTwo[1:-1]
#Get rid of quotation marks
str_overlap_BCLCS_rare = (', '.join(str_NoSquare))
#Definition Query for Wetlands
lyr_wet.definitionQuery = wet_ID + r" IN (" + str_overlap_BCLCS_rare + r")"

calc1000 = 1000
#Apply the Distance
arcpy.CalculateField_management (lyr_wet, uniqueClass_field, calc1000)

#remove def quer
lyr_wet.definitionQuery = ""
lyr_BCLCS.definitionQuery = ""

### End OF39



###OF40 - Maximum Dominance of BCLCS Class 4
uniqueClass_field = "OF40_MaxDom_BCLCS"
arcpy.AddField_management(wet_comp, uniqueClass_field, "DOUBLE")

#Gotta think about more

###End OF40


###OF41 - Number of BCLCS Class 4 fields w/i 100m 

#First add the field to the copied Wetland Complex
numClass_field = "OF41_NumClasses_BCLCSwi100m"
arcpy.AddField_management(wet_comp, numClass_field, "LONG")

#output feature
wetland_BCLCS_100m = output_gdb + r"\Wet100m_BCLCS_intersect_" + time
#union wetlands and BCLCS
#arcpy.Union_analysis([lyr_BCLCS, wetbuff_100m], wetland_BCLCS_100m_union)
#Using intersect to try to reduce time - Does not REDCUE TIME
#arcpy.Intersect_analysis([lyr_BCLCS, wetbuff_100m], wetland_BCLCS_100m_union, "ALL")

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_100m, lyr_BCLCS, wetland_BCLCS_100m, "JOIN_ONE_TO_MANY", "KEEP_COMMON")

#create a def queryable layer from the union
arcpy.MakeFeatureLayer_management(wetland_BCLCS_100m,"wetland_BCLCS_100m_lyr")
lyr_wet_BCLCS_100m = arcpy.mapping.Layer("wetland_BCLCS_100m_lyr")


#iterate through Wet Comp ID
with arcpy.da.UpdateCursor(wet_comp, [wet_ID, numClass_field]) as cursor:
	for test in cursor:
		lyr_wet_BCLCS_100m.definitionQuery = wet_ID + ' = ' + str(test[0])[:-2]
			
		#getcount of BCLCS type
		result = arcpy.GetCount_management(lyr_wet_BCLCS_100m)
		num_classes = int(result.getOutput(0))
		
		test[1] = num_classes
		cursor.updateRow(test)
		

lyr_wet_BCLCS_100m.definitionQuery = ""

#End OF41 



### OF42 - Number of BCLCS Class 4 fields w/i 2km

#First add the field to the copied Wetland Complex
numClass_field = "OF42_NumClasses_BCLCSwi2km"
arcpy.AddField_management(wet_comp, numClass_field, "DOUBLE")

#output feature
BCLCS_2km = output_gdb + r"\Wet2km_BCLCS_intersect" + time
#union wetlands and BCLCS

#Union causing issues... Repair Geometry of Both Doesn't seem to help.
#arcpy.RepairGeometry_management(lyr_BCLCS)
#arcpy.RepairGeometry_management(wetbuff_2km)

#Spatial Join
arcpy.SpatialJoin_analysis(wetbuff_2km, lyr_BCLCS, BCLCS_2km, "JOIN_ONE_TO_MANY", "KEEP_COMMON")

#create a def queryable layer from the union
arcpy.MakeFeatureLayer_management(BCLCS_2km,"BCLCS_2km_lyr")
lyr_wet_BCLCS_2km = arcpy.mapping.Layer("BCLCS_2km_lyr")


#iterate through Wet Comp ID
with arcpy.da.UpdateCursor(wet_comp, [wet_ID, numClass_field]) as cursor:
	for test in cursor:
		lyr_wet_BCLCS_2km.definitionQuery = wet_ID + ' = ' + str(test[0])[:-2]

		#getcount of BCLCS type
		result = arcpy.GetCount_management(lyr_wet_BCLCS_2km)
		num_classes = int(result.getOutput(0))
		
		test[1] = num_classes
		cursor.updateRow(test)

lyr_wet_BCLCS_2km.definitionQuery = ""

# End OF42 #

numClass_field = "Wet_Area_100m"
arcpy.AddField_management(wet_comp, numClass_field, "DOUBLE")

#Build a table entry that states the area of Wetland + 100m 
#create a def queryable layer from the clip
arcpy.MakeFeatureLayer_management(wetbuff_100m,"wetbuff_100m_lyr")
lyr_wetbuff100m = arcpy.mapping.Layer("wetbuff_100m_lyr")

#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
desc = arcpy.Describe(lyr_wetbuff100m)
geomField = desc.shapeFieldName
wetbuff100m_areaFieldName = str(geomField) + "_Area"

#iterate through Wet Comp ID
with arcpy.da.UpdateCursor(lyr_wet, [wet_ID, numClass_field]) as cursor:
	for test in cursor:
		wetArea = 0
		
		lyr_wetbuff100m.definitionQuery = wet_ID + ' = ' + str(test[0])[:-2]
		
		cursor2 = arcpy.SearchCursor(lyr_wetbuff100m) 
		#calculate the total area of Decid w/i 100m
		for test2 in cursor2:
			wetArea = test2.getValue(wetbuff100m_areaFieldName) + wetArea
		
		test[1] = wetArea
		cursor.updateRow(test)

# OF 43 Amount of Decidious w/i 100m #

#First add the field to the copied Wetland Complex
numClass_field = "DecidiousArea_BCLCS_wi100m"
numPCNT_field = "OF43_DecidiousPCNT_BCLCS_wi100m"
arcpy.AddField_management(wet_comp, numClass_field, "DOUBLE")
arcpy.AddField_management(wet_comp, numPCNT_field, "DOUBLE")

#Definition query on decidious (aka Broadleaf)
lyr_BCLCS.definitionQuery = r"BCLCS_LEVEL_4 = 'TB'"
#output clip
area_decid_wi100m = output_gdb + r"\decid_clip_100m_" + time

#clip
arcpy.Clip_analysis(wetbuff_100m, lyr_BCLCS, area_decid_wi100m)

#create a def queryable layer from the clip
arcpy.MakeFeatureLayer_management(area_decid_wi100m,"decid_BCLCS_lyr")
lyr_decid_BCLCS = arcpy.mapping.Layer("decid_BCLCS_lyr")





#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
desc = arcpy.Describe(lyr_decid_BCLCS)
geomField = desc.shapeFieldName
decid_BCLCS_areaFieldName = str(geomField) + "_Area"

#iterate through Wet Comp ID
with arcpy.da.UpdateCursor(lyr_wet, [wet_ID, numClass_field]) as cursor:
	for test in cursor:
		decid_area = 0
		
		lyr_decid_BCLCS.definitionQuery = wet_ID + ' = ' + str(test[0])[:-2]
		
		cursor2 = arcpy.SearchCursor(lyr_decid_BCLCS) 
		#calculate the total area of Decid w/i 100m
		for test2 in cursor2:
			decid_area = test2.getValue(decid_BCLCS_areaFieldName) + decid_area
				
		test[1] = decid_area
		cursor.updateRow(test)

lyr_BCLCS.definitionQuery = r""
calc1 = r"!DecidiousArea_BCLCS_wi100m! / !Wet_Area_100m!"
arcpy.CalculateField_management (lyr_wet, numPCNT_field, calc1, r"PYTHON")

# End OF43 



### OF44 - Amount of Coniferious w/i 100m 
#First add the field to the copied Wetland Complex
numClass_field = "ConiferousArea_BCLCS_wi100m"
numPCNT_field = "OF44_ConiferousPCNT_BCLCS_wi100m"
arcpy.AddField_management(wet_comp, numClass_field, "DOUBLE")
arcpy.AddField_management(wet_comp, numPCNT_field, "DOUBLE")
#Definition query on decidious (aka Broadleaf)
lyr_BCLCS.definitionQuery = r"BCLCS_LEVEL_4 = 'TC'"
#output clip
area_conifer_wi100m = output_gdb + r"\conifer_clip_" + time

#clip
arcpy.Clip_analysis(wetbuff_100m, lyr_BCLCS, area_conifer_wi100m)

#create a def queryable layer from the clip
arcpy.MakeFeatureLayer_management(area_conifer_wi100m,"conif_BCLCS_lyr")
lyr_conif_BCLCS = arcpy.mapping.Layer("conif_BCLCS_lyr")

#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
desc = arcpy.Describe(lyr_conif_BCLCS)
geomField = desc.shapeFieldName
conif_BCLCS_areaFieldName = str(geomField) + "_Area"

#iterate through Wet Comp ID
with arcpy.da.UpdateCursor(wet_comp, [wet_ID, numClass_field]) as cursor:
	for test in cursor:
		conif_area = 0
		
		lyr_conif_BCLCS.definitionQuery = wet_ID + ' = ' + str(test[0])[:-2]


		cursor2 = arcpy.SearchCursor(lyr_conif_BCLCS) 
		#calculate the total area of Decid w/i 100m
		for test2 in cursor2:
			conif_area = test2.getValue(conif_BCLCS_areaFieldName) + conif_area
		
		test[1] = conif_area
		cursor.updateRow(test)
		
lyr_BCLCS.definitionQuery = r""

calc1 = r"!ConiferousArea_BCLCS_wi100m! / !Wet_Area_100m!"
arcpy.CalculateField_management (lyr_wet, numPCNT_field, calc1, r"PYTHON")
### End OF44 

### Not an OF, but Mixed Treed
#First add the field to the copied Wetland Complex
numPCNT_field = "OFxx_MixedTreePCNT_BCLCS_wi100m"
numClass_field = "MixedTreeArea_BCLCS_wi100m"
arcpy.AddField_management(wet_comp, numClass_field, "DOUBLE")
arcpy.AddField_management(wet_comp, numPCNT_field, "DOUBLE")
#Definition query on decidious (aka Broadleaf)
lyr_BCLCS.definitionQuery = r"BCLCS_LEVEL_4 = 'TM'"
#output clip
area_mixed_wi100m = output_gdb + r"\mixed_clip_100m_" + time

#clip
arcpy.Clip_analysis(wetbuff_100m, lyr_BCLCS, area_mixed_wi100m)

#create a def queryable layer from the clip
arcpy.MakeFeatureLayer_management(area_mixed_wi100m,"conif_BCLCS_lyr")
lyr_mixed_BCLCS = arcpy.mapping.Layer("conif_BCLCS_lyr")

#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
desc = arcpy.Describe(lyr_mixed_BCLCS)
geomField = desc.shapeFieldName
mixed_BCLCS_areaFieldName = str(geomField) + "_Area"

#iterate through Wet Comp ID
with arcpy.da.UpdateCursor(wet_comp, [wet_ID, numClass_field]) as cursor:
	for test in cursor:
		mixed_area = 0
		lyr_mixed_BCLCS.definitionQuery = wet_ID + ' = ' + str(test[0])[:-2]

		cursor2 = arcpy.SearchCursor(lyr_mixed_BCLCS) 
		#calculate the total area of Decid w/i 100m
		for test2 in cursor2:
			mixed_area = test2.getValue(mixed_BCLCS_areaFieldName) + mixed_area
		
		test[1] = mixed_area
		cursor.updateRow(test)
		
		
lyr_BCLCS.definitionQuery = r""

#Calculate the percent w/i 100m
calc1 = r"!MixedTreeArea_BCLCS_wi100m! / !Wet_Area_100m!"
arcpy.CalculateField_management (lyr_wet, numPCNT_field, calc1, r"PYTHON")


### End of Extra Info 


# OF45 - Amount of NonTreed Veg w/i 100m

#First add the field to the copied Wetland Complex
numPCNT_field = "OF45_NonTreedVegPCNT_BCLCS_wi100m"
numClass_field = "NonTreedVegArea_BCLCS_wi100m"
arcpy.AddField_management(wet_comp, numClass_field, "DOUBLE")
arcpy.AddField_management(wet_comp, numPCNT_field, "DOUBLE")

#Definition query on decidious (aka Broadleaf)
lyr_BCLCS.definitionQuery = r"BCLCS_LEVEL_1 = 'V' AND BCLCS_LEVEL_2 = 'N'"
#output clip
area_NonTree_wi100m = output_gdb + r"\NonTreeVeg"

#clip
arcpy.Clip_analysis(wetbuff_100m, lyr_BCLCS, area_NonTree_wi100m)

#create a def queryable layer from the clip
arcpy.MakeFeatureLayer_management(area_NonTree_wi100m,"nonTreed_BCLCS_lyr")
lyr_nonTreed_BCLCS = arcpy.mapping.Layer("nonTreed_BCLCS_lyr")

#get the areafield name to avoid geometry vs shape issue (Thanks you Carol Mahood)
desc = arcpy.Describe(lyr_nonTreed_BCLCS)
geomField = desc.shapeFieldName
nonTreed_BCLCS_areaFieldName = str(geomField) + "_Area"

#iterate through Wet Comp ID
with arcpy.da.UpdateCursor(wet_comp, [wet_ID,numClass_field]) as cursor:
	for test in cursor:
		non_area = 0
		lyr_nonTreed_BCLCS.definitionQuery = wet_ID + ' = ' + str(test[0])[:-2]
		
		cursor2 = arcpy.SearchCursor(lyr_nonTreed_BCLCS) 
		#calculate the total area of Decid w/i 100m
		for test2 in cursor2:
			non_area = test2.getValue(nonTreed_BCLCS_areaFieldName) + non_area
		
		test[1] = non_area
		cursor.updateRow(test)
		

lyr_BCLCS.definitionQuery = r""

#Calculate the percent w/i 100m
calc1 = r"!NonTreedVegArea_BCLCS_wi100m! / !Wet_Area_100m!"
arcpy.CalculateField_management (lyr_wet, numPCNT_field, calc1, r"PYTHON")
# End OF45
