# pyright: reportMissingImports=false, reportMissingModuleSource=false
bl_info = {
    "name" : "Mario Kart Wii Utilities",
    "author" : "Gabriela_",
    "version" : (1, 10, 1),
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
import locale
import bmesh
import numpy as np
from mathutils import Vector
import time
import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
    IntProperty,
    FloatVectorProperty,
    PointerProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    orientation_helper,
    path_reference_mode,
    axis_conversion,
)
from bpy.app.handlers import persistent
from . import export_obj

from nodeitems_utils import NodeItem, register_node_categories, unregister_node_categories
from nodeitems_builtins import ShaderNodeCategory

BLENDER_30 = bpy.app.version[0] >= 3
BLENDER_33 = bpy.app.version[0] >= 3 and bpy.app.version[1] >= 3
BLENDER_34 = bpy.app.version[0] >= 3 and bpy.app.version[1] >= 4
lastselection = []
setting1users = ["A2", "A3", "A6", "A8", "A9", "A10"]
setting2users = ["A3", "A6", "A10"]


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

def dummyKCLFunction(self,context):
    a = 2
    b = 1
    c = 3
    d = 7
    active=context.active_object
    if(active):
        bpy.context.view_layer.objects.active=active
    return

class MyProperties(bpy.types.PropertyGroup):
    global areaTypes
    
    #
    #
    # AREA
    #
    #
    
    scale : FloatProperty(name= "Export scale", min= 0.0001, max= 100000, default= 100, description= "Set scale at which your KMP will be exported",update=dummyKCLFunction)
 #region came_types
    kmp_cameEnumType : EnumProperty(name = "Type", items=[("B5", "Opening", "Opening camera, follows route; from its position, it looks at View Start and shifts view to View End if set, otherwise looks at player. This camera type only requires a route. It does not need an AREA Entry."),
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
    kmp_cameRes : IntProperty(name= "Timeline route resolution", min= 2, default= 20, update=updateCame, 
                                            description= "Amount of points to create from timeline")
    kmp_cameGoToNext : BoolProperty(name= "Switch to next after finished", description="Play the next camera (if found) after finishing")
    kmp_cameStop : BoolProperty(name="Disable looping", description="Disable automatic looping of animation")
    kmp_cameOffset : IntProperty(name="ID Offset", default=0, min=0,max=255,description="Add an offset to exported IDs")
    kmp_cameRouteOffset : IntProperty(name="Route ID Offset", default=0, min=0,max=255,description="Add an offset to exported Route IDs")
#endregion
 #region kcl_types   

    #
    #
    # KCL
    #
    #
    
    kcl_showFlag : BoolProperty(name="Current object flag", default=False)

    kcl_masterType : EnumProperty(name = "Type", items=[("T00", "Road (0x00)", ''),
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
                                                            ],update=dummyKCLFunction)
    kcl_variant : IntProperty(name= "Variant", min=0, max=7, default= 0,update=dummyKCLFunction)
    kcl_shadow : IntProperty(name= "Shadow", min=0, max=7, default= 0,update=dummyKCLFunction,description="Controls BLIGHT index of KCL flag")
    kcl_wheelDepth : IntProperty(name="Wheel Depth", default=0, min=0, max=2, description="Higher values (0, 1, 2 are possible) will inset drivers' wheels deeper into road. It likely has other subtle effects on wheel physics; exact details are unknown.")
    kcl_trickable : BoolProperty(name= "Trickable", default=False,update=dummyKCLFunction, description="Makes the road trickable")
    kcl_drivable : BoolProperty(name= "Reject road", default=False,update=dummyKCLFunction,description="Pushes player away from driving on the road")
    kcl_bounce : BoolProperty(name= "Soft Wall", default=False, description="Used to get rid of bean corners, use only on walls that meet road",update=dummyKCLFunction)
    
    kclVariantT00 : EnumProperty(name = "Variant", items=[("0", "Normal", ''),
                                                                ("1", "Dirt with GFX (7.3 , 8.3)", ''),
                                                                ("2", "Dirt without GFX", ''),
                                                                ("3", "Smooth", ''),
                                                                ("4", "Wood", ''),
                                                                ("5", "Snow", ''),
                                                                ("6", "Metal grate", ''),
                                                                ("7", "Normal (Sound cuts off)", '')],update=dummyKCLFunction)
    kclVariantT01 : EnumProperty(name = "Variant", items=[("0", "White sand", ''),
                                                                ("1", "Dirt", ''),
                                                                ("2", "Water", ''),
                                                                ("3", "Snow", ''),
                                                                ("4", "Grass", ''),
                                                                ("5", "Yellow sand", ''),
                                                                ("6", "Sand, no GFX", ''),
                                                                ("7", "Dirt, no GFX", '')],update=dummyKCLFunction)
    kclVariantT02 : EnumProperty(name = "Variant", items=[("0", "Orange Sand", ''),
                                                                ("1", "Dirt", ''),
                                                                ("2", "Water", ''),
                                                                ("3", "Grass, darker GFX", ''),
                                                                ("4", "Grass, lighter GFX", ''),
                                                                ("5", "Carpet", ''),
                                                                ("6", "Gravel", ''),
                                                                ("7", "Gravel, different impact SFX", '')],update=dummyKCLFunction)
    kclVariantT03 : EnumProperty(name = "Variant", items=[("0", "Sand", ''),
                                                                ("1", "Dirt", ''),
                                                                ("2", "Mud", ''),
                                                                ("3", "Water, no GFX", ''),
                                                                ("4", "Grass", ''),
                                                                ("5", "Sand, lighter GFX", ''),
                                                                ("6", "Gravel, different impact SFX", ''),
                                                                ("7", "Carpet", '')],update=dummyKCLFunction)
    kclVariantT04 : EnumProperty(name = "Variant", items=[("0", "Sand", ''),
                                                                ("1", "Dirt", ''),
                                                                ("2", "Mud", ''),
                                                                ("3", "Flowers", ''),
                                                                ("4", "Grass", ''),
                                                                ("5", "Snow", ''),
                                                                ("6", "Sand", ''),
                                                                ("7", "Dirt, no GFX", '')],update=dummyKCLFunction)
    kclVariantT05 : EnumProperty(name = "Variant", items=[("0", "Ice", ''),
                                                                ("1", "Mud", ''),
                                                                ("2", "Water", ''),
                                                                ("6", "Normal road, different sound", '')],update=dummyKCLFunction)
    kclVariantT06 : EnumProperty(name = "Variant", items=[("0", "Default", ''),
                                                                ("1", "(Check description)", 'if used in course.kcl and casino_roulette is nearby, the road slowly rotates everything around it counterclockwise. Used in Chain Chomp Wheel.'),
                                                                ("2", "Unknown", '')],update=dummyKCLFunction)
    kclVariantT07 : EnumProperty(name = "Variant", items=[("0", "2 flips", ''),
                                                                ("1", "1 flip", ''),
                                                                ("2", "No flips", '')],update=dummyKCLFunction) 
    kclVariantT08 : EnumProperty(name = "Variant", items=[("0", "Stage 2, used in GBA Bowser Castle 3", ''),
                                                                ("1", "Stage 3, used in SNES Ghost Valley 2", ''),
                                                                ("2", "Stage 1, used in GBA Shy Guy Beach", ''),
                                                                ("3", "Stage 4, used in Mushroom Gorge", ''),
                                                                ("4", "Stage 5, Bouncy mushroom", ''),
                                                                ("5", "Stage 4, used in Chain Chomp Wheel", ''),
                                                                ("6", "Stage 2, used in DS Yoshi Falls and Funky Stadium", ''),
                                                                ("7", "Stage 4, unused", '')],update=dummyKCLFunction)   
    kclVariantT09 : EnumProperty(name = "Variant", items=[("0", "Unknown", ''),
                                                                ("1", "Unknown", ''),
                                                                ("2", "Used on metal grates", ''),
                                                                ("3", "Unknown. Used on wooden paths/grass/mushrooms", ''),
                                                                ("4", "Unknown", ''),
                                                                ("5", "Unknown. Used on grass/bushes", ''),
                                                                ("6", "Unknown", '')],update=dummyKCLFunction)   
    kclVariantT0A : EnumProperty(name = "Variant", items=[("0", "Sand", ''),
                                                                ("1", "Sand/Underwater", ''),
                                                                ("2", "Unknown", ''),
                                                                ("3", "Ice", ''),
                                                                ("4", "Dirt", ''),
                                                                ("5", "Grass", ''),
                                                                ("6", "Wood", ''),
                                                                ("7", "Dark sand with GFX", '')],update=dummyKCLFunction)
    kclVariantT0B : EnumProperty(name = "Variant", items=[("0", "Moving water that follows a route, pulling the player downwards.",''),
                                                                ("1", "Moving water that follows a route and strongly pulls the player downwards, making it hard to drive.",''),
                                                                ("2", "Moving water that follows a route from the start of the path to the end of it.",''),
                                                                ("3", "Moving water that follows a route from the start of the path to the end of it and disables player's acceleration", 'Uses 2 AREA settings:\nSetting 1: Current player\'s speed modifier.\neg. value of 100 will keep current player\'s speed. Values below 100 will slow down player until full stop.\nSetting 2: Moving speed.'),
                                                                ("4", "Moving asphalt",''),
                                                                ("5", "Moving asphalt (2)",''),
                                                                ("6", "Moving road",''),
                                                                ("7", "Moving road (2)",'')],
                                                                update=dummyKCLFunction)
    kclVariantT0C : EnumProperty(name = "Variant", items=[("0", "Normal", ''),
                                                                ("1", "Rock", ''),
                                                                ("2", "Metal", ''),
                                                                ("3", "Wood", ''),
                                                                ("4", "Ice", ''),
                                                                ("5", "Bush", ''),
                                                                ("6", "Rope", ''),
                                                                ("7", "Rubber", '')],update=dummyKCLFunction)
    kclVariantT0D : EnumProperty(name = "Variant", items=[("0", "No spark and no character wall hit voice", ''),
                                                                ("1", "Spark and character wall hit voice", '')],update=dummyKCLFunction)
    kclVariantT0E : EnumProperty(name = "Variant", items=[("0", "Unknown", ''),
                                                                ("1", "Unknown. Used on rock walls", ''),
                                                                ("2", "Unknown. Used on metal walls", ''),
                                                                ("3", "Unknown", ''),
                                                                ("4", "Unknown. Unused", ''),
                                                                ("5", "Unknown. Used on grass/bushes", ''),
                                                                ("6", "Unknown. Unused", '')],update=dummyKCLFunction)
    kclVariantT0F : EnumProperty(name = "Variant", items=[("0", "Normal", ''),
                                                                ("1", "Rock", ''),
                                                                ("2", "Metal", ''),
                                                                ("3", "Wood", ''),
                                                                ("4", "Ice", ''),
                                                                ("5", "Bush", ''),
                                                                ("6", "Rope", ''),
                                                                ("7", "Rubber", '')],update=dummyKCLFunction)
    kclVariantT10 : EnumProperty(name = "Variant", items=[("0", "Air fall", ''),
                                                                ("1", "Water", ''),
                                                                ("2", "Lava", ''),
                                                                ("3", "Icy water (Ice on respawn)", ''),
                                                                ("4", "Lava, no GFX", ''),
                                                                ("5", "Burning air fall", ''),
                                                                ("6", "Quicksand", ''),
                                                                ("7", "Short fall", '')],update=dummyKCLFunction)
    kclVariant10Index : IntProperty(name = "KMP Index", default = 0, min = 0, max = 7,update=dummyKCLFunction) 
    kclVariantT11 : EnumProperty(name = "Variant", items=[("0", "To point 0", ''),
                                                                ("1", "To point 1", ''),
                                                                ("2", "To point 2", ''),
                                                                ("3", "To point 3", ''),
                                                                ("4", "To point 4", ''),
                                                                ("5", "To point 5", ''),
                                                                ("6", "To point 6", ''),
                                                                ("7", "To point 7", '')],update=dummyKCLFunction)
    kclVariant12Index : IntProperty(name = "AREA Index", default = 0, min = 0, max = 7,update=dummyKCLFunction) 
    kclVariantT13 : EnumProperty(name = "Variant", items=[("0", "Default", ''),
                                                                ("1", "Boost pad applied", ''),
                                                                ("2", "Unknown", '')],update=dummyKCLFunction)
    kclVariantT14 : EnumProperty(name = "Variant", items=[("0", "Normal", ''),
                                                                ("1", "Rock", ''),
                                                                ("2", "Metal", ''),
                                                                ("3", "Wood", ''),
                                                                ("4", "Ice", ''),
                                                                ("5", "Bush", ''),
                                                                ("6", "Rope", ''),
                                                                ("7", "Rubber", '')],update=dummyKCLFunction)
    kclVariantT15 : EnumProperty(name = "Variant", items=[("0", "Moves west with BeltCrossing and escalator. ", ''),
                                                                ("1", "Moves east with BeltCrossing and west with escalator.", ''),
                                                                ("2", "Moves east with BeltEasy", ''),
                                                                ("3", "Moves west with BeltEasy", ''),
                                                                ("4", "Rotates around BeltCurveA clockwise", ''),
                                                                ("5", "Rotates around BeltCurveA counterclockwise", ''),
                                                                ("6", "Unknown", '')],update=dummyKCLFunction)
    kclVariantT16 : EnumProperty(name = "Variant", items=[("0", "Wood", ''),
                                                                ("1", "Gravel, different impact SFX.", ''),
                                                                ("2", "Carpet", ''),
                                                                ("3", "Dirt, no GFX", ''),
                                                                ("4", "Sand, different impact and drift SFX, no GFX", ''),
                                                                ("5", "Normal road, SFX on slot 4.4", ''),
                                                                ("6", "Normal road", ''),
                                                                ("7", "Mud with GFX", '')],update=dummyKCLFunction)
    kclVariantT17 : EnumProperty(name = "Variant", items=[("0", "Normal road, different sound", ''),
                                                                ("1", "Carpet", ''),
                                                                ("2", "Grass, GFX on 8.3", ''),
                                                                ("3", "Normal road, used on green mushrooms", ''),
                                                                ("4", "Grass", ''),
                                                                ("5", "Glass road with SFX", ''),
                                                                ("6", "Dirt (unused)", ''),
                                                                ("7", "Normal road, SFX on slot 4.4", '')],update=dummyKCLFunction)
    
    kclVariantT18Circuits : EnumProperty(name = "Track", items=[("11", "Luigi Circuit", ''),
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
                                                                ("84", "N64 Bowser's Caslte", '')],update=dummyKCLFunction)
    kclVariantT1811 : EnumProperty(name = "Variant", items=[("0", "No audience noise", ''),
                                                ("1", "Soft audience noise", ''),
                                                ("2", "Audience noise. The race starts with this sound", ''),
                                                ("3", "Lound audience noice", '')],update=dummyKCLFunction)
    kclVariantT1813 : EnumProperty(name = "Variant", items=[("0", "Deactivate all", ''),
                                                ("3", "Enable cave SFX + echo", '')],update=dummyKCLFunction)
    kclVariantT1814 : EnumProperty(name = "Variant", items=[("0", "Sounds off", ''),
                                                ("1", "Hydraulic press area", ''),
                                                ("2", "Shipping dock area", ''),
                                                ("3", "Moving belt area", ''),
                                                ("4", "Steam room", ''),
                                                ("5", "Restart music at beginning", ''),
                                                ("6", "Bulldozer area", ''),
                                                ("7", "Audience area", '')],update=dummyKCLFunction)
    kclVariantT1821 : EnumProperty(name = "Variant", items=[("0", "Deactivates echo", ''),
                                                ("1", "Weak echo", ''),
                                                ("2", "Loud echo", '')],update=dummyKCLFunction)
    kclVariantT1822 : EnumProperty(name = "Variant", items=[("0", "Resets all sound triggers. Shopping mall ambience requires this to play", ''),
                                                ("1", "Weak shopping mall ambience + disables echo", ''),
                                                ("2", "Loud shopping mall ambience + strong echo", ''),
                                                ("3", "Resets all sound triggers and prevents shopping mall ambience from playing until 0 is hit again", ''),
                                                ("4", "Loud shopping mall ambience + disables echo", ''),
                                                ("5", "Same as 3?", '')],update=dummyKCLFunction)
    kclVariantT1823 : EnumProperty(name = "Variant", items=[("0", "Deactivates cheering", ''),
                                                ("1", "Weak cheering ambience", ''),
                                                ("2", "Loud cheering ambience", ''),
                                                ("3", "Loudest cheering ambience.", ''),
                                                ("4", "Enables cheering when going off half-pipe ramps", '')],update=dummyKCLFunction)
    kclVariantT1824 : EnumProperty(name = "Variant", items=[("0", "Music change (outside)", ''),
                                                ("1", "Music change (cave) + gentle echo", ''),
                                                ("2", "Echo", ''),
                                                ("3", "Strong echo", '')],update=dummyKCLFunction)
    kclVariantT1831 : EnumProperty(name = "Variant", items=[("0", "Deactivate echo", ''),
                                                ("1", "Weak echo", ''),
                                                ("2", "Echo", '')],update=dummyKCLFunction)
    kclVariantT1832 : EnumProperty(name = "Variant", items=[("0", "Music change (normal)", ''),
                                                ("1", "Music change (normal), echo", ''),
                                                ("2", "Stronger echo", ''),
                                                ("3", "Music change (underwater), water ambience enabled when entering from 0, 5 or 6, diabled otherwise", ''),
                                                ("4", "Strongest echo, water ambience enabled", ''),
                                                ("5", "Music change (normal), strongest echo, water ambience enabled when entering from 3", ''),
                                                ("6", "Music change (riverside)", '')],update=dummyKCLFunction)
    kclVariantT1833 : EnumProperty(name = "Variant", items=[("0", "Deactivate echo and wind ambience", ''),
                                                ("1", "No effect", ''),
                                                ("2", "Weak echo", ''),
                                                ("3", "Loud echo", ''),
                                                ("4", "Enables wind ambience, deactivates echo", '')],update=dummyKCLFunction)
    kclVariantT1834 : EnumProperty(name = "Variant", items=[("0", "Deactivate echo", ''),
                                                ("1", "Weak echo, toggles after two seconds", ''),
                                                ("2", "Loud echo, toggles after one second", ''),
                                                ("3", "Loud echo, toggles after two seconds", '')],update=dummyKCLFunction)
    kclVariantT1841 : EnumProperty(name = "Variant", items=[("0", "Music change (normal)", ''),
                                                ("1", "Music change (indoors, where the bats come from the sides)", ''),
                                                ("2", "Music change (indoors, where the half-pipes are)", ''),
                                                ("3", "Music change (indoors, where the Pokeys are)", '')],update=dummyKCLFunction)
    kclVariantT1842 : EnumProperty(name = "Variant", items=[("0", "Deactivate city ambience, default music", ''),
                                                ("1", "Stage 2, weak city ambience, adds flute to music", ''),
                                                ("2", "Stage 4, louder city ambience, disable echo", ''),
                                                ("3", "Stage 5, loudest city ambience, disable echo", ''),
                                                ("4", "Stage 3, loud city ambience, enable echo", ''),
                                                ("5", "Stage 1, weakest city ambience, enable echo", '')],update=dummyKCLFunction)
    kclVariantT1843 : EnumProperty(name = "Variant", items=[("0", "Disable one-time use sound trigger (like Bowser's howl)", ''),
                                                ("1", "Bowser's howl + echo. Put 7 at the end of a turn to be able to reuse Bowser's howl", ''),
                                                ("2", "Sound distortion + echo", ''),
                                                ("3", "Deactivate sound distortion + echo", ''),
                                                ("4", "Add drums + echo on music + koopaBall/koopaFigure SFX", ''),
                                                ("5", "Deactivate koopaBall/koopaFigure SFX", ''),
                                                ("6", "Add drums without echo", ''),
                                                ("7", "Back to normal. Allow reuse for one-time use sound trigger", '')],update=dummyKCLFunction)
    kclVariantT1844 : EnumProperty(name = "Variant", items=[("0", "Deactivator", ''),
                                                ("1", "Gate sound 1 (add a deactivator before and after if you use only one gate)", ''),
                                                ("2", "Star ring sound 1", ''),
                                                ("3", "Star ring sound 2", ''),
                                                ("4", "Star ring sound 3", ''),
                                                ("5", "Star ring sound 4", ''),
                                                ("6", "Tunnel sound (add a deactivator to stop it)", '')],update=dummyKCLFunction)
    kclVariantT1854 : EnumProperty(name = "Variant", items=[("0", "Deactivates cheering", ''),
                                                ("1", "Loud cheering", ''),
                                                ("2", "Louder cheering", ''),
                                                ("3", "Weak cheering", '')],update=dummyKCLFunction)
    kclVariantT1861 : EnumProperty(name = "Variant", items=[("0", "Deactivate all", ''),
                                                ("1", "Cave echo", ''),
                                                ("2", "Cave SFX", '')],update=dummyKCLFunction)
    kclVariantT1863 : EnumProperty(name = "Variant", items=[("0", "Unknown. In a position such that a player may collide with this trigger if they complete the dock shortcut", ''),
                                                ("1", "Very, very distant whistles, cheers and chatter from spectators", ''),
                                                ("2", "Very distant whistles, cheers and chatter from spectators", ''),
                                                ("3", "Distant whistles, cheers and chatter from spectators", ''),
                                                ("4", "Whistles, cheers and chatter from spectators", ''),
                                                ("5", "Single wind gust just before the dock section", ''),
                                                ("6", "No spectator ambience", ''),
                                                ("7", "The same as 6? Used between triggers of type 6", '')],update=dummyKCLFunction)
    kclVariantT1873 : EnumProperty(name = "Variant", items=[("0", "No jungle ambience. Used near water sections", ''),
                                                ("1", "Jungle ambience (bird squawks, insect hum, animal roar). Used as a buffer between types 0 and 2", ''),
                                                ("2", "Intense jungle ambience, used in areas of deep forest", ''),
                                                ("3", "Cave ambience", '')],update=dummyKCLFunction)
    kclVariantT1874 : EnumProperty(name = "Variant", items=[("0", "No echo", ''),
                                                ("1", "Weak echo", ''),
                                                ("2", "Loud echo", '')],update=dummyKCLFunction)
    kclVariantT1883 : EnumProperty(name = "Variant", items=[("0", "Deactivate all", ''),
                                                ("1", "Jungle SFX (animals)", ''),
                                                ("2", "Water + wind SFX", '')],update=dummyKCLFunction)
    kclVariantT1884 : EnumProperty(name = "Variant", items=[("0", "Disable one-time use sound trigger (like Bowser's howl)", ''),
                                                ("1", "Turns lava SFX off + disables echo", ''),
                                                ("2", "Bowser's howl. Put 0 at the end of a turn to be able to reuse this", ''),
                                                ("3", "Turns lava SFX off", ''),
                                                ("4", "Turns lava SFX off + echo", ''),
                                                ("5", "Echo", ''),
                                                ("6", "Strong echo", '')],update=dummyKCLFunction)

    kclVariantT1A : EnumProperty(name = "Variant", items=[("0", "Enable BLIGHT effect", ''),
                                                                ("1", "Enable BLIGHT effect (different from 0?)", ''),
                                                                ("2", "Water splash (pocha)", ''),
                                                                ("3", "starGate door activation", ''),
                                                                ("4", "Half-pipe cancellation", ''),
                                                                ("5", "Coin despawner", ''),
                                                                ("6", "Smoke effect on the player when going through dark smoke (truckChimSmkW)", ''),
                                                                ("7", "Unknown", '')],update=dummyKCLFunction)
    kclVariantT1D : EnumProperty(name = "Variant", items=[("0", "Carpet, different impact SFX", ''),
                                                                ("1", "Normal road, different sound, different impact SFX", ''),
                                                                ("2", "Normal road", ''),
                                                                ("3", "Glass road", ''),
                                                                ("4", "Carpet", ''),
                                                                ("5", "No sound, star crash impact SFX (requires starGate for SFX)", ''),
                                                                ("6", "Sand", ''),
                                                                ("7", "Dirt", '')],update=dummyKCLFunction)
    kclVariantT1E : EnumProperty(name = "Variant", items=[("0", "Cacti", ''),
                                                                ("1", "Unknown (rubber wall?)", ''),
                                                                ("2", "Unknown (rubber wall?)", ''),
                                                                ("3", "Unknown", ''),
                                                                ("4", "Unknown, SFX on 4.4", ''),
                                                                ("5", "Unknown", ''),
                                                                ("6", "Unknown", ''),
                                                                ("7", "Unknown", '')],update=dummyKCLFunction)
    kclVariantT1F : EnumProperty(name = "Variant", items=[("0", "Fast Wall, Bump", ''),
                                                                ("2", "Slow Wall, No Effect", '')],update=dummyKCLFunction)    

    kclFinalFlag : StringProperty(name = "Flag")                                                            
#endregion
#region kcl_settings
    kcl_applyMaterial : EnumProperty(name = "Material", items=[("0", "Random color", ''),
                                                                        ("2", "Use custom scheme", ''),
                                                                        ("1", "Keep original", '')],default="2",update=dummyKCLFunction)
    kcl_applyName : EnumProperty(name = "Name", items=[("0", "Flag only", ''),
                                                                    ("1", "Add type label", ''),
                                                                    ("2", "Add type and variant label", ''),
                                                                    ("3", "Add to original", '')
                                                                    ],default="1",update=dummyKCLFunction)
    kcl_autoSeparate : BoolProperty(name = "Auto-separate in Edit Mode", default=True, description="Automatically separate selection when applying flags in edit mode.",update=dummyKCLFunction)
    util_addVCs : BoolProperty(name="Auto-add Vertex Colours Data", default=True)
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
areaTypes = [("A0", "Camera", 'Defines which camera is being used while entering this AREA'),
            ("A1", "EnvEffect", 'Defines an area where EnvFire and EnvSnow is not used, and EnvKareha is used'),
            ("A2", "BFG Entry Swapper", 'Controls which posteffect.bfg is being used'),
            ("A3", "Moving Road", 'Causes moving road terrain in KCL to move'),
            ("A4", "Destination Point", 'This AREA type is used as first destination for Force Recalculation'),
            ("A5", "Minimap Control", 'Used to crop minimap on tournaments'),
            ("A6", "BBLM Changer", 'Changes bloom and glow settings using .bblm files'),
            ("A7", "Flying Boos", 'Flying Boos will appear while inside of this AREA (Requires b_teresa)'),
            ("A8", "Object Grouper", 'Groups objects together'),
            ("A9", "Group Unloader", 'Disables objects of selected group'),
            ("A10", "Fall Boundary", 'Used to define fall boundaries on tournaments')]
current_version = "v0.1.13.2"
latest_version = "v0.1.13.2"
prerelease_version = "v0.1.13.2"

kcl_typeATypes = ["T00","T01","T02","T03","T04","T05","T06","T07","T08","T09","T0A","T16","T17","T1D","T0B"]
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

class buildSZSCurrent(bpy.types.Operator):
    bl_idname = "szs.build"
    bl_label = "Export SZS"

    def execute(self, context):
        bpy.ops.szs.export()
        return {'FINISHED'}

class KMPUtilities(bpy.types.Panel):
    global latest_version, prerelease_version, current_version
    bl_label = "Main Utilities"
    bl_idname = "MKW_PT_Kmp"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    
    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='BLENDER')

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
        merge = layout.column()
        merge.operator("mkw.objectmerge")
        if(bpy.context.object != None):
            current_mode = bpy.context.object.mode
        else:
            current_mode = 'OBJECT'
        merge.enabled = True
        if(current_mode != 'OBJECT'):
            merge.enabled = False
            
        #layout.operator("kmpe.load")
        if(current_mode == 'VERTEX_PAINT'):
            layout.operator("kmpt.getcolour")
        layout.operator("szs.export", icon="MOD_BUILD")
class KCLSettings(bpy.types.Panel):
    bl_label = "KCL Settings"
    bl_idname = "MKW_PT_KclSet"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='PREFERENCES')
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        layout.prop(mytool, "kcl_applyMaterial")
        layout.prop(mytool, "kcl_applyName")
        layout.prop(mytool, "kcl_autoSeparate")


class KCLUtilities(bpy.types.Panel):
    global finalFlag, kcl_typeATypes, wszstInstalled
    bl_label = "KCL Utilities"
    bl_idname = "MKW_PT_Kcl"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"

    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='FACESEL')
    def draw(self, context):
        
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt   
        text="Please download Wiimms SZS Tools (WSZST) to Import/Export KCL."
        variantPropName = "kclVariant" + mytool.kcl_masterType
        box = layout.box()
        column = box.column()
        column.prop(mytool,"kcl_showFlag",
            icon="TRIA_DOWN" if mytool.kcl_showFlag else "TRIA_RIGHT", emboss=False
        )
        if(mytool.kcl_showFlag):
            activeObject = context.active_object
            if not (activeObject in context.selected_objects):
                column.label(text="No object selected")
            else:
                name = activeObject.name
                if(checkFlagInName001(name,full=False,hex=True)):
                    if(name[-3:].isnumeric() and name[-4] == "."):
                        name = name[:-4]
                    if not checkHEX23(name):
                        _kclType,_variant,_shadow,_trickable,_drivable,_softWall,_depth = decodeFlag(name[-4:])
                        column.label(text="Flag: 0x{0}".format(name[-4:]))
                        column.label(text="Type: {0}".format(mytool.bl_rna.properties['kcl_masterType'].enum_items[_kclType].name))
                        variantName = "kclVariant" + _kclType
                        variant = 0
                        try:
                            variant = mytool.bl_rna.properties[variantName].enum_items[_variant].name
                        except KeyError:
                            pass
                        if(variant != 0):
                            column.label(text="Variant: {0}".format(variant))
                        if(_kclType in kcl_typeATypes):
                            column.label(text="Shadow: {0}, Wheel Depth: {1}".format(_shadow,_depth))
                            column.label(text="Trickable: {0}, Reject: {1}".format("Yes" if _trickable else "No","No" if _drivable else "Yes"))
                        elif(_kclType in kcl_wallTypes):
                            column.label(text="Shadow: {0}, Soft Wall: {1}".format(_shadow,_softWall))
                        elif(_kclType == "T10"):
                            column.label(text="KMP Index: {0}".format(_shadow))
                        column.operator("kcl.getback")
                    else:
                       column.label(text="HEX23 not supported yet") 
                else:
                    column.label(text="No KCL flag found.")
                
            
        if(wszstInstalled):
            layout.operator("kcl.load")
        else:
            _label_multiline(
                context=context,
                text=text,
                parent=layout
            )
            layout.operator("open.wszst")
        
        layout.prop(mytool, "kcl_masterType")
        layout.prop(mytool, variantPropName)
        if(mytool.kcl_masterType == "T18"):
            layout.prop(mytool, "kclVariantT18Circuits")
            t18variant = "kclVariantT18" + mytool.kclVariantT18Circuits
            layout.prop(mytool, t18variant)
        
        if(mytool.kcl_masterType in kcl_typeATypes):
            layout.prop(mytool, "kcl_wheelDepth")
            
        if(mytool.kcl_masterType == "T10"):
            layout.prop(mytool, "kclVariant10Index")
        else:
            row1 = layout.row()
            row1.prop(mytool, "kcl_shadow")
            #row1.operator("kcl.addblight")
        if(mytool.kcl_masterType in kcl_typeATypes):
            row1 = layout.row()
            row1.prop(mytool, "kcl_trickable")
            #row1.operator("kcl.updatetrickable")
            row2 = layout.row()
            row2.prop(mytool, "kcl_drivable")
            #row2.operator("kcl.updatereject")
        if(mytool.kcl_masterType == "T19"):
            text='This flag is mainly used with "Soft Walls"'
            _label_multiline(
                context=context,
                text=text,
                parent=layout
            )
        if(mytool.kcl_masterType in kcl_wallTypes):
            layout.prop(mytool, "kcl_bounce") 
            
        layout.operator("kcl.addblight")
        layout.operator("kcl.applyflag")
        
        if(wszstInstalled):
            layout.operator("kcl.export")
        
class AREAUtilities(bpy.types.Panel):
    bl_label = "AREA Utilities"
    bl_idname = "MKW_PT_KmpArea"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='CUBE')
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
        active = None
        if(context.selected_objects):
            if(context.active_object):
                if(context.active_object.is_area):
                    active = context.active_object

        
        if(active):
            layout.label(text="AREA Settings")
            ac_area_type = active.area_type

        area_settings = layout.column()
        
        if(active):
            area_settings.prop(active,"area_type")
            area_settings.prop(active,"area_pror")
            if(ac_area_type == 'A0'):
                area_settings.prop(active,"area_id")
            elif(ac_area_type == 'A1'):
                area_settings.prop(active,"area_kareha")
            elif(ac_area_type == 'A2'):
                area_settings.prop(active,"area_bfg")
            elif(ac_area_type == 'A3'):
                area_settings.prop(active,"area_route")
                area_settings.label(text="Variant 0x0002 Settings ")
                area_settings.prop(active,"area_acc")
                area_settings.prop(active,"area_spd")
            elif(ac_area_type == 'A4'):
                area_settings.prop(active,"area_enpt")
            elif(ac_area_type == 'A6'):
                area_settings.prop(active,"area_bblm")
                area_settings.prop(active,"area_bblm_trans")
            elif(ac_area_type in ['A8','A9']):
                area_settings.prop(active,"area_group")
            elif(ac_area_type == 'A10'):
                area_settings.prop(active,"area_coob_enabled")
                if(active.area_coob_enabled):
                    area_settings.prop(active,"area_coob_version")
                    if(active.area_coob_version == 'Riidefi'):
                        area_settings.prop(active,"area_coob_rii_p1")
                        area_settings.prop(active,"area_coob_rii_p2")
                        area_settings.prop(active,"area_coob_rii_invert")
                    else:
                        area_settings.prop(active,"area_coob_kevin_mode")
                        area_settings.prop(active,"area_coob_kevin_checkpoint")
        
        if(bpy.context.object != None):
            current_mode = bpy.context.object.mode
        else:
            current_mode = 'OBJECT'
        
        if(current_mode != 'OBJECT'):
            area_create_column.enabled = False
        else:
            area_create_column.enabled = True
        
class CAMEUtilities(bpy.types.Panel):
    bl_label = "Opening Camera Utilities"
    bl_idname = "MKW_PT_KmpCame"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='VIEW_CAMERA')
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        active = context.active_object
        if(scene.frame_start != 0 or scene.render.fps != 60):
            layout.operator("came.setup")
        came_create_column = layout.column()
        came_create_column.operator("came.create")
        layout.operator("kmpt.came")
        active = None

        if(len(context.selected_objects)>0):
            if(context.active_object):
                if(context.active_object.is_came):
                    active = context.active_object
                elif(context.active_object.is_view_point):
                    active = context.active_object.link_to_came
        if(active):
            box = layout.box()
            box.prop(mytool,"kmp_cameOffset")
            box.prop(active,"is_main_came")
            box.prop_search(active,"came_next",scene,"objects")
            box.prop(active,"came_route")
            box.prop(active,"came_frames")

        layout.prop(mytool, "kmp_cameGoToNext")
        layout.prop(mytool, "kmp_cameStop")

        if(bpy.context.object != None):
            current_mode = bpy.context.object.mode
        else:
            current_mode = 'OBJECT'
        came_create_column.enabled = True
        if(current_mode != 'OBJECT'):
            came_create_column.enabled = False
            

class RouteUtilities(bpy.types.Panel):
    bl_label = "Route Utilities"
    bl_idname = "MKW_PT_Route"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='CURVE_DATA')
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
        
    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='MATERIAL')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        layout.prop(mytool, "util_addVCs")
        layout.operator("mkw.matdel")
        layout.operator("kmpt.vercolor")
        layout.operator("kmpt.blend")
        layout.operator("kmpt.hashed")
        layout.operator("kmpt.clip")
        layout.operator("kmpt.metalic")
        layout.operator("kmpt.specular")


class ShaderUtilities(bpy.types.Panel):
    bl_label = "Shader Utilities"
    bl_idname = "MKW_PT_Shader"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "MKW Utils"

    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='MATERIAL')
    def draw(self,context):
        layout = self.layout
        layout.operator("kmpt.vercolor")
        layout.operator("kmpt.blend")
        layout.operator("kmpt.hashed")
        layout.operator("kmpt.clip")
        layout.operator("kmpt.metalic")
        layout.operator("kmpt.specular")

class ShaderGroupUtilities(bpy.types.Panel):
    bl_label = "Shader Node Groups Utilities"
    bl_idname = "MKW_PT_ShaderGroup"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='NODETREE')
    def draw(self,context):
        layout = self.layout
        layout.operator("mat.addmirror")
        layout.operator("mat.addmirroru")
        layout.operator("mat.addmirrorv")

class get_vertex_color(bpy.types.Operator):
    bl_idname = "kmpt.getcolour"
    bl_label = "Get Vertex Color"
    bl_description = "Gets color of currently selected vertex"
    def execute(self, context):
        selectedOBJ = bpy.context.selected_objects[0]
        i=0
        selected = None
        for vert in selectedOBJ.data.vertices:
            if vert.select:
                selected = i
                break
            i+=1
        colours = getSelVertColour(selected)
        bpy.data.brushes["Draw"].color[0] = colours[0][0]
        bpy.data.brushes["Draw"].color[1] = colours[0][1]
        bpy.data.brushes["Draw"].color[2] = colours[0][2]
        return {'FINISHED'}

def getSelVertColour(vertex_index: int):

    mode_initial = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    mesh = bpy.context.edit_object.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.verts.ensure_lookup_table() # Required before vertex lookup
    vc_layer = bm.loops.layers.color.active
    
    colours = []
    if vc_layer is None:
        colours.append(Vector.Fill(4))
    else:
        
        for loop in bm.verts[vertex_index].link_loops:
            colours.append(loop[vc_layer])
    
    bpy.ops.object.mode_set(mode=mode_initial)
    return colours

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
                                if not shader.inputs['Alpha'].links:
                                    mat.node_tree.links.new(shader.inputs['Alpha'], node.outputs['Alpha'])
        return {'FINISHED'}


class set_alpha_hashed(bpy.types.Operator):
    bl_idname = "kmpt.hashed"
    bl_label = "Add Alpha Hashed"
    bl_description = "Add Alpha Node from Image Texture and set Alpha mode to Hashed"
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
                                if not shader.inputs['Alpha'].links:
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
                                if not shader.inputs['Alpha'].links:
                                    mat.node_tree.links.new(shader.inputs['Alpha'], node.outputs['Alpha'])
        return {'FINISHED'}
class remove_specular_metalic(bpy.types.Operator):
    bl_idname = "kmpt.metalic"
    bl_label = "Remove Specular and Metalic"
    bl_description = "Removes unwanted shininess from materials"
    bl_options = {'UNDO'}
    def execute(self, context):
        selected = bpy.context.selected_objects
        for obj in selected:
            if obj.type == 'MESH' and not obj.active_material == None:
                for item in obj.material_slots:
                    mat = bpy.data.materials[item.name]
                    if mat.use_nodes:
                        if(BLENDER_30):
                            mat.node_tree.nodes['Principled BSDF'].inputs[7].default_value = 0
                            mat.node_tree.nodes['Principled BSDF'].inputs[6].default_value = 0
                        else:                    
                            mat.node_tree.nodes['Principled BSDF'].inputs[4].default_value = 0
                            mat.node_tree.nodes['Principled BSDF'].inputs[5].default_value = 0
    

        return {'FINISHED'}

class restore_specular_metalic(bpy.types.Operator):
    bl_idname = "kmpt.specular"
    bl_label = "Restore Specular"
    bl_description = "Restores shininess from materials"
    bl_options = {'UNDO'}
    def execute(self, context):
        selected = bpy.context.selected_objects
        for obj in selected:
            if obj.type == 'MESH' and not obj.active_material == None:
                for item in obj.material_slots:
                    mat = bpy.data.materials[item.name]
                    if mat.use_nodes:
                        if(BLENDER_30):
                            mat.node_tree.nodes['Principled BSDF'].inputs[7].default_value = 0.5
                        else:                    
                            mat.node_tree.nodes['Principled BSDF'].inputs[5].default_value = 0.5
    

        return {'FINISHED'}

class add_vertex_col(bpy.types.Operator):
    bl_idname = "kmpt.vercolor"
    bl_label = "Add Vertex Colors Nodes"
    bl_description = "Adds vertex colors nodes on material and selected objects (if not already found)"
    bl_options = {'UNDO'}
    def execute(self, context):
        selected = bpy.context.selected_objects
        for obj in selected:
            if obj.type == 'MESH' and not obj.active_material == None:
                if(BLENDER_33):
                    if not obj.data.color_attributes:
                        obj.data.color_attributes.new(name="Vertex Colors",type='BYTE_COLOR',domain='CORNER')
                else:
                    if not obj.data.vertex_colors:
                        obj.data.vertex_colors.new(name="Vertex Colors")

                for item in obj.material_slots:
                    mat = bpy.data.materials[item.name]
                    if mat.use_nodes:
                        shader = mat.node_tree.nodes['Principled BSDF']
                        txtNode = None
                        principled = None
                        for node in mat.node_tree.nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                principled = node
                                for n_inputs in node.inputs:
                                    for node_links in n_inputs.links:
                                        txtNode = node_links.from_node
                        if(hasattr(txtNode, "type")):
                            if(txtNode.type == 'TEX_IMAGE'):
                                txtNode.location = (-500,300)
                                vertexNode = mat.node_tree.nodes.new("ShaderNodeVertexColor")
                                vertexNode.location = (-410,-140)
                                mixRGBNode = mat.node_tree.nodes.new("ShaderNodeMixRGB")
                                mixRGBNode.location = (-180,100)
                                mixRGBNode.blend_type = 'MULTIPLY'
                                mixRGBNode.inputs[0].default_value = 1
                                alphaMathNode = mat.node_tree.nodes.new("ShaderNodeMath")
                                alphaMathNode.location = (-170,-180)
                                alphaMathNode.operation = 'MULTIPLY'
                                links = mat.node_tree.links
                                links.new(mixRGBNode.inputs['Color1'], txtNode.outputs['Color'])
                                links.new(mixRGBNode.inputs['Color2'], vertexNode.outputs['Color'])
                                links.new(principled.inputs['Base Color'], mixRGBNode.outputs['Color'])

                                links.new(alphaMathNode.inputs[0], txtNode.outputs['Alpha'])
                                links.new(alphaMathNode.inputs[1], vertexNode.outputs['Alpha'])
                                links.new(principled.inputs['Alpha'], alphaMathNode.outputs['Value'])


                            else:
                                self.report({"WARNING"}, "Couldn't find a Image Texture connected to Principled BSDF: {0}".format(mat.name))
                        else:
                            self.report({"WARNING"}, "Couldn't find any Image Texture node: {0}".format(mat.name))
                                        
        return {'FINISHED'}
                                

class add_mirrorUV(bpy.types.Operator):
    bl_idname = "mat.addmirror"
    bl_label = "Add Mirror UV Node"
    bl_options = {'UNDO'}
    def execute(self, context): 
        my_group = create_mirror_group()
        test_node = bpy.context.active_object.active_material.node_tree.nodes.new('ShaderNodeGroup')
        test_node.node_tree = bpy.data.node_groups[my_group.name]
        test_node.location = (-500,0)
        return {'FINISHED'}

class add_mirrorU(bpy.types.Operator):
    bl_idname = "mat.addmirroru"
    bl_label = "Add Mirror U Node"
    bl_options = {'UNDO'}
    def execute(self, context): 
        my_group = create_mirror_group(key="u",name="Mirror U")
        test_node = bpy.context.active_object.active_material.node_tree.nodes.new('ShaderNodeGroup')
        test_node.node_tree = bpy.data.node_groups[my_group.name]
        test_node.location = (-500,0)
        return {'FINISHED'}

class add_mirrorV(bpy.types.Operator):
    bl_idname = "mat.addmirrorv"
    bl_label = "Add Mirror V Node"
    bl_options = {'UNDO'}
    def execute(self, context): 
        my_group = create_mirror_group(key="v",name="Mirror V")
        test_node = bpy.context.active_object.active_material.node_tree.nodes.new('ShaderNodeGroup')
        test_node.node_tree = bpy.data.node_groups[my_group.name]
        test_node.location = (-500,0)
        return {'FINISHED'}


def create_mirror_group(key="uv",name='Mirror UV'):
    if(name in bpy.data.node_groups):
        return bpy.data.node_groups[name]

    mirror_group = bpy.data.node_groups.new(name, 'ShaderNodeTree')
    mirror_group.name = name
    group_outputs = mirror_group.nodes.new('NodeGroupOutput')
    mirror_group.outputs.new('NodeSocketVector','Vector')
    group_outputs.location = (300,0)

    uvMap = mirror_group.nodes.new("ShaderNodeUVMap")
    uvMap.location = (-500,0)

    seperateNode = mirror_group.nodes.new("ShaderNodeSeparateXYZ")
    seperateNode.location = (-300,0)

    combineNode = mirror_group.nodes.new("ShaderNodeCombineXYZ")
    combineNode.location = (200,0)

    flipX = mirror_group.nodes.new("ShaderNodeMath")
    flipX.location = (-150,100)
    flipX.inputs[1].default_value = 1
    flipX.operation = 'PINGPONG'

    flipY = mirror_group.nodes.new("ShaderNodeMath")
    flipY.location = (-150,-100)
    flipY.inputs[1].default_value = 1
    flipY.operation = 'PINGPONG'

    links = mirror_group.links
    links.new(seperateNode.inputs['Vector'], uvMap.outputs['UV'])
    links.new(flipX.inputs['Value'],seperateNode.outputs['X'])
    links.new(flipY.inputs['Value'],seperateNode.outputs['Y'])

    links.new(combineNode.inputs['Z'],seperateNode.outputs['Z'])
    if("u" in key):
        links.new(combineNode.inputs['X'],flipX.outputs['Value'])
    else:
        links.new(combineNode.inputs['X'],seperateNode.outputs['X'])
    if("v" in key):
        links.new(combineNode.inputs['Y'],flipY.outputs['Value'])
    else:
        links.new(combineNode.inputs['Y'],seperateNode.outputs['Y'])

    links.new(group_outputs.inputs['Vector'],combineNode.outputs['Vector'])

    return mirror_group

        
class ShaderTEVGroup(bpy.types.ShaderNodeCustomGroup):
    bl_name = 'ShaderTEVGroup'
    bl_label = 'Wii TEV Stage'

    def _updateVal(self, context):
        bias = float(self.BiasEnum)
        scale = float(self.Scale)
        op = int(self.Operation)
        if(BLENDER_34):
            if bias < 0:
                self.node_tree.nodes['Mix.006'].blend_type = 'SUBTRACT'
                bias = bias * -1
            else:
                self.node_tree.nodes['Mix.006'].blend_type = 'ADD'
            self.node_tree.nodes['Mix.006'].inputs[7].default_value = (bias,bias,bias,1)
            self.node_tree.nodes['Mix.007'].inputs[7].default_value = (scale,scale,scale,1)

            self.node_tree.nodes['Mix.004'].inputs[0].default_value = (op - 1) * -1
            self.node_tree.nodes['Mix.005'].inputs[0].default_value = op
        else:
            if bias < 0:
                self.node_tree.nodes['Bias'].blend_type = 'SUBTRACT'
                bias = bias * -1
            else:
                self.node_tree.nodes['Bias'].blend_type = 'ADD'
            self.node_tree.nodes['Bias'].inputs[2].default_value = (bias,bias,bias,1)
            self.node_tree.nodes['Scale'].inputs[2].default_value = (scale,scale,scale,1)

            self.node_tree.nodes['DMinus'].inputs[0].default_value = (op - 1) * -1
            self.node_tree.nodes['DPlus'].inputs[0].default_value = op
        

    BiasEnum : bpy.props.EnumProperty(name="Bias", items={('-0.5','-0.5',''),('0.0','0.0',''),('+0.5','+0.5','')}, default='0.0', update=_updateVal)
    Operation : bpy.props.EnumProperty(name="Operation", items={('1','Add',''),('0','Subtract',''),}, default='1', update=_updateVal)
    Scale : bpy.props.EnumProperty(name="Scale", items={('0.5','0.5',''),('1','1',''),('2','2',''),('4','4','')}, default='1', update=_updateVal)

    def init(self, context):
        self.node_tree=bpy.data.node_groups.new("." + self.bl_name, 'ShaderNodeTree')
        group_inputs = self.node_tree.nodes.new('NodeGroupInput')
        group_output = self.node_tree.nodes.new('NodeGroupOutput')
        group_inputs.location = (-700,0)
        self.node_tree.inputs.new('NodeSocketColor','A')
        self.node_tree.inputs.new('NodeSocketColor','B')
        self.node_tree.inputs.new('NodeSocketColor','C')
        self.node_tree.inputs.new('NodeSocketColor','D')
        group_output.location = (1000,0)
        self.node_tree.outputs.new('NodeSocketColor',"Color")
        if(BLENDER_34):
            oneMinusNode = self.node_tree.nodes.new("ShaderNodeMix")
            oneMinusNode.location = (-500,200)
            oneMinusNode.data_type = 'RGBA'
            oneMinusNode.blend_type = 'SUBTRACT'
            oneMinusNode.inputs[0].default_value = 1
            oneMinusNode.inputs[6].default_value = [1,1,1,1]
            oneMinusNode.label = "1-C"

            
            CtimesB = self.node_tree.nodes.new("ShaderNodeMix")
            CtimesB.location = (-500,-100)
            CtimesB.data_type = 'RGBA'
            CtimesB.blend_type = 'MULTIPLY'
            CtimesB.inputs[0].default_value = 1
            CtimesB.label = "C*B"

            timesA = self.node_tree.nodes.new("ShaderNodeMix")
            timesA.location = (-300,200)
            timesA.data_type = 'RGBA'
            timesA.blend_type = 'MULTIPLY'
            timesA.inputs[0].default_value = 1
            timesA.label = "(1-C)*A"

            addCB = self.node_tree.nodes.new("ShaderNodeMix")
            addCB.location = (-100,0)
            addCB.data_type = 'RGBA'
            addCB.blend_type = 'ADD'
            addCB.inputs[0].default_value = 1

            Dminus = self.node_tree.nodes.new("ShaderNodeMix")
            Dminus.location = (100,50)
            Dminus.data_type = 'RGBA'
            Dminus.blend_type = 'SUBTRACT'
            Dminus.inputs[0].default_value = 0

            Dplus = self.node_tree.nodes.new("ShaderNodeMix")
            Dplus.location = (300,50)
            Dplus.data_type = 'RGBA'
            Dplus.blend_type = 'ADD'
            Dplus.inputs[0].default_value = 1
            
            biasNode = self.node_tree.nodes.new("ShaderNodeMix")
            biasNode.location = (500,0)
            biasNode.data_type = 'RGBA'
            biasNode.blend_type = 'ADD'
            biasNode.inputs[0].default_value = 1
            biasNode.inputs[7].default_value = [0,0,0,1]

            scaleNode = self.node_tree.nodes.new("ShaderNodeMix")
            scaleNode.location = (700,0)
            scaleNode.data_type = 'RGBA'
            scaleNode.blend_type = 'MULTIPLY'
            scaleNode.inputs[0].default_value = 1
            scaleNode.inputs[7].default_value = [1,1,1,1]

            link = self.node_tree.links.new
            link(oneMinusNode.inputs[7], group_inputs.outputs['C'])
            link(CtimesB.inputs[7], group_inputs.outputs['C'])
            link(CtimesB.inputs[6], group_inputs.outputs['B'])
            link(timesA.inputs[7], oneMinusNode.outputs[2])
            link(timesA.inputs[6], group_inputs.outputs['A'])
            link(addCB.inputs[7],CtimesB.outputs[2])
            link(addCB.inputs[6],timesA.outputs[2])

            link(Dminus.inputs[7],group_inputs.outputs['D'])
            link(Dplus.inputs[7],group_inputs.outputs['D'])

            link(Dminus.inputs[6],addCB.outputs[2])
            link(Dplus.inputs[6],Dminus.outputs[2])

            link(biasNode.inputs[6],Dplus.outputs[2])
            link(scaleNode.inputs[6],biasNode.outputs[2])
            link(group_output.inputs[0],scaleNode.outputs[2])
        else:
            oneMinusNode = self.node_tree.nodes.new("ShaderNodeMixRGB")
            oneMinusNode.location = (-500,200)
            oneMinusNode.blend_type = 'SUBTRACT'
            oneMinusNode.inputs[0].default_value = 1
            oneMinusNode.inputs[1].default_value = [1,1,1,1]
            oneMinusNode.label = "1-C"

            
            CtimesB = self.node_tree.nodes.new("ShaderNodeMixRGB")
            CtimesB.location = (-500,-100)
            CtimesB.blend_type = 'MULTIPLY'
            CtimesB.inputs[0].default_value = 1
            CtimesB.label = "C*B"

            timesA = self.node_tree.nodes.new("ShaderNodeMixRGB")
            timesA.location = (-300,200)
            timesA.blend_type = 'MULTIPLY'
            timesA.inputs[0].default_value = 1
            timesA.label = "(1-C)*A"

            addCB = self.node_tree.nodes.new("ShaderNodeMixRGB")
            addCB.location = (-100,0)
            addCB.blend_type = 'ADD'
            addCB.inputs[0].default_value = 1

            Dminus = self.node_tree.nodes.new("ShaderNodeMixRGB")
            Dminus.location = (100,50)
            Dminus.blend_type = 'SUBTRACT'
            Dminus.inputs[0].default_value = 0
            Dminus.label = "DMinus"
            Dminus.name = "DMinus"

            Dplus = self.node_tree.nodes.new("ShaderNodeMixRGB")
            Dplus.location = (300,50)
            Dplus.blend_type = 'ADD'
            Dplus.inputs[0].default_value = 1
            Dplus.label = "DPlus"
            Dplus.name = "DPlus"
            
            biasNode = self.node_tree.nodes.new("ShaderNodeMixRGB")
            biasNode.location = (500,0)
            biasNode.blend_type = 'ADD'
            biasNode.inputs[0].default_value = 1
            biasNode.inputs[2].default_value = [0,0,0,1]
            biasNode.label = "Bias"
            biasNode.name = "Bias"

            scaleNode = self.node_tree.nodes.new("ShaderNodeMixRGB")
            scaleNode.location = (700,0)
            scaleNode.blend_type = 'MULTIPLY'
            scaleNode.inputs[0].default_value = 1
            scaleNode.inputs[2].default_value = [1,1,1,1]
            scaleNode.label = "Scale"
            scaleNode.name = "Scale"

            

            link = self.node_tree.links.new
            link(oneMinusNode.inputs[2], group_inputs.outputs['C'])
            link(CtimesB.inputs[2], group_inputs.outputs['C'])
            link(CtimesB.inputs[1], group_inputs.outputs['B'])
            link(timesA.inputs[2], oneMinusNode.outputs[0])
            link(timesA.inputs[1], group_inputs.outputs['A'])
            link(addCB.inputs[2],CtimesB.outputs[0])
            link(addCB.inputs[1],timesA.outputs[0])

            link(Dminus.inputs[2],group_inputs.outputs['D'])
            link(Dplus.inputs[2],group_inputs.outputs['D'])

            link(Dminus.inputs[1],addCB.outputs[0])
            link(Dplus.inputs[1],Dminus.outputs[0])

            link(biasNode.inputs[1],Dplus.outputs[0])
            link(scaleNode.inputs[1],biasNode.outputs[0])
            link(group_output.inputs[0],scaleNode.outputs[0])



    def draw_buttons(self, context, layout):
        column=layout.column()
        column.prop(self, 'Operation', text='Operation')
        column.prop(self, 'BiasEnum', text='Bias')
        column.prop(self, 'Scale', text='Scale')
        
    def copy(self, node):
        self.node_tree=node.node_tree.copy()

    def free(self):
        bpy.data.node_groups.remove(self.node_tree, do_unlink=True)


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
        decimal = locale.localeconv()["decimal_point"]
        objectsToExport = []
        for object in selected:
            if object.is_view_point:
                object = object.link_to_came
            if(object.is_main_came):
                if object.is_came:
                    if object in objectsToExport:
                        continue
                    objectsToExport.insert(0,object)
                    obj = object.came_next
                    while obj != None:
                        if obj.is_view_point:
                            obj = obj.link_to_came
                        if obj in objectsToExport:
                            break
                        objectsToExport.append(obj)
                        obj = obj.came_next

                    break
        for object in selected:
            if object.is_view_point:
                object = object.link_to_came  
            if object in objectsToExport:
                continue 
            if object.is_came:
                objectsToExport.append(object)
                obj = object.came_next
                while obj != None:
                    if obj.is_view_point:
                        obj = obj.link_to_came
                    if obj in objectsToExport:
                        break
                    objectsToExport.append(obj)
                    obj = obj.came_next
                    
            
        id = 0
        j = 0
        skippedCames = 0
        for object in objectsToExport:
            fovs = []
            vpposs = []
            fovkeyframes = []
            vpkeyframes = []

            cameraName = object.data.name
            fov = bpy.data.cameras[cameraName].angle
            fov = fov * 180 / 3.1415
            fov = round(fov * 9.0 / 16.0, 0)            
            if hasattr(object.data, "animation_data"):
                if hasattr(object.data.animation_data, "action"):
                    if(hasattr(object.data.animation_data.action, "fcurves")):
                        fovcurves = object.data.animation_data.action.fcurves
                        for curve in fovcurves:        
                            if("lens" in curve.data_path):
                                keyframePoints = curve.keyframe_points
                                for keyframe in keyframePoints:
                                    f = keyframe.co[0]
                                    scene.frame_set(int(f))
                                    fovkeyframes.append(int(f))
                                    cameraName = object.data.name
                                    fov = bpy.data.cameras[cameraName].angle
                                    fov = fov * 180 / 3.1415
                                    fov = round(fov * 9 / 16, 0)
                                    fovs.append(fov)
                        if(fovkeyframes[0] > 1):
                            self.report({"WARNING"}, r'Camera "{0}": First FOV keyframe needs to be at frame 0'.format(object.name))
                            return {'CANCELLED'}
                        if(len(fovkeyframes) > 2):
                            self.report({"WARNING"}, r'Camera "{0}": You can not have more than 2 FOV keyframes'.format(object.name))
                            return {'CANCELLED'}
                    else:
                        fovs.append(fov)
                        fovs.append(fov)
                        fovkeyframes.append(0)
                        fovkeyframes.append(0)
                else:
                    fovs.append(fov)
                    fovs.append(fov)
                    fovkeyframes.append(0)
                    fovkeyframes.append(0)
            else:
                fovs.append(fov)
                fovs.append(fov)
                fovkeyframes.append(0)
                fovkeyframes.append(0)
            viewpoint = object.link_to_vp
            loc = viewpoint.location
            position = [loc[0] * scale,loc[1] * scale,loc[2] * scale]
            if(hasattr(viewpoint, "animation_data")):
                if(hasattr(viewpoint.animation_data, "action")):
                    if(hasattr(viewpoint.animation_data.action, "fcurves")):
                        vpcurves = viewpoint.animation_data.action.fcurves
                        for curve in vpcurves:
                            keyframePoints = curve.keyframe_points
                            for keyframe in keyframePoints:
                                if(keyframe.co[0] not in vpkeyframes):  
                                    f = keyframe.co[0]
                                    vpkeyframes.append(int(f))
                                    scene.frame_set(int(f))
                                    loc = viewpoint.location
                                    position = [loc[0] * scale,loc[1] * scale,loc[2] * scale]
                                    vpposs.append(position)
                        if(vpkeyframes[0] > 1):
                            self.report({"WARNING"}, r'Camera "{0}": First View Point keyframe needs to be at frame 0'.format(object.name))
                            return {'CANCELLED'}
                        if(len(vpkeyframes) > 2):
                            self.report({"WARNING"}, r'Camera "{0}": You can not have more than 2 View Point keyframes'.format(object.name))
                            return {'CANCELLED'}
                    else:
                        vpposs.append(position)
                        vpposs.append(position)
                        vpkeyframes.append(0)
                        vpkeyframes.append(0)
                else:
                    vpposs.append(position)
                    vpposs.append(position)
                    vpkeyframes.append(0)
                    vpkeyframes.append(0)
            else:
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
            xpos = round(object.location[0] * scale, 3)
            ypos = round(object.location[2] * scale, 3)
            zpos = round(object.location[1] * scale * -1, 3)
            vsxpos = round(vpposs[0][0], 0)
            vsypos = round(vpposs[0][2], 0)
            vszpos = round(vpposs[0][1] * -1, 0)
            vexpos = round(vpposs[1][0], 0)
            veypos = round(vpposs[1][2], 0)
            vezpos = round(vpposs[1][1] * -1, 0)
            frames = object.came_frames
            nextCameId = 'FF'
            if(object.came_next != None):
                nextCameId = objectsToExport.index(object.came_next) + mytool.kmp_cameOffset
            id = id + 1            
            nextRouteID = object.came_route


            dataValues = [
                str(j).zfill(2),
                "05",
                str(nextCameId).zfill(2),
                "00",
                str(nextRouteID).zfill(2),
                "0000",
                str(fovSpeed).zfill(4),
                str(vpSpeed).zfill(4),
                "00",
                "00",
                str(xpos),
                str(ypos),
                str(zpos),
                "0",
                "0",
                "0",
                str(int(fovs[0])),
                str(int(fovs[1])),
                str(vsxpos),
                str(vsypos),
                str(vszpos),
                str(vexpos),
                str(veypos),
                str(vezpos),
                str(frames)
            ]
            dataValue = ("\t").join(dataValues)+"\n"
            data += dataValue
            j=j+1
            
        if(decimal != "."):
            data.replace(".",decimal)
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
        decimal = locale.localeconv()["decimal_point"]
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
                    keyframes.append(int(f))
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
            if(i != a-1):
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
        if(decimal != "."):
            data.replace(".",decimal)
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
        decimal = locale.localeconv()["decimal_point"]
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
            scene.frame_set(int(f))
            keyframes.append(int(f))
            loc = activeObject.location
            position = [math.floor(loc[0] * scale),math.floor(loc[1] * scale),math.floor(loc[2] * scale)]
            locations.append(position)
        speed = []
        vectors = []
        a = len(keyframes)
        for i in range(a):
            vectors.append(Vector(locations[i]))
        for i in range(a):
            if(i != a-1):
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
        if(decimal != "."):
            data.replace(".",decimal)
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
        bpy.ops.object.select_all(action='DESELECT')

        bpy.ops.mesh.primitive_uv_sphere_add(radius=scale/63.5,location=cursor_position)
        bpy.ops.object.mode_set(mode='OBJECT')
        vpName="New View Point"
        vp = bpy.context.object
        vp.name = vpName
        vp.is_view_point = True


        bpy.ops.object.camera_add(align='VIEW', location=camePosition)
        
        bpy.ops.transform.resize(value=(scale/10,scale/10,scale/10))
        bpy.ops.object.constraint_add(type='TRACK_TO')
        bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'
        bpy.context.object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
        bpy.context.object.constraints["Track To"].target = vp
        cameName="New Opening Camera"
        came = bpy.context.object
        scene.camera = bpy.context.object
        came.name = cameName
        came.is_came = True
        objs = [ob for ob in bpy.context.scene.objects if ob.is_came]
        if(len(objs)==1):
            came.is_main_came = True
        came.link_to_vp = vp
        vp.link_to_came = came
        cames = [ob for ob in bpy.context.scene.objects if ob.is_came]

        create_collection(came,vp,name="[New Camera {0}]".format(len(cames)),parent="[CAME]")
        

          
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

class remove_duplicate_materials(bpy.types.Operator):
    bl_idname = "mkw.matdel"
    bl_label = "Remove duplicate materials"
    bl_description = "Removes duplicated materials"
    bl_options = {'UNDO'}
    def execute(self, context):
        remove_all_duplicate_materials()
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
        if material != og_material:
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
    


finalFlag = ''
properFlag = ''
class apply_kcl_flag(bpy.types.Operator):
    global kcl_typeATypes, finalFlag, kcl_wallTypes, properFlag
    bl_idname = "kcl.applyflag"
    bl_label = "Apply Flag"
    bl_options = {'UNDO'}
    bl_description = "Apply current flag"
    
    @classmethod
    def poll(cls,context):
        b = True
        if not context.selected_objects:
            b = False
        return b
    
    def execute(self, context):
        selection = []
        oldSelection = []
        separated = []
        lastActive = 0
        if not bpy.context.object:
            self.report({'WARNING'},"Check failed. No object found")
            return {'CANCELLED'}

        current_mode = bpy.context.object.mode
        wasInEditMode = False
        scene = context.scene
        mytool = scene.kmpt
        if(current_mode == 'EDIT' and mytool.kcl_autoSeparate):
            wasInEditMode = True
            oldSelection = context.selected_objects
            lastActive = context.active_object
            if(lastActive not in oldSelection):
                oldSelection.append(lastActive)
            try:
                bpy.ops.mesh.separate(type='SELECTED')
            except RuntimeError:
                self.report({'WARNING'},"Nothing selected")
                return {'CANCELLED'}
            bpy.ops.object.mode_set(mode='OBJECT')
            selection = context.selected_objects
            if(lastActive not in selection):
                selection.append(lastActive)
            lastActive.select_set(False)
            separated = [i for i in selection if i not in oldSelection]
            bpy.context.view_layer.objects.active = context.selected_objects[0]
            selection.append(context.selected_objects[0])


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
        y = mytool.kcl_shadow
        y = '{:03b}'.format(int(y))
        if(mytool.kcl_masterType in kcl_typeATypes):
            w = "0" + str(int(mytool.kcl_drivable)) + str(int(mytool.kcl_trickable))
            x = '{:02b}'.format(int(mytool.kcl_wheelDepth))
            typeaflag = w+x+y
        if(mytool.kcl_masterType == "T1A"):
            typeaflag = y

        a = '{:01b}'.format(int(mytool.kcl_masterType[1],16))
        b = '{:04b}'.format(int(mytool.kcl_masterType[2],16))
        flag = typeaflag+z+a+b

        if(mytool.kcl_masterType == 'T10'):
            flag = '{:08b}'.format(mytool.kclVariant10Index)+z+a+b
        if(mytool.kcl_masterType == 'T12'):
            flag = '{:08b}'.format(18)
        if(mytool.kcl_masterType in kcl_wallTypes):
            w = int(mytool.kcl_bounce == True)
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
        if(wasInEditMode):
            for i in separated:
                i.name = properFlag
                i.data.name = properFlag
        else:
            if(activeObject in context.selected_objects):
                activeObject.name = properFlag
                activeObject.data.name = properFlag
        decodeFlag(properFlag[-4:])
        if(wasInEditMode):
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            for i in selection:
                bpy.ops.object.select_all(action='DESELECT')
                try:
                    verts = [vert.co for vert in i.data.vertices]
                    if not verts:
                        i.select_set(True)
                        selection.remove(i)
                        bpy.ops.object.delete()
                        bpy.ops.object.select_all(action='DESELECT')
                except ReferenceError:
                    pass
            for obj in selection:
                try:
                    obj.select_set(True)
                except ReferenceError:
                    pass
            if lastActive in selection:
                bpy.context.view_layer.objects.active = lastActive
            else:
                bpy.context.view_layer.objects.active = selection[0]
            bpy.ops.object.mode_set(mode='EDIT')
        if(mytool.kcl_applyMaterial == '1'):
            return {"FINISHED"}

        mat = bpy.data.materials.get(flagOnly)
        if mat is None:
            mat = bpy.data.materials.new(name=flagOnly)
            if(mytool.kcl_applyMaterial == "0"):
                mat.diffuse_color = (random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),1)
            elif(mytool.kcl_applyMaterial == "2"):
                color = getSchemeColor(context,mytool.kcl_masterType,mytool.kcl_trickable,mytool.kcl_drivable==False,mytool.kcl_shadow)
                mat.diffuse_color = (color[0],color[1],color[2],1)
        if(wasInEditMode):
            for i in separated:
                if i:
                    i.data.materials.clear()
                    i.data.materials.append(mat)
        else:
            context.active_object.data.materials.clear()
            context.active_object.data.materials.append(mat)
        return {'FINISHED'}

class get_flag_back(bpy.types.Operator):
    bl_idname = "kcl.getback"
    bl_label = "Get Flag Values"
    bl_options = {'UNDO'}

    def execute(self, context):

        scene = context.scene
        mytool = scene.kmpt
        activeObject = context.active_object
        name = activeObject.name
        if(checkFlagInName001(name,full=False,hex=True)):
            if(name[-3:].isnumeric() and name[-4] == "."):
                name = name[:-4]
            if(checkHEX23(name)):
                return {'FINISHED'}

            _kclType,_variant,_shadow,_trickable,_drivable,_softWall,_depth = decodeFlag(name[-4:])
            mytool.kcl_masterType = _kclType
            variantName = "kclVariant" + _kclType
            if(hasattr(mytool,variantName)):
                setattr(mytool,variantName,_variant)        
            if(_kclType in kcl_typeATypes):
                mytool.kcl_wheelDepth = _depth
                mytool.kcl_trickable = _trickable
                mytool.kcl_drivable = False if _drivable else True
            elif(_kclType in kcl_wallTypes):
                mytool.kcl_bounce = _softWall
            if(_kclType == "T10"):
                mytool.kclVariant10Index = _shadow
            else:
                mytool.kcl_shadow = _shadow    

        return {'FINISHED'}

def updateBit(operator,context,key="ltr"):
    selection = []
    oldSelection = []
    separated = []
    lastActive = 0
    current_mode = bpy.context.object.mode
    active = context.active_object
    newFlag = ""
    wasInEditMode = False
    scene = context.scene
    mytool = scene.kmpt
    if(current_mode == 'EDIT' and mytool.kcl_autoSeparate):
        wasInEditMode = True
        oldSelection = context.selected_objects
        lastActive = context.active_object
        if(lastActive not in oldSelection):
            oldSelection.append(lastActive)
        for i in oldSelection:
            if not checkFlagInName001(i.name):
                if(i.name[-4]=="."):
                    i.name = i.name[:-4]
                operator.report({"WARNING"}, "At least one of selected objects does not have proper flag.")
                return {'CANCELLED'}      

        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')
        selection = context.selected_objects
        if(lastActive not in selection):
            selection.append(lastActive)
        lastActive.select_set(False)
        separated = [i for i in selection if i not in oldSelection]
        bpy.context.view_layer.objects.active = context.selected_objects[0]
        selection.append(context.selected_objects[0])
    elif not checkFlagInName001(active.name):
        return

    if(wasInEditMode):
        for i in separated:
            bits = i.name[-8:-4]
            bits = bin(int(bits, 16))[2:].zfill(16)
            if("l" in key):
                bits = bits[:5] + bin(int(mytool.kcl_shadow))[2:].zfill(3) + bits[8:]
            if("t" in key):
                bits = bits[:2] + bin(int(mytool.kcl_trickable))[2:].zfill(1) + bits[3:]
            if("r" in key):
                bits = bits[:1] + bin(int(mytool.kcl_drivable))[2:].zfill(1) + bits[2:]
            newFlag = hex(int(bits,2))[2:].zfill(4)
            i.name = i.name[:-8] + newFlag.upper()
            i.data.name = i.name
    else:
        i = active
        if(i.name[-4]=="."):
            i.name = i.name[:-4]
        bits = i.name[-4:]
        bits = bin(int(bits, 16))[2:].zfill(16)
        if("l" in key):
            bits = bits[:5] + bin(int(mytool.kcl_shadow))[2:].zfill(3) + bits[8:]
        if("t" in key):
            bits = bits[:2] + bin(int(mytool.kcl_trickable))[2:].zfill(1) + bits[3:]
        if("r" in key):
            bits = bits[:1] + bin(int(mytool.kcl_drivable))[2:].zfill(1) + bits[2:]
        newFlag = hex(int(bits,2))[2:].zfill(4)
        i.name = i.name[:-4] + newFlag.upper()
        i.data.name = i.name


    if(wasInEditMode):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        verts = [vert.co for vert in lastActive.data.vertices]
        if not verts:
            lastActive.select_set(True)
            selection.remove(lastActive)
            bpy.ops.object.delete()
            bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            obj.select_set(True)

        if lastActive in selection:
            bpy.context.view_layer.objects.active = lastActive
        else:
            bpy.context.view_layer.objects.active = selection[0]
        bpy.ops.object.mode_set(mode='EDIT')
    if(mytool.kcl_applyMaterial == "1"):
        return 
    if(wasInEditMode):
        for i in separated:
            if(i.name[-4]=="."):
                i.name = i.name[:-4]
            flagOnly = i.name[-9:]
            mat = bpy.data.materials.get(flagOnly)
            if mat is None:
                mat = bpy.data.materials.new(name=flagOnly)
                if(mytool.kcl_applyMaterial == "0"):
                    mat.diffuse_color = (random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),1)
                elif(mytool.kcl_applyMaterial == "2"):
                    _kclType,_variant,_shadow,_trickable,_drivable,_softWall,_d = decodeFlag(flagOnly[-4:])
                    color = getSchemeColor(context,_kclType,_trickable,_drivable,_shadow)
                    mat.diffuse_color = (color[0],color[1],color[2],1)
            i.data.materials.clear()
            i.data.materials.append(mat)
    else:
        if(i.name[-4]=="."):
            active.name = active.name[:-4]
        flagOnly = active.name[-9:]
        mat = bpy.data.materials.get(flagOnly)
        if mat is None:
            mat = bpy.data.materials.new(name=flagOnly)
            if(mytool.kcl_applyMaterial == "0"):
                mat.diffuse_color = (random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),1)
            elif(mytool.kcl_applyMaterial == "2"):
                _kclType,_variant,_shadow,_trickable,_drivable,_softWall,_d = decodeFlag(flagOnly[-4:])
                color = getSchemeColor(context,_kclType,_trickable,_drivable,_shadow)
                mat.diffuse_color = (color[0],color[1],color[2],1)
        context.active_object.data.materials.clear()
        context.active_object.data.materials.append(mat)


class add_blight(bpy.types.Operator):
    bl_idname = "kcl.addblight"
    bl_label = "Update BLIGHT"
    bl_options = {'UNDO'}
    bl_description = "Updates BLIGHT (Shadow) without changing other flag bits"

    @classmethod
    def poll(cls,context):
        b = True
        if not context.selected_objects:
            b = False
        return b

    def execute(self, context):
        updateBit(self,context,key="l")
                
        return {'FINISHED'}
        
class add_trickable(bpy.types.Operator):
    bl_idname = "kcl.updatetrickable"
    bl_label = "Update Trickable"
    bl_options = {'UNDO'}
    bl_description = "Updates Trickable without changing other flag bits"

    @classmethod
    def poll(cls,context):
        b = True
        if not context.selected_objects:
            b = False
        return b

    def execute(self, context):
        updateBit(self,context,key="t")
        return {'FINISHED'}

class add_reject(bpy.types.Operator):
    bl_idname = "kcl.updatereject"
    bl_label = "Update Reject"
    bl_options = {'UNDO'}
    bl_description = "Updates Reject Road without changing other flag bits"

    @classmethod
    def poll(cls,context):
        b = True
        if not context.selected_objects:
            b = False
        return b

    def execute(self, context):
        updateBit(self,context,key="r")
        return {'FINISHED'}

def decodeFlag(bareFlag):
    binary = bin(int(bareFlag, 16))[2:].zfill(16)
    kclType = "T"+hex(int(binary[-5:],2))[2:].zfill(2).upper()
    variant = hex(int(binary[-8:-5],2))[2:]
    shadow = int(binary[5:8],2)
    depth = int(binary[3:5],2)
    trickable = int(binary[2],2)
    drivable = int(str(binary[1]) == "0")
    softWall = int(binary[0],2)

    return kclType,variant,shadow,trickable,drivable,softWall,depth


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
    bl_idname = "kcl.export"
    bl_label = "Export KCL"
    bl_options = {'UNDO','PRESET'}
    filename_ext = ".kcl"

    filter_glob: StringProperty(
        default='*.kcl',
        options={'HIDDEN'}
    )
    kclExportScale : FloatProperty(name="Scale", min = 0.0001, max = 10000, default = 100)
    kclExportQuality : EnumProperty(name="Quality", items=[("SMALL","Small","Creates relative small KCL file. Might help with lag. (Don't use if you want to use speedmod above 1.5)"),
                                                                        ("MEDIUM","Medium","Default KCL encoding values."),
                                                                        ("CHARY","Chary","Nintendo like values, that are very careful. Use it only for experiments or if MEDIUM fails"),
                                                                        ("CUSTOM","Custom","Freely change octree settings")], default="MEDIUM")
    kclExportSelection : BoolProperty(name="Selection only", default=False)
    kclExportFlagOnly : BoolProperty(name="Only objects with KCL Flag", default=True)
    kclExportLowerWalls : BoolProperty(name="Lower Walls", default=False)
    kclExportLowerWallsBy : IntProperty(name="Lower Walls by", default= 30)
    kclExportLowerDegree : IntProperty(name="Degree", default= 45)
    kclExportWeakWalls : BoolProperty(name="Soften Walls")
    kclExportUnBeanCorner : EnumProperty(name="Method", items=[("NONE","None","Don't lower or change wall flags"),
                                                                        ("WEAK","Soften Walls","Change the walls flag in order to remove bean corners (Nintendo method)"),
                                                                        ("LOWER","Lower Walls","Lower walls in order to remove bean corners"),
                                                                        ("BOTH","Both","Use both methods (Not recomended)")], default="WEAK") 
    kclExportFixAll : BoolProperty(name="Fix All")
    kclExportDrop : BoolProperty(name="Drop All")
    kclExportDropUnused : BoolProperty(name="Drop Unused")
    kclExportDropFixed : BoolProperty(name="Drop Fixed")
    kclExportDropInvalid : BoolProperty(name="Drop Invalid")
    kclExportRemoveFacedown : BoolProperty(name="Remove facedown road")
    kclExportRemoveFaceup : BoolProperty(name="Remove faceup walls")
    kclExportConvFaceup : BoolProperty(name="Convert faceup walls to road")
    kclHEXOther : BoolProperty(name="Export legacy (HEX23 and HEX4) formats", default=False)
    kclExportTriArea : FloatProperty(name="Minimal Tri Area", min = 0.001, max = 6.0, default = 1.0, description="(Value for already scaled and encoded KCL) Define the minimal area size of KCL triangles. The intention is to ignore triangles that are generally to small. Values between 0.01 and 4.0 are recommended. The careful value 1.0 is used as default. Value 0 disables this filter functionality.")
    kclExportTriHeight : FloatProperty(name="Minimal Tri Height", min = 0.001, max = 4.0, default = 1.0, description="(Value for already scaled and encoded KCL) Define the minimal height of KCL triangles. The intention is to ignore deformed triangles (very slim, but long). Values between 0.01 and 2.0 are recommended. The careful value 1.0 is used as default. Value 0 disables this filter functionality.")
    
    kclEncodeUseScale : BoolProperty(name="Use Export Scale for Translation",default=True)
    kclEncodeScale : FloatVectorProperty(name="Scale", default=(1.0,1.0,1.0), min=0.00001,max=1000000)
    kclEncodeShift : FloatVectorProperty(name="Shift", default=(0.0,0.0,0.0), min=-1000000,max=1000000)
    kclEncodeRotate : FloatVectorProperty(name="Rotate", default=(0.0,0.0,0.0), min=-1000000,max=1000000)
    kclEncodeTranslate : FloatVectorProperty(name="Translate", default=(0.0,0.0,0.0), min=-1000000,max=1000000)


    kclSetKCL_BITS : IntProperty(name="KCL_BITS", default=0, min=0,max=20,description="0 to disable. This constant defines the number of bits used for the hash part of the octree. The result is, that the world will be divided in 2^bits base cubes. The number of bits is sometimes reduced because of technical limits")
    kclSetKCL_BLOW : IntProperty(name="KCL_BLOW", default=400, min=0,max=10000,description="For the octree, the world is divided into many cubes of equal size, normally 512*512*512 units. For collisions of an object (eg. driver or item) the octree is traversed to find a list with important triangles (faces) for the current positions. It is important, that near triagles of the neighbor cubes are also included into the triangle list")
    kclSetKCL_MAX : FloatVectorProperty(name="KCL_MAX", default=(0,0,0),description="KCL_MAX is a vector value. If a coordinate is set, it is used as maximal coordinate for the collision detection. The default is the maximum of all triangle points. However, this value is only used for the base cube calculations (number and size). The real upper border is then: MIN + N_CUBES * CUBE_SIZE.")
    kclSetKCL_MAX_DEPTH : IntProperty(name="KCL_MAX_DEPTH", default=10, min=0,max=30,description="KCL_MAX_DEPTH is 1 critieria of 3 to abort the cube recursion. The recursion is aborted and if the maximum octree depth KCL_MAX_DEPTH is reached; the default is 10. Nintendos tracks have values in the range of 3..6, but under the influence of KCL_MIN_SIZE")
    kclSetKCL_MAX_TRI : IntProperty(name="KCL_MAX_TRI", default=30, min=5,max=500,description="KCL_MAX_TRI is together with KCL_MAX_SIZE 1 critieria of 3 to abort the cube recursion. If creating the octree, a cube is divided into 8 equal sub cubes as long as the number of related triangles is larger than KCL_MAX_TRI. This condition is ignored, if the cube itself is larger than KCL_MAX_SIZE")
    kclSetKCL_MIN : FloatVectorProperty(name="KCL_MIN", default=(0,0,0),description="KCL_MIN is a vector value. If a coordinate is set, it is used as minimal coordinate for the collision detection. The default is the minimum of all triangle points.")
    kclSetKCL_MIN_SIZE : IntProperty(name="KCL_MIN_SIZE", default=512,min=1,max=1048576,description="KCL_MAX_TRI is together with KCL_MAX_SIZE 1 critieria of 3 to abort the cube recursion. If creating the octree, a cube is divided into 8 equal sub cubes as long as the number of related triangles is larger than KCL_MAX_TRI. This condition is ignored, if the cube itself is larger than KCL_MAX_SIZE")
    kclSetKCL_MAX_SIZE : IntProperty(name="KCL_MAX_SIZE", default=0, min=256,max=1048576,description="KCL_MAX_SIZE is together with KCL_MAX_TRI 1 criteria of 3 to abort the cube recursion. The recursion is aborted, the cube size is smaller or equal KCL_MAX_TRI and the number of triangles is smaller or equal KCL_MAX_TRI.")


    def draw(self,context):
        layout = self.layout

        selectionBox = layout.box()
        selectionBox.label(text="Export Settings", icon='MESH_DATA')
        selection = selectionBox.column()
        selection.prop(self,"kclExportScale")
        selection.prop(self,"kclExportSelection")
        selection.prop(self,"kclExportFlagOnly")

        unbeancornerBox = layout.box()
        unbeancornerBox.label(text="Un-Bean Corner", icon='NORMALS_VERTEX_FACE')
        unbeancorner = unbeancornerBox.column()
        unbeancorner.prop(self,"kclExportUnBeanCorner")
        if(self.kclExportUnBeanCorner == "LOWER" or self.kclExportUnBeanCorner == "BOTH"):
            unbeancorner.prop(self,"kclExportLowerWallsBy")
            unbeancorner.prop(self,"kclExportLowerDegree")

        wkcltSettingsBox = layout.box()
        wkcltSettingsBox.label(text="WKCLT Settings", icon='MODIFIER')
        wkcltSettings = wkcltSettingsBox.column()
        wkcltSettings.prop(self,"kclExportQuality")
        if self.kclExportQuality == "CUSTOM":
            wkcltSettingsCustomBox = wkcltSettings.box()
            wkcltSettingsCustomBox.label(text="Advanced Quality Settings", icon='MODIFIER_DATA')
            wkcltSettingsCustomBox.label(text="0 = Ignore / Use default")
            wkcltcustomColumn = wkcltSettingsCustomBox.column()
            wkcltcustomColumn.prop(self,"kclSetKCL_BITS")
            wkcltcustomColumn.prop(self,"kclSetKCL_BLOW")
            kclmax = wkcltSettingsCustomBox.row()
            kclmax.prop(self,"kclSetKCL_MAX")
            wkcltcustomColumn = wkcltSettingsCustomBox.column()
            wkcltcustomColumn.prop(self,"kclSetKCL_MAX_DEPTH")
            wkcltcustomColumn.prop(self,"kclSetKCL_MAX_TRI")
            kclmin = wkcltSettingsCustomBox.row()
            kclmin.prop(self,"kclSetKCL_MIN")
            wkcltcustomColumn = wkcltSettingsCustomBox.column()
            wkcltcustomColumn.prop(self,"kclSetKCL_MIN_SIZE")
            wkcltcustomColumn.prop(self,"kclSetKCL_MAX_SIZE")
        wkcltSettings.prop(self,"kclExportFixAll")
        if not self.kclExportFixAll:
            wkcltSettings.prop(self,"kclExportDrop")
            if not self.kclExportDrop:
                wkcltSettings.prop(self,"kclExportDropUnused")
                wkcltSettings.prop(self,"kclExportDropInvalid")
                wkcltSettings.prop(self,"kclExportDropFixed")
            wkcltSettings.prop(self,"kclExportRemoveFacedown")
            wkcltSettings.prop(self,"kclExportRemoveFaceup")
        wkcltSettings.prop(self,"kclExportConvFaceup")
        wkcltSettings.prop(self,"kclHEXOther")
        wkcltSettings.prop(self,"kclExportTriArea")
        wkcltSettings.prop(self,"kclExportTriHeight")

        wkcltEncode = layout.box()
        wkcltEncode.label(text="Encode Transformations (X, Y, Z)", icon='FILE_TICK')
        wkcltEncode.prop(self,"kclEncodeUseScale")
        row1=wkcltEncode.row()
        row1.prop(self,"kclEncodeScale")
        row2=wkcltEncode.row()
        row2.prop(self,"kclEncodeShift")
        row3=wkcltEncode.row()
        row3.prop(self,"kclEncodeRotate")
        row4=wkcltEncode.row()
        row4.prop(self,"kclEncodeTranslate")

    def execute(self, context):
        filepath = self.filepath
        activeObject = bpy.context.active_object
        if hasattr(activeObject,"type"):
            if(activeObject.type == "MESH"):
                bpy.ops.object.mode_set(mode='OBJECT')
        
        selection = context.selected_objects        

        objectsToExport = []
        if(self.kclExportSelection):
            objectsToExport = selection
        else:
            objectsToExport = [obj for obj in bpy.data.objects if obj.type == "MESH"]
        
        if(self.kclExportFlagOnly):
            objectsToExport1 = [obj for obj in objectsToExport if checkFlagInName001(obj.name,full=False,hex=self.kclHEXOther)]
            objectsToExport = objectsToExport1

        if not objectsToExport:
            self.report({"ERROR_INVALID_INPUT"},"Could not export. Output file would be empty.")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for obj in objectsToExport:
            obj.select_set(True)

        selectionBool = False
        if(self.kclExportSelection or self.kclExportFlagOnly):
            selectionBool = True

        bpy.ops.export_scene.objkcl(filepath=filepath, use_selection=selectionBool, use_blen_objects=False, use_materials=False, use_normals=True, use_triangles=True, group_by_object=True, global_scale=self.kclExportScale,use_mesh_modifiers=True)
        
        wkclt = "wkclt encode \"" + filepath + "\""
        if(self.kclEncodeScale[:] != (1.0,1.0,1.0)):
            wkclt += (" --scale " + str(self.kclEncodeScale[:])[1:-1].replace(" ", ""))
        if(self.kclEncodeShift[:] != (0.0,0.0,0.0)):
            value = self.kclEncodeShift
            if(self.kclEncodeUseScale):
                value[0] = round(value[0] * self.kclExportScale,3)
                value[1] = round(value[1] * self.kclExportScale,3)
                value[2] = round(value[2] * self.kclExportScale,3)
            wkclt += (" --shift " + str(value[:])[1:-1].replace(" ", ""))
        
        if(self.kclEncodeRotate[:] != (0.0,0.0,0.0)):
            wkclt += (" --rot " + str(self.kclEncodeRotate[:])[1:-1].replace(" ", ""))
        if(self.kclEncodeTranslate[:] != (0.0,0.0,0.0)):
            value = self.kclEncodeTranslate
            if(self.kclEncodeUseScale):
                value[0] = round(value[0] * self.kclExportScale,4)
                value[1] = round(value[1] * self.kclExportScale,4)
                value[2] = round(value[2] * self.kclExportScale,4)
            wkclt += (" --translate " + str(value[:])[1:-1].replace(" ", ""))
        
        wkclt += " --tri-area " + str(self.kclExportTriArea)
        wkclt += " --tri-height " + str(self.kclExportTriHeight)
        wkclt += " -o --kcl="
        wkclt += ("WEAKWALLS," if self.kclExportUnBeanCorner == "WEAK" or self.kclExportUnBeanCorner == "BOTH" else "")
        wkclt += ("DROP," if self.kclExportDrop else "")
        wkclt += ("FIXALL," if self.kclExportFixAll else "")
        wkclt += ("DROPUNUSED," if self.kclExportDropUnused else "")
        wkclt += ("DROPFIXED," if self.kclExportDropFixed else "")
        wkclt += ("DROPINVALID," if self.kclExportDropInvalid else "")
        wkclt += ("RMFACEDOWN," if self.kclExportRemoveFacedown else "")
        wkclt += ("RMFACEUP," if self.kclExportRemoveFaceup else "")
        wkclt += ("CONVFACEUP," if self.kclExportConvFaceup else "")
        wkclt += ("HEX," if self.kclHEXOther else "")
        if self.kclExportQuality != "CUSTOM":
            wkclt += self.kclExportQuality
        
        script_file = os.path.normpath(__file__)
        directory = os.path.dirname(script_file)
        if (self.kclExportUnBeanCorner == "LOWER" or self.kclExportUnBeanCorner == "BOTH"):
           # wkclt += (" --kcl-script=\"" + directory + "\lower-walls.txt\" --const lower=" + str(self.kclExportLowerWallsBy) + ",degree=" + str(self.kclExportLowerDegree)+ ",") 
            wkclt += r' --kcl-script="{0}\lower-walls.txt" --const lower={1},degree={2},'.format(directory,str(self.kclExportLowerWallsBy),str(self.kclExportLowerDegree))
        else:
            if(self.kclExportQuality == "CUSTOM"):
                wkclt += " --const "
        if(self.kclExportQuality == "CUSTOM"):
            if(self.kclSetKCL_BITS != 0): 
                wkclt += "KCL_BITS="+str(self.kclSetKCL_BITS) + ","
            blow = str(self.kclSetKCL_BLOW) if self.kclSetKCL_BLOW > 0 else "400"
            wkclt += "KCL_BLOW="+ blow + ","
            if(self.kclSetKCL_MAX[:] != (0,0,0)): 
                wkclt += "KCL_MAX=v"+str((self.kclSetKCL_MAX)[:]).replace(" ", "") + ","
            if(self.kclSetKCL_MAX_DEPTH != 10 and self.kclSetKCL_MAX_DEPTH != 0):
                wkclt += "KCL_MAX_DEPTH="+ str(self.kclSetKCL_MAX_DEPTH) + ","
            if(self.kclSetKCL_MAX_TRI != 30 and self.kclSetKCL_MAX_TRI != 0):
                wkclt += "KCL_MAX_TRI="+ str(self.kclSetKCL_MAX_TRI) + ","
            if(self.kclSetKCL_MIN[:] != (0,0,0)): 
                wkclt += "KCL_MIN=v"+str((self.kclSetKCL_MIN)[:]).replace(" ", "") + ","
            if(self.kclSetKCL_MIN_SIZE != 512 and self.kclSetKCL_MIN_SIZE != 0):
                wkclt += "KCL_MIN_SIZE="+ str(self.kclSetKCL_MIN_SIZE) + ","
            if(self.kclSetKCL_MAX_SIZE != 0):
                wkclt += "KCL_MAX_SIZE="+ str(self.kclSetKCL_MAX_SIZE) + ","
        
        print(wkclt)
        os.system(wkclt)

        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            obj.select_set(True)

        return {'FINISHED'}

class import_kcl_file(bpy.types.Operator, ImportHelper):
    bl_idname = "kcl.load"
    bl_label = "Import KCL"       
    filename_ext = '.kcl'
    bl_options = {'UNDO'}
    bl_description = "Loads KCL file"
    
    filter_glob: StringProperty(
        default='*.kcl;*.szs',
        options={'HIDDEN'}
    )
        
    kclImportColor : EnumProperty(name = "Imported colors", items=[("0", "Random color", ''),
                                                                    ("1", "Use custom scheme", '')],default="1")
    kclImportScale : FloatProperty(name = "Scale", default=0.01, max=100,min=0.0001)

    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt

        filepath = self.filepath
        #I love my object mode
        if(bpy.context.active_object):
            bpy.ops.object.mode_set(mode='OBJECT')


        #Decode KCL to OBJ
        filedata = ""
        currentTime = time.time() #Get the current time, add to filepath
        objFilepath = filepath[:-4] + str(currentTime) + ".obj"
        wkcltCommand = r'wkclt decode "{0}" -o --dest "{1}"'.format(filepath,objFilepath)
        os.system(wkcltCommand)

        #Import OBJ to Blenduh
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.import_scene.obj(filepath=objFilepath,use_split_groups=True,use_image_search=False)

        context.view_layer.objects.active = bpy.context.selected_objects[0]
        objs = bpy.context.selected_objects
        
        #Long ass scale commands
        bpy.ops.transform.resize(value=(self.kclImportScale, self.kclImportScale, self.kclImportScale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

        #remove duplicated mats if they exists
        remove_all_duplicate_materials()
        merge_duplicate_flags(context)
        for obj in objs:
            #Split the name for KCL Flags
            params = obj.name.upper().split("_")
            type = "T" + params[1]

            #Get Label, assign new Name
            label = labelDict[type]
            a = (label,params[1],params[2])
            newName = ("_").join(a)
            obj.name = newName

            flag = params[2][1:]
            properFlag = "_" + params[1] + "_" + params[2]

            #Get mat, if doesn't exist, create one
            obj.data.materials.clear()
            mat = bpy.data.materials.get(properFlag)
            if mat is None:
                mat = bpy.data.materials.new(name=properFlag)
                if(self.kclImportColor == "0"):
                    mat.diffuse_color = (random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),1)
                elif(self.kclImportColor == "1"):
                    _kclType,_variant,_shadow,_trickable,_drivable,_softWall,_d = decodeFlag(flag)
                    colorR = getSchemeColor(context,_kclType,_trickable,_drivable,_shadow)           
                    mat.diffuse_color = (colorR[0],colorR[1],colorR[2],1)
            #Assign mat
            obj.data.materials.append(mat)


        #Delete temp file
        if os.path.exists(objFilepath):
            os.remove(objFilepath)
            os.remove(objFilepath[:-3] + "mtl")
        merge_duplicate_flags(context)
        return {'FINISHED'}

class export_autodesk_dae(bpy.types.Operator, ExportHelper):
    bl_idname = "export.autodesk_dae"
    bl_label = "Export Autodesk DAE"    
    bl_description = "Export BrawlBox/BrawlCrate friendly Collada (.dae) file"
    filename_ext = ".dae"
    filter_glob: StringProperty(
        default='*.dae',
        options={'HIDDEN'}
    )
    daeExportPathMode : EnumProperty(name="Path Mode", items=[('AUTO', "Auto", ""),
                                                                        ('COPY', "Copy", "")])
    daeExportSelection : BoolProperty(name="Selection only", default = False)
    daeExportCollection : BoolProperty(name="Active collection", default = False)
    daeExportScale : FloatProperty(name="Scale", default = 1)


    def execute(self, context):
        filepath = self.filepath
        bpy.ops.export_scene.fbx(filepath = filepath, use_selection = self.daeExportSelection,  filter_glob='*.dae', use_active_collection = self.daeExportCollection, global_scale = self.daeExportScale, apply_scale_options='FBX_SCALE_NONE', object_types={'MESH','ARMATURE'}, use_mesh_modifiers=True, path_mode=self.daeExportPathMode, bake_anim=False)
        dae_convert(filepath=filepath)
        return {'FINISHED'}

def dae_convert(filepath):
    script_file = os.path.normpath(__file__)
    directory = os.path.dirname(script_file)
    curTime = str(time.time()/2)
    converterDir = "\"" + directory + "\\bin\\FbxConverter.exe" + "\""
    daeFile = filepath[:-4]+curTime+".dae"
    command = converterDir + " \"" + filepath + "\" \"" + daeFile + "\" /sffFBX /dffCOLLADA /v"
    a = os.popen(command).read()
    print(a)
    os.remove(filepath)
    filename = filepath.split("\\")[-1]
    os.rename(daeFile,filepath)

class export_minimap(bpy.types.Operator, ExportHelper):
    bl_idname = "export.minimap"
    bl_label = "ABMatt: Export Minimap BRRES"    
    bl_description = "Export Minimap BRRES using ABMatt"
    filename_ext = ".brres"
    filter_glob: StringProperty(
        default='*.brres',
        options={'HIDDEN'}
    )

    exportScale : FloatProperty(name="Scale", default = 100)
    exportSelection : BoolProperty(name="Selection Only", default = False)
    exportCollection : BoolProperty(name="Active collection", default = False)

    @classmethod
    def poll(cls,context):
        a = False
        check = os.popen('abmatt').read()
        if(check.startswith("USAGE: abmatt")):
            a = True
        return a

    def execute(self, context):
        filepath = self.filepath
        filename = filepath.split("\\")[-1]
        name = '.'.join(filename.split(".")[:-1])
        curTime = str(time.time())
        if not 'map' in name:
            name += ".map"
        brresName = name + ".brres"
        daeName = name + curTime + ".dae"
        tempFilepath = '\\'.join(filepath.split("\\")[:-1])
        daeFilepath = tempFilepath + "\\" + daeName
        brresFilepath = tempFilepath + "\\" + brresName
        bpy.ops.export_scene.fbx(filepath = daeFilepath, use_selection = self.exportSelection, filter_glob='*.dae', use_active_collection = self.exportCollection, global_scale = self.exportScale, apply_scale_options='FBX_SCALE_NONE', object_types={'MESH'}, use_mesh_modifiers=True, bake_anim=False)
        dae_convert(filepath=daeFilepath)
        abmatt = r'abmatt convert "{0}" to "{1}" -o'.format(daeFilepath,brresFilepath)
        print(abmatt)
        os.system(abmatt)
        os.remove(daeFilepath)
        if(brresFilepath != filepath):
            os.rename(brresFilepath,filepath)

        return {'FINISHED'}

def export_autodesk_dae_button(self, context):
    self.layout.operator("export.autodesk_dae", text="Autodesk Collada (.dae)")
def export_minimap_button(self, context):
    self.layout.operator("export.minimap", text="Export Minimap BRRES (Abmatt)")
def export_kcl_button(self, context):
    self.layout.operator("kcl.export", text="Export KCL (Wiimms)")
def import_kcl_button(self, context):
    self.layout.operator("kcl.load", text="Import KCL (Wiimms)")

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
        if(obj.name != original_name and obj.type == 'MESH'):
            
            name = obj.name
            if(name[-3:].isnumeric() and name[-4] =='.'):
                name = name[:-4]
            if(name == common_name):
                duplicated_names.append(obj.name)
    return duplicated_names

def merge_duplicate(context):
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
        obj1 = bpy.data.objects.get(objName)
        if(hasattr(obj1,"data")):
            obj1.data.name = objName
        # MeshName = meshes[i].name
        # if(MeshName[-3:].isnumeric() and MeshName[-4] == "."):
        #     meshes[i].name = MeshName[:-4]
        i=i+1    
    return True

def merge_duplicate_flags(context):
    i = 0
    active = context.active_object
    bpy.ops.object.select_all(action='DESELECT')
    
    objects=[ob.name for ob in bpy.context.view_layer.objects if ob.visible_get() and checkFlagInName001(ob.name)]
    meshes=[ob.data for ob in bpy.context.view_layer.objects if ob.visible_get() and checkFlagInName001(ob.name)]
    if(active.name[-3:].isnumeric() and active.name[-4] == "."):
        active.name = active.name[:-4]
    activeName = active.name
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
        obj1 = bpy.data.objects.get(objName)
        if(hasattr(obj1,"data")):
            obj1.data.name = objName
        # MeshName = meshes[i].name
        # if(MeshName[-3:].isnumeric() and MeshName[-4] == "."):
        #     meshes[i].name = MeshName[:-4]
        i=i+1
    try:
        bpy.data.objects[activeName].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[activeName]
    except ReferenceError:
        pass
        
    return True

class merge_duplicate_objects(bpy.types.Operator):
    bl_idname = "mkw.objectmerge"
    bl_label = "Merge duplicate objects"
    bl_description = "Joins objects with duplicate names (*.001, *.002 etc.)"
    bl_options = {'UNDO'}
    def execute(self, context):
        merge_duplicate(context)
        merge_duplicate(context)
        
        return {'FINISHED'}


class toggle_face_orientation(bpy.types.Operator):
    bl_idname = "mkw.toggleface"
    bl_label = "Toggle Face Orientation"
    bl_description = "Toggles Face Orientation"

    def execute(self, context):
        space = context.area.spaces.active
        space.overlay.show_face_orientation = not space.overlay.show_face_orientation
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
            if not object.is_area:
                continue
            object_position = object.location



            areaNumber = '{0:0{1}X}'.format(x,2)
            areaShape = '{0:0{1}X}'.format(int(object.area_shape),2)
            areaType = '{0:0{1}X}'.format(int(object.area_type[1:],16),2)
            areaID = "FF"
            if(object.area_id != -1 and object.area_type == 'A0'):
                areaID = '{0:0{1}X}'.format(int(object.area_id), 2)
            areaPrority = object.area_pror
            areaSet1 = 0
            areaSet2 = 0
            areaRoute = "FF"
            areaEnemy = "FF"
            if(object.area_type == 'A1'):
                areaSet1 = int(object.area_kareha)
            elif(object.area_type == 'A2'):
                areaSet1 = object.area_bfg
            elif(object.area_type == 'A3'):
                areaSet1 = object.area_acc
                areaSet2 = object.area_spd
                areaRoute = '{0:0{1}X}'.format(int(object.area_route), 2)
            elif(object.area_type == 'A4'):
                if(object.area_enpt != -1):
                    areaEnemy = '{0:0{1}X}'.format(int(object.area_enpt), 2)
            elif(object.area_type == 'A6'):
                areaSet1 = object.area_bblm
                areaSet2 = object.area_bblm_trans
            elif(object.area_type in ['A8','A9']):
                areaSet1 = object.area_group
            elif(object.area_type == 'A10'):
                if(object.area_coob_enabled):
                    if(object.area_coob_version == "kHacker"):
                        areaRoute = 1
                        areaSet1 = object.area_coob_kevin_mode
                        areaSet2 = object.area_coob.kevin_checkpoint
                    else:
                        areaRoute = "FF"
                        areaSet1 = object.area_coob_rii_p1
                        areaSet2 = object.area_coob_rii_p2
                        if(object.area_coob_rii_invert):
                            areaSet1 = object.area_coob_rii_p2
                            areaSet2 = object.area_coob_rii_p1
                            
                        
            areaSet1 = '{0:0{1}X}'.format(int(areaSet1), 4)
            areaSet2 = '{0:0{1}X}'.format(int(areaSet2), 4)
            areaSet = str(areaSet1) + str(areaSet2)
            if(areaRoute != "FF"):
                areaRoute = '{0:0{1}X}'.format(int(areaRoute), 2)
            if(areaEnemy != "FF"):
                areaEnemy = '{0:0{1}X}'.format(int(areaEnemy), 2)
                
            xpos = round(object_position[0] * scale, 2)
            ypos = round(object_position[2] * scale, 2)
            zpos = round(object_position[1] * scale * -1, 2)
            xrot = round(math.degrees(object.rotation_euler[0]), 2)
            yrot = round(math.degrees(object.rotation_euler[2]), 2)
            zrot = round(math.degrees(object.rotation_euler[1]), 2)
            xscl = round(object.scale[0],2)
            yscl = round(object.scale[2],2)
            zscl = round(object.scale[1],2)
            myData = [
                str(areaNumber),
                str(areaShape),
                str(areaType),
                str(areaID),
                str(areaPrority),
                str(xpos),
                str(ypos),
                str(zpos),
                str(xrot),
                str(yrot),
                str(zrot),
                str(xscl),
                str(yscl),
                str(zscl),
                str(areaSet),
                str(areaRoute) + str(areaEnemy),
                '0000\n']
            dataValue = "\t".join(myData)
            data = data + dataValue
            x = x + 1
            
        bpy.context.window_manager.clipboard = data
        return {'FINISHED'}

def create_collection(*args,name="MyCollection",parent=None):
    cols = [col for col in bpy.data.collections if col.name==name]
    parCol = None
    if not cols:
        myCol = bpy.data.collections.new(name)
        if(parent==None):
            bpy.context.scene.collection.children.link(myCol)
        else:
            parCols = [col for col in bpy.data.collections if col.name==parent]
            parCol = None
            if not parCols:
                parCol = bpy.data.collections.new(parent)
                bpy.context.scene.collection.children.link(parCol)
            else:
                parCol = parCols[0]
            parCol.children.link(myCol)
            myCol = parCol.children.get(name)
    if(len(cols)!=1):
        cols = bpy.context.scene.collection.children.get(name)
        if(parent != None and parCol):
            cols = parCol.children.get(name)
    else:
        cols = cols[0]
    if args:
        for arg in args:
            if not hasattr(arg,"type"):
                continue
            if arg.type != 'MESH' and not 'CAMERA':
                continue
            for coll in arg.users_collection:
                coll.objects.unlink(arg)
            cols.objects.link(arg)
        bpy.context.view_layer.objects.active = args[0]
        



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
        bpy.ops.object.select_all(action='DESELECT')
        
        bpy.ops.mesh.primitive_cube_add(size=10000/scale, location=cursor_position)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.translate(value=(0,0,5000/scale), orient_type='GLOBAL')
        bpy.ops.object.mode_set(mode='OBJECT')

        activeObject = bpy.context.active_object
        activeObject.name = "New Cubic Area"
        activeObject.is_area = True

        create_collection(activeObject,name="[AREA]")
        
        
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
        
        bpy.ops.mesh.primitive_cylinder_add(radius=5000/scale, depth=10000/scale, location=cursor_position, vertices=128)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.translate(value=(0,0,5000/scale), orient_type='GLOBAL')
        bpy.ops.object.mode_set(mode='OBJECT')

        activeObject = bpy.context.active_object
        activeObject.name = "New Cylindrical Area"
        activeObject.is_area = True
        activeObject.area_shape = True
        create_collection(activeObject,name="[AREA]")
        return {'FINISHED'}
  
loading = 0

area_label_dict = {
   0: "Camera",
   1: "EnvEffect",
   2: "BFG Entry Swapper",
   3: "Moving Road",
   4: "Destination Point",
   5: "Minimap Control",
   6: "BBLM Changer",
   7: "Flying Boos",
   8: "Object Grouper",
   9: "Group Unloader",
   10: "Fall Boundary",
   11: "Conditional Out of Bounds" ,
}

class load_kmp_area(bpy.types.Operator, ImportHelper):
    global area_label_dict
    bl_idname = "kmpc.load"
    bl_label = "Import KMP AREAs"       
    filename_ext = '.kmp'
    bl_description = "Loads KMP file and imports AREAs with settings"
    bl_options = {'UNDO'}  
    filter_glob: StringProperty(
        default='*.kmp',
        options={'HIDDEN'}
    )
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        global loading
        loading = 1

        path = self.filepath
        kmp_areas = []
        with open(path,"rb") as file:
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
                obj = None
                activeObject = None
                if(str(areaShape) == "0"):
                    bpy.ops.mesh.primitive_cube_add(size=10000/scale, location=areaLocation)
                    activeObject = bpy.context.active_object
                    activeObject.area_shape = False

                if(str(areaShape) == "1"):
                    bpy.ops.mesh.primitive_cylinder_add(radius=5000/scale, depth=10000/scale, location=areaLocation)
                    activeObject = bpy.context.active_object
                    activeObject.area_shape = True
                
                activeObject.is_area = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.transform.translate(value=(0,0,5000/scale), orient_type='GLOBAL')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.transform.resize(value=areaScale, orient_type='LOCAL')        
                string_areaType = 'A'+str(areaType)
                activeObject.area_type = string_areaType
                activeObject.area_pror = areaPriority
                activeObject.rotation_euler[0] = areaRotation[0]
                activeObject.rotation_euler[1] = areaRotation[1]
                activeObject.rotation_euler[2] = areaRotation[2]
                areaTypeLabel = areaType
                if(areaType == 0):
                    activeObject.area_id = areaCAME
                elif(areaType == 1):
                    activeObject.area_kareha = areaSet1>0
                elif(areaType == 2):
                    activeObject.area_bfg = areaSet1
                elif(areaType == 3):
                    activeObject.area_route = areaRoute
                    activeObject.area_acc = areaSet1
                    activeObject.area_spd = areaSet2
                elif(areaType == 4):
                    activeObject.area_enpt = areaEnemy
                elif(areaType == 6):
                    activeObject.area_bblm = areaSet1
                    activeObject.area_bblm_trans = areaSet2
                elif(areaType in [8,9]):
                    activeObject.area_group = areaSet1
                elif(areaType == 10):
                    if(areaSet1 != 0 or areaSet2 != 0):
                        activeObject.area_coob_enabled = 1
                        if(areaRoute == 1):
                            activeObject.area_coob_version = "kHacker"
                            activeObject.area_coob_kevin_mode = str(areaSet1)
                            activeObject.area_coob_kevin_checkpoint = areaSet2
                        else:
                            activeObject.area_coob_version = "Riidefi"
                            activeObject.coob_rii_p1 = areaSet1
                            activeObject.coob_rii_p2 = areaSet2
                    areaTypeLabel = 11
                create_collection(activeObject,name="[{0}]".format(area_label_dict[areaTypeLabel]),parent="[AREA]")
                activeObject.name = "KMP AREA {0}: {1}".format(i,area_label_dict[areaTypeLabel])
        
        loading = 0
        return {'FINISHED'}

class load_kmp_enemy(bpy.types.Operator, ImportHelper):
    bl_idname = "kmpe.load"
    bl_label = "Import Enemy Paths as Curve"       
    filename_ext = '.kmp'
    bl_description = "Imports main enemy path as curve. Used for previewing replay cameras."
    
    filter_glob: StringProperty(
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

def checkFxxxx(name):
    if(len(name) < 6):
        return False
    try:
        i = int(name[-4:],16)
    except ValueError:
        return False
    if(name[-6] != "_"):
        return False
    if(name[-5] != "F"):
        return False
    return True

def checkHEX4(name):
    if(len(name) < 5):
        return False
    try:
        i = int(name[-4:],16)
    except ValueError:
        return False
    if(name[-5] != "_"):
        return False
    return True

def checkHEX23(name):
    if(len(name)<7):
        return False
    try:
        i = int(name[-3:],16)
    except ValueError:
        return False
    if(name[-4] != "_"):
        return False
    try:
        i = int(name[-6:-5],16)
    except ValueError:
        return False
    if(name[-7] != "_"):
        return False
    return True



def checkFlagInName(name,full=True,hex=False):
    if(full):
        if(len(name) < 9):
            return False
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
    else:
        if not hex:
            return checkFxxxx(name)
        else:
            return checkFxxxx(name) or checkHEX23(name) or checkHEX4(name)

def checkFlagInName001(name,full=True,hex=False):
    if(len(name) < 4):
        return False
    if(name[-3:].isnumeric() and name[-4] == '.'):
        name = name[:-4]
    result = checkFlagInName(name,full=full,hex=hex)
    return result

oldFrameCount = 250
from mathutils import Matrix
casting = False
@persistent
def update_scene_handler(scene):

    global lastselection, setting1users, setting2users, oldFrameCount, casting
    mytool = scene.kmpt
    activeObject = bpy.context.active_object
    obj = activeObject
    if hasattr(obj, "is_came"):
        if(obj.is_view_point):
            obj = obj.link_to_came
        if(obj.is_came):
            if(lastselection != obj):
                if(obj.type == 'CAMERA'):
                    bpy.context.scene.camera = obj
                    scene.frame_end = obj.came_frames
    if(lastselection != activeObject):
        if(mytool.util_addVCs):
            if obj.type == 'MESH':
                if(BLENDER_33):
                    if not obj.data.color_attributes:
                        obj.data.color_attributes.new(name="Vertex Colors",type='BYTE_COLOR',domain='CORNER')
                else:
                    if not obj.data.vertex_colors:
                        obj.data.vertex_colors.new(name="Vertex Colors")
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
    create_node_groups()

@persistent
def frame_change_handler(scene):
    mytool = scene.kmpt
    activeObject = bpy.context.active_object
    scene = bpy.context.scene
    if(scene.frame_current == scene.frame_end):
        if(bpy.context.screen.is_animation_playing):
            if BLENDER_30:
                if(bpy.context.screen.is_scrubbing):
                    return
            if(mytool.kmp_cameGoToNext == True):
                if(activeObject.is_came):
                    ob = activeObject.came_next
                    if ob != None:
                        if(ob.is_view_point):
                            ob = ob.link_to_came
                        scene.camera = ob
                        scene.frame_current = 0
                        scene.frame_end = ob.came_frames
                        bpy.context.view_layer.objects.active = ob
                    else:
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

    filter_glob: StringProperty(
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

    filter_glob: StringProperty(
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
    updates_bool : BoolProperty(name="Check for updates", default=True)
    prerelease_bool : BoolProperty(name="Check for pre-release versions", default=False)

    openScheme : BoolProperty(name="Custom KCL Flag Scheme")

    darkenBLIGHT : BoolProperty(name="Darken Shadow Flags",default=True)
    blightScale : FloatProperty(name="Scale",min=0.0,max=0.1,default=0.3)
    addTintToTrickable : BoolProperty(name="Add Color Tint to Trickable",default=True)
    trickableColor : FloatVectorProperty(name='Color', subtype='COLOR',min=0.0,max=1.0,default=[0.8,0.8,0])
    trickableScale : FloatProperty(name="Scale",min=0.0,max=1.0,default=0.3)
    addTintToReject : BoolProperty(name="Add Color Tint to non-Drivable",default=True)
    rejectColor : FloatVectorProperty(name='Color', subtype='COLOR',min=0.0,max=1.0,default=[1,0,0])
    rejectScale : FloatProperty(name="Scale",min=0.0,max=1.0,default=0.4)

    kclColorT00 : FloatVectorProperty(name='Road (0x00)', subtype='COLOR',min=0.0,max=1.0,default=[0.8,0.8,0.8])
    kclColorT01 : FloatVectorProperty(name='Slippery Road 1 (0x01)', subtype='COLOR',min=0.0,max=1.0,default=[0.7,0.65,0.3])
    kclColorT02 : FloatVectorProperty(name='Weak Off-road (0x02)', subtype='COLOR',min=0.0,max=1.0,default=[0.25,0.43,0])
    kclColorT03 : FloatVectorProperty(name='Off-road (0x03)', subtype='COLOR',min=0.0,max=1.0,default=[0,0.3,0])
    kclColorT04 : FloatVectorProperty(name='Heavy Off-road (0x04)', subtype='COLOR',min=0.0,max=1.0,default=[0,0.15,0])
    kclColorT05 : FloatVectorProperty(name='Slippery Road 2 (0x05)', subtype='COLOR',min=0.0,max=1.0,default=[0,0.45,0.45])
    kclColorT06 : FloatVectorProperty(name='Boost Panel (0x06)', subtype='COLOR',min=0.0,max=1.0,default=[0.6,0.3,0])
    kclColorT07 : FloatVectorProperty(name='Boost Ramp (0x07)', subtype='COLOR',min=0.0,max=1.0,default=[0.45,0.126,0])
    kclColorT08 : FloatVectorProperty(name='Jump Pad (0x08)', subtype='COLOR',min=0.0,max=1.0,default=[1,0.8,0])
    kclColorT09 : FloatVectorProperty(name='Item Road (0x09)', subtype='COLOR',min=0.0,max=1.0,default=[0.7,0,0.4])
    kclColorT0A : FloatVectorProperty(name='Solid Fall (0x0A)', subtype='COLOR',min=0.0,max=1.0,default=[0.3,0,0])
    kclColorT0B : FloatVectorProperty(name='Moving Road (0x0B)', subtype='COLOR',min=0.0,max=1.0,default=[0,0,0.45])
    kclColorT0C : FloatVectorProperty(name='Wall (0x0C)', subtype='COLOR',min=0.0,max=1.0,default=[0.25,0.25,0.25])
    kclColorT0D : FloatVectorProperty(name='Invisible Wall (0x0D)', subtype='COLOR',min=0.0,max=1.0,default=[0,1,1])
    kclColorT0E : FloatVectorProperty(name='Item Wall (0x0E)', subtype='COLOR',min=0.0,max=1.0,default=[0.5,0.2,0.6])
    kclColorT0F : FloatVectorProperty(name='Wall 3 (0x0F)', subtype='COLOR',min=0.0,max=1.0,default=[0.3,0.3,0.3])

    kclColorT10 : FloatVectorProperty(name='Fall Boundary (0x10)', subtype='COLOR',min=0.0,max=1.0,default=[1,0,0])
    kclColorT11 : FloatVectorProperty(name='Cannon Activator (0x11)', subtype='COLOR',min=0.0,max=1.0,default=[0.7,0,0.4])
    kclColorT12 : FloatVectorProperty(name='Force Recalculation (0x12)', subtype='COLOR',min=0.0,max=1.0,default=[0.2,0.2,0.3])
    kclColorT13 : FloatVectorProperty(name='Half-pipe Ramp (0x13)', subtype='COLOR',min=0.0,max=1.0,default=[0,0.333,0.65])
    kclColorT14 : FloatVectorProperty(name='Wall (0x14)', subtype='COLOR',min=0.0,max=1.0,default=[0.35,0.35,0.35])
    kclColorT15 : FloatVectorProperty(name='Moving Road (0x15)', subtype='COLOR',min=0.0,max=1.0,default=[0,0,0.56])
    kclColorT16 : FloatVectorProperty(name='Sticky Road (0x16)', subtype='COLOR',min=0.0,max=1.0,default=[0.6,0.3,0.6])
    kclColorT17 : FloatVectorProperty(name='Road (0x17)', subtype='COLOR',min=0.0,max=1.0,default=[0.8,0.8,0.8])
    kclColorT18 : FloatVectorProperty(name='Sound Trigger (0x18)', subtype='COLOR',min=0.0,max=1.0,default=[0.2,0.3,0.5])
    kclColorT19 : FloatVectorProperty(name='Weak Wall (0x19)', subtype='COLOR',min=0.0,max=1.0,default=[0.4,0.4,0.3])
    kclColorT1A : FloatVectorProperty(name='Effect Trigger (0x1A)', subtype='COLOR',min=0.0,max=1.0,default=[0.2,0.1,0.3])
    kclColorT1B : FloatVectorProperty(name='Item State Modifier (0x1B)', subtype='COLOR',min=0.0,max=1.0,default=[0.45,0.3,0.3])
    kclColorT1C : FloatVectorProperty(name='Half-Pipe Invisible Wall (0x1C)', subtype='COLOR',min=0.0,max=1.0,default=[0.1,0.5,0.5])
    kclColorT1D : FloatVectorProperty(name='Moving Road (0x1D)', subtype='COLOR',min=0.0,max=1.0,default=[0,0,0.36])
    kclColorT1E : FloatVectorProperty(name='Special Wall (0x1E)', subtype='COLOR',min=0.0,max=1.0,default=[0.6,0.4,0.5])
    kclColorT1F : FloatVectorProperty(name='Wall 5 (0x1F)', subtype='COLOR',min=0.0,max=1.0,default=[0.2,0.2,0.2])
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

@orientation_helper(axis_forward='-Z', axis_up='Y')
class ExportOBJKCL(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.objkcl"
    bl_label = 'Export OBJKCL'
    bl_description = "There's no OBJKCL. Never was. I'm talking from outside of the system. We stop the simulation. Look under the pillow, you will find bag of gummy bears. Eat them all. You will fall asleep and wake up in 2009. We will start all over again."

    # context group
    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
    )
    use_animation: BoolProperty(
        name="Animation",
        description="Write out an OBJ for each frame",
        default=False,
    )

    # object group
    use_mesh_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers",
        default=True,
    )
    # extra data group
    use_edges: BoolProperty(
        name="Include Edges",
        description="",
        default=True,
    )
    use_smooth_groups: BoolProperty(
        name="Smooth Groups",
        description="Write sharp edges as smooth groups",
        default=False,
    )
    use_smooth_groups_bitflags: BoolProperty(
        name="Bitflag Smooth Groups",
        description="Same as 'Smooth Groups', but generate smooth groups IDs as bitflags "
        "(produces at most 32 different smooth groups, usually much less)",
        default=False,
    )
    use_normals: BoolProperty(
        name="Write Normals",
        description="Export one normal per vertex and per face, to represent flat faces and sharp edges",
        default=True,
    )
    use_uvs: BoolProperty(
        name="Include UVs",
        description="Write out the active UV coordinates",
        default=True,
    )
    use_materials: BoolProperty(
        name="Write Materials",
        description="Write out the MTL file",
        default=True,
    )
    use_triangles: BoolProperty(
        name="Triangulate Faces",
        description="Convert all faces to triangles",
        default=False,
    )
    use_nurbs: BoolProperty(
        name="Write Nurbs",
        description="Write nurbs curves as OBJ nurbs rather than "
        "converting to geometry",
        default=False,
    )
    use_vertex_groups: BoolProperty(
        name="Polygroups",
        description="",
        default=False,
    )

    # grouping group
    use_blen_objects: BoolProperty(
        name="OBJ Objects",
        description="Export Blender objects as OBJ objects",
        default=True,
    )
    group_by_object: BoolProperty(
        name="OBJ Groups",
        description="Export Blender objects as OBJ groups",
        default=False,
    )
    group_by_material: BoolProperty(
        name="Material Groups",
        description="Generate an OBJ group for each part of a geometry using a different material",
        default=False,
    )
    keep_vertex_order: BoolProperty(
        name="Keep Vertex Order",
        description="",
        default=False,
    )

    global_scale: FloatProperty(
        name="Scale",
        min=0.01, max=1000.0,
        default=1.0,
    )


    path_mode: path_reference_mode

    check_extension = True

    def draw(self,context):
        layout = self.layout
        layout.label(text="There's no OBJKCL. Never was. I'm talking from outside of the system. We stop the simulation. Look under the pillow, you will find bag of gummy bears. Eat them all. You will fall asleep and wake up in 2009. We will start all over again.")

    def execute(self, context):
        from . import export_obj

        from mathutils import Matrix
        filepath = self.filepath
        keywords = self.as_keywords(
            ignore=(
                "axis_forward",
                "axis_up",
                "global_scale",
                "check_existing",
                "filter_glob",
            ),
        )

        global_matrix = (
            Matrix.Scale(self.global_scale, 4) @
            axis_conversion(
                to_forward=self.axis_forward,
                to_up=self.axis_up,
            ).to_4x4()
        )

        keywords["global_matrix"] = global_matrix
        return export_obj.save(context, **keywords)

    def draw(self, context):
        pass

def update_area_material(self,context):
    if not context:
        return
    obj = context.active_object
    define_area_mats()
    mat = bpy.data.materials.get("kmpc.area." + obj.area_type)
    obj.data.materials.clear()
    obj.data.materials.append(mat) 

def pool_came_objects(self,object):
    return object.is_came

shut_the_fuck_up_im_updating_you = False
def mark_as_first_came(self,context):
    global shut_the_fuck_up_im_updating_you
    if(shut_the_fuck_up_im_updating_you):
        return
    shut_the_fuck_up_im_updating_you = True
    if not context:
        return
    objs = [ob for ob in bpy.context.scene.objects if ob.is_came]
    for ob in objs:
        ob.is_main_came = False
    active = context.active_object
    if(context.active_object.is_view_point):
        active = context.active_object.link_to_came
    active.is_main_came = True
    shut_the_fuck_up_im_updating_you = False

def updateLastFrame(self,context):
    active = context.active_object
    scene = context.scene
    scene.frame_end = active.came_frames

def register_came():
    bpy.types.Object.is_came = BoolProperty(
        name="Is CAME?",
        default=False

    )
    bpy.types.Object.is_view_point = BoolProperty(
        name="Is View Point?",
        default=False
    )
    bpy.types.Object.link_to_vp = PointerProperty(
        name="Pointer To VP",
        type=bpy.types.Object
    )
    bpy.types.Object.link_to_came = PointerProperty(
        name="Pointer to CAME",
        type=bpy.types.Object
    )
    bpy.types.Object.came_next = PointerProperty(
        name="Next Camera",
        type=bpy.types.Object,
        poll=pool_came_objects
    )
    bpy.types.Object.came_route = IntProperty(
        name="Custom Route ID",
        default=0,
        min=0,
        max=255
    )
    bpy.types.Object.is_main_came = BoolProperty(
        name="Use as First CAME",
        default=False,
        update=mark_as_first_came
    )
    bpy.types.Object.came_frames = IntProperty(
        name="Duration (Frames)",
        default=220,
        min=0,
        max=65535,
        update=updateLastFrame
    )

def register_area():
    global areaTypes

    bpy.types.Object.is_area = BoolProperty(
        name="Is AREA?",
        default=False,
        update=update_area_material
    )
    bpy.types.Object.area_shape = BoolProperty(
        default = False
    )
    bpy.types.Object.area_type = EnumProperty(
        name="Area Type",
        items=areaTypes,
        default='A0',
        update=update_area_material
    )
    bpy.types.Object.area_pror = IntProperty(
        name = "Priority", 
        min= 0, 
        default= 0, 
        max=255,
        description= "When 2 AREAs of same type a overlapping then the one\with higher priority is getting considered"
    )            
    bpy.types.Object.area_id = IntProperty(
        name = "CAME Index",
        min=0,
        default=0,
        max=255,
        description= "ID of camera which will be activated while entering AREA (Decimal)"
    )          
    bpy.types.Object.area_kareha = BoolProperty(
        name = "Use EnvKarehaUp",
        default = False,
        description= "If EnvKareha is being used, selecting this option will use EnvKarehaUp instead"
    )
    bpy.types.Object.area_bfg = IntProperty(
        name = "BFG Entry",
        min = 0,
        default = 0,
        max = 255,
        description= "ID of posteffect.bfg entry which will be used while inside of the AREA"
    )
    bpy.types.Object.area_route = IntProperty(
        name = "Route",
        min = 0,
        default = 0,
        max = 255,
        description= "A Route used by moving road KCL to push player along. Setting this to '-1' will moving road to push players towards this AREA origin point"
    )
    bpy.types.Object.area_acc = IntProperty(
        name = "Acceleration",
        min = 0,
        default = 0,
        max = 65535,
        description= "Defines acceleration and deceleration speed for Variant 0x0002. The higher value, the easier is to speed up and harder to slow down"
    )
    bpy.types.Object.area_spd =  IntProperty(
        name = "Speed",
        min = 0,
        default = 0,
        max = 65535,
        description="Defines the speed of moving water"
    )
    bpy.types.Object.area_enpt = IntProperty(
        name = "Enemy Point",
        default = -1,
        min = -1,
        max = 254,
        description="Defines the next enemy point for CPU when colliding with Force Recalculation KCL"
    )
    bpy.types.Object.area_bblm = IntProperty(
        name = "BBLM File Entry",
        default = 0,
        min = 0,
        max = 255,
        description="Controls the index of posteffect.bblm to use, being 0 the default file, 1 posteffect.bblm1 and so on"
    )
    bpy.types.Object.area_bblm_trans = IntProperty(
        name = "Transition Time",
        default = 30,
        min = 0,
        max = 65535,
        description = "Transition between entries in frames"
    )
    bpy.types.Object.area_group = IntProperty(
        name = "Group",
        min = 0,
        max = 65535,
        default = 0,
        description= "Defines the group for AREA type 8 (Object Grouper) and 9 (Group Unloader) to work together"
    )
    bpy.types.Object.area_coob_enabled = BoolProperty(
        name = "Use as COoB",
        default = False,
        description = "Use this type of AREA as Conditional Out of Bounds (Both Riidefi's and kHacker's versions are supported)"
    )
    bpy.types.Object.area_coob_version = EnumProperty(
        name = "COoB Mode", 
        items=[("kHacker", "kHacker35000vr", "Use kHacker's cheat code"),
              ("Riidefi", "Ridefii", "Use Riidefi's cheat code\nThe AREA will be enabled if and only if a player is in the Cth checkpoint sector such that P1 <= C < P2.\nNOTE: If both P1 and P2 are zero, this code is disabled, and the boundary is unconditionally enabled.\nNOTE: If P1 > P2, the range functions in blacklist mode. The AREA will be disabled within P2 <= C < P1, and enabled everywhere else.")],
        default='Riidefi'
    )
    bpy.types.Object.area_coob_kevin_mode = EnumProperty(
        name = "In KCP region", 
        items=[("0", "Enable COoB", 'Enables this Fall Boundaries while inside entered key checkpoint region'),
            ("1", "Disable COoB", 'Disables this Fall Boundaries while inside entered key checkpoint region')],
        default = '0'
    )
    bpy.types.Object.area_coob_kevin_checkpoint = IntProperty(
        name = "KCL Region",
        min = 0,
        max = 255,

    )
    bpy.types.Object.area_coob_rii_p1 = IntProperty(
        name = "Checkpoint 1 (P1)",
        min = 0,
        max = 255,
        default = 0,
        description = "First checkpoint of the range (P1 <= C < P2)"
    )
    bpy.types.Object.area_coob_rii_p2 = IntProperty(
        name = "Checkpoint 2 (P2)",
        min = 0,
        max = 255,
        default = 0,
        description = "Second checkpoint of the range (P1 <= C < P2)"
    )
    bpy.types.Object.area_coob_rii_invert = BoolProperty(
        name = "Invert condition",
        default = False,
        description = "Checking this option will invert when condition is meet. For example if you have this AREA enabled only when the player is in chosen checkpoint range, it will make it enabled only when the player is OUTSIDE chosen checkpoint range"
    )


def define_area_mats():
    for i in range(11):   
        matName = "kmpc.area.A" + str(i)
        mat = bpy.data.materials.get(matName)
        if mat is None:
            mat = bpy.data.materials.new(matName)
            mat.diffuse_color = matColors[i]
            mat.blend_method = 'BLEND' 


def create_node_groups():
    create_mirror_group()
    create_mirror_group(key="u",name="Mirror U")
    create_mirror_group(key="v",name="Mirror V")

mynodescat = [ShaderNodeCategory("SH_TEV_STAGE", "My Nodes", items=[NodeItem("ShaderTEVGroup")]),]

classes = [ShaderTEVGroup,get_vertex_color,toggle_face_orientation,add_vertex_col,PreferenceProperty,add_mirrorUV,get_flag_back,add_mirrorU,add_trickable,add_reject, add_mirrorV, ShaderUtilities, MyProperties, restore_specular_metalic, ShaderGroupUtilities, export_minimap, set_alpha_hashed, KMPUtilities, remove_duplicate_materials, KCLSettings, KCLUtilities,ExportPrefs,ImportPrefs,ExportOBJKCL, AREAUtilities,CAMEUtilities, RouteUtilities, MaterialUtilities,add_blight, scene_setup, keyframes_to_route, openWSZSTPage, openIssuePage, timeline_to_route, set_alpha_blend, set_alpha_clip, remove_specular_metalic, create_camera, kmp_came, apply_kcl_flag, cursor_kmp, import_kcl_file, kmp_gobj, kmp_area, kmp_c_cube_area, kmp_c_cylinder_area, load_kmp_area, load_kmp_enemy, export_kcl_file, openGithub, merge_duplicate_objects, export_autodesk_dae]
 
wszstInstalled = False
addon_keymaps = []
def register():
    global wszstInstalled
    wszst = os.popen('wszst version').read()
    if(wszst.startswith("wszst: Wiimms SZS Tool")):
        wszstInstalled = True
    script_file = os.path.normpath(__file__)
    directory = os.path.dirname(script_file)
    if directory.endswith("Blender-KMP-Utilities"):
        
        register_area()
        register_came()
        for cls in classes:
            bpy.utils.register_class(cls)
        bpy.app.handlers.frame_change_post.append(frame_change_handler)
        bpy.app.handlers.load_post.append(load_file_handler)
        bpy.app.handlers.depsgraph_update_post.append(update_scene_handler)
        bpy.types.TOPBAR_MT_file_export.append(export_autodesk_dae_button)
        bpy.types.TOPBAR_MT_file_export.append(export_minimap_button)
        if(wszstInstalled):
            bpy.types.TOPBAR_MT_file_export.append(export_kcl_button)
            bpy.types.TOPBAR_MT_file_import.append(import_kcl_button)
        bpy.types.Scene.kmpt = PointerProperty(type= MyProperties)
        
    else:
        bpy.utils.register_class(BadPluginInstall)

    register_node_categories("MY_CUSTOM", mynodescat)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("kcl.applyflag", type='F', value='PRESS', shift=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("kcl.addblight", type='W', value='PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("mkw.toggleface", type='U', value='PRESS', shift=True)
        addon_keymaps.append((km, kmi))
 
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
    bpy.types.TOPBAR_MT_file_export.remove(export_minimap_button)
    try:
        bpy.types.TOPBAR_MT_file_export.remove(export_kcl_button)
        bpy.types.TOPBAR_MT_file_import.remove(import_kcl_button)
    except RuntimeError:
        pass
    del bpy.types.Scene.kmpt
    
    unregister_node_categories("MY_CUSTOM")
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

 
if __name__ == "__main__":
    register()