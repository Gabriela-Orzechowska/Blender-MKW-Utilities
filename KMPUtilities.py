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
                    
class MyProperties(bpy.types.PropertyGroup):
    
    scale : bpy.props.FloatProperty(name= "Scale", soft_min= 0.0001, soft_max= 100000, default= 100)
 

        
class KMPUtilities(bpy.types.Panel):
    bl_label = "KMP Utilities"
    bl_idname = "PT_KMP"
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
        layout.label(text="AREA")
        layout.operator("kmpc.area")
        area_create_column = layout.column();
        area_create_column.operator("kmpc.c_cube_area")
        area_create_column.operator("kmpc.c_cylinder_area")
        
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
            xpos = round(object_position[0] * scale, 2)
            ypos = round(object_position[2] * scale, 2)
            zpos = round(object_position[1] * scale * -1, 2)
            xrot = round(math.degrees(object.rotation_euler[0]), 2)
            yrot = round(math.degrees(object.rotation_euler[2]), 2)
            zrot = round(math.degrees(object.rotation_euler[1]), 2)
            xscl = round(object.scale[0],2)
            yscl = round(object.scale[2],2)
            zscl = round(object.scale[1],2)
            position = str(x) + "\t00\t00\tFF\t00\t" + str(xpos) + "\t" + str(ypos) + "\t" + str(zpos) + "\t" + str(xrot) + "\t" + str(yrot) + "\t" + str(zrot) + "\t" + str(xscl) + "\t" + str(yscl) + "\t" + str(zscl) + "\t00000000\tFFFF\t0000\n"
            data = data + position
            x = x + 1
        
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
        
        bpy.ops.mesh.primitive_cube_add(size=10000/scale, location=cursor_position)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.translate(value=(0,0,5000/scale), orient_type='GLOBAL')
        bpy.ops.object.mode_set(mode='OBJECT')
        activeObject = bpy.context.active_object
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
        
        bpy.ops.mesh.primitive_cylinder_add(radius=5000/scale, depth=10000/scale, location=cursor_position)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.translate(value=(0,0,5000/scale), orient_type='GLOBAL')
        bpy.ops.object.mode_set(mode='OBJECT')
        activeObject = bpy.context.active_object
        mat = bpy.data.materials.get("kmpc.area")
        if mat is None:
          mat = bpy.data.materials.new(name="kmpc.area")
          mat.diffuse_color = (0.8, 0.123, 0, 0.6)
          mat.blend_method = 'BLEND'
          
          
        activeObject.data.materials.append(mat)
        return {'FINISHED'}
  
      
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
        areaOffset = 80 + sectionOffsets[9]
        file.seek(areaOffset, 0)
        areaNumber = struct.unpack('>H', file.read(2))[0]
        areaUnused = struct.unpack('>H', file.read(2))[0]
        scale = mytool.scale
        areas = []
        for i in range(int(areaNumber)):
            areaShape = struct.unpack('>b', file.read(1))[0]
            areaType = struct.unpack('>b', file.read(1))
            areaCAME = struct.unpack('>b', file.read(1))
            areaPriority = struct.unpack('>b', file.read(1))
            areaXPos = struct.unpack('>f', file.read(4))[0]
            areaYPos = struct.unpack('>f', file.read(4))[0]
            areaZPos = struct.unpack('>f', file.read(4))[0]
            areaXRot = struct.unpack('>f', file.read(4))[0]
            areaYRot = struct.unpack('>f', file.read(4))[0]
            areaZRot = struct.unpack('>f', file.read(4))[0]
            areaXScale = struct.unpack('>f', file.read(4))[0]
            areaYScale = struct.unpack('>f', file.read(4))[0]
            areaZScale = struct.unpack('>f', file.read(4))[0]
            areaSet = struct.unpack('>I', file.read(4))[0]
            areaRoute = struct.unpack('>H', file.read(2))[0]
            areaEnemy = struct.unpack('>H', file.read(2))[0]
            
            areaLocation = (areaXPos/scale, areaZPos/scale * -1, areaYPos/scale)
            areaRotation = (math.radians(areaXRot), math.radians(areaZRot), math.radians(areaYRot))
            areaScale = (areaXScale, areaZScale, areaYScale)
            if(str(areaShape) == "0"):
                bpy.ops.mesh.primitive_cube_add(size=10000/scale, location=areaLocation, rotation=areaRotation)
                cube = bpy.context.selected_objects[0]
                cube.name = "AREA_" + str(i)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.transform.translate(value=(0,0,5000/scale), orient_type='GLOBAL')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.transform.resize(value=areaScale, orient_type='LOCAL')      
            if(str(areaShape) == "1"):
                bpy.ops.mesh.primitive_cylinder_add(radius=5000/scale, depth=10000/scale, location=cursor_position)
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
            
        
        
        return {'FINISHED'}

    
    
classes = [MyProperties, KMPUtilities, cursor_kmp, kmp_gobj, kmp_area, kmp_c_cube_area, kmp_c_cylinder_area, load_kmp]
 
 
 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
        bpy.types.Scene.kmpt = bpy.props.PointerProperty(type= MyProperties)
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.my_tool
 
 
 
if __name__ == "__main__":
    register()