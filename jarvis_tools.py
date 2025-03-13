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
        box.label(text="Batch Conversion", icon='FILE_FOLDER')
        box.operator("jarvis.batch_convert_xml")
        
        # Export for Web
        box = layout.box()
        box.label(text="Export for Web", icon='WORLD')
        box.operator("jarvis.export_glb")

class SimplifyTransparency(bpy.types.Operator):
    """Break all Alpha Node Links in Materials"""
    bl_idname = "jarvis.simplify_transparency"
    bl_label = "Simplify Transparency"

    def execute(self, context):
        for material in bpy.data.materials:
            if material.use_nodes and material.node_tree:
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        for link in material.node_tree.links:
                            if link.to_socket == node.inputs['Alpha']:
                                material.node_tree.links.remove(link)
        
        self.report({'INFO'}, "Alpha nodes unlinked in all materials!")
        return {'FINISHED'}

class ExportGLB(bpy.types.Operator):
    """Export scene to .glb format with Alpha fixes"""
    bl_idname = "jarvis.export_glb"
    bl_label = "Export GLB for Web"

    def execute(self, context):
        # Remove alpha nodes from all materials except basic_glass
        for material in bpy.data.materials:
            if material.name != "basic_glass" and material.node_tree:
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        for link in material.node_tree.links:
                            if link.to_socket.name == 'Alpha':
                                material.node_tree.links.remove(link)
        
        # Open GLB export dialog
        bpy.ops.export_scene.gltf(filepath="", export_format='GLB')
        
        self.report({'INFO'}, "GLB export completed!")
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
