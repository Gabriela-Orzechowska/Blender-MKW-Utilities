bl_info = {
    "name" : "Mario Kart Wii Utilities",
    "author" : "Gabriela_",
    "version" : (1, 7, 1),
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
from mathutils import Vector
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
def updateCame(self, context):
    
    global lastselection
    scene = context.scene
    mytool = scene.kmpt
    activeObject = bpy.context.active_object
    if(hasattr(activeObject, "name") == False):
        return

    if(lastselection == activeObject):
        if(activeObject.name.startswith("CAME_")): 
            name = activeObject.name
            properties = name.split("_")
            ctype = str(mytool.kmp_cameEnumType)[1]
            id = str(properties[1]) if mytool.kmp_cameCustomId == -1 else str(mytool.kmp_cameCustomId)
            checkName = "CAME_"+str(id)
            for ob in bpy.context.scene.objects:
                if(checkName in ob.name):
                    id = str(properties[1])

            frameCount = str(scene.frame_end)
            cameName = properties[0] + "_" + str(id) + "_" + mytool.kmp_cameEnumType[1] + "_" + str(mytool.kmp_cameOpNext) + "_" + str(mytool.kmp_cameRoute) + "_" + str(frameCount)

            activeObject.name = cameName
            oldVP = bpy.context.scene.objects["CAMEVP_" + properties[1]]
            vpName = "CAMEVP_" + id
            oldVP.name = vpName



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
                                                                    ("A6", "BBLM Changer", 'Changes bloom and glow settings using .bblm files'),
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
    kmp_areaIDK1 : bpy.props.IntProperty(name = "BBLM file entry", min= 0, default= 0, update=updateArea, 
                                        description= "Controls which posteffect.bblm* file to use. Number 0 defines default .bblm, value of * will use .bblm*")
    kmp_areaIDK2 : bpy.props.IntProperty(name = "Transition time", min= 0, default= 0, update=updateArea, 
                                        description= "Transition between entries in frames")
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
 #region came_types
    kmp_cameEnumType : bpy.props.EnumProperty(name = "Type", items=[("B5", "Opening", "Opening camera, follows route; from its position, it looks at View Start and shifts view to View End if set, otherwise looks at player. This camera type only requires a route. It does not need an AREA Entry."),
                                                                    ("B0", "Goal", "Activates immediately after passing the goal; with the player as the origin, the camera's View Start position both follows and points towards View End."),
                                                                    ("B1", "FixSearch", "Camera stays static in View Start location, and always looks towards the player. It is almost the same as PathSearch but with no route."),
                                                                    ("B2", "PathSearch", "Route controlled, always looks at the player. Only the position of the first route point is used and will always face the player."),
                                                                    ("B3", "KartFollow", "With the player as the origin, the camera's location is at View Start and it follows and points towards View End. If View Start and View End are 0, it will directly face the player backwards. This is similar to the Goal camera type."),
                                                                    ("B4", "KartPathFollow", "From its position, it looks at View Start and shifts view to View End. If neither are set, it will just look at the player from wherever it is positioned."),
                                                                    ("B6", "OP_PathMoveAt", "This camera will move along a route with the player and turn with the player as well. The camera is affected by things like turning and tricking. Only the first point of the route is used."),
                                                                    ("B7", "MiniGame", 'Unknown'),
                                                                    ("B8", "MissionSuccess", 'Unknown'),
                                                                    ("B9", "Unknown", 'Unknown')],
                                                                    update=updateCame)
    kmp_cameCustomId : bpy.props.IntProperty(name= "Custom Index (Read desc)", min= -1, default= -1, update=updateCame, 
                                            description= "Overwrite CAME index, can't skip numbers, make sure it does not collide with others in KMP")
    kmp_cameOpNext : bpy.props.IntProperty(name= "Next Camera", min= -1, default= -1, update=updateCame, 
                                            description= "Next Opening Camera to use after finishing")
    kmp_cameRoute : bpy.props.IntProperty(name= "Custom Route ID", min= -1, default= -1, update=updateCame, 
                                            description= "Can be filled later in KMP Cloud unless you sure it is correct")
    kmp_cameRes : bpy.props.IntProperty(name= "Timeline route resolution", min= 2, default= 20, update=updateCame, 
                                            description= "Amount of points to create from timeline")
    kmp_cameGoToNext : bpy.props.BoolProperty(name= "Switch to next after finished", description="Play the next camera (if found) after finishing")
    kmp_cameStop : bpy.props.BoolProperty(name="Disable looping", description="Disable automatic looping of animation")
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
    kcl_bounce : bpy.props.BoolProperty(name= "Soft Wall", default=False, description="Used to get rid of bean corners, use only on walls that meet road")
    
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
                                                                        ("2", "Use custom scheme", ''),
                                                                        ("1", "Keep original", '')],default="2")
    kcl_applyName : bpy.props.EnumProperty(name = "Name", items=[("0", "Flag only", ''),
                                                                    ("1", "Add type label", ''),
                                                                    ("2", "Add type and variant label", ''),
                                                                    ("3", "Add to original", ''),
                                                                    ("4", "Add to mesh name only",'')],default="1")
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

current_version = "v0.1.7-1"
latest_version = "v0.1.7-1"
prerelease_version = "v0.1.7-1"

kcl_typeATypes = ["T00","T01","T02","T03","T04","T05","T06","T07","T08","T09","T0A","T16","T17","T1D"]
kcl_wallTypes = ["T0C","T0D","T0E","T0F","T1E","T1F", "T19"]

class openGithub(bpy.types.Operator):
    bl_idname = "open.download"
    bl_label = "Download from GitHub"

    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        if(get_prefs(context).prerelease_bool):
            responseVersions = requests.get("https://api.github.com/repos/Gabriela-Orzechowska/Blender-MKW-Utilities/releases")
            prerelease = responseVersions.json()[0]["url"]
            responseVersions = requests.get(prerelease)
            prerelease_version = responseVersions.json()["tag_name"]
            webbrowser.get().open('https://github.com/Gabriela-Orzechowska/Blender-MKW-Utilities/releases/tag/{0}'.format(prerelease_version))
        else:
            webbrowser.get().open('http://www.github.com/Gabriela-Orzechowska/Blender-KMP-Utilities/releases/latest')
        return {'FINISHED'}

class openWSZSTPage(bpy.types.Operator):
    bl_idname = "open.wszst"
    bl_label = "Download WSZST"

    def execute(self, context):
        webbrowser.get().open('https://szs.wiimm.de/download.html')
        return {'FINISHED'}

class openIssuePage(bpy.types.Operator):
    bl_idname = "open.issue"
    bl_label = "Report a bug"

    def execute(self, context):
        webbrowser.get().open('https://github.com/Gabriela-Orzechowska/Blender-MKW-Utilities/issues/new')
        return {'FINISHED'}

class KMPUtilities(bpy.types.Panel):
    global latest_version, prerelease_version, current_version
    bl_label = "Main Utilities"
    bl_idname = "MKW_PT_Kmp"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        newVersionLayout = layout.column()
        updateText = "New version available!: {0}"
        if(get_prefs(context).updates_bool):
            if(get_prefs(context).prerelease_bool):
                if(prerelease_version != current_version):
                    newVersionLayout.label(text=updateText.format(prerelease_version))
                    newVersionLayout.operator("open.download")
                    newVersionLayout.label(text="")
            elif(latest_version != current_version):
                newVersionLayout.label(text=updateText.format(latest_version))
                newVersionLayout.operator("open.download")
                newVersionLayout.label(text="") 
        layout.operator("open.issue")
        layout.prop(mytool, "scale")
        layout.operator("kmpc.cursor")
        layout.operator("kmpc.gobj")
        layout.operator("mkw.objectmerge")
        #layout.operator("kmpe.load")

class KCLSettings(bpy.types.Panel):
    bl_label = "KCL Settings"
    bl_idname = "MKW_PT_KclSet"
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
    global wszstInstalled
    bl_label = "KCL Utilities"
    bl_idname = "MKW_PT_Kcl"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt   
        text="Please download Wiimms SZS Tools (WSZST) to Import/Export KCL."
        
        
        if(wszstInstalled):
            layout.operator("kclc.load")
        else:
            _label_multiline(
                context=context,
                text=text,
                parent=layout
            )
            layout.operator("open.wszst")
        layout.prop(mytool, "kcl_masterType")
        variantPropName = "kclVariant" + mytool.kcl_masterType
        layout.prop(mytool, variantPropName)
        if(mytool.kcl_masterType == "T10"):
            layout.prop(mytool, "kclVariant10Index")
        if(mytool.kcl_masterType == "T18"):
            layout.prop(mytool, "kclVariantT18Circuits")
            t18variant = "kclVariantT18" + mytool.kclVariantT18Circuits
            layout.prop(mytool, t18variant)
        if(mytool.kcl_masterType in kcl_typeATypes or mytool.kcl_masterType == "T1A" or mytool.kcl_masterType in kcl_wallTypes):
            layout.prop(mytool, "kcl_shadow")
        if(mytool.kcl_masterType in kcl_typeATypes):
            layout.prop(mytool, "kcl_trickable")
            layout.prop(mytool, "kcl_drivable")
        if(mytool.kcl_masterType == "T19"):
            text='This flag is mainly used with "Soft Walls"'
            _label_multiline(
                context=context,
                text=text,
                parent=layout
            )
        if(mytool.kcl_masterType in kcl_wallTypes):
            layout.prop(mytool, "kcl_bounce") 
        
        layout.operator("kclc.applyflag")
        if(wszstInstalled):
            layout.operator("kclc.export")
        
class AREAUtilities(bpy.types.Panel):
    bl_label = "AREA Utilities"
    bl_idname = "MKW_PT_KmpArea"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        layout.operator("kmpc.load")
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
        
class CAMEUtilities(bpy.types.Panel):
    bl_label = "Opening Cameras Utilities"
    bl_idname = "MKW_PT_KmpCame"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        if(scene.frame_start is not 0 or scene.render.fps is not 60):
            layout.operator("came.setup")
        came_create_column = layout.column()
        came_create_column.operator("came.create")
        layout.operator("kmpt.came")
        #layout.prop(mytool, "kmp_cameEnumType")
        layout.prop(mytool, "kmp_cameCustomId")
        layout.prop(mytool, "kmp_cameOpNext")
        layout.prop(mytool, "kmp_cameRoute")
        layout.prop(mytool, "kmp_cameGoToNext")
        layout.prop(mytool, "kmp_cameStop")

        if(bpy.context.object is not None):
            current_mode = bpy.context.object.mode
        else:
            current_mode = 'OBJECT'
        
        if(current_mode != 'OBJECT'):
            came_create_column.enabled = False
        else:
            came_create_column.enabled = True

class RouteUtilities(bpy.types.Panel):
    bl_label = "Route Utilities"
    bl_idname = "MKW_PT_Route"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        layout.operator("came.route")
        layout.prop(mytool, "kmp_cameRes")
        layout.operator("came.smoothroute")

class MaterialUtilities(bpy.types.Panel):
    bl_label = "Material Utilities"
    bl_idname = "MKW_PT_Material"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        layout.operator("kmpt.blend")
        layout.operator("kmpt.clip")
        layout.operator("kmpt.metalic")

class set_alpha_blend(bpy.types.Operator):
    bl_idname = "kmpt.blend"
    bl_label = "Add Alpha Blend"
    bl_description = "Add Alpha Node from Image Texture and set Alpha mode to Blend"
    bl_options = {'UNDO'}
    def execute(self, context):
        selected = bpy.context.selected_objects
        for obj in selected:
            if obj.type == 'MESH' and not obj.active_material == None:
                for item in obj.material_slots:
                    mat = bpy.data.materials[item.name]
                    if mat.use_nodes:                    
                        mat.blend_method = 'BLEND'
                        shader = mat.node_tree.nodes['Principled BSDF']
                        for node in mat.node_tree.nodes:
                            if node.type == 'TEX_IMAGE':
                                mat.node_tree.links.new(shader.inputs['Alpha'], node.outputs['Alpha'])
        return {'FINISHED'}
class set_alpha_clip(bpy.types.Operator):
    bl_idname = "kmpt.clip"
    bl_label = "Add Alpha Clip"
    bl_description = "Add Alpha Node from Image Texture and set Alpha mode to Clip"
    bl_options = {'UNDO'}
    def execute(self, context):
        selected = bpy.context.selected_objects
        for obj in selected:
            if obj.type == 'MESH' and not obj.active_material == None:
                for item in obj.material_slots:
                    mat = bpy.data.materials[item.name]
                    if mat.use_nodes:                    
                        mat.blend_method = 'CLIP'
                        shader = mat.node_tree.nodes['Principled BSDF']
                        for node in mat.node_tree.nodes:
                            if node.type == 'TEX_IMAGE':
                                mat.node_tree.links.new(shader.inputs['Alpha'], node.outputs['Alpha'])
        return {'FINISHED'}
class remove_specular_metalic(bpy.types.Operator):
    bl_idname = "kmpt.metalic"
    bl_label = "Remove Specular and Metalic"
    bl_description = "Remove unwanted shininess from materials"
    bl_options = {'UNDO'}
    def execute(self, context):
        selected = bpy.context.selected_objects
        for obj in selected:
            if obj.type == 'MESH' and not obj.active_material == None:
                for item in obj.material_slots:
                    mat = bpy.data.materials[item.name]
                    if mat.use_nodes:                    
                        mat.node_tree.nodes['Principled BSDF'].inputs[4].default_value = 0
                        mat.node_tree.nodes['Principled BSDF'].inputs[5].default_value = 0
    

        return {'FINISHED'}

class kmp_came(bpy.types.Operator):
    bl_idname = "kmpt.came"
    bl_label = "CAME to KMP Cloud"
    bl_description = "Converts selected objects data and puts them into clipboard as CAME"
    
    def execute(self, context):
        data = ""
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        selected = bpy.context.selected_objects
        selected.sort(key=lambda obj: obj.name)
            
        for object in selected:
            if not object.name.startswith("CAME_"):
                continue
            fovs = []
            vpposs = []
            fovkeyframes = []
            vpkeyframes = []

            properties = object.name.split("_")
            if(hasattr(object.data, "animation_data")):
                if(hasattr(object.data.animation_data, "action")):
                    if(hasattr(object.data.animation_data.action, "fcurves")):
                        fovcurves = object.data.animation_data.action.fcurves
                        for curve in fovcurves:        
                            if("lens" in curve.data_path):
                                keyframePoints = curve.keyframe_points
                                for keyframe in keyframePoints:
                                    f = keyframe.co[0]
                                    scene.frame_set(f)
                                    fovkeyframes.append(f)
                                    cameraName = object.data.name
                                    fov = bpy.data.cameras[cameraName].angle
                                    fov = fov * 180 / 3.1415
                                    fov = round(fov * 9 / 16, 0)
                                    fovs.append(fov)
                        if(fovkeyframes[0] > 1):
                            self.report({"WARNING"}, "Camera {0}: First FOV keyframe needs to be at frame 0".format(properties[1]))
                            return {'CANCELLED'}
                        if(len(fovkeyframes) > 2):
                            self.report({"WARNING"}, "Camera {0}: You can not have more that 2 FOV keyframes".format(properties[1]))
                            return {'CANCELLED'}
                    else:
                        cameraName = object.data.name
                        fov = bpy.data.cameras[cameraName].angle
                        fov = fov * 180 / 3.1415
                        fov = round(fov * 9.0 / 16.0, 0)
                        fovs.append(fov)
                        fovs.append(fov)
                        fovkeyframes.append(0)
                        fovkeyframes.append(0)
                else:
                    cameraName = object.data.name
                    fov = bpy.data.cameras[cameraName].angle
                    fov = fov * 180 / 3.1415
                    fov = round(fov * 9 / 16, 0)
                    fovs.append(fov)
                    fovs.append(fov)
                    fovkeyframes.append(0)
                    fovkeyframes.append(0)
            else:
                cameraName = object.data.name
                fov = bpy.data.cameras[cameraName].angle
                fov = fov * 180 / 3.1415
                fov = round(fov * 9 / 16, 0)
                fovs.append(fov)
                fovs.append(fov)
                fovkeyframes.append(0)
                fovkeyframes.append(0)
            viewpoint = bpy.context.scene.objects["CAMEVP_" + properties[1]]
            if(hasattr(viewpoint, "animation_data")):
                if(hasattr(viewpoint.animation_data, "action")):
                    if(hasattr(viewpoint.animation_data.action, "fcurves")):
                        vpcurves = viewpoint.animation_data.action.fcurves
                        for curve in vpcurves:
                            keyframePoints = curve.keyframe_points
                            for keyframe in keyframePoints:
                                if(keyframe.co[0] not in vpkeyframes):  
                                    f = keyframe.co[0]
                                    vpkeyframes.append(f)
                                    scene.frame_set(f)
                                    loc = viewpoint.location
                                    position = [loc[0] * scale,loc[1] * scale,loc[2] * scale]
                                    vpposs.append(position)
                        if(vpkeyframes[0] > 1):
                            self.report({"WARNING"}, "Camera {0}: First View Point keyframe needs to be at frame 0".format(properties[1]))
                            return {'CANCELLED'}
                        if(len(vpkeyframes) > 2):
                            self.report({"WARNING"}, "Camera {0}: You can not have more that 2 View Point keyframes".format(properties[1]))
                            return {'CANCELLED'}
                    else:
                        loc = viewpoint.location
                        position = [loc[0] * scale,loc[1] * scale,loc[2] * scale]
                        vpposs.append(position)
                        vpposs.append(position)
                        vpkeyframes.append(0)
                        vpkeyframes.append(0)
                else:
                    loc = viewpoint.location
                    position = [loc[0] * scale,loc[1] * scale,loc[2] * scale]
                    vpposs.append(position)
                    vpposs.append(position)
                    vpkeyframes.append(0)
                    vpkeyframes.append(0)
            else:
                loc = viewpoint.location
                position = [loc[0] * scale,loc[1] * scale,loc[2] * scale]
                vpposs.append(position)
                vpposs.append(position)
                vpkeyframes.append(0)
                vpkeyframes.append(0)
            a = len(vpkeyframes)
            vectors = []
            for i in range(a):
                vectors.append(Vector(vpposs[i]))       
            vpSpeed = 0
            if(vpkeyframes[1] - vpkeyframes[0] != 0):
                vpSpeed = (vectors[1]- vectors[0]).length  * 100 / vpkeyframes[1] - vpkeyframes[0]
            sped = math.floor(vpSpeed)
            vpSpeed = "{0:0{1}X}".format(int(vpSpeed),4)
            fovSpeed=0
            if(fovkeyframes[1] - fovkeyframes[0] != 0):
                fovSpeed = abs(fovs[1] - fovs[0])  * 100 / fovkeyframes[1] - fovkeyframes[0]
            fovSpeed = math.floor(fovSpeed)
            fovSpeed = "{0:0{1}X}".format(int(fovSpeed),4)
            for i in range(len(properties)):
                if(properties[i] == "-1"):
                    properties[i] = "FF"
            xpos = round(object.location[0] * scale, 3)
            ypos = round(object.location[2] * scale, 3)
            zpos = round(object.location[1] * scale * -1, 3)
            vsxpos = round(vpposs[0][0], 0)
            vsypos = round(vpposs[0][2], 0)
            vszpos = round(vpposs[0][1] * -1, 0)
            vexpos = round(vpposs[1][0], 0)
            veypos = round(vpposs[1][2], 0)
            vezpos = round(vpposs[1][1] * -1, 0)
            frames = properties[5]
            dataValue = properties[1].zfill(2) + "\t" + properties[2].zfill(2) + "\t" + properties[3].zfill(2) + "\t00\t"+ properties[4].zfill(2) +"\t0000\t"+str(fovSpeed)+"\t"+str(vpSpeed)+"\t00\t00\t"+str(xpos)+"\t"+str(ypos)+"\t"+str(zpos)+"\t0\t0\t0\t"+str(int(fovs[0]))+"\t"+str(int(fovs[1]))+"\t"+str(vsxpos)+"\t"+str(vsypos)+"\t"+str(vszpos)+"\t"+str(vexpos)+"\t"+str(veypos)+"\t"+str(vezpos)+"\t"+str(frames)+"\n"
            data += dataValue
        bpy.context.window_manager.clipboard = data
        return {'FINISHED'}

class keyframes_to_route(bpy.types.Operator):
    bl_idname = "came.route"
    bl_label = "Keyframes to KMP Cloud Route"
    bl_description = "Converts active object's keyframes and puts them into clipboard as Route Points"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        keyframes = []
        locations = []
        activeObject = bpy.context.active_object
        if not hasattr(activeObject, "animation_data"):
            self.report({"WARNING"}, "Selected object does not have any keyframes")
            return {'CANCELLED'}
        if not hasattr(activeObject.animation_data, "action"):
            self.report({"WARNING"}, "Selected object does not have any keyframes")
            return {'CANCELLED'}
        if not hasattr(activeObject.animation_data.action, "fcurves"):
            self.report({"WARNING"}, "Selected object does not have any keyframes")
            return {'CANCELLED'}
        fcurves = activeObject.animation_data.action.fcurves
        for curve in fcurves:
            keyframePoints = curve.keyframe_points
            i = 0
            for keyframe in keyframePoints:
                
                if(keyframe.co[0] not in keyframes):  
                    f = keyframe.co[0]
                    if(i==0 and f!=0):
                        self.report({'WARNING'}, "First Keyframe should be at frame 0")
                        return {'CANCELLED'}
                    keyframes.append(f)
                    scene.frame_set(int(f))
                    loc = activeObject.location
                    position = [loc[0] * scale,loc[1] * scale,loc[2] * scale]
                    locations.append(position)
                    i=i+1
                   
        speed = []
        vectors = []
        a = len(keyframes)
        for i in range(a):
            vectors.append(Vector(locations[i]))
        for i in range(a):
            if(i is not a-1):
                sped = (vectors[i+1]- vectors[i]).length / keyframes[i+1] - keyframes[i]
                speed.append(sped)
        speed.append(0)
        data =""
        for i in range(a):
            xpos = round(vectors[i][0], 3)
            ypos = round(vectors[i][2], 3)
            zpos = round(vectors[i][1]* -1, 3)
            sped = abs(speed[i])
            sped = math.floor(sped)
            sped = "{0:0{1}X}".format(sped,4)
            dataValue = str(i).zfill(2) + "\t" + str(xpos) + "\t" + str(ypos) + "\t" + str(zpos) + "\t" + str(sped) + "\t" + "0000" + "\n"
            data += dataValue
        bpy.context.window_manager.clipboard = data
        return {'FINISHED'}

class timeline_to_route(bpy.types.Operator):
    bl_idname = "came.smoothroute"
    bl_label = "Timeline to KMP Cloud Route"
    bl_description = "Converts active object's movement and puts them into clipboard as Route Points"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        keyframes = []
        locations = []
        activeObject = bpy.context.active_object
        if not hasattr(activeObject, "animation_data"):
           return {'FINISHED'}  
        if not hasattr(activeObject.animation_data, "action"):
            return {'FINISHED'}
        if not hasattr(activeObject.animation_data.action, "fcurves"):
            return {'FINISHED'}
        resolution = mytool.kmp_cameRes
        interval = math.ceil(scene.frame_end / resolution)
        for i in range(resolution):
            f = i*interval
            if(i == resolution-1):
                f = scene.frame_end
            scene.frame_set(f)
            keyframes.append(f)
            loc = activeObject.location
            position = [math.floor(loc[0] * scale),math.floor(loc[1] * scale),math.floor(loc[2] * scale)]
            locations.append(position)
        speed = []
        vectors = []
        a = len(keyframes)
        for i in range(a):
            vectors.append(Vector(locations[i]))
        for i in range(a):
            if(i is not a-1):
                sped = math.floor((vectors[i+1]- vectors[i]).length) / (keyframes[i+1] - keyframes[i])
                speed.append(sped)
        speed.append(0)
        data =""
        for i in range(a):
            xpos = round(vectors[i][0], 3)
            ypos = round(vectors[i][2], 3)
            zpos = round(vectors[i][1] * -1, 3)
            sped = abs(speed[i])
            sped = math.floor(sped)
            sped = "{0:0{1}X}".format(sped,4)
            dataValue = str(i).zfill(2) + "\t" + str(xpos) + "\t" + str(ypos) + "\t" + str(zpos) + "\t" + str(sped) + "\t" + "0000" + "\n"
            data += dataValue
        bpy.context.window_manager.clipboard = data
        return {'FINISHED'}
class create_camera(bpy.types.Operator):
    bl_idname = "came.create"
    bl_label = "Create Camera"
    bl_description = "Creates Camera objects with viewpoint"
    bl_options = {'UNDO'}
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        camePosition = context.space_data.region_3d.view_location
        scale = mytool.scale
        cursor_position = context.scene.cursor.location
        existingCames = 0
        bpy.ops.object.select_all(action='DESELECT')

        for obj in bpy.data.objects:
            if "came_" in obj.name.lower():
                existingCames += 1
        freeID = False

        while freeID == False:
            for obj in bpy.data.objects:
                testName="came_"+str(existingCames)
                if testName in obj.name.lower():
                    existingCames+=1
                    continue
                else:
                    freeID = True
            freeID = True

        bpy.ops.mesh.primitive_uv_sphere_add(radius=scale/63.5,location=cursor_position)
        bpy.ops.object.mode_set(mode='OBJECT')
        name="CAMEVP_"+str(existingCames)
        mytool.kmp_cameCustomId = existingCames
        vp = bpy.context.object
        bpy.context.object.name = name
        bpy.ops.object.camera_add(align='VIEW', location=camePosition)
        bpy.ops.transform.resize(value=(scale/10,scale/10,scale/10))
        bpy.ops.object.constraint_add(type='TRACK_TO')
        bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'
        bpy.context.object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
        bpy.context.object.constraints["Track To"].target = vp
        name="CAME_"+str(existingCames)+"_5_0_0_"
        name+=str(scene.frame_end)
        scene.camera = bpy.context.object
        bpy.context.object.name = name
        updateCame(self, context)

          
        return {'FINISHED'}

class scene_setup(bpy.types.Operator):
    bl_idname = "came.setup"
    bl_label = "Setup Scene"
    bl_description = "Setups timeline data"
    bl_options = {'UNDO'}
    def execute(self, context):
        scene = context.scene
        scene.render.fps = 60
        scene.frame_start = 0
        return {'FINISHED'}

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
            z = '{:03b}'.format(int(z))
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
        if(mytool.kcl_masterType == "T1A"):
            y = mytool.kcl_shadow
            y = '{:03b}'.format(int(y))
            typeaflag = y

        a = '{:01b}'.format(int(mytool.kcl_masterType[1],16))
        b = '{:04b}'.format(int(mytool.kcl_masterType[2],16))
        flag = typeaflag+z+a+b

        if(mytool.kcl_masterType == 'T10'):
            flag = '{:08b}'.format(mytool.kclVariant10Index)+z+a+b
        if(mytool.kcl_masterType == 'T12'):
            flag = '{:08b}'.format(a+b)
        if(mytool.kcl_masterType in kcl_wallTypes):
            w = int(mytool.kcl_bounce == True)
            y = mytool.kcl_shadow
            y = '{:03b}'.format(int(y))
            flag = str(w)+"0000"+y+z+a+b

        finalFlag = '{:04x}'.format(int(flag,2))
        mytool.kclFinalFlag = finalFlag 
        properFlag = "_"+mytool.kcl_masterType[1:]+"_F"+finalFlag
        properFlag = properFlag.upper()
        flagOnly = properFlag
        
        activeObject = context.active_object
        if not hasattr(activeObject,"type"):
            self.report({'WARNING'}, "Please select a mesh.")
            return {'FINISHED'}

        if(activeObject.type != "MESH"):
            self.report({'WARNING'}, "Selected object is not a mesh.")
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
            aobjName = activeObject.name
            if(objName[-3:].isnumeric() and objName[-4] == "."):
                objName = objName[:-4]
            if(checkFlagInName(objName)):
                objName = objName[:-9]
            if(objName[-3:].isnumeric() and objName[-4] == "."):
                objName = objName[:-4]
            if(aobjName[-3:].isnumeric() and aobjName[-4] == "."):
                aobjName = aobjName[:-4]
            if(checkFlagInName(aobjName)):
                aobjName = aobjName[:-9]
            if(aobjName[-3:].isnumeric() and aobjName[-4] == "."):
                aobjName = aobjName[:-4]
            properFlag = aobjName + properFlag
        if(mytool.kcl_applyName is not "4"):
            activeObject.name = properFlag
        activeObject.data.name = properFlag
        decodeFlag(properFlag[-4:])
        if(mytool.kcl_applyMaterial == "1"):
            return {'FINISHED'}
        context.active_object.data.materials.clear()
        mat = bpy.data.materials.get(flagOnly)
        if mat is None:
            mat = bpy.data.materials.new(name=flagOnly)
            if(mytool.kcl_applyMaterial == "0"):
                mat.diffuse_color = (random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),1)
            elif(mytool.kcl_applyMaterial == "2"):
                color = getSchemeColor(context,mytool.kcl_masterType,mytool.kcl_trickable,mytool.kcl_drivable,mytool.kcl_shadow)
                mat.diffuse_color = (color[0],color[1],color[2],1)
        context.active_object.data.materials.append(mat)


        return {'FINISHED'}

def decodeFlag(bareFlag):
    binary = bin(int(bareFlag, 16))[2:].zfill(16)
    kclType = "T"+hex(int(binary[-5:],2))[2:].zfill(2).upper()
    variant = hex(int(binary[-8:-5],2))[2:]
    shadow = int(binary[5:8],2)
    trickable = int(binary[2],2)
    drivable = int(str(binary[1]) == "0")
    softWall = int(binary[0],2)

    return kclType,variant,shadow,trickable,drivable,softWall


def getSchemeColor(context,kclType,trickable,drivable,shadow):
    global kcl_typeATypes, kcl_wallTypes
    getName = "kclColor" + kclType
    colorT = getattr(get_prefs(context), getName)
    color = [0,0,0]
    color[0] = colorT[0]
    color[1] = colorT[1]
    color[2] = colorT[2]
    if(kclType not in kcl_wallTypes):
        if(int(shadow) > 0):
            if(get_prefs(context).darkenBLIGHT):
                blightScale = get_prefs(context).blightScale
                color[0] = color[0] * (1-blightScale)
                color[1] = color[1] * (1-blightScale)
                color[2] = color[2] * (1-blightScale)
    if(kclType in kcl_typeATypes):
        if(trickable == True):
            if(get_prefs(context).addTintToTrickable):
                tint = getattr(get_prefs(context),"trickableColor")
                tintScale = getattr(get_prefs(context),"trickableScale")
                color[0] = color[0] - (0.5 * tintScale) + (tint[0] * tintScale)
                color[1] = color[1] - (0.5 * tintScale) + (tint[1] * tintScale)
                color[2] = color[2] - (0.5 * tintScale) + (tint[2] * tintScale)
        if(drivable == False):
            if(get_prefs(context).addTintToReject):
                tint = getattr(get_prefs(context),"rejectColor")
                tintScale = getattr(get_prefs(context),"rejectScale")
                color[0] = color[0] - (0.5 * tintScale) + (tint[0] * tintScale)
                color[1] = color[1] - (0.5 * tintScale) + (tint[1] * tintScale)
                color[2] = color[2] - (0.5 * tintScale) + (tint[2] * tintScale)
    return color

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
    kclExportFlagOnly : bpy.props.BoolProperty(name="Only objects with flag", default=True)
    kclExportScale : bpy.props.FloatProperty(name="Scale", min = 0.0001, max = 10000, default = 100)
    kclExportLowerWalls : bpy.props.BoolProperty(name="Lower Walls", default=True)
    kclExportLowerWallsBy : bpy.props.IntProperty(name="Lower Walls by", default= 30)
    kclExportLowerDegree : bpy.props.IntProperty(name="Degree", default= 45)
    kclExportWeakWalls : bpy.props.BoolProperty(name="Weak Walls")
    kclExportDropUnused : bpy.props.BoolProperty(name="Drop Unused")
    kclExportDropFixed : bpy.props.BoolProperty(name="Drop Fixed")
    kclExportDropInvalid : bpy.props.BoolProperty(name="Drop Invalid")
    kclExportRemoveFacedown : bpy.props.BoolProperty(name="Remove facedown road")
    kclExportRemoveFaceup : bpy.props.BoolProperty(name="Remove faceup walls")

    def execute(self, context):
        filepath = self.filepath
        bpy.ops.object.mode_set(mode='OBJECT')
        selection = context.selected_objects
        objectsToExport = []
        if(self.kclExportSelection):
            objectsToExport = selection
        else:
            objectsToExport = [obj for obj in bpy.data.objects if obj.type == "MESH"]
        
        if(self.kclExportFlagOnly):
            objectsToExport1 = [obj for obj in objectsToExport if checkFlagInName(obj.data.name)]
            objectsToExport = objectsToExport1

        bpy.ops.object.select_all(action='DESELECT')
        for obj in objectsToExport:
            obj.select_set(True)

        
        selectionBool = False
        if(self.kclExportSelection or self.kclExportFlagOnly):
            selectionBool = True

        bpy.ops.export_scene.obj(filepath=filepath, use_selection=selectionBool, use_blen_objects=False, use_materials=False, use_normals=True, use_triangles=True, group_by_object=True, global_scale=self.kclExportScale)
        
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

        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            obj.select_set(True)

        return {'FINISHED'}

class import_kcl_file(bpy.types.Operator, ImportHelper):
    bl_idname = "kclc.load"
    bl_label = "Import KCL file"       
    filename_ext = '.kcl'
    bl_options = {'UNDO'}
    bl_description = "Loads KCL file"
    
    filter_glob: bpy.props.StringProperty(
        default='*.kcl',
        options={'HIDDEN'}
    )

    kclImportColor : bpy.props.EnumProperty(name = "Imported colors", items=[("0", "Random color", ''),
                                                                        ("1", "Use custom scheme", '')],default="1")
    kclImportScale : bpy.props.FloatProperty(name = "Scale", default=0.01, max=100,min=0.0001)

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
        bpy.ops.transform.resize(value=(self.kclImportScale, self.kclImportScale, self.kclImportScale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
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
                            if(self.kclImportColor == "0"):
                                 mat.diffuse_color = (random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),1)
                            elif(self.kclImportColor == "1"):
                                _kclType,_variant,_shadow,_trickable,_drivable,_softWall = decodeFlag(properFlag[-4:])
                                colorR = getSchemeColor(context,_kclType,_trickable,_drivable,_shadow)
                                
                                mat.diffuse_color = (colorR[0],colorR[1],colorR[2],1)
                        obj.data.materials.append(mat)

        
        return {'FINISHED'}

class export_autodesk_dae(bpy.types.Operator, ExportHelper):
    bl_idname = "export.autodesk_dae"
    bl_label = "Export Autodesk DAE"    
    bl_description = "Export BrawlBox/BrawlCrate friendly Collada (.dae) file"
    filename_ext = ".dae"
    filter_glob: bpy.props.StringProperty(
        default='*.dae',
        options={'HIDDEN'}
    )
    daeExportPathMode : bpy.props.EnumProperty(name="Path Mode", items=[('AUTO', "Auto", ""),
                                                                        ('COPY', "Copy", "")])
    daeExportSelection : bpy.props.BoolProperty(name="Selection only", default = False)
    daeExportCollection : bpy.props.BoolProperty(name="Active collection", default = False)
    daeExportScale : bpy.props.FloatProperty(name="Scale", default = 1)



    def execute(self, context):
        filepath = self.filepath
        os.system("del \"" + filepath[:-4]+"-pomidor.dae\"")
        bpy.ops.export_scene.fbx(filepath = filepath, use_selection = self.daeExportSelection,  filter_glob='*.dae', use_active_collection = self.daeExportCollection, global_scale = self.daeExportScale, apply_scale_options='FBX_SCALE_NONE', object_types={'MESH'}, use_mesh_modifiers=True, path_mode=self.daeExportPathMode)
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
def export_kcl_button(self, context):
    self.layout.operator("kclc.export", text="KCL")
def import_kcl_button(self, context):
    self.layout.operator("kclc.load", text="KCL")

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
                continue
            object_position = object.location
            name = object.name
            properties = name.split("_")
            areaNumber = '{0:0{1}X}'.format(int(properties[1]), 2)
            areaShape = '{0:0{1}X}'.format(int(properties[2]), 2)
            areaType = '{0:0{1}X}'.format(int(properties[3]), 2)
            areaID = "FF" if properties[4] == "-1" else '{0:0{1}X}'.format(int(properties[4]), 2)
            areaPrority = '{0:0{1}X}'.format(int(properties[5]), 2)
            areaSet1 = '{0:0{1}X}'.format(int(properties[6]), 4)
            areaSet2 = '{0:0{1}X}'.format(int(properties[7]), 4)
            areaSet = str(areaSet1) + str(areaSet2)
            areaRoute = '{0:0{1}X}'.format(int(properties[8]), 2)
            if properties[8] == "-1":
                areaRoute = "FF"
            areaEnemy = '{0:0{1}X}'.format(int(properties[9]), 2)
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
class load_kmp_area(bpy.types.Operator, ImportHelper):
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
            areaRoute = struct.unpack('>B', file.read(1))[0]
            areaEnemy = struct.unpack('>B', file.read(1))[0]
            areaPadding = struct.unpack('>h', file.read(2))[0]
            if(areaEnemy == 255):
                areaEnemy = -1
            if(areaRoute == 255):
                areaRoute = -1
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
            
        file.close()
        loading = 0
        return {'FINISHED'}

class load_kmp_enemy(bpy.types.Operator, ImportHelper):
    bl_idname = "kmpe.load"
    bl_label = "Import Enemy Paths as Curve"       
    filename_ext = '.kmp'
    bl_description = "Imports main enemy path as curve. Used for previewing replay cameras."
    
    filter_glob: bpy.props.StringProperty(
        default='*.kmp',
        options={'HIDDEN'}
    )
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
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
        
        enptOffset = 80 + sectionOffsets[1]
        enphOffset = 80 + sectionOffsets[2]
        file.seek(enphOffset, 0)
        enphNumber = struct.unpack('>H', file.read(2))[0]
        enphUnused = struct.unpack('>H', file.read(2))[0]
        giantPointShitfest = []
        groupShitfest = [0]
        loop = True
        while(loop):
            enphStart = struct.unpack('>B', file.read(1))[0]
            enphLenght = struct.unpack('>B', file.read(1))[0]
            enphLast = enphStart+enphLenght-1
            file.seek(6, 1)
            enphNext0 = struct.unpack('>B', file.read(1))[0]
            enphNextOffset = 84 + sectionOffsets[2] + (16 * enphNext0)
            file.seek(enphNextOffset, 0)
            for i in range(int(enphLenght)):
                giantPointShitfest.append(enphStart+i)
            
            if(enphNext0 in groupShitfest):
                loop=False
            groupShitfest.append(enphNext0)
        biggerPointShitfest = []
        for i in giantPointShitfest:
            enptPointOffset = 84 + sectionOffsets[1] + (20 * i)
            file.seek(enptPointOffset, 0)
            position = [0,0,0]
            x = struct.unpack('>f', file.read(4))[0]
            y = struct.unpack('>f', file.read(4))[0]
            z = struct.unpack('>f', file.read(4))[0]
            position[0] = x / scale
            position[2] = y / scale
            position[1] = z / scale * -1
            biggerPointShitfest.append(position)

        crv = bpy.data.curves.new('crv', 'CURVE')
        crv.dimensions = '3D'
        spline = crv.splines.new(type='BEZIER')
        spline.bezier_points.add(len(biggerPointShitfest) - 1) 
        for p, new_co in zip(spline.bezier_points, biggerPointShitfest):
            p.co = (new_co)
        obj = bpy.data.objects.new('ENPT', crv)
        bpy.data.scenes[0].collection.objects.link(obj)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='AUTOMATIC')
        bpy.ops.object.mode_set(mode='OBJECT')




        file.close()
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
            
oldFrameCount = 250
@persistent
def update_scene_handler(scene):

    global lastselection, setting1users, setting2users, oldFrameCount
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
    scale = mytool.scale


    if(loading == 0):
        currentFrameCount = scene.frame_end

        if(currentFrameCount is not oldFrameCount):
            for object in bpy.context.selected_objects:
                updateCame(object,bpy.context)
            oldFrameCount = currentFrameCount
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
                    if(object.name.startswith("CAMEVP_")):
                        if(object.name[-4] == "."):
                            existingCames = -1 * i - 1
                            for obj in bpy.data.objects:
                                if "camevp_" in obj.name.lower():
                                    existingCames = existingCames + 1
                            name = object.name[:-5] + str(existingCames)
                            object.name=name
                    if(object.name.startswith("CAME_")):
                        if(object.name[-4] == "."):
                            existingCames = -1 * i - 1
                            for obj in bpy.data.objects:
                                if "came_" in obj.name.lower():
                                    existingCames = existingCames + 1
                            name = object.name[:-4]
                            properties = name.split("_")
                            object.name = "CAME_" + str(existingCames) + "_" + properties[2] + "_" + properties[3] + "_" + properties[4] + "_" + properties[5]
                            newVP = "CAMEVP_" + str(existingCames)
                            oldVPpos = bpy.context.scene.objects["CAMEVP_" + properties[1]].location
                            if newVP not in scene.objects.keys():
                                bpy.ops.mesh.primitive_uv_sphere_add(radius=scale/63.5,location=oldVPpos)
                                name="CAMEVP_"+str(existingCames)
                                bpy.context.object.name = name
                                vp = bpy.context.scene.objects["CAMEVP_" + str(existingCames)]
                                object.constraints["Track To"].target = vp
                                object.select_set(True)
                                vp.select_set(True)
                            else:
                                vp = bpy.context.scene.objects["CAMEVP_" + str(existingCames)]
                                s=0
                                if(vp.select_get()):
                                    s=1
                                object.constraints["Track To"].target = vp
                                object.select_set(True)
                                if(s==1):
                                    vp.select_set(True)

                   


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

            if(activeObject.name.startswith("CAME_")):
                if(lastselection != activeObject):
                    name = activeObject.name
                    properties = name.split("_")   
                    mytool.kmp_cameEnumType = "B" + properties[2]
                    mytool.kmp_cameCustomId = int(properties[1])
                    mytool.kmp_cameOpNext = int(properties[3])
                    mytool.kmp_cameRoute = int(properties[4])
                    scene.frame_end = int(properties[5])
            if(activeObject.name.startswith("CAME_")):
                if(lastselection != activeObject):
                    if(activeObject.type == 'CAMERA'):
                        bpy.context.scene.camera = activeObject
    lastselection = activeObject

@persistent
def load_file_handler(dummy):
    global current_version, latest_version, prerelease_version
    responseLatest = requests.get("https://api.github.com/repos/Gabriela-Orzechowska/Blender-MKW-Utilities/releases/latest")
    responseVersions = requests.get("https://api.github.com/repos/Gabriela-Orzechowska/Blender-MKW-Utilities/releases")
    prerelease = responseVersions.json()[0]["url"]
    responseVersions = requests.get(prerelease)
    prerelease_version = responseVersions.json()["tag_name"]
    latest_version = responseLatest.json()["tag_name"]

@persistent
def frame_change_handler(scene):
    mytool = scene.kmpt
    activeObject = bpy.context.active_object
    scene = bpy.context.scene
    if(scene.frame_current == scene.frame_end):
        if(bpy.context.screen.is_animation_playing):
            if(mytool.kmp_cameGoToNext == True):
                if(activeObject.type == 'CAMERA'):
                    properties = activeObject.name.split("_")
                    checkName = "CAME_"+str(properties[3])+"_"
                    found = 0
                    for ob in bpy.context.scene.objects:

                        if(checkName in ob.name):
                            bpy.ops.object.select_all(action='DESELECT')
                            ob.select_set(True)
                            bpy.context.view_layer.objects.active =ob
                            obproperties = ob.name.split("_")
                            scene.frame_end = int(obproperties[5])
                            scene.frame_current = 0
                            scene.camera = ob
                            found = 1
                    if(found == 0):
                        if(mytool.kmp_cameStop):
                            bpy.ops.screen.animation_cancel(restore_frame=False)
            elif(mytool.kmp_cameStop):
                bpy.ops.screen.animation_cancel(restore_frame=False)


def get_prefs(context):
	return context.preferences.addons[__name__].preferences

def set_bit(value, bit_index):
     return value | (1 << bit_index)

def get_bit(value, bit_index):
     return value & (1 << bit_index)

def clear_bit(value, bit_index):
     return value & ~(1 << bit_index)

class ExportPrefs(bpy.types.Operator, ExportHelper):
    bl_idname = "prefs.export"
    bl_label = "Export Preferences"
    filename_ext = ".utils_pref"

    filter_glob: bpy.props.StringProperty(
        default='*.utils_pref',
        options={'HIDDEN'}
    )

    def execute(self, context):
        filepath = self.filepath
        file = open(filepath,'wb')
        boolToByte = 0xFF if get_prefs(context).prerelease_bool else 0x00
        settings = 0
        settings += int(get_prefs(context).darkenBLIGHT==True)*16
        settings += int(get_prefs(context).addTintToTrickable==True)*8
        settings += int(get_prefs(context).addTintToReject==True)*4
        settings += int(get_prefs(context).prerelease_bool==True)*2
        settings += int(get_prefs(context).updates_bool==True)
        file.write(struct.pack('>4s',bytes("UPEF","ascii")))
        file.write(struct.pack('>B',0x0A))
        file.write(struct.pack('>B',settings))
        file.write(struct.pack('>f',get_prefs(context).blightScale))
        values = get_prefs(context).trickableColor
        file.write(struct.pack('>3f',values[0],values[1],values[2]))
        file.write(struct.pack('>f',get_prefs(context).trickableScale))
        values = get_prefs(context).rejectColor
        file.write(struct.pack('>3f',values[0],values[1],values[2]))
        file.write(struct.pack('>f',get_prefs(context).rejectScale))
        for i in range(32):
            color = "kclColorT" + hex(i)[2:].zfill(2).upper()
            values = getattr(get_prefs(context), color)
            file.write(struct.pack('>3f',values[0],values[1],values[2]))
        
        
        
        file.close()
        return {'FINISHED'}
class ImportPrefs(bpy.types.Operator, ImportHelper):
    bl_idname = "prefs.import"
    bl_label = "Import Preferences"
    filename_ext = ".utils_pref"

    filter_glob: bpy.props.StringProperty(
        default='*.utils_pref',
        options={'HIDDEN'}
    )

    def execute(self, context):
        filepath = self.filepath
        file = open(filepath,'rb')
        header = struct.unpack('>4s', file.read(4))[0].decode("ascii")
        if(header != "UPEF"):
            self.report({"WARNING"}, "Wrong file header")
            return {'CANCELLED'}
        version = struct.unpack('>B', file.read(1))[0]
        settings = struct.unpack('>B', file.read(1))[0]
        settingsBin = '{:08b}'.format(settings)
        setattr(get_prefs(context),"updates_bool",settingsBin[7]=='1')
        setattr(get_prefs(context),"prerelease_bool",settingsBin[6]=='1')
        setattr(get_prefs(context),"addTintToReject",settingsBin[5]=='1')
        setattr(get_prefs(context),"addTintToTrickable",settingsBin[4]=='1')
        setattr(get_prefs(context),"darkenBLIGHT",settingsBin[3]=='1')
        blightScale = struct.unpack('>f', file.read(4))[0]
        get_prefs(context).blightScale = blightScale
        trickableTint = [0,0,0]
        trickableTint[0] = struct.unpack('>f', file.read(4))[0]
        trickableTint[1] = struct.unpack('>f', file.read(4))[0]
        trickableTint[2] = struct.unpack('>f', file.read(4))[0]
        get_prefs(context).trickableColor = trickableTint
        trickableScale = struct.unpack('>f', file.read(4))[0]
        get_prefs(context).trickableScale = trickableScale
        rejectTint =[0,0,0]
        rejectTint[0] = struct.unpack('>f', file.read(4))[0]
        rejectTint[1] = struct.unpack('>f', file.read(4))[0]
        rejectTint[2] = struct.unpack('>f', file.read(4))[0]
        get_prefs(context).rejectColor = rejectTint
        rejectScale = struct.unpack('>f', file.read(4))[0]
        get_prefs(context).rejectScale = rejectScale
        for i in range(32):
            color = "kclColorT" + hex(i)[2:].zfill(2).upper()
            values = [0,0,0]
            values[0] = struct.unpack('>f', file.read(4))[0]
            values[1] = struct.unpack('>f', file.read(4))[0]
            values[2] = struct.unpack('>f', file.read(4))[0]
            setattr(get_prefs(context),color,values)
        
        
        
        file.close()
        return {'FINISHED'}
class PreferenceProperty(bpy.types.AddonPreferences):
    bl_idname = __name__
#region preferences
    updates_bool : bpy.props.BoolProperty(name="Check for updates", default=True)
    prerelease_bool : bpy.props.BoolProperty(name="Check for pre-release versions", default=False)

    openScheme : bpy.props.BoolProperty(name="Custom KCL Flag Scheme")

    darkenBLIGHT : bpy.props.BoolProperty(name="Darken Shadow Flags",default=True)
    blightScale : bpy.props.FloatProperty(name="Scale",min=0.0,max=0.1,default=0.3)
    addTintToTrickable : bpy.props.BoolProperty(name="Add Color Tint to Trickable",default=True)
    trickableColor : bpy.props.FloatVectorProperty(name='Color', subtype='COLOR',min=0.0,max=1.0,default=[0.8,0.8,0])
    trickableScale : bpy.props.FloatProperty(name="Scale",min=0.0,max=1.0,default=0.3)
    addTintToReject : bpy.props.BoolProperty(name="Add Color Tint to non-Drivable",default=True)
    rejectColor : bpy.props.FloatVectorProperty(name='Color', subtype='COLOR',min=0.0,max=1.0,default=[1,0,0])
    rejectScale : bpy.props.FloatProperty(name="Scale",min=0.0,max=1.0,default=0.4)

    kclColorT00 : bpy.props.FloatVectorProperty(name='Road (0x00)', subtype='COLOR',min=0.0,max=1.0,default=[0.8,0.8,0.8])
    kclColorT01 : bpy.props.FloatVectorProperty(name='Slippery Road 1 (0x01)', subtype='COLOR',min=0.0,max=1.0,default=[0.7,0.65,0.3])
    kclColorT02 : bpy.props.FloatVectorProperty(name='Weak Off-road (0x02)', subtype='COLOR',min=0.0,max=1.0,default=[0.25,0.43,0])
    kclColorT03 : bpy.props.FloatVectorProperty(name='Off-road (0x03)', subtype='COLOR',min=0.0,max=1.0,default=[0,0.3,0])
    kclColorT04 : bpy.props.FloatVectorProperty(name='Heavy Off-road (0x04)', subtype='COLOR',min=0.0,max=1.0,default=[0,0.15,0])
    kclColorT05 : bpy.props.FloatVectorProperty(name='Slippery Road 2 (0x05)', subtype='COLOR',min=0.0,max=1.0,default=[0,0.45,0.45])
    kclColorT06 : bpy.props.FloatVectorProperty(name='Boost Panel (0x06)', subtype='COLOR',min=0.0,max=1.0,default=[0.6,0.3,0])
    kclColorT07 : bpy.props.FloatVectorProperty(name='Boost Ramp (0x07)', subtype='COLOR',min=0.0,max=1.0,default=[0.45,0.126,0])
    kclColorT08 : bpy.props.FloatVectorProperty(name='Jump Pad (0x08)', subtype='COLOR',min=0.0,max=1.0,default=[1,0.8,0])
    kclColorT09 : bpy.props.FloatVectorProperty(name='Item Road (0x09)', subtype='COLOR',min=0.0,max=1.0,default=[0.7,0,0.4])
    kclColorT0A : bpy.props.FloatVectorProperty(name='Solid Fall (0x0A)', subtype='COLOR',min=0.0,max=1.0,default=[0.3,0,0])
    kclColorT0B : bpy.props.FloatVectorProperty(name='Moving Road (0x0B)', subtype='COLOR',min=0.0,max=1.0,default=[0,0,0.45])
    kclColorT0C : bpy.props.FloatVectorProperty(name='Wall (0x0C)', subtype='COLOR',min=0.0,max=1.0,default=[0.25,0.25,0.25])
    kclColorT0D : bpy.props.FloatVectorProperty(name='Invisible Wall (0x0D)', subtype='COLOR',min=0.0,max=1.0,default=[0,1,1])
    kclColorT0E : bpy.props.FloatVectorProperty(name='Item Wall (0x0E)', subtype='COLOR',min=0.0,max=1.0,default=[0.5,0.2,0.6])
    kclColorT0F : bpy.props.FloatVectorProperty(name='Wall 3 (0x0F)', subtype='COLOR',min=0.0,max=1.0,default=[0.3,0.3,0.3])

    kclColorT10 : bpy.props.FloatVectorProperty(name='Fall Boundary (0x10)', subtype='COLOR',min=0.0,max=1.0,default=[1,0,0])
    kclColorT11 : bpy.props.FloatVectorProperty(name='Cannon Activator (0x11)', subtype='COLOR',min=0.0,max=1.0,default=[0.7,0,0.4])
    kclColorT12 : bpy.props.FloatVectorProperty(name='Force Recalculation (0x12)', subtype='COLOR',min=0.0,max=1.0,default=[0.2,0.2,0.3])
    kclColorT13 : bpy.props.FloatVectorProperty(name='Half-pipe Ramp (0x13)', subtype='COLOR',min=0.0,max=1.0,default=[0,0.333,0.65])
    kclColorT14 : bpy.props.FloatVectorProperty(name='Wall (0x14)', subtype='COLOR',min=0.0,max=1.0,default=[0.35,0.35,0.35])
    kclColorT15 : bpy.props.FloatVectorProperty(name='Moving Road (0x15)', subtype='COLOR',min=0.0,max=1.0,default=[0,0,0.56])
    kclColorT16 : bpy.props.FloatVectorProperty(name='Sticky Road (0x16)', subtype='COLOR',min=0.0,max=1.0,default=[0.6,0.3,0.6])
    kclColorT17 : bpy.props.FloatVectorProperty(name='Road (0x17)', subtype='COLOR',min=0.0,max=1.0,default=[0.8,0.8,0.8])
    kclColorT18 : bpy.props.FloatVectorProperty(name='Sound Trigger (0x18)', subtype='COLOR',min=0.0,max=1.0,default=[0.2,0.3,0.5])
    kclColorT19 : bpy.props.FloatVectorProperty(name='Weak Wall (0x19)', subtype='COLOR',min=0.0,max=1.0,default=[0.4,0.4,0.3])
    kclColorT1A : bpy.props.FloatVectorProperty(name='Effect Trigger (0x1A)', subtype='COLOR',min=0.0,max=1.0,default=[0.2,0.1,0.3])
    kclColorT1B : bpy.props.FloatVectorProperty(name='Item State Modifier (0x1B)', subtype='COLOR',min=0.0,max=1.0,default=[0.45,0.3,0.3])
    kclColorT1C : bpy.props.FloatVectorProperty(name='Half-Pipe Invisible Wall (0x1C)', subtype='COLOR',min=0.0,max=1.0,default=[0.1,0.5,0.5])
    kclColorT1D : bpy.props.FloatVectorProperty(name='Moving Road (0x1D)', subtype='COLOR',min=0.0,max=1.0,default=[0,0,0.36])
    kclColorT1E : bpy.props.FloatVectorProperty(name='Special Wall (0x1E)', subtype='COLOR',min=0.0,max=1.0,default=[0.6,0.4,0.5])
    kclColorT1F : bpy.props.FloatVectorProperty(name='Wall 5 (0x1F)', subtype='COLOR',min=0.0,max=1.0,default=[0.2,0.2,0.2])
#endregion
    
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        row = layout.row()
        row.operator("prefs.import")
        row.operator("prefs.export")
        col = layout.column()
        col.prop(self, "updates_bool")
        if(self.updates_bool):
            col.prop(self, "prerelease_bool")
        box = layout.box()
        column = box.column()
        column.prop(self,"openScheme",
            icon="TRIA_DOWN" if self.openScheme else "TRIA_RIGHT", emboss=False
        )
        if(self.openScheme):
            column.prop(self,"darkenBLIGHT")
            if(self.darkenBLIGHT):
                column.prop(self,"blightScale")
            column.prop(self,"addTintToTrickable")
            if(self.addTintToTrickable):
                column.prop(self,"trickableColor")
                column.prop(self,"trickableScale")
            column.prop(self,"addTintToReject")
            if(self.addTintToReject):
                column.prop(self,"rejectColor")
                column.prop(self,"rejectScale")
            column.label(text="")
            for i in range (32):
                name = "kclColorT"+'{0:0{1}X}'.format(i,2)
                column.prop(self,name)

import textwrap
def _label_multiline(context, text, parent):
    chars = int(context.region.width / 7) 
    wrapper = textwrap.TextWrapper(width=chars)
    text_lines = wrapper.wrap(text=text)
    for text_line in text_lines:
        parent.label(text=text_line)

    
def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

class BadPluginInstall(bpy.types.Panel):
    bl_label = "Wrong plugin installation!"
    bl_idname = "MKW_PT_Bad"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        text="The plugin could not load properly."
        text2="Please make sure to install plugin as a ZIP through User Preferences."
        _label_multiline(
            context=context,
            text=text,
            parent=layout
        )
        _label_multiline(
            context=context,
            text=text2,
            parent=layout
        )


classes = [PreferenceProperty, MyProperties, KMPUtilities, KCLSettings, KCLUtilities,ExportPrefs,ImportPrefs, AREAUtilities, CAMEUtilities, RouteUtilities, MaterialUtilities, scene_setup, keyframes_to_route, openWSZSTPage, openIssuePage, timeline_to_route, set_alpha_blend, set_alpha_clip, remove_specular_metalic, create_camera, kmp_came, apply_kcl_flag, cursor_kmp, import_kcl_file, kmp_gobj, kmp_area, kmp_c_cube_area, kmp_c_cylinder_area, load_kmp_area, load_kmp_enemy, export_kcl_file, openGithub, merge_duplicate_objects, export_autodesk_dae]
 
wszstInstalled = False
 
def register():
    global wszstInstalled
    wszst = os.popen('wszst version').read()
    if(wszst.startswith("wszst: Wiimms SZS Tool")):
        wszstInstalled = True
    script_file = os.path.normpath(__file__)
    directory = os.path.dirname(script_file)
    if directory.endswith("Blender-KMP-Utilities"):
        for cls in classes:
            bpy.utils.register_class(cls)
        bpy.app.handlers.depsgraph_update_post.append(update_scene_handler)
        bpy.app.handlers.frame_change_post.append(frame_change_handler)
        bpy.app.handlers.load_post.append(load_file_handler)
        bpy.types.TOPBAR_MT_file_export.append(export_autodesk_dae_button)
        if(wszstInstalled):
            bpy.types.TOPBAR_MT_file_export.append(export_kcl_button)
            bpy.types.TOPBAR_MT_file_import.append(import_kcl_button)
        bpy.types.Scene.kmpt = bpy.props.PointerProperty(type= MyProperties)
        
    else:
        bpy.utils.register_class(BadPluginInstall)

 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    try:
        bpy.utils.unregister_class(BadPluginInstall)
    except RuntimeError:
        pass
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.frame_change_post.clear()
    bpy.app.handlers.load_post.clear()
    bpy.types.TOPBAR_MT_file_export.remove(export_autodesk_dae_button)
    try:
        bpy.types.TOPBAR_MT_file_export.remove(export_kcl_button)
        bpy.types.TOPBAR_MT_file_import.remove(import_kcl_button)
    except RuntimeError:
        pass
    del bpy.types.Scene.kmpt
 
 
if __name__ == "__main__":
    register()