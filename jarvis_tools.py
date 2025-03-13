bl_info = {
    "name": "Jarvis Tools",
    "blender": (3, 0, 0),
    "category": "Object",
}

import bpy
import os
import glob
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
        
        # Step 3: Export
        box = layout.box()
        box.label(text="Step 3: Export", icon='EXPORT')
        box.operator("jarvis.export_model")
        box.operator("jarvis.verify_export")
        box.operator("jarvis.pack_textures")
        
        # Batch Conversion Section
        box.label(text="Batch Conversion", icon='FILE_FOLDER')
        box.operator("jarvis.batch_convert_xml")

class BatchConvertXML(bpy.types.Operator, ImportHelper):
    """Batch Convert .xml Files to .fbx or .obj"""
    bl_idname = "jarvis.batch_convert_xml"
    bl_label = "Batch Convert XML"
    
    directory: StringProperty(subtype='DIR_PATH')
    output_directory: StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        # Prompt before execution
        self.report({'INFO'}, "Before running this function, please ensure all your model files and textures are in the same folder. Please ensure a proper output folder is selected that is different from your source files.")
        
        source_folder = self.directory
        output_folder = self.output_directory

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        xml_files = glob.glob(os.path.join(source_folder, "**", "*.xml"), recursive=True)

        for xml_file in xml_files:
            # Placeholder for actual conversion using Sollumz
            self.report({'INFO'}, f"Converting {xml_file} to .fbx/.obj")
            # Implement conversion logic here

        self.report({'INFO'}, "Batch conversion complete!")
        return {'FINISHED'}

# Register classes
classes = [
    JarvisToolsPanel,
    BatchConvertXML,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()