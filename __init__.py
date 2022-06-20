bl_info = {
    "name" : "Mario Kart Wii Utilities",
    "author" : "Gabriela_",
    "version" : (1, 0),
    "blender" : (2, 82, 0),
    "location" : "View3d > Tool",
    "warning" : "",
    "wiki_url" : "",
    "category": "Export",
}

import os
import bpy
import math
import random
import struct 
import requests
import webbrowser
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.app.handlers import persistent


lastselection = []
setting1users = ["A2", "A3", "A6", "A8", "A9", "A10"]
setting2users = ["A3", "A6", "A10"]
   
def updateArea(self, context):
    checkMaterial()
    #0 - AREA Header
    #1 - Number
    #2 - Shape
    #3 - Type
    #4 - CAME
    #5 - Priority
    #6 - Setting 1
    #7 - Setting 2
    #8 - Route
    #9 - Enemy Point
    
    global lastselection, setting1users, setting2users
    scene = context.scene
    mytool = scene.kmpt
    activeObject = bpy.context.active_object
    if(hasattr(activeObject, "name") == False):
        return

    if(lastselection == activeObject):
        if(activeObject.name.startswith("AREA_")): 
            name = activeObject.name
            properties = name.split("_")
            ctype = str(mytool.kmp_areaEnumType)
            #Set properties to correct  values from variables
            kmp_areaSet1 = "0"
            kmp_areaSet2 = "0"
            kmp_areaID = "-1"
            if(ctype == 'A0'):
                kmp_areaID = str(mytool.kmp_areaID)
            kmp_areaRoute = "-1"
            if(ctype == 'A3'):
                kmp_areaRoute = str(mytool.kmp_areaRoute)
            kmp_areaEnemy = "-1"
            if(ctype == 'A4'):
                kmp_areaEnemy = str(mytool.kmp_areaEnemy)
            if(ctype == 'A1'):
                kmp_areaSet1 = str(int(mytool.kmp_areaEvnKarehaUp))
            elif(ctype == 'A2'):
                kmp_areaSet1 = str(mytool.kmp_areaPostEffectEntry) 
            elif(ctype == 'A3'):
                kmp_areaSet1 = str(mytool.kmp_areaMovingRouteSet1) 
                kmp_areaSet2 = str(mytool.kmp_areaMovingRouteSet2) 
            elif(ctype == 'A6'):
                kmp_areaSet1 = str(mytool.kmp_areaIDK1) 
                kmp_areaSet2 = str(mytool.kmp_areaIDK2) 
            elif(ctype == 'A8' or ctype == 'A9'):
                kmp_areaSet1 = str(mytool.kmp_areaGroup)
            elif(ctype == 'A10'):
                if(mytool.kmp_areaUseCOOB):
                    if(mytool.kmp_areaCOOBVersion == "kHacker"):
                        kmp_areaRoute = "1"
                        kmp_areaSet2 = str(mytool.kmp_areakHackerCheckpoint)
                        kmp_areaSet1 = str(mytool.kmp_areakHackerMode)
                    elif(mytool.kmp_areaCOOBVersion == "Riidefi"):
                        kmp_areaRoute = "-1"
                        if(mytool.kmp_areaRiidefiInvert == True):
                            kmp_areaSet1 = str(mytool.kmp_areaRiidefiP2)
                            kmp_areaSet2 = str(mytool.kmp_areaRiidefiP1)
                        else:
                            kmp_areaSet1 = str(mytool.kmp_areaRiidefiP1)
                            kmp_areaSet2 = str(mytool.kmp_areaRiidefiP2)
                                
            areaName = properties[0] + "_" + properties[1] + "_"  + properties[2] + "_"  + str(mytool.kmp_areaEnumType[1:]) + "_"  + kmp_areaID + "_" +\
            str(mytool.kmp_areaPrority) + "_"  + kmp_areaSet1 + "_"  + kmp_areaSet2 + "_"  + kmp_areaRoute + "_"  + kmp_areaEnemy
            bpy.context.active_object.name = areaName
            mat = bpy.data.materials.get("kmpc.area." + mytool.kmp_areaEnumType)
            bpy.context.active_object.data.materials.clear()
            bpy.context.active_object.data.materials.append(mat)
                   
class MyProperties(bpy.types.PropertyGroup):
    
    #
    #
    # AREA
    #
    #
    
    scale : bpy.props.FloatProperty(name= "Export scale", min= 0.0001, max= 100000, default= 100, description= "Set scale at which your KMP will be exported")
 #region area_types  
    #AREA Section
    kmp_areaEnumType : bpy.props.EnumProperty(name = "Type", items=[("A0", "Camera", 'Defines which camera is being used while entering this AREA'),
                                                                    ("A1", "EnvEffect", 'Defines an area where EnvFire and EnvSnow is not used, and EnvKareha is used'),
                                                                    ("A2", "BFG Entry Swapper", 'Controls which posteffect.bfg is being used'),
                                                                    ("A3", "Moving Road", 'Causes moving road terrain in KCL to move'),
                                                                    ("A4", "Destination Point", 'This AREA type is used as first destination for Force Recalculation'),
                                                                    ("A5", "Minimap Control", 'Used to crop minimap on tournaments'),
                                                                    ("A6", "Music Changer", 'Changes music effects'),
                                                                    ("A7", "Flying Boos", 'Flying Boos will appear while inside of this AREA (Requires b_teresa)'),
                                                                    ("A8", "Object Grouper", 'Groups objects together'),
                                                                    ("A9", "Group Unloader", 'Disables objects of selected group'),
                                                                    ("A10", "Fall Boundary", 'Used to define fall boundaries on tournaments')],
                                                                    update=updateArea)
    kmp_areaPrority : bpy.props.IntProperty(name = "Priority", min= 0, default= 0, update=updateArea, 
                                            description= "When 2 AREAs of same type a overlapping then the one\with higher priority is getting considered")                                                                
    kmp_areaSet1 : bpy.props.StringProperty(name = "Set1", default= "0", update=updateArea)
    kmp_areaSet2 : bpy.props.StringProperty(name = "Set2", default= "0", update=updateArea)
    #AREA0
    kmp_areaID : bpy.props.IntProperty(name = "CAME", min= 0, default= 0, update=updateArea, 
                                        description= "ID of camera which will be activated while entering AREA (Decimal)")
    #AREA1
    kmp_areaEvnKarehaUp : bpy.props.BoolProperty(name= "Use EnvKarehaUp?", update=updateArea, 
                                                description= "If EnvKareha is being used, selecting this option will use EnvKarehaUp instead")
    #AREA2
    kmp_areaPostEffectEntry : bpy.props.IntProperty(name= "BFG Entry", min= 0, default= 0, update=updateArea,
                                                    description= "ID of posteffect.bfg entry which will be used while inside of the AREA")
    #AREA3
    kmp_areaRoute : bpy.props.IntProperty(name= "Route", default= -1, update=updateArea, 
                                            description= "A Route used by moving road KCL to push player along. Setting this to '-1' will moving road to push players towards this AREA origin point")
    kmp_areaMovingRouteSet1 : bpy.props.IntProperty(name="Acceleration", soft_min= 0, default = 0, update=updateArea, 
                                                    description= "Defines acceleration and deceleration speed for Variant 0x0002. The higher value, the easier is to speed up and harder to slow down")
    kmp_areaMovingRouteSet2 : bpy.props.IntProperty(name="Speed", soft_min= 0, default = 0, update=updateArea, 
                                                    description= "Defines the speed of moving water")
    #AREA4
    kmp_areaEnemy : bpy.props.IntProperty(name = "EN Point", default= -1, update=updateArea, 
                                        description= "(Unsure) Defines the next enemy point ID (decimal) after entering AREA")
    #AREA6
    kmp_areaIDK1 : bpy.props.IntProperty(name = "Unknown Setting 1", min= 0, default= 0, update=updateArea, 
                                        description= "Unknown. Undocumented. Always 1 on Nintendo tracks")
    kmp_areaIDK2 : bpy.props.IntProperty(name = "Unknown Setting 2", min= 0, default= 0, update=updateArea, 
                                        description= "Unknown. Undocumented. (Very unsure) Defines music volume change")
    #AREA8&9
    kmp_areaGroup : bpy.props.IntProperty(name = "Group", min= 0, default= 0, update=updateArea,
                                        description= "Defines the group for AREA type 8 (Object Grouper) and 9 (Group Unloader) to work together")
    #AREA10
    kmp_areaUseCOOB : bpy.props.BoolProperty(name = "Conditional Out of Bounds?", default = False, 
                                        description = "You can use this type of AREA as Conditional Out of Bounds (Both Riidefi's and kHacker's versions are supported)",
                                                                    update=updateArea)
    kmp_areaCOOBVersion : bpy.props.EnumProperty(name = "COoB Mode", items=[("kHacker", "kHacker35000vr", "Use kHacker's cheat code"),
                                                                            ("Riidefi", "Ridefii", "Use Riidefi's cheat code\nThe AREA will be enabled if and only if a player is in the Cth checkpoint sector such that P1 <= C < P2.\nNOTE: If both P1 and P2 are zero, this code is disabled, and the boundary is unconditionally enabled.\nNOTE: If P1 > P2, the range functions in blacklist mode. The AREA will be disabled within P2 <= C < P1, and enabled everywhere else.")],
                                                                    update=updateArea)
    kmp_areakHackerMode : bpy.props.EnumProperty(name = "In KCP region", items=[("0", "Enable COoB", 'Enables this Fall Boundaries while inside entered key checkpoint region'),
                                                                            ("1", "Disable COoB", 'Disables this Fall Boundaries while inside entered key checkpoint region')],
                                                                    update=updateArea)
    kmp_areakHackerCheckpoint : bpy.props.IntProperty(name = "KCL Region", min = 0, max = 255, description = "Condition is met while player is inside this key checkpoint region",
                                                                    update=updateArea)
    kmp_areaRiidefiP1 : bpy.props.IntProperty(name="Checkpoint 1 (P1)", min = 0, max = 255, description = "First checkpoint of the range (P1 <= C < P2)", update=updateArea)
    kmp_areaRiidefiP2 : bpy.props.IntProperty(name="Checkpoint 2 (P2)", min = 0, max = 255, description = "Second checkpoint of the range (P1 <= C < P2)", update=updateArea)
    kmp_areaRiidefiInvert : bpy.props.BoolProperty(name="Invert", description = "Checking this option will invert when condition is meet. For example if you have this AREA enabled only when the player is in chosen checkpoint range, it will make it enabled only when the player is OUTSIDE chosen checkpoint range", update=updateArea) 


#endregion
 #region kcl_types   

    #
    #
    # KCL
    #
    #
    
    
    kcl_masterType : bpy.props.EnumProperty(name = "Type", items=[("T00", "Road (0x00)", ''),
                                                            ("T01", "Slippery Road 1 (0x01)", ''),
                                                            ("T02", "Weak Off-road (0x02)", ''),
                                                            ("T03", "Off-road (0x03)", ''),
                                                            ("T04", "Heavy Off-road (0x04)", ''),
                                                            ("T05", "Slippery Road 2 (0x05)", ''),
                                                            ("T06", "Boost Pad (0x06)", ''),
                                                            ("T07", "Boost Ramp (0x07)", ''),
                                                            ("T08", "Jump Pad (0x08)", ''),
                                                            ("T09", "Item Road (0x09)", ''),
                                                            ("T0A", "Solid Fall (0x0A)", ''),
                                                            ("T0B", "Moving Water (0x0B)", ''),
                                                            ("T0C", "Wall (0x0C)", ''),
                                                            ("T0D", "Invisible Wall (0x0D)", ''),
                                                            ("T0E", "Item Wall (0x0E)", ''),
                                                            ("T0F", "Wall 2 (0x0F)", ''),
                                                            ("T10", "Fall Boundary (0x10)", ''),
                                                            ("T11", "Cannon Activator (0x11)", ''),
                                                            ("T12", "Force Recalculation (0x12)", ''),
                                                            ("T13", "Half-pipe Ramp (0x13)", ''),
                                                            ("T14", "Wall 3 (0x14)", ''),
                                                            ("T15", "Moving Road (0x15)", ''),
                                                            ("T16", "Sticky Road (0x16)", ''),
                                                            ("T17", "Road 2 (0x17)", ''),
                                                            ("T18", "Sound Trigger (0x18)", ''),
                                                            ("T19", "Weak Wall (0x19)", ''),
                                                            ("T1A", "Effect Trigger (0x1A)", ''),
                                                            ("T1B", "Item State Modifier (0x1B)", ''),
                                                            ("T1C", "Half-pipe Invisible Road (0x1C)", ''),
                                                            ("T1D", "Moving Road 2 (0x1D)", ''),
                                                            ("T1E", "Special Wall (0x1E)", ''),
                                                            ("T1F", "Wall 5 (0x1F)", ''),
                                                            ])
    kcl_variant : bpy.props.IntProperty(name= "Variant", min=0, max=7, default= 0)
    kcl_shadow : bpy.props.IntProperty(name= "Shadow", min=0, max=7, default= 0)
    kcl_trickable : bpy.props.BoolProperty(name= "Trickable", default=False)
    kcl_drivable : bpy.props.BoolProperty(name= "Drivable", default=True)
    kcl_bounce : bpy.props.BoolProperty(name= "Bounce", default=True)
    
    kclVariantT00 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Normal", ''),
                                                                ("1", "Dirt with GFX (7.3 , 8.3)", ''),
                                                                ("2", "Dirt without GFX", ''),
                                                                ("3", "Smooth", ''),
                                                                ("4", "Wood", ''),
                                                                ("5", "Snow", ''),
                                                                ("6", "Metal grate", ''),
                                                                ("7", "Normal (Sound cuts off)", '')])
    kclVariantT01 : bpy.props.EnumProperty(name = "Variant", items=[("0", "White sand", ''),
                                                                ("1", "Dirt", ''),
                                                                ("2", "Water", ''),
                                                                ("3", "Snow", ''),
                                                                ("4", "Grass", ''),
                                                                ("5", "Yellow sand", ''),
                                                                ("6", "Sand, no GFX", ''),
                                                                ("7", "Dirt, no GFX", '')])
    kclVariantT02 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Orange Sand", ''),
                                                                ("1", "Dirt", ''),
                                                                ("2", "Water", ''),
                                                                ("3", "Grass, darker GFX", ''),
                                                                ("4", "Grass, lighter GFX", ''),
                                                                ("5", "Carpet", ''),
                                                                ("6", "Gravel", ''),
                                                                ("7", "Gravel, different impact SFX", '')])
    kclVariantT03 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Sand", ''),
                                                                ("1", "Dirt", ''),
                                                                ("2", "Mud", ''),
                                                                ("3", "Water, no GFX", ''),
                                                                ("4", "Grass", ''),
                                                                ("5", "Sand, lighter GFX", ''),
                                                                ("6", "Gravel, different impact SFX", ''),
                                                                ("7", "Carpet", '')])
    kclVariantT04 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Sand", ''),
                                                                ("1", "Dirt", ''),
                                                                ("2", "Mud", ''),
                                                                ("3", "Flowers", ''),
                                                                ("4", "Grass", ''),
                                                                ("5", "Snow", ''),
                                                                ("6", "Sand", ''),
                                                                ("7", "Dirt, no GFX", '')])
    kclVariantT05 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Ice", ''),
                                                                ("1", "Mud", ''),
                                                                ("2", "Water", ''),
                                                                ("6", "Normal road, different sound", '')])
    kclVariantT06 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Default", ''),
                                                                ("1", "(Check description)", 'if used in course.kcl and casino_roulette is nearby, the road slowly rotates everything around it counterclockwise. Used in Chain Chomp Wheel.'),
                                                                ("2", "Unknown", '')])
    kclVariantT07 : bpy.props.EnumProperty(name = "Variant", items=[("0", "2 flips", ''),
                                                                ("1", "1 flip", ''),
                                                                ("2", "No flips", '')]) 
    kclVariantT08 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Stage 2, used in GBA Bowser Castle 3", ''),
                                                                ("1", "Stage 3, used in SNES Ghost Valley 2", ''),
                                                                ("2", "Stage 1, used in GBA Shy Guy Beach", ''),
                                                                ("3", "Stage 4, used in Mushroom Gorge", ''),
                                                                ("4", "Stage 5, Bouncy mushroom", ''),
                                                                ("5", "Stage 4, used in Chain Chomp Wheel", ''),
                                                                ("6", "Stage 2, used in DS Yoshi Falls and Funky Stadium", ''),
                                                                ("7", "Stage 4, unused", '')])   
    kclVariantT09 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Unknown", ''),
                                                                ("1", "Unknown", ''),
                                                                ("2", "Used on metal grates", ''),
                                                                ("3", "Unknown. Used on wooden paths/grass/mushrooms", ''),
                                                                ("4", "Unknown", ''),
                                                                ("5", "Unknown. Used on grass/bushes", ''),
                                                                ("6", "Unknown", '')])   
    kclVariantT0A : bpy.props.EnumProperty(name = "Variant", items=[("0", "Sand", ''),
                                                                ("1", "Sand/Underwater", ''),
                                                                ("2", "Unknown", ''),
                                                                ("3", "Ice", ''),
                                                                ("4", "Dirt", ''),
                                                                ("5", "Grass", ''),
                                                                ("6", "Wood", ''),
                                                                ("7", "Unknown", '')])
    kclVariantT0B : bpy.props.EnumProperty(name = "Variant", items=[("0", "Moving water that follows a route, pulling the player downwards.", 'Route settings:\n1 = speed\n2 = unknown'),
                                                                ("1", "Moving water that follows a route and strongly pulls the player downwards, making it hard to drive.", 'Route settings:\n1 = speed\n2 = unknown'),
                                                                ("2", "Moving water that follows a route from the start of the path to the end of it.", 'Route settings:\n1 = unknown\n2 = with value 1, the moving water direction rotates 90 degrees.\nIt also uses two settings in the AREA:\nAt 0x28 = acceleration/deceleration modifier\nAt 0x2A = route speed (speed at which the route pulls the player)\n (Supported by AREA plugin)'),
                                                                ("3", "Moving water with no route.", 'It pulls you down and you cannot move from it'),
                                                                ("4", "Moving asphalt", 'Route settings:\n1 = speed\n2 = unknown'),
                                                                ("6", "Moving road", 'Route settings:\n1 = speed\n2 = unknown')])
    kclVariantT0C : bpy.props.EnumProperty(name = "Variant", items=[("0", "Normal", ''),
                                                                ("1", "Rock", ''),
                                                                ("2", "Metal", ''),
                                                                ("3", "Wood", ''),
                                                                ("4", "Ice", ''),
                                                                ("5", "Bush", ''),
                                                                ("6", "Rope", ''),
                                                                ("7", "Rubber", '')])
    kclVariantT0D : bpy.props.EnumProperty(name = "Variant", items=[("0", "No spark and no character wall hit voice", ''),
                                                                ("1", "Spark and character wall hit voice", '')])
    kclVariantT0E : bpy.props.EnumProperty(name = "Variant", items=[("0", "Unknown", ''),
                                                                ("1", "Unknown. Used on rock walls", ''),
                                                                ("2", "Unknown. Used on metal walls", ''),
                                                                ("3", "Unknown", ''),
                                                                ("4", "Unknown. Unused", ''),
                                                                ("5", "Unknown. Used on grass/bushes", ''),
                                                                ("6", "Unknown. Unused", '')])
    kclVariantT0F : bpy.props.EnumProperty(name = "Variant", items=[("0", "Normal", ''),
                                                                ("1", "Rock", ''),
                                                                ("2", "Metal", ''),
                                                                ("3", "Wood", ''),
                                                                ("4", "Ice", ''),
                                                                ("5", "Bush", ''),
                                                                ("6", "Rope", ''),
                                                                ("7", "Rubber", '')])
    kclVariantT10 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Air fall", ''),
                                                                ("1", "Water", ''),
                                                                ("2", "Lava", ''),
                                                                ("3", "Icy water (Ice on respawn)", ''),
                                                                ("4", "Lava, no GFX", ''),
                                                                ("5", "Burning air fall", ''),
                                                                ("6", "Quicksand", ''),
                                                                ("7", "Short fall", '')])
    kclVariant10Index : bpy.props.IntProperty(name = "KMP Index", default = 0, min = 0, max = 255) 
    kclVariantT11 : bpy.props.EnumProperty(name = "Variant", items=[("0", "To point 0", ''),
                                                                ("1", "To point 1", ''),
                                                                ("2", "To point 2", ''),
                                                                ("3", "To point 3", ''),
                                                                ("4", "To point 4", ''),
                                                                ("5", "To point 5", ''),
                                                                ("6", "To point 6", ''),
                                                                ("7", "To point 7", '')])
    kclVariant12Index : bpy.props.IntProperty(name = "AREA Index", default = 0, min = 0, max = 7) 
    kclVariantT13 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Default", ''),
                                                                ("1", "Boost pad applied", ''),
                                                                ("2", "Unknown", '')])
    kclVariantT14 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Normal", ''),
                                                                ("1", "Rock", ''),
                                                                ("2", "Metal", ''),
                                                                ("3", "Wood", ''),
                                                                ("4", "Ice", ''),
                                                                ("5", "Bush", ''),
                                                                ("6", "Rope", ''),
                                                                ("7", "Rubber", '')])
    kclVariantT15 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Moves west with BeltCrossing and escalator. ", ''),
                                                                ("1", "Moves east with BeltCrossing and west with escalator.", ''),
                                                                ("2", "Moves east with BeltEasy", ''),
                                                                ("3", "Moves west with BeltEasy", ''),
                                                                ("4", "Rotates around BeltCurveA clockwise", ''),
                                                                ("5", "Rotates around BeltCurveA counterclockwise", ''),
                                                                ("6", "Unknown", '')])
    kclVariantT16 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Wood", ''),
                                                                ("1", "Gravel, different impact SFX.", ''),
                                                                ("2", "Carpet", ''),
                                                                ("3", "Dirt, no GFX", ''),
                                                                ("4", "Sand, different impact and drift SFX, no GFX", ''),
                                                                ("5", "Normal road, SFX on slot 4.4", ''),
                                                                ("6", "Normal road", ''),
                                                                ("7", "Mud with GFX", '')])
    kclVariantT17 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Normal road, different sound", ''),
                                                                ("1", "Carpet", ''),
                                                                ("2", "Grass, GFX on 8.3", ''),
                                                                ("3", "Normal road, used on green mushrooms", ''),
                                                                ("4", "Grass", ''),
                                                                ("5", "Glass road with SFX", ''),
                                                                ("6", "Dirt (unused)", ''),
                                                                ("7", "Normal road, SFX on slot 4.4", '')])
    
    kclVariantT18Circuits : bpy.props.EnumProperty(name = "Track", items=[("11", "Luigi Circuit", ''),
                                                                ("13", "Mushroom Gorge", ''),
                                                                ("14", "Toad's Factory", ''),
                                                                ("21", "Mario Circuit", ''),
                                                                ("22", "Coconut Mall", ''),
                                                                ("23", "DK Summit (Snowboard Cross)", ''),
                                                                ("24", "Wario's Gold Mine", ''),
                                                                ("31", "Daisy Circuit", ''),
                                                                ("32", "Koopa Cape", ''),
                                                                ("33", "Maple Treeway", ''),
                                                                ("34", "Grumble Volcano", ''),
                                                                ("41", "Dry Dry Ruins", ''),
                                                                ("42", "Moonview Highway", ''),
                                                                ("43", "Bowser's Castle", ''),
                                                                ("44", "Rainbow Road", ''),
                                                                ("54", "N64 Mario Raceway", ''),
                                                                ("61", "N64 Sherbet Land", ''),
                                                                ("63", "DS Delfino Square", ''),
                                                                ("73", "N64 DK's Jungle Parkway", ''),
                                                                ("74", "GCN Mario Circuit", ''),
                                                                ("83", "GCN DK Mountain", ''),
                                                                ("84", "N64 Bowser's Caslte", '')])
    kclVariantT1811 : bpy.props.EnumProperty(name = "Variant", items=[("0", "No audience noise", ''),
                                                ("1", "Soft audience noise", ''),
                                                ("2", "Audience noise. The race starts with this sound", ''),
                                                ("3", "Lound audience noice", '')])
    kclVariantT1813 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Deactivate all", ''),
                                                ("3", "Enable cave SFX + echo", '')])
    kclVariantT1814 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Sounds off", ''),
                                                ("1", "Hydraulic press area", ''),
                                                ("2", "Shipping dock area", ''),
                                                ("3", "Moving belt area", ''),
                                                ("4", "Steam room", ''),
                                                ("5", "Restart music at beginning", ''),
                                                ("6", "Bulldozer area", ''),
                                                ("7", "Audience area", '')])
    kclVariantT1821 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Deactivates echo", ''),
                                                ("1", "Weak echo", ''),
                                                ("2", "Loud echo", '')])
    kclVariantT1822 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Resets all sound triggers. Shopping mall ambience requires this to play", ''),
                                                ("1", "Weak shopping mall ambience + disables echo", ''),
                                                ("2", "Loud shopping mall ambience + strong echo", ''),
                                                ("3", "Resets all sound triggers and prevents shopping mall ambience from playing until 0 is hit again", ''),
                                                ("4", "Loud shopping mall ambience + disables echo", ''),
                                                ("5", "Same as 3?", '')])
    kclVariantT1823 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Deactivates cheering", ''),
                                                ("1", "Weak cheering ambience", ''),
                                                ("2", "Loud cheering ambience", ''),
                                                ("3", "Loudest cheering ambience.", ''),
                                                ("4", "Enables cheering when going off half-pipe ramps", '')])
    kclVariantT1824 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Music change (outside)", ''),
                                                ("1", "Music change (cave) + gentle echo", ''),
                                                ("2", "Echo", ''),
                                                ("3", "Strong echo", '')])
    kclVariantT1831 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Deactivate echo", ''),
                                                ("1", "Weak echo", ''),
                                                ("2", "Echo", '')])
    kclVariantT1832 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Music change (normal)", ''),
                                                ("1", "Music change (normal), echo", ''),
                                                ("2", "Stronger echo", ''),
                                                ("3", "Music change (underwater), water ambience enabled when entering from 0, 5 or 6, diabled otherwise", ''),
                                                ("4", "Strongest echo, water ambience enabled", ''),
                                                ("5", "Music change (normal), strongest echo, water ambience enabled when entering from 3", ''),
                                                ("6", "Music change (riverside)", '')])
    kclVariantT1833 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Deactivate echo and wind ambience", ''),
                                                ("1", "No effect", ''),
                                                ("2", "Weak echo", ''),
                                                ("3", "Loud echo", ''),
                                                ("4", "Enables wind ambience, deactivates echo", '')])
    kclVariantT1834 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Deactivate echo", ''),
                                                ("1", "Weak echo, toggles after two seconds", ''),
                                                ("2", "Loud echo, toggles after one second", ''),
                                                ("3", "Loud echo, toggles after two seconds", '')])
    kclVariantT1841 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Music change (normal)", ''),
                                                ("1", "Music change (indoors, where the bats come from the sides)", ''),
                                                ("2", "Music change (indoors, where the half-pipes are)", ''),
                                                ("3", "Music change (indoors, where the Pokeys are)", '')])
    kclVariantT1842 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Deactivate city ambience, default music", ''),
                                                ("1", "Stage 2, weak city ambience, adds flute to music", ''),
                                                ("2", "Stage 4, louder city ambience, disable echo", ''),
                                                ("3", "Stage 5, loudest city ambience, disable echo", ''),
                                                ("4", "Stage 3, loud city ambience, enable echo", ''),
                                                ("5", "Stage 1, weakest city ambience, enable echo", '')])
    kclVariantT1843 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Disable one-time use sound trigger (like Bowser's howl)", ''),
                                                ("1", "Bowser's howl + echo. Put 7 at the end of a turn to be able to reuse Bowser's howl", ''),
                                                ("2", "Sound distortion + echo", ''),
                                                ("3", "Deactivate sound distortion + echo", ''),
                                                ("4", "Add drums + echo on music + koopaBall/koopaFigure SFX", ''),
                                                ("5", "Deactivate koopaBall/koopaFigure SFX", ''),
                                                ("6", "Add drums without echo", ''),
                                                ("7", "Back to normal. Allow reuse for one-time use sound trigger", '')])
    kclVariantT1844 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Deactivator", ''),
                                                ("1", "Gate sound 1 (add a deactivator before and after if you use only one gate)", ''),
                                                ("2", "Star ring sound 1", ''),
                                                ("3", "Star ring sound 2", ''),
                                                ("4", "Star ring sound 3", ''),
                                                ("5", "Star ring sound 4", ''),
                                                ("6", "Tunnel sound (add a deactivator to stop it)", '')])
    kclVariantT1854 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Deactivates cheering", ''),
                                                ("1", "Loud cheering", ''),
                                                ("2", "Louder cheering", ''),
                                                ("3", "Weak cheering", '')])
    kclVariantT1861 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Deactivate all", ''),
                                                ("1", "Cave echo", ''),
                                                ("2", "Cave SFX", '')])
    kclVariantT1863 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Unknown. In a position such that a player may collide with this trigger if they complete the dock shortcut", ''),
                                                ("1", "Very, very distant whistles, cheers and chatter from spectators", ''),
                                                ("2", "Very distant whistles, cheers and chatter from spectators", ''),
                                                ("3", "Distant whistles, cheers and chatter from spectators", ''),
                                                ("4", "Whistles, cheers and chatter from spectators", ''),
                                                ("5", "Single wind gust just before the dock section", ''),
                                                ("6", "No spectator ambience", ''),
                                                ("7", "The same as 6? Used between triggers of type 6", '')])
    kclVariantT1873 : bpy.props.EnumProperty(name = "Variant", items=[("0", "No jungle ambience. Used near water sections", ''),
                                                ("1", "Jungle ambience (bird squawks, insect hum, animal roar). Used as a buffer between types 0 and 2", ''),
                                                ("2", "Intense jungle ambience, used in areas of deep forest", ''),
                                                ("3", "Cave ambience", '')])
    kclVariantT1874 : bpy.props.EnumProperty(name = "Variant", items=[("0", "No echo", ''),
                                                ("1", "Weak echo", ''),
                                                ("2", "Loud echo", '')])
    kclVariantT1883 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Deactivate all", ''),
                                                ("1", "Jungle SFX (animals)", ''),
                                                ("2", "Water + wind SFX", '')])
    kclVariantT1884 : bpy.props.EnumProperty(name = "Variant", items=[("0", "Disable one-time use sound trigger (like Bowser's howl)", ''),
                                                ("1", "Turns lava SFX off + disables echo", ''),
                                                ("2", "Bowser's howl. Put 0 at the end of a turn to be able to reuse this", ''),
                                                ("3", "Turns lava SFX off", ''),
                                                ("4", "Turns lava SFX off + echo", ''),
                                                ("5", "Echo", ''),
                                                ("6", "Strong echo", '')])

    kclVariantT1A : bpy.props.EnumProperty(name = "Variant", items=[("0", "BRSTM reset", ''),
                                                                ("1", "Enable shadow effect", ''),
                                                                ("2", "Water splash (pocha)", ''),
                                                                ("3", "starGate door activation", ''),
                                                                ("4", "Half-pipe cancellation", ''),
                                                                ("5", "Coin despawner", ''),
                                                                ("6", "Smoke effect on the player when going through dark smoke (truckChimSmkW)", ''),
                                                                ("7", "Unknown", '')])
    kclVariantT1D : bpy.props.EnumProperty(name = "Variant", items=[("0", "Carpet, different impact SFX", ''),
                                                                ("1", "Normal road, different sound, different impact SFX", ''),
                                                                ("2", "Normal road", ''),
                                                                ("3", "Glass road", ''),
                                                                ("4", "Carpet", ''),
                                                                ("5", "No sound, star crash impact SFX (requires starGate for SFX)", ''),
                                                                ("6", "Sand", ''),
                                                                ("7", "Dirt", '')])
    kclVariantT1E : bpy.props.EnumProperty(name = "Variant", items=[("0", "Cacti", ''),
                                                                ("1", "Unknown (rubber wall?)", ''),
                                                                ("2", "Unknown (rubber wall?)", ''),
                                                                ("3", "Unknown", ''),
                                                                ("4", "Unknown, SFX on 4.4", ''),
                                                                ("5", "Unknown", ''),
                                                                ("6", "Unknown", ''),
                                                                ("7", "Unknown", '')])
    kclVariantT1F : bpy.props.EnumProperty(name = "Variant", items=[("0", "Fast Wall, Bump", ''),
                                                                ("2", "Slow Wall, No Effect", '')])    

    kclFinalFlag : bpy.props.StringProperty(name = "Flag")                                                            
#endregion
#region kcl_settings
    kcl_applyMaterial : bpy.props.EnumProperty(name = "Material", items=[("0", "Random color", ''),
                                                                        ("1", "Keep original", '')])
    kcl_applyName : bpy.props.EnumProperty(name = "Name", items=[("0", "Flag only", ''),
                                                                    ("1", "Add type label", ''),
                                                                    ("2", "Add type and variant label", ''),
                                                                    ("3", "Add to original", ''),
                                                                    ("4", "Add to mesh name only",'')])
#endregion

labelDict = {
    "T00": "ROAD",
    "T01": "SLIPPERY1",
    "T02": "WEAK_OFFROAD",
    "T03": "OFFROAD",
    "T04": "HEAVY_OFFROAD",
    "T05": "SLIPPERY2",
    "T06": "BOOST_PANEL",
    "T07": "BOOST_RAMP",
    "T08": "JUMP_PAD",
    "T09": "ITEM_ROAD",
    "T0A": "SOLID_FALL",
    "T0B": "MOVING_ROAD",
    "T0C": "WALL",
    "T0D": "INVISIBLE_WALL",
    "T0E": "ITEM_WALL",
    "T0F": "WALL_3",
    "T10": "FALL_BOUNDARY",
    "T11": "CANNON",
    "T12": "FORCE_RECALCULATION",
    "T13": "HALFPIPE",
    "T14": "WALL_4",
    "T15": "MOVING_ROAD",
    "T16": "STICKY_ROAD",
    "T17": "ROAD",
    "T18": "SOUND_TRIGGER",
    "T19": "WEAK_WALL",
    "T1A": "EFFECT_TRIGGER",
    "T1B": "ITEM_STATE_MODIFIER",
    "T1C": "HALFPIPE_WALL",
    "T1D": "MOVING_ROAD",
    "T1E": "SPECIAL_WALL",
    "T1F": "WALL_5"
    
    

}

current_version = "v0.1.5.-3"
latest_version = "v0.1.5.-3"

kcl_typeATypes = ["T00","T01","T02","T03","T04","T05","T06","T07","T08","T09","T0A","T16","T17","T1D"]
kcl_wallTypes = ["T0C","T0D","T0E","T0F","T1E","T1F", "T19"]

class openGithub(bpy.types.Operator):
    bl_idname = "open.download"
    bl_label = "Download from GitHub"

    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        webbrowser.get().open('http://www.github.com/Gabriela-Orzechowska/Blender-KMP-Utilities/releases/latest')
        return {'FINISHED'}

class KMPUtilities(bpy.types.Panel):
    global latest_version
    bl_label = "Main Utilities"
    bl_idname = "_PT_KMP_"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        if(latest_version != current_version):
            newVersionLayout = layout.column()
            newVersionLayout.label(text="New version available!: " + latest_version)
            newVersionLayout.operator("open.download")
            newVersionLayout.label(text="")
        
        layout.prop(mytool, "scale")
        layout.operator("kmpc.load")
        layout.operator("kmpc.cursor")
        layout.operator("kmpc.gobj")
        layout.operator("mkw.objectmerge")

class KCLSettings(bpy.types.Panel):
    bl_label = "KCL Settings"
    bl_idname = "_PT_KCL_SET_"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        layout.prop(mytool, "kcl_applyMaterial")
        layout.prop(mytool, "kcl_applyName")

class KCLUtilities(bpy.types.Panel):
    global finalFlag
    global kcl_typeATypes
    bl_label = "KCL Utilities"
    bl_idname = "_PT_KCL_"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt   
        layout.operator("kclc.load")
        layout.prop(mytool, "kcl_masterType")
        variantPropName = "kclVariant" + mytool.kcl_masterType
        layout.prop(mytool, variantPropName)
        if(mytool.kcl_masterType == "T10"):
            layout.prop(mytool, "kclVariant10Index")
        if(mytool.kcl_masterType == "T12"):
            layout.prop(mytool, "kclVariant12Index")
        if(mytool.kcl_masterType == "T18"):
            layout.prop(mytool, "kclVariantT18Circuits")
            t18variant = "kclVariantT18" + mytool.kclVariantT18Circuits
            layout.prop(mytool, t18variant)
        if(mytool.kcl_masterType in kcl_typeATypes):
            layout.prop(mytool, "kcl_shadow")
            layout.prop(mytool, "kcl_trickable")
            layout.prop(mytool, "kcl_drivable")
        if(mytool.kcl_masterType == "T19"):
            layout.label(text = "Nintendo  uses  this  type  without")    
            layout.label(text = "'Bounce' flag.")  
        if(mytool.kcl_masterType in kcl_wallTypes):
            layout.prop(mytool, "kcl_bounce") 
        
        layout.operator("kclc.applyflag")
        layout.operator("kclc.export")
        
class AREAUtilities(bpy.types.Panel):
    bl_label = "AREA Utilities"
    bl_idname = "_PT_KMP_AREA_"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        layout.operator("kmpc.area")
        layout.label(text="Create AREA")
        area_create_column = layout.column()
        area_create_column.operator("kmpc.c_cube_area")
        area_create_column.operator("kmpc.c_cylinder_area")
        
        layout.label(text="AREA Settings")
        area_setting_column = layout.column()
        area_setting_column.prop(mytool, "kmp_areaEnumType")
        area_setting_column.prop(mytool, "kmp_areaPrority")
        if(mytool.kmp_areaEnumType == "A0"):
            area_setting_column.prop(mytool, "kmp_areaID")
        elif(mytool.kmp_areaEnumType == "A1"):
            area_setting_column.prop(mytool, "kmp_areaEvnKarehaUp")
        elif(mytool.kmp_areaEnumType == "A2"):
            area_setting_column.prop(mytool, "kmp_areaPostEffectEntry")
        elif(mytool.kmp_areaEnumType == "A3"):
            area_setting_column.prop(mytool, "kmp_areaRoute")
            area_setting_column.label(text="Variant 0x0002 Settings ")
            area_setting_column.prop(mytool, "kmp_areaMovingRouteSet1")
            area_setting_column.prop(mytool, "kmp_areaMovingRouteSet2")
        elif(mytool.kmp_areaEnumType == "A4"):
             area_setting_column.prop(mytool, "kmp_areaEnemy")
        elif(mytool.kmp_areaEnumType == "A6"):
             area_setting_column.prop(mytool, "kmp_areaIDK1")
             area_setting_column.prop(mytool, "kmp_areaIDK2")
        elif(mytool.kmp_areaEnumType == "A8" or mytool.kmp_areaEnumType == "A9"):
             area_setting_column.prop(mytool, "kmp_areaGroup")
        elif(mytool.kmp_areaEnumType == "A10"):
            area_setting_column.prop(mytool, "kmp_areaUseCOOB")
            if(mytool.kmp_areaUseCOOB):
                area_setting_column.prop(mytool, "kmp_areaCOOBVersion")
                if(mytool.kmp_areaCOOBVersion == "kHacker"):
                    area_setting_column.prop(mytool, "kmp_areakHackerMode")
                    area_setting_column.prop(mytool, "kmp_areakHackerCheckpoint")
                elif(mytool.kmp_areaCOOBVersion == "Riidefi"):
                    area_setting_column.prop(mytool, "kmp_areaRiidefiP1")
                    area_setting_column.prop(mytool, "kmp_areaRiidefiP2")
                    area_setting_column.prop(mytool, "kmp_areaRiidefiInvert")

        
        if(bpy.context.object is not None):
            current_mode = bpy.context.object.mode
        else:
            current_mode = 'OBJECT'
        
        if(current_mode != 'OBJECT'):
            area_create_column.enabled = False
        else:
            area_create_column.enabled = True
        
def replace_material(bad_mat, good_mat):
    bad_mat.user_remap(good_mat)
    bpy.data.materials.remove(bad_mat)
    
    
def get_duplicate_materials(og_material):
    
    common_name = og_material.name
    
    if common_name[-3:].isnumeric():
        common_name = common_name[:-4]
    
    duplicate_materials = []
    
    for material in bpy.data.materials:
        if material is not og_material:
            name = material.name
            if name[-3:].isnumeric() and name[-4] == ".":
                name = name[:-4]
            
            if name == common_name:
                duplicate_materials.append(material)
    
    text = "{} duplicate materials found"
    
    return duplicate_materials


def remove_all_duplicate_materials():
    i = 0
    while i < len(bpy.data.materials):
        
        og_material = bpy.data.materials[i]
        
        
        # get duplicate materials
        duplicate_materials = get_duplicate_materials(og_material)
        
        # replace all duplicates
        for duplicate_material in duplicate_materials:
            replace_material(duplicate_material, og_material)
        
        # adjust name to no trailing numbers
        if og_material.name[-3:].isnumeric() and og_material.name[-4] == ".":
            og_material.name = og_material.name[:-4]
            
        i = i+1
    



#endregion
finalFlag = ''
properFlag = ''
class apply_kcl_flag(bpy.types.Operator):
    global kcl_typeATypes, finalFlag, kcl_wallTypes, properFlag
    bl_idname = "kclc.applyflag"
    bl_label = "Apply Flag"
    bl_options = {'UNDO'}
    bl_description = "Apply current flag"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        variantPropName = "kclVariant" + mytool.kcl_masterType
        z = '000'
        if(hasattr(mytool, variantPropName)):
            z = getattr(mytool, variantPropName)
            z = '{:03b}'.format(int(z)).zfill(3)
        if(mytool.kcl_masterType == 'T18'):
            t18variant = "kclVariantT18" + mytool.kclVariantT18Circuits
            z = getattr(mytool,t18variant)
            z = '{:03b}'.format(int(z))
        typeaflag = ''
        if(mytool.kcl_masterType in kcl_typeATypes):
            y = mytool.kcl_shadow
            y = '{:03b}'.format(int(y))
            w = "0" + str(int(mytool.kcl_drivable == False)) + str(int(mytool.kcl_trickable))
            typeaflag = w+"00"+y
        a = '{:01b}'.format(int(mytool.kcl_masterType[1],16))
        b = '{:04b}'.format(int(mytool.kcl_masterType[2],16))
        flag = typeaflag+z+a+b
        if(mytool.kcl_masterType == 'T10'):
            flag = '{:08b}'.format(mytool.kclVariant10Index)+z+a+b
        if(mytool.kcl_masterType == 'T12'):
            flag = '{:08b}'.format(mytool.kclVariant12Index)+a+b
        if(mytool.kcl_masterType in kcl_wallTypes):
            w = int(mytool.kcl_bounce == False)
            flag = str(w)+"0000000"+z+a+b

        finalFlag = '{:04x}'.format(int(flag,2))
        mytool.kclFinalFlag = finalFlag 
        properFlag = "_"+mytool.kcl_masterType[1:]+"_F"+finalFlag
        properFlag = properFlag.upper()
        activeObject = context.active_object
        if(activeObject.type != "MESH"):
            self.report({'WARNING', "Selected object is not a mesh."})
            return {'FINISHED'}
        if(mytool.kcl_applyName == "1"):   
            properFlag = labelDict[mytool.kcl_masterType] + properFlag
        elif(mytool.kcl_applyName == "2"):   
            variant = '{:03x}'.format(int(flag[:-5],2)).upper()
            properFlag = labelDict[mytool.kcl_masterType] + "_"+ variant + properFlag
        elif(mytool.kcl_applyName == "3"):  
            objName = activeObject.name
            if(objName[-3:].isnumeric() and objName[-4] == "."):
                objName = objName[:-4]
            if(checkFlagInName(objName)):
                objName = objName[:-9]
            if(objName[-3:].isnumeric() and objName[-4] == "."):
                objName = objName[:-4]
            properFlag = objName + properFlag
        elif(mytool.kcl_applyName == "4"):  
            objName = activeObject.data.name
            if(objName[-3:].isnumeric() and objName[-4] == "."):
                objName = objName[:-4]
            if(checkFlagInName(objName)):
                objName = objName[:-9]
            if(objName[-3:].isnumeric() and objName[-4] == "."):
                objName = objName[:-4]
            properFlag = objName + properFlag
        if(mytool.kcl_applyName is not "4"):
            activeObject.name = properFlag
        activeObject.data.name = properFlag
        if(mytool.kcl_applyMaterial == "1"):
            return {'FINISHED'}
        context.active_object.data.materials.clear()
        mat = bpy.data.materials.get(properFlag)
        if mat is None:
            mat = bpy.data.materials.new(name=properFlag)
            mat.diffuse_color = (random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),1)
        context.active_object.data.materials.append(mat)


        return {'FINISHED'}

class export_kcl_file(bpy.types.Operator, ExportHelper):
    bl_idname = "kclc.export"
    bl_label = "Export KCL"
    bl_options = {'UNDO'}
    filename_ext = ".kcl"

    filter_glob: bpy.props.StringProperty(
        default='*.kcl',
        options={'HIDDEN'}
    )
    kclExportSelection : bpy.props.BoolProperty(name="Selection only", default=False)
    kclExportScale : bpy.props.FloatProperty(name="Scale", min = 0.0001, max = 10000, default = 1)
    kclExportLowerWalls : bpy.props.BoolProperty(name="Lower Walls", default=True)
    kclExportLowerWallsBy : bpy.props.IntProperty(name="Lower Walls by", default= 30)
    kclExportLowerDegree : bpy.props.IntProperty(name="Degree", default= 45)
    kclExportWeakWalls : bpy.props.BoolProperty(name="Weak Walls")
    kclExportDropUnused : bpy.props.BoolProperty(name="Drop Unused")
    kclExportDropFixed : bpy.props.BoolProperty(name="Drop Fixed")
    kclExportDropInvalid : bpy.props.BoolProperty(name="Drop Invalid")
    kclExportRemoveFacedown : bpy.props.BoolProperty(name="Remove facedown road", default=True)
    kclExportRemoveFaceup : bpy.props.BoolProperty(name="Remove faceup walls", default=True)

    def execute(self, context):
        filepath = self.filepath

        bpy.ops.export_scene.obj(filepath=filepath, use_selection=self.kclExportSelection, use_blen_objects=False, use_materials=False, use_normals=True, use_triangles=True, group_by_object=True, global_scale=self.kclExportScale)
        
        wkclt = "wkclt encode \"" + filepath + "\" -o --kcl="
        wkclt += ("WEAKWALLS," if self.kclExportWeakWalls else "")
        wkclt += ("DROPUNUSED," if self.kclExportDropUnused else "")
        wkclt += ("DROPFIXED," if self.kclExportDropFixed else "")
        wkclt += ("DROPINVALID," if self.kclExportDropInvalid else "")
        wkclt += ("RMFACEDOWN," if self.kclExportRemoveFacedown else "")
        wkclt += ("RMFACEUP," if self.kclExportRemoveFaceup else "")
        
        script_file = os.path.normpath(__file__)
        directory = os.path.dirname(script_file)
        if (self.kclExportLowerWalls):
            wkclt += (" --kcl-script=\"" + directory + "\lower-walls.txt\" --const lower=" + str(self.kclExportLowerWallsBy) + ",degree=" + str(self.kclExportLowerDegree) if self.kclExportLowerWalls else "")
        os.system(wkclt)

        return {'FINISHED'}

class import_kcl_file(bpy.types.Operator, ImportHelper):
    bl_idname = "kclc.load"
    bl_label = "Import KCL file"       
    filename_ext = '.kcl'
    bl_description = "Loads KCL file"
    
    filter_glob: bpy.props.StringProperty(
        default='*.kcl',
        options={'HIDDEN'}
    )
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale

        filepath = self.filepath
        os.system("del \""+filepath[:-3]+"flag\"")
        os.system("wkclt cff \"" + filepath + "\" -o")
        file = open(filepath[:-3]+"flag") 
        flags = []
        i = 0
        n = 48
        while(i in range(n)):
            file.readline()
            i += 1
        a = True
        while a:
            line = file.readline()
            line = line.replace("\t","")
            line = line[:-48].strip()
            flag = line.split("=")[0]
            if(flag is not ''):
                flags.append(flag)
            if not line:
                a = False
        file.close()
        os.system("del \""+filepath[:-3]+"flag\"")
        os.system("wkclt decode \"" + filepath + "\" -o")
        bpy.ops.import_scene.obj(filepath=filepath[:-3]+"obj")
        os.system("del \""+filepath[:-3]+"obj\"")
        os.system("del \""+filepath[:-3]+"mtl\"")
        context.view_layer.objects.active = bpy.context.selected_objects[0]
        objs = bpy.context.selected_objects
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type='MATERIAL')
        bpy.ops.object.mode_set(mode='OBJECT')
        objs = bpy.context.selected_objects
        remove_all_duplicate_materials()
        for obj in objs:
            materialName = obj.material_slots[0].name
            i = 0
            materialName = materialName.split("_")
            v = int(materialName[1])
            for f in flags:
                if(f.startswith(materialName[0].upper())):
                    i += 1
                    if(i == v):
                        splitF = f.split("_")
                        properFlag = "_" + splitF[1] + "_" + splitF[2]
                        label = labelDict["T"+splitF[1]]
                        labelFlag = label+properFlag
                        obj.name = labelFlag
                        obj.data.name = labelFlag
                        obj.data.materials.clear()
                        mat = bpy.data.materials.get(properFlag)
                        if mat is None:
                            mat = bpy.data.materials.new(name=properFlag)
                            mat.diffuse_color = (random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),1)
                        obj.data.materials.append(mat)

        
        return {'FINISHED'}

class export_autodesk_dae(bpy.types.Operator, ExportHelper):
    bl_idname = "export.autodesk_dae"
    bl_label = "Export Autodesk DAE"    
    bl_description = "Export BrawlBox/BrawlCrate friendly Collada (.dae) file"
    filename_ext = ".dae"
    daeExportPathMode : bpy.props.EnumProperty(name="Path Mode", items=[('AUTO', "Auto", ""),
                                                                        ('COPY', "Copy", "")])
    daeExportSelection : bpy.props.BoolProperty(name="Selection only", default = False)
    daeExportCollection : bpy.props.BoolProperty(name="Active collection", default = False)
    daeExportScale : bpy.props.FloatProperty(name="Scale", default = 1)



    def execute(self, context):
        filepath = self.filepath
        os.system("del \"" + filepath[:-4]+"-pomidor.dae\"")
        bpy.ops.export_scene.fbx(filepath = filepath, use_selection = self.daeExportSelection,  filter_glob='*.dae', use_active_collection = self.daeExportCollection, global_scale = self.daeExportScale, apply_scale_options='FBX_SCALE_NONE', object_types={'MESH'}, use_mesh_modifiers=True)
        script_file = os.path.normpath(__file__)
        directory = os.path.dirname(script_file)
        converterDir = "\"" + directory + "\\bin\\FbxConverter.exe" + "\""
        command = converterDir + " \"" + filepath + "\" \"" + filepath[:-4]+"-pomidor.dae" + "\" /sffFBX /dffCOLLADA /v"
        os.system("\"" + command + "\"")
        os.system("del \"" + filepath+"\"")
        filename = filepath.split("\\")[-1]
        os.system("rename \"" + filepath[:-4]+"-pomidor.dae\" \"" + filename + "\"")

        return {'FINISHED'}

def export_autodesk_dae_button(self, context):
    self.layout.operator("export.autodesk_dae", text="Autodesk Collada (.dae)")
    
def join_duplicate_objects(main_object, duplicate_object):
    bpy.ops.object.select_all(action='DESELECT')
    obj1 = bpy.data.objects.get(duplicate_object)
    obj2 = bpy.data.objects.get(main_object)
    if(obj1 and obj2):
        if(obj1.type != 'MESH' and obj2.type != 'MESH'):
            return
        bpy.context.view_layer.objects.active = obj2
        obj2.select_set(True)
        obj1.select_set(True)
        bpy.ops.object.join() 
        bpy.ops.object.select_all(action='DESELECT')

def get_duplicated_names(original_name):
    common_name = original_name

    if(common_name[-3:].isnumeric()):
        if(common_name[-4] == '.'):
            common_name = common_name[:-4]

    duplicated_names = []
    objects=[ob for ob in bpy.context.view_layer.objects if ob.visible_get()]
    for obj in objects:
        if(obj.name is not original_name and obj.type == 'MESH'):
            
            name = obj.name
            if(name[-3:].isnumeric() and name[-4] =='.'):
                name = name[:-4]
            if(name == common_name):
                duplicated_names.append(obj.name)
    return duplicated_names

class merge_duplicate_objects(bpy.types.Operator):
    bl_idname = "mkw.objectmerge"
    bl_label = "Merge duplicate objects"
    bl_description = "Joins objects with duplicate names (*.001, *.002 etc.)"
    bl_options = {'UNDO'}
    def execute(self, context):
        i = 0
        bpy.ops.object.select_all(action='DESELECT')
        objects=[ob.name for ob in bpy.context.view_layer.objects if ob.visible_get()]
        meshes=[ob.data for ob in bpy.context.view_layer.objects if ob.visible_get()]
		
        while i < len(objects):
            objName = objects[i]
            duplicate_names = get_duplicated_names(objName)
            for name in duplicate_names:
                join_duplicate_objects(objName, name)
            if(objName[-3:].isnumeric() and objName[-4] == "."):
                obj1 = bpy.data.objects.get(objName)
                if(obj1):
                    obj1.name = objName[:-4]
                    obj1.data.name = objName[:-4]
            MeshName = meshes[i].name
            if(MeshName[-3:].isnumeric() and MeshName[-4] == "."):
                meshes[i].name = MeshName[:-4]
            i=i+1
        i = 0
        objects=[ob.name for ob in bpy.context.view_layer.objects if ob.visible_get()]
        meshes=[ob.data for ob in bpy.context.view_layer.objects if ob.visible_get()]
		
        while i < len(objects):
            objName = objects[i]
            duplicate_names = get_duplicated_names(objName)
            for name in duplicate_names:
                join_duplicate_objects(objName, name)
            if(objName[-3:].isnumeric() and objName[-4] == "."):
                obj1 = bpy.data.objects.get(objName)
                if(obj1):
                    obj1.name = objName[:-4]
                    obj1.data.name = objName[:-4]
            MeshName = meshes[i].name
            if(MeshName[-3:].isnumeric() and MeshName[-4] == "."):
                meshes[i].name = MeshName[:-4]
            i=i+1
        
        return {'FINISHED'}

class cursor_kmp (bpy.types.Operator):
    bl_idname = "kmpc.cursor"
    bl_label = "3D Cursor position to KMP Cloud"
    bl_description = "Converts current 3D Cursor position and puts into clipboard"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        cursor_position = context.scene.cursor.location
        scale = mytool.scale
        xpos = round(cursor_position[0] * scale, 2)
        ypos = round(cursor_position[2] * scale, 2)
        zpos = round(cursor_position[1] * scale * -1, 2) 

        position = str(xpos) + "\t" + str(ypos) + "\t" + str(zpos)
        bpy.context.window_manager.clipboard = position
        return {'FINISHED'}

class kmp_gobj (bpy.types.Operator):
    bl_idname = "kmpc.gobj"
    bl_label = "Selected to KMP Cloud GOBJ"
    bl_description = "Converts selected objects position and puts them into clipboard as GOBJ"
    
    def execute(self, context):
        data = ""
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        selected = bpy.context.selected_objects
        x = 0
        for object in selected:
            object_position = object.location
            xpos = round(object_position[0] * scale, 2)
            ypos = round(object_position[2] * scale, 2)
            zpos = round(object_position[1] * scale * -1, 2)
            xrot = round(math.degrees(object.rotation_euler[0]), 2)
            yrot = round(math.degrees(object.rotation_euler[2]), 2)
            zrot = round(math.degrees(object.rotation_euler[1]), 2)
            xscl = round(object.scale[0],2)
            yscl = round(object.scale[2],2)
            zscl = round(object.scale[1],2)
            position = str(x) + "\t" + str(xpos) + "\t" + str(ypos) + "\t" + str(zpos) + "\t" + str(xrot) + "\t" + str(yrot) + "\t" + str(zrot) + "\t" + str(xscl) + "\t" + str(yscl) + "\t" + str(zscl) + "\tFFFF\t0000\t0000\t0000\t0000\t0000\t0000\t0000\t0000\t003F\n"
            data = data + position
            x = x + 1
        
        bpy.context.window_manager.clipboard = data
        return {'FINISHED'}
    
class kmp_area (bpy.types.Operator):
    bl_idname = "kmpc.area"
    bl_label = "AREA to KMP Cloud"
    bl_description = "Converts selected objects position and puts them into clipboard as AREA"
    
    def execute(self, context):
        data = ""
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        selected = bpy.context.selected_objects
        x = 0
        for object in selected:
            if not object.name.startswith("AREA_"):
                self.report({"WARNING"}, "One or more selected objects is not a proper AREA")
                return {'CANCELLED'}
            
        for object in selected:
            object_position = object.location
            name = object.name
            properties = name.split("_")
            areaNumber = '0x{0:0{1}X}'.format(int(properties[1]), 2)[2:]
            areaShape = '0x{0:0{1}X}'.format(int(properties[2]), 2)[2:]
            areaType = '0x{0:0{1}X}'.format(int(properties[3]), 2)[2:]
            areaID = "FF" if properties[4] == "-1" else '0x{0:0{1}X}'.format(int(properties[4]), 2)[2:]
            areaPrority = '0x{0:0{1}X}'.format(int(properties[5]), 2)[2:]
            areaSet1 = '0x{0:0{1}X}'.format(int(properties[6]), 4)[2:]
            areaSet2 = '0x{0:0{1}X}'.format(int(properties[7]), 4)[2:]
            areaSet = str(areaSet1) + str(areaSet2)
            areaRoute = '0x{0:0{1}X}'.format(int(properties[8]), 2)[2:]
            if properties[8] == "-1":
                areaRoute = "FF"
            areaEnemy = '0x{0:0{1}X}'.format(int(properties[9]), 2)[2:]
            if properties[9] == "-1":
                areaEnemy = "FF"
            xpos = round(object_position[0] * scale, 2)
            ypos = round(object_position[2] * scale, 2)
            zpos = round(object_position[1] * scale * -1, 2)
            xrot = round(math.degrees(object.rotation_euler[0]), 2)
            yrot = round(math.degrees(object.rotation_euler[2]), 2)
            zrot = round(math.degrees(object.rotation_euler[1]), 2)
            xscl = round(object.scale[0],2)
            yscl = round(object.scale[2],2)
            zscl = round(object.scale[1],2)
            dataValue = str("%02d" % x) + "\t" + str(areaShape) + "\t" + str(areaType) + "\t" + str(areaID) + "\t" + str(areaPrority)  + "\t" +\
            str(xpos) + "\t" + str(ypos) + "\t" + str(zpos) + "\t" + str(xrot) + "\t" + str(yrot) + "\t" + str(zrot) + "\t" + str(xscl) + "\t" + str(yscl) + "\t" + str(zscl) +\
            "\t" + str(areaSet) + "\t" + str(areaRoute) + str(areaEnemy) + "\t0000\n"
            data = data + dataValue
            x = x + 1
            
        bpy.context.window_manager.clipboard = data
        return {'FINISHED'}


class kmp_c_cube_area (bpy.types.Operator):
    bl_idname = "kmpc.c_cube_area"
    bl_label = "Create cube AREA Model"
    bl_description = "Creates a cubic AREA Model is proper scale and origin (Move it only in OBJECT mode)"
    bl_options = {'UNDO'}   
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        cursor_position = context.scene.cursor.location
        
        existingAreas = 0
        for obj in bpy.data.objects:
            if "area_" in obj.name.lower():
                existingAreas = existingAreas + 1
        
        bpy.ops.mesh.primitive_cube_add(size=10000/scale, location=cursor_position)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.translate(value=(0,0,5000/scale), orient_type='GLOBAL')
        bpy.ops.object.mode_set(mode='OBJECT')
        activeObject = bpy.context.active_object
        activeObject.name = "AREA_" + str(existingAreas) + "_0_0_0_0_0_0_-1_0"
        updateArea(self, context)
        name = activeObject.name
        properties = name.split("_")
        mytool.kmp_areaEnumType = "A" + properties[3]
        mytool.kmp_areaID = int(float(properties[4]))
        mytool.kmp_areaPrority = int(properties[5])
        mytool.kmp_areaSet1 = properties[6]
        mytool.kmp_areaSet2 = properties[7]
        mytool.kmp_areaRoute = int(properties[8])
        mytool.kmp_areaEnemy = int(properties[9])
          
        return {'FINISHED'}


class kmp_c_cylinder_area (bpy.types.Operator):
    bl_idname = "kmpc.c_cylinder_area"
    bl_label = "Create cylinder AREA Model"
    bl_description = "Creates a cylindrical AREA Model is proper scale and origin (Move it only in OBJECT mode)"
    bl_options = {'UNDO'}    
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        cursor_position = context.scene.cursor.location
        
        existingAreas = 0
        for obj in bpy.data.objects:
            if "area_" in obj.name.lower():
                existingAreas = existingAreas + 1
        
        bpy.ops.mesh.primitive_cylinder_add(radius=5000/scale, depth=10000/scale, location=cursor_position, vertices=128)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.translate(value=(0,0,5000/scale), orient_type='GLOBAL')
        bpy.ops.object.mode_set(mode='OBJECT')
        activeObject = bpy.context.active_object
        activeObject.name = "AREA_" + str(existingAreas) + "_1_0_0_0_0_0_-1_0"
        updateArea(self, context)
        name = activeObject.name
        properties = name.split("_")
        mytool.kmp_areaEnumType = "A" + properties[3]
        mytool.kmp_areaID = int(float(properties[4]))
        mytool.kmp_areaPrority = int(properties[5])
        mytool.kmp_areaSet1 = properties[6]
        mytool.kmp_areaSet2 = properties[7]
        mytool.kmp_areaRoute = int(properties[8])
        mytool.kmp_areaEnemy = int(properties[9])
        return {'FINISHED'}
  
loading = 0
class load_kmp(bpy.types.Operator, ImportHelper):
    bl_idname = "kmpc.load"
    bl_label = "Import KMP AREAs"       
    filename_ext = '.kmp'
    bl_description = "Loads KMP file and imports AREAs with settings"
    
    filter_glob: bpy.props.StringProperty(
        default='*.kmp',
        options={'HIDDEN'}
    )
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        global loading
        loading = 1
        
        checkMaterial()
        
        path = self.filepath
        file = open(path, "rb")
        magic = struct.unpack('4s', file.read(4))[0].decode("ascii")
        if(magic != "RKMD"):
            self.report({"WARNING"}, "Wrong file magic")
            return {'CANCELLED'}
        
        fileLen = struct.unpack(">I", file.read(4))[0]
        sectionNumber = struct.unpack(">H", file.read(2))[0]
        headerLen = struct.unpack(">H", file.read(2))[0]
        versionNumber = struct.unpack(">I", file.read(4))[0]
        sectionOffsets = []
        for i in range(int(sectionNumber)):
            sectionOffsets.append(struct.unpack(">I", file.read(4))[0])
        
        existingAreas = 0
        for obj in bpy.data.objects:
            if "area_" in obj.name.lower():
                existingAreas = existingAreas + 1
        
        areaOffset = 80 + sectionOffsets[9]
        file.seek(areaOffset, 0)
        areaNumber = struct.unpack('>H', file.read(2))[0]
        areaUnused = struct.unpack('>H', file.read(2))[0]
        scale = mytool.scale
        areas = []
        for i in range(int(areaNumber)):
            areaShape = struct.unpack('>b', file.read(1))[0]
            areaType = struct.unpack('>b', file.read(1))[0]
            areaCAME = struct.unpack('>b', file.read(1))[0]
            areaPriority = struct.unpack('>b', file.read(1))[0]
            areaXPos = struct.unpack('>f', file.read(4))[0]
            areaYPos = struct.unpack('>f', file.read(4))[0]
            areaZPos = struct.unpack('>f', file.read(4))[0]
            areaXRot = struct.unpack('>f', file.read(4))[0]
            areaYRot = struct.unpack('>f', file.read(4))[0]
            areaZRot = struct.unpack('>f', file.read(4))[0]
            areaXScale = struct.unpack('>f', file.read(4))[0]
            areaYScale = struct.unpack('>f', file.read(4))[0]
            areaZScale = struct.unpack('>f', file.read(4))[0]
            areaSet1 = struct.unpack('>H', file.read(2))[0]
            areaSet2 = struct.unpack('>H', file.read(2))[0]
            areaRoute = struct.unpack('>b', file.read(1))[0]
            areaEnemy = struct.unpack('>b', file.read(1))[0]
            areaPadding = struct.unpack('>h', file.read(2))[0]
            areaLocation = (areaXPos/scale, areaZPos/scale * -1, areaYPos/scale)
            areaRotation = (math.radians(areaXRot), math.radians(areaZRot), math.radians(areaYRot))
            areaScale = (areaXScale, areaZScale, areaYScale)
            areaName = "AREA_" + str(existingAreas + i) + "_" + '{:X}'.format(areaShape) + "_" + str(int(areaType)) + "_" + str(int(areaCAME))\
            + "_" + '{:X}'.format(areaPriority) + "_" + '{:X}'.format(areaSet1) + "_" + '{:X}'.format(areaSet2) + "_" + str(areaRoute) + "_" + str(areaEnemy)
             
            areaName = areaName.upper()
            if(str(areaShape) == "0"):
                bpy.ops.mesh.primitive_cube_add(size=10000/scale, location=areaLocation, rotation=areaRotation)
                obj = bpy.context.selected_objects[0]
                obj.name = areaName
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.transform.translate(value=(0,0,5000/scale), orient_type='GLOBAL')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.transform.resize(value=areaScale, orient_type='LOCAL')      
            if(str(areaShape) == "1"):
                bpy.ops.mesh.primitive_cylinder_add(radius=5000/scale, depth=10000/scale, location=areaLocation, rotation=areaRotation)
                obj = bpy.context.selected_objects[0]
                obj.name = areaName
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.transform.translate(value=(0,0,5000/scale), orient_type='GLOBAL')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.transform.resize(value=areaScale, orient_type='LOCAL')          
            activeObject = bpy.context.active_object
            mat = bpy.data.materials.get("kmpc.area.A" + str(int(areaType)))
            activeObject.data.materials.append(mat)
            
        
        loading = 0
        return {'FINISHED'}

matColors = [(1.0, 0.262251, 0, 0.6), 
            (0, 0.009134, 0.274677, 0.6), 
            (0.838799, 0, 0.262251, 0.6), 
            (0.138432, 0.015209, 0.194618, 0.6), 
            (0.341914, 0.337474, 0.273874, 0.6), 
            (0.018564, 0.016922, 0.031063, 0.6),
            (0.341914, 0.337474, 0.273874, 0.6),
            (0, 0.341914, 0.066626, 0.6), 
            (0.8, 0.879623, 0, 0.6), 
            (0.445201, 0.8, 0.296138, 0.6), 
            (0.806953, 0.006, 0.016807, 0.6)]

def checkFlagInName(name):
    try:
        i = int(name[-4:],16)
    except ValueError:
        return False
    if(name[-6] != "_"):
        return False
    if(name[-5] != "F"):
        return False
    try:
        i = int(name[-8:-7],16)
    except ValueError:
        return False
    if(name[-9] != "_"):
        return False
    return True


def checkMaterial():
    for i in range(11):   
        matName = "kmpc.area.A" + str(i)
        mat = bpy.data.materials.get(matName)
        if mat is None:
            mat = bpy.data.materials.new(matName)
            mat.diffuse_color = matColors[i]
            mat.blend_method = 'BLEND' 
            
@persistent
def update_scene_handler(scene):

    global lastselection, setting1users, setting2users
    mytool = scene.kmpt
    activeObject = bpy.context.active_object
    #0 - AREA Header
    #1 - Number
    #2 - Shape
    #3 - Type
    #4 - CAME
    #5 - Priority
    #6 - Setting 1
    #7 - Setting 2
    #8 - Route
    #9 - Enemy Point
    


    if(loading == 0):
        for i in range(len(scene.objects)):
            for object in scene.objects:
                if(hasattr(object, "name")):
                    if(object.name.startswith("AREA_")):
                        if(object.name[-4] == "."):
                            existingAreas = -1 * i - 1
                            for obj in bpy.data.objects:
                                if "area_" in obj.name.lower():
                                    existingAreas = existingAreas + 1
                            name = object.name[:-4]
                            properties = name.split("_")
                            object.name = "AREA_" + str(existingAreas) + "_" + properties[2] + "_" + properties[3] + "_" + properties[4] + "_" + properties[5] + "_" + properties[6] + "_" + properties[7] + "_" + properties[8] + "_" + properties[9]


        if hasattr(activeObject, "name"):
            if(activeObject.name.startswith("AREA_")):
                if(lastselection != activeObject):
                    name = activeObject.name
                    properties = name.split("_")
                    mytool.kmp_areaEnumType = "A" + properties[3]
                    mytool.kmp_areaPrority = int(properties[5])
                    mytool.kmp_areaSet1 = properties[6]
                    mytool.kmp_areaSet2 = properties[7]
                    mytool.kmp_areaEnemy = int(properties[9])
                    #Clear settings which are not in selected AREA type
                    mytool.kmp_areaID = int(float(properties[4]))
                    mytool.kmp_areaRoute = int(properties[8])
                    mytool.kmp_areaEnemy = int(float(properties[9]))
                    mytool.kmp_areaSet1 = "0" if mytool.kmp_areaEnumType not in setting1users else properties[6]
                    mytool.kmp_areaSet2 = "0" if mytool.kmp_areaEnumType not in setting2users else properties[7]
                    mytool.kmp_areaPostEffectEntry = int(mytool.kmp_areaSet1)
                    mytool.kmp_areaMovingRouteSet1 = int(mytool.kmp_areaSet1)
                    mytool.kmp_areaMovingRouteSet2 = int(mytool.kmp_areaSet2)
                    mytool.kmp_areaIDK1 = int(mytool.kmp_areaSet1)
                    mytool.kmp_areaIDK2 = int(mytool.kmp_areaSet2)
                    mytool.kmp_areaGroup = int(mytool.kmp_areaSet1)
                    mytool.kmp_areaUseCOOB = False
                    mytool.kmp_areaRiidefiP1 = 0
                    mytool.kmp_areaRiidefiP2 = 0
                    mytool.kmp_areaRiidefiInvert = False
                    mytool.kmp_areakHackerMode = "0"
                    mytool.kmp_areakHackerCheckpoint = 0
                    if(mytool.kmp_areaEnumType == "A10"):
                        if(mytool.kmp_areaRoute == "1" or mytool.kmp_areaSet1 is not "0" or mytool.kmp_areaSet2 is not "0"):
                            mytool.kmp_areaUseCOOB = True
                        mytool.kmp_areaCOOBVersion = "kHacker" if mytool.kmp_areaRoute == 1 else "Riidefi"
                        if(mytool.kmp_areaCOOBVersion == "kHacker"):
                            mytool.kmp_areakHackerMode = mytool.kmp_areaSet1
                            mytool.kmp_areakHackerCheckpoint = int(mytool.kmp_areaSet2)
                        mytool.kmp_areaRiidefiInvert = int(mytool.kmp_areaSet1) > int(mytool.kmp_areaSet2)
                        if(mytool.kmp_areaRiidefiInvert):
                            mytool.kmp_areaRiidefiP1 = int(mytool.kmp_areaSet2)
                            mytool.kmp_areaRiidefiP2 = int(mytool.kmp_areaSet1)
                        else:
                            mytool.kmp_areaRiidefiP1 = int(mytool.kmp_areaSet1)
                            mytool.kmp_areaRiidefiP2 = int(mytool.kmp_areaSet2)

                

            
    lastselection = activeObject



@persistent
def load_file_handler(dummy):
    global current_version, latest_version
    response = requests.get("https://api.github.com/repos/Gabriela-Orzechowska/Blender-MKW-Utilities/releases/latest")
    latest_version = response.json()["name"]
    if(latest_version == current_version):
        return
    ShowMessageBox("There's a new version available: " + latest_version, "New version available!")

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

classes = [MyProperties, KMPUtilities, KCLSettings, KCLUtilities, AREAUtilities, apply_kcl_flag, cursor_kmp, import_kcl_file, kmp_gobj, kmp_area, kmp_c_cube_area, kmp_c_cylinder_area, load_kmp, export_kcl_file, openGithub, merge_duplicate_objects, export_autodesk_dae]
 
 
 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.app.handlers.depsgraph_update_post.append(update_scene_handler)
    bpy.app.handlers.load_post.append(load_file_handler)
    bpy.types.TOPBAR_MT_file_export.append(export_autodesk_dae_button)
    bpy.types.Scene.kmpt = bpy.props.PointerProperty(type= MyProperties)
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.load_post.clear()
    bpy.types.TOPBAR_MT_file_export.remove(export_autodesk_dae_button)
    del bpy.types.Scene.kmpt
 
 
if __name__ == "__main__":
    register()