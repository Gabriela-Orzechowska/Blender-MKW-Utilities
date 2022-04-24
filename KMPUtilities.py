bl_info = {
    "name" : "KMP Utilities",
    "author" : "Gabriela_",
    "version" : (1, 0),
    "blender" : (2, 82, 0),
    "location" : "View3d > Tool",
    "warning" : "",
    "wiki_url" : "",
    "category": "Export",
}

import bpy
import math
import struct 
from bpy_extras.io_utils import ImportHelper


lastselection = []
setting1users = ["A2", "A3", "A6", "A8", "A9"]
setting2users = ["A3", "A6"]
    
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
            kmp_areaEnemy = "0"
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
                                
            areaName = properties[0] + "_" + properties[1] + "_"  + properties[2] + "_"  + str(mytool.kmp_areaEnumType[1:]) + "_"  + kmp_areaID + "_" +\
            str(mytool.kmp_areaPrority) + "_"  + kmp_areaSet1 + "_"  + kmp_areaSet2 + "_"  + kmp_areaRoute + "_"  + kmp_areaEnemy
            bpy.context.active_object.name = areaName
            mat = bpy.data.materials.get("kmpc.area." + mytool.kmp_areaEnumType)
            bpy.context.active_object.data.materials.clear()
            bpy.context.active_object.data.materials.append(mat)
                   
class MyProperties(bpy.types.PropertyGroup):
    
    scale : bpy.props.FloatProperty(name= "Export scale", soft_min= 0.0001, soft_max= 100000, default= 100, description= "Set scale at which your KMP will be exported")
    
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
    kmp_areaPrority : bpy.props.IntProperty(name = "Priority", soft_min= 0, default= 0, update=updateArea, 
                                            description= "When 2 AREAs of same type a overlapping then the one\with higher priority is getting considered")                                                                
    kmp_areaSet1 : bpy.props.StringProperty(name = "Set1", default= "0", update=updateArea)
    kmp_areaSet2 : bpy.props.StringProperty(name = "Set2", default= "0", update=updateArea)
    #AREA0
    kmp_areaID : bpy.props.IntProperty(name = "CAME", soft_min= 0, default= 0, update=updateArea, 
                                        description= "ID of camera which will be activated while entering AREA (Decimal)")
    #AREA1
    kmp_areaEvnKarehaUp : bpy.props.BoolProperty(name= "Use EnvKarehaUp?", update=updateArea, 
                                                description= "If EnvKareha is being used, selecting this option will use EnvKarehaUp instead")
    #AREA2
    kmp_areaPostEffectEntry : bpy.props.IntProperty(name= "BFG Entry", soft_min= 0, default= 0, update=updateArea,
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
    kmp_areaIDK1 : bpy.props.IntProperty(name = "Unknown Setting 1", soft_min= 0, default= 0, update=updateArea, 
                                        description= "Unknown. Undocumented. Always 1 on Nintendo tracks")
    kmp_areaIDK2 : bpy.props.IntProperty(name = "Unknown Setting 2", soft_min= 0, default= 0, update=updateArea, 
                                        description= "Unknown. Undocumented. (Very unsure) Defines music volume change")
    #AREA8&9
    kmp_areaGroup : bpy.props.IntProperty(name = "Group", soft_min= 0, default= 0, update=updateArea,
                                        description= "Defines the group for AREA type 8 (Object Grouper) and 9 (Group Unloader) to work together")

    
        
class KMPUtilities(bpy.types.Panel):
    bl_label = "KMP Utilities"
    bl_idname = "_PT_KMP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MKW Utils"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.kmpt
        layout.prop(mytool, "scale")
        layout.operator("kmpc.load")
        layout.operator("kmpc.cursor")
        layout.operator("kmpc.gobj")
        
class AREAUtilities(bpy.types.Panel):
    bl_label = "AREA Utilities"
    bl_idname = "_PT_KMP_AREA"
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
            area_setting_column.prop(mytool, "kmp_areaMovingRouteSet1")
            area_setting_column.prop(mytool, "kmp_areaMovingRouteSet2")
        elif(mytool.kmp_areaEnumType == "A4"):
             area_setting_column.prop(mytool, "kmp_areaEnemy")
        elif(mytool.kmp_areaEnumType == "A6"):
             area_setting_column.prop(mytool, "kmp_areaIDK1")
             area_setting_column.prop(mytool, "kmp_areaIDK2")
        elif(mytool.kmp_areaEnumType == "A8" or mytool.kmp_areaEnumType == "A9"):
             area_setting_column.prop(mytool, "kmp_areaGroup")
        
        if(bpy.context.object is not None):
            current_mode = bpy.context.object.mode
        else:
            current_mode = 'OBJECT'
        
        if(current_mode != 'OBJECT'):
            area_create_column.enabled = False
        else:
            area_create_column.enabled = True
        


class cursor_kmp (bpy.types.Operator):
    bl_idname = "kmpc.cursor"
    bl_label = "Position from 3D Cursor"
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
        print(position)
        bpy.context.window_manager.clipboard = position
        return {'FINISHED'}

class kmp_gobj (bpy.types.Operator):
    bl_idname = "kmpc.gobj"
    bl_label = "GOBJ from Selected"
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
    bl_label = "AREA from Selected"
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
            areaNumber = "%02d" % (int(properties[1],))
            areaShape = "%02d" % (int(properties[2],))
            areaType = "%02d" % (int(properties[3],))
            areaID = "FF" if properties[4] == "-1" else '{:X}'.format(int(float(properties[4])))
            areaPrority = "%02d" % (int(properties[5],))
            areaSet1 = '{:X}'.format(int(properties[6]))
            areaSet2 = '{:X}'.format(int(properties[7]))
            areaSet = str(areaSet1) + str(areaSet2)
            areaRoute = '{:X}'.format(int(properties[8]))
            if properties[8] == "-1":
                areaRoute = "FFFF"
            areaEnemy = format(int(properties[9], 16), '04x')
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
            "\t" + str(areaSet) + "\t" + str(areaRoute) + "\t" + str(areaEnemy) + "\n"
            data = data + dataValue
            x = x + 1
            
            print(areaSet)
        bpy.context.window_manager.clipboard = data
        return {'FINISHED'}


class kmp_c_cube_area (bpy.types.Operator):
    bl_idname = "kmpc.c_cube_area"
    bl_label = "Create cube AREA Model"
    bl_description = "Creates a cubic AREA Model is proper scale and origin (Move it only in OBJECT mode)"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        cursor_position = context.scene.cursor.location
        
        existingAreas = 0;
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
        name = activeObject.name
        properties = name.split("_")
        mytool.kmp_areaEnumType = "A" + properties[3]
        mytool.kmp_areaID = int(float(properties[4]))
        mytool.kmp_areaPrority = int(properties[5])
        mytool.kmp_areaSet1 = properties[6]
        mytool.kmp_areaSet2 = properties[7]
        mytool.kmp_areaRoute = int(properties[8])
        mytool.kmp_areaEnemy = int(properties[9])
        mat = bpy.data.materials.get("kmpc.area")
        if mat is None:
          mat = bpy.data.materials.new(name="kmpc.area")
          mat.diffuse_color = (0.8, 0.123, 0, 0.6)
          mat.blend_method = 'BLEND' 
        activeObject.data.materials.append(mat)
          
          
        return {'FINISHED'}


class kmp_c_cylinder_area (bpy.types.Operator):
    bl_idname = "kmpc.c_cylinder_area"
    bl_label = "Create cylinder AREA Model"
    bl_description = "Creates a cylider AREA Model is proper scale and origin (Move it only in OBJECT mode)"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        cursor_position = context.scene.cursor.location
        
        existingAreas = 0;
        for obj in bpy.data.objects:
            if "area_" in obj.name.lower():
                existingAreas = existingAreas + 1
        
        bpy.ops.mesh.primitive_cylinder_add(radius=5000/scale, depth=10000/scale, location=cursor_position)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.translate(value=(0,0,5000/scale), orient_type='GLOBAL')
        bpy.ops.object.mode_set(mode='OBJECT')
        activeObject = bpy.context.active_object
        activeObject.name = "AREA_" + str(existingAreas) + "_1_0_0_0_0_0_-1_0"
        name = activeObject.name
        properties = name.split("_")
        mytool.kmp_areaEnumType = "A" + properties[3]
        mytool.kmp_areaID = int(float(properties[4]))
        mytool.kmp_areaPrority = int(properties[5])
        mytool.kmp_areaSet1 = properties[6]
        mytool.kmp_areaSet2 = properties[7]
        mytool.kmp_areaRoute = int(properties[8])
        mytool.kmp_areaEnemy = int(properties[9])
        mat = bpy.data.materials.get("kmpc.area")
        if mat is None:
          mat = bpy.data.materials.new(name="kmpc.area")
          mat.diffuse_color = (0.8, 0.123, 0, 0.6)
          mat.blend_method = 'BLEND'
          
          
        activeObject.data.materials.append(mat)
        return {'FINISHED'}
  
loading = 0
class load_kmp(bpy.types.Operator, ImportHelper):
    bl_idname = "kmpc.load"
    bl_label = "Load KMP file"       
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
        print(sectionOffsets)
        
        existingAreas = 0;
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
            areaRoute = struct.unpack('>h', file.read(2))[0]
            areaEnemy = struct.unpack('>h', file.read(2))[0]
            areaLocation = (areaXPos/scale, areaZPos/scale * -1, areaYPos/scale)
            areaRotation = (math.radians(areaXRot), math.radians(areaZRot), math.radians(areaYRot))
            areaScale = (areaXScale, areaZScale, areaYScale)
            areaName = "AREA_" + str(existingAreas + i) + "_" + '{:X}'.format(areaShape) + "_" + str(int(areaType)) + "_" + str(int(areaCAME))\
            + "_" + '{:X}'.format(areaPriority) + "_" + '{:X}'.format(areaSet1) + "_" + '{:X}'.format(areaSet2) + "_" + '{:X}'.format(areaRoute) + "_" + '{:X}'.format(areaEnemy)
             
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


def checkMaterial():
    for i in range(11):   
        matName = "kmpc.area.A" + str(i)
        mat = bpy.data.materials.get(matName)
        if mat is None:
            mat = bpy.data.materials.new(matName)
            mat.diffuse_color = matColors[i]
            mat.blend_method = 'BLEND' 

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
                

            
    lastselection = activeObject

classes = [MyProperties, KMPUtilities, AREAUtilities, cursor_kmp, kmp_gobj, kmp_area, kmp_c_cube_area, kmp_c_cylinder_area, load_kmp]
 
 
 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(update_scene_handler)
    bpy.types.Scene.kmpt = bpy.props.PointerProperty(type= MyProperties)
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.depsgraph_update_post.remove(update_scene_handler)
    del bpy.types.Scene.my_tool 
 
 
if __name__ == "__main__":
    register()