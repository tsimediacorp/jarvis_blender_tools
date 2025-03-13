bl_info = {
    "name": "Jarvis Tools",
    "blender": (3, 0, 0),
    "category": "Object",
}

import bpy
import os
import glob
import time
import shutil
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

class JarvisToolsPanel(bpy.types.Panel):
    """Main panel for Jarvis Tools"""
    bl_label = "Jarvis Tools"
    bl_idname = "OBJECT_PT_jarvis_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Jarvis Tools"

    def draw(self, context):
        layout = self.layout
        
        # Step 1: Model Prep & Import
        box = layout.box()
        box.label(text="Step 1: Model Preparation & Import", icon='IMPORT')
        box.operator("jarvis.import_model")
        box.operator("jarvis.validate_model")
        box.operator("jarvis.auto_fix")
        
        # Step 2: Modifications
        box = layout.box()
        box.label(text="Step 2: Modifications", icon='MODIFIER')
        box.operator("jarvis.fix_uvs")
        box.operator("jarvis.apply_transformations")
        box.operator("jarvis.optimize_geometry")
        box.operator("jarvis.generate_lods")
        
        # Transparency Fixes
        box = layout.box()
        box.label(text="Transparency Fixes", icon='SHADING_RENDERED')
        box.operator("jarvis.simplify_transparency")
        
        # Step 3: Export
        box = layout.box()
        box.label(text="Step 3: Export", icon='EXPORT')
        box.operator("jarvis.export_model")
        box.operator("jarvis.verify_export")
        box.operator("jarvis.pack_textures")
        
        # Batch Conversion Section
        box = layout.box()
        box.label(text="Batch Conversion", icon='FILE_FOLDER')
        box.operator("jarvis.batch_convert_xml")
        
        # Export for Web
        box = layout.box()
        box.label(text="Export for Web", icon='WORLD')
        box.operator("jarvis.export_glb")

class BatchConvertXML(bpy.types.Operator, ImportHelper):
    """Batch Convert .xml Files to .fbx or .obj"""
    bl_idname = "jarvis.batch_convert_xml"
    bl_label = "Batch Convert XML"
    
    directory: StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        source_folder = self.directory
        if not source_folder:
            self.report({'ERROR'}, "No source folder selected!")
            return {'CANCELLED'}
        
        # Ensure Sollumz is installed and find the correct operator
        time.sleep(1)  # Give Blender time to fully register add-ons
        if not hasattr(bpy.ops.sollumz, "import_assets"):
            self.report({'ERROR'}, "Sollumz import operator not found! Make sure the add-on is properly installed and enabled.")
            return {'CANCELLED'}
        
        # Create the 'Converted' output folder
        output_folder = os.path.join(source_folder, "Converted")
        os.makedirs(output_folder, exist_ok=True)
        
        xml_files = glob.glob(os.path.join(source_folder, "**", "*.xml"), recursive=True)
        texture_files = glob.glob(os.path.join(source_folder, "**", "*.png"), recursive=True) + \
                        glob.glob(os.path.join(source_folder, "**", "*.jpg"), recursive=True) + \
                        glob.glob(os.path.join(source_folder, "**", "*.jpeg"), recursive=True) + \
                        glob.glob(os.path.join(source_folder, "**", "*.tga"), recursive=True)
        
        if not xml_files:
            self.report({'WARNING'}, "No XML files found in the selected folder.")
            return {'CANCELLED'}
        
        # Copy textures to Converted folder
        for tex in texture_files:
            shutil.copy(tex, output_folder)
            self.report({'INFO'}, f"Copied texture: {tex}")

        for xml_file in xml_files:
            output_fbx = os.path.join(output_folder, os.path.splitext(os.path.basename(xml_file))[0] + ".fbx")
            
            # Switch to Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Import the XML file using Sollumz
            try:
                bpy.ops.sollumz.import_assets(filepath=xml_file)
                bpy.context.view_layer.update()
                
                # Ensure all objects are selected after import, excluding collision geometry and rigs
                for obj in bpy.context.scene.objects:
                    if "col" not in obj.name.lower() and obj.type not in {'ARMATURE'}:
                        obj.select_set(True)
                    else:
                        obj.select_set(False)
                
                bpy.context.view_layer.objects.active = bpy.context.scene.objects[0] if bpy.context.scene.objects else None
                
                # Check if objects are imported
                imported_objects = [obj for obj in bpy.context.scene.objects if obj.select_get()]
                if not imported_objects:
                    self.report({'WARNING'}, f"No valid objects detected from {xml_file} after import. Skipping export.")
                    continue
                
            except Exception as e:
                self.report({'ERROR'}, f"Failed to import {xml_file}: {str(e)}")
                continue
            
            # Export to FBX
            try:
                bpy.ops.export_scene.fbx(filepath=output_fbx, use_selection=True, use_mesh_modifiers=False, path_mode='COPY')
                self.report({'INFO'}, f"Converted {xml_file} to {output_fbx}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to export {output_fbx}: {str(e)}")
                continue
        
        self.report({'INFO'}, "Batch conversion completed! Converted files and textures are in the 'Converted' folder.")
        return {'FINISHED'}

# Register classes
classes = [
    JarvisToolsPanel,
    BatchConvertXML,
    ExportGLB,
    SimplifyTransparency,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
