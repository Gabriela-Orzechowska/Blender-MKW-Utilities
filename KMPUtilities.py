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

    
def updateArea(self, context):
    scene = context.scene
    mytool = scene.kmpt
    activeObject = bpy.context.active_object
    if(lastselection == activeObject):
        if(activeObject.name.startswith("AREA_")): 
            name = activeObject.name
            properties = name.split("_")
            if(mytool.kmp_areaEnumType != 'A0'):
                mytool.kmp_areaID = -1
            areaName = properties[0] + "_" + properties[1] + "_"  + properties[2] + "_"  + str(mytool.kmp_areaEnumType[1:]) + "_"  + str(mytool.kmp_areaID) + "_" +\
            str(mytool.kmp_areaPrority) + "_"  + mytool.kmp_areaSet1 + "_"  + mytool.kmp_areaSet2 + "_"  + mytool.kmp_areaRoute + "_"  + mytool.kmp_areaEnemy
            bpy.context.active_object.name = areaName
                   
class MyProperties(bpy.types.PropertyGroup):
    
    scale : bpy.props.FloatProperty(name= "Scale", soft_min= 0.0001, soft_max= 100000, default= 100)
    #kmp_areaType : bpy.props.IntProperty(name = "Type", default= 0, update=updateArea)
    kmp_areaEnumType : bpy.props.EnumProperty(name = "Type", items=[("A0", "Camera", ''),
                                                                    ("A1", "EnvEffect", ''),
                                                                    ("A2", "BFG Entry Swapper", ''),
                                                                    ("A3", "Moving Road", ''),
                                                                    ("A4", "Destination Point", ''),
                                                                    ("A5", "Minimap Control", ''),
                                                                    ("A6", "Music Changer", ''),
                                                                    ("A7", "Flying Boos", ''),
                                                                    ("A8", "Object Grouper", ''),
                                                                    ("A9", "Group Unloading", ''),
                                                                    ("A10", "Fall Boundary", '')],
                                                                    update=updateArea)
    kmp_areaID : bpy.props.IntProperty(name = "CAME", default= 0, update=updateArea)
    kmp_areaPrority : bpy.props.IntProperty(name = "Priority", default= 0, update=updateArea)
    kmp_areaSet1 : bpy.props.StringProperty(name = "Set1", default= "0", update=updateArea)
    kmp_areaSet2 : bpy.props.StringProperty(name = "Set2", default= "0", update=updateArea)
    kmp_areaRoute : bpy.props.StringProperty(name = "Route", default= "0", update=updateArea)
    kmp_areaEnemy : bpy.props.StringProperty(name = "Enemy point ID", default= "0", update=updateArea)
 
    
        
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
        area_setting_column.prop(mytool, "kmp_areaID")
        area_setting_column.prop(mytool, "kmp_areaPrority")
        area_setting_column.prop(mytool, "kmp_areaSet1")
        area_setting_column.prop(mytool, "kmp_areaSet2")
        area_setting_column.prop(mytool, "kmp_areaRoute")
        area_setting_column.prop(mytool, "kmp_areaEnemy")
        
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
    
    def execute(self, context):
        data = ""
        scene = context.scene
        mytool = scene.kmpt
        scale = mytool.scale
        selected = bpy.context.selected_objects
        x = 0
        for object in selected:
            object_position = object.location
            name = object.name
            properties = name.split("_")
            areaNumber = "%02d" % (int(properties[1],))
            areaShape = "%02d" % (int(properties[2],))
            areaType = "%02d" % (int(properties[3],))
            areaID = int(float(properties[4]))
            if(str(areaID) == "-1"):
                areaID = "FF"
            else:
                areaID = "%02d" % (int(float(properties[4])))
            
            areaPrority = "%02d" % (int(properties[5],))
            areaSet1 = format(int(properties[6], 16), '04x')
            areaSet2 = format(int(properties[7], 16), '04x')
            areaSet = str(areaSet1) + str(areaSet2)
            areaRoute = format(int(properties[8], 16), '04x')
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
        activeObject.name = "AREA_" + str(existingAreas) + "_0_0_0_0_0_0_FFFF_0"
        name = activeObject.name
        properties = name.split("_")
        mytool.kmp_areaEnumType = "A" + properties[3]
        mytool.kmp_areaID = int(float(properties[4]))
        mytool.kmp_areaPrority = int(properties[5])
        mytool.kmp_areaSet1 = properties[6]
        mytool.kmp_areaSet2 = properties[7]
        mytool.kmp_areaRoute = properties[8]
        mytool.kmp_areaEnemy = properties[9]
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
        activeObject.name = "AREA_" + str(existingAreas) + "_1_0_0_0_0_0_FFFF_0"
        name = activeObject.name
        properties = name.split("_")
        mytool.kmp_areaEnumType = "A" + properties[3]
        mytool.kmp_areaID = int(float(properties[4]))
        mytool.kmp_areaPrority = int(properties[5])
        mytool.kmp_areaSet1 = properties[6]
        mytool.kmp_areaSet2 = properties[7]
        mytool.kmp_areaRoute = properties[8]
        mytool.kmp_areaEnemy = properties[9]
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
            areaRoute = struct.unpack('>H', file.read(2))[0]
            areaEnemy = struct.unpack('>H', file.read(2))[0]
            
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
            mat = bpy.data.materials.get("kmpc.area")
            if mat is None:
                mat = bpy.data.materials.new(name="kmpc.area")
                mat.diffuse_color = (0.8, 0.123, 0, 0.6)
                mat.blend_method = 'BLEND' 
            activeObject.data.materials.append(mat)
            
        
        loading = 0
        return {'FINISHED'}



def update_scene_handler(scene):
    global lastselection
    mytool = scene.kmpt
    activeObject = bpy.context.active_object
    if(loading == 0):
        if(activeObject.name.startswith("AREA_")):
            if(lastselection != activeObject):
                name = activeObject.name
                properties = name.split("_")
                mytool.kmp_areaEnumType = "A" + properties[3]
                mytool.kmp_areaID = int(float(properties[4]))
                mytool.kmp_areaPrority = int(properties[5])
                mytool.kmp_areaSet1 = properties[6]
                mytool.kmp_areaSet2 = properties[7]
                mytool.kmp_areaRoute = properties[8]
                mytool.kmp_areaEnemy = properties[9]
            
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