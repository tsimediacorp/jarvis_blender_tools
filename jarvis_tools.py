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
import traceback
import importlib
import sys
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, IntProperty
from importlib import import_module

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
    """Batch Convert .xml Files to .fbx using Direct Sollumz Import"""
    bl_idname = "jarvis.batch_convert_xml"
    bl_label = "Batch Convert XML"
    
    directory: StringProperty(subtype='DIR_PATH')
    
    filter_glob: StringProperty(
        default="*.xml",
        options={'HIDDEN'},
    )
    
    wait_time: IntProperty(
        name="Wait Time (seconds)",
        description="Time to wait after import to ensure processing completes",
        default=2,
        min=0,
        max=10
    )
    
    debug_mode: BoolProperty(
        name="Debug Mode",
        description="Create a detailed log file to diagnose issues",
        default=True
    )
    
    def safe_delete_all(self, context):
        """Safely delete all objects"""
        try:
            # First ensure we're in object mode
            if context.object and context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Select all objects
            for obj in context.scene.objects:
                obj.select_set(True)
            
            # Delete selected objects if any
            if any(obj.select_get() for obj in context.scene.objects):
                bpy.ops.object.delete()
            
            return True
        except Exception as e:
            if self.debug_mode:
                print(f"Error in safe_delete_all: {str(e)}")
            return False
    
    def execute(self, context):
        source_folder = self.directory
        if not source_folder:
            self.report({'ERROR'}, "No source folder selected!")
            return {'CANCELLED'}
        
        # Create log file if debug mode is enabled
        log_path = None
        if self.debug_mode:
            log_path = os.path.join(source_folder, "conversion_log.txt")
            with open(log_path, 'w') as log_file:
                log_file.write("Jarvis Tools XML Conversion Log\n")
                log_file.write("===============================\n\n")
                log_file.write(f"Started conversion at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                log_file.write(f"Blender version: {bpy.app.version_string}\n")
                log_file.write(f"Wait time: {self.wait_time} seconds\n\n")
        
        # Attempt to import Sollumz by its known dotted module name
        try:
            sollumz_module = importlib.import_module("bl_ext.user_default.sollumz")
            YFT = sollumz_module.cwxml.fragment.YFT
            create_fragment_obj = sollumz_module.yft.yftimport.create_fragment_obj
            
            if log_path:
                with open(log_path, 'a') as log_file:
                    log_file.write("Successfully imported Sollumz from bl_ext.user_default.sollumz\n")
        except Exception as e:
            error_msg = f"Failed to import Sollumz modules from bl_ext.user_default.sollumz: {str(e)}"
            self.report({'ERROR'}, error_msg)
            if log_path:
                with open(log_path, 'a') as log_file:
                    log_file.write(f"ERROR: {error_msg}\n")
                    log_file.write("TRACE: " + traceback.format_exc() + "\n")
            return {'CANCELLED'}
        
        # Optional: Check if we have access to Sollumz import functionality
        if not hasattr(bpy.ops.sollumz, "import_assets"):
            self.report({'ERROR'}, "Sollumz import_assets operator not found! Ensure the add-on is properly installed and enabled.")
            return {'CANCELLED'}
        
        # Create output folder
        output_folder = os.path.join(source_folder, "Converted")
        os.makedirs(output_folder, exist_ok=True)
        
        # Find XML files
        xml_files = glob.glob(os.path.join(source_folder, "**", "*.yft.xml"), recursive=True)
        texture_files = (
            glob.glob(os.path.join(source_folder, "**", "*.png"), recursive=True) +
            glob.glob(os.path.join(source_folder, "**", "*.jpg"), recursive=True) +
            glob.glob(os.path.join(source_folder, "**", "*.jpeg"), recursive=True) +
            glob.glob(os.path.join(source_folder, "**", "*.tga"), recursive=True)
        )
        
        if not xml_files:
            self.report({'WARNING'}, "No YFT XML files found in the selected folder.")
            return {'CANCELLED'}
        
        # Log file list if debug mode is enabled
        if log_path:
            with open(log_path, 'a') as log_file:
                log_file.write(f"\nFound {len(xml_files)} YFT XML files to process:\n")
                for xml in xml_files:
                    log_file.write(f"  - {xml}\n")
                log_file.write(f"\nFound {len(texture_files)} texture files\n")
        
        # Copy textures to Converted folder
        for tex in texture_files:
            try:
                dest_path = os.path.join(output_folder, os.path.basename(tex))
                shutil.copy(tex, dest_path)
                self.report({'INFO'}, f"Copied texture: {os.path.basename(tex)}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed copying texture {os.path.basename(tex)}: {e}")
        
        success_count = 0
        error_count = 0
        
        # Process each XML file
        for xml_file in xml_files:
            if log_path:
                with open(log_path, 'a') as log_file:
                    log_file.write(f"\n{'='*50}\n")
                    log_file.write(f"Processing: {xml_file}\n")
                    log_file.write(f"{'='*50}\n")
            
            # Set up output paths
            base_filename = os.path.splitext(os.path.basename(xml_file))[0]
            # For YFT files, remove the .yft part too
            if base_filename.endswith(".yft"):
                base_filename = base_filename[:-4]
            
            output_fbx = os.path.join(output_folder, base_filename + ".fbx")
            
            self.report({'INFO'}, f"Processing file: {xml_file}")
            
            # Clear the scene first
            self.safe_delete_all(context)
            
            # Also delete all collections except the default "Scene Collection"
            for collection in list(bpy.data.collections):
                bpy.data.collections.remove(collection)
                
            # Clear unused data blocks
            for block in bpy.data.meshes:
                if block.users == 0:
                    bpy.data.meshes.remove(block)
            for block in bpy.data.materials:
                if block.users == 0:
                    bpy.data.materials.remove(block)
            for block in bpy.data.textures:
                if block.users == 0:
                    bpy.data.textures.remove(block)
            for block in bpy.data.images:
                if block.users == 0:
                    bpy.data.images.remove(block)
            
            bpy.context.view_layer.update()
            
            # Record existing data
            existing_objs = set(bpy.data.objects)
            existing_meshes = set(bpy.data.meshes)
            existing_collections = set(bpy.data.collections)
            
            if log_path:
                with open(log_path, 'a') as log_file:
                    log_file.write(f"Before import - Objects: {len(existing_objs)}, ")
                    log_file.write(f"Meshes: {len(existing_meshes)}, ")
                    log_file.write(f"Collections: {len(existing_collections)}\n")
            
            # Attempt direct import with create_fragment_obj
            import_success = False
            frag_obj = None
            
            try:
                # Skip _hi.yft.xml files - handle the base version only
                if "_hi.yft.xml" in xml_file:
                    if log_path:
                        with open(log_path, 'a') as log_file:
                            log_file.write("Skipping _hi.yft.xml file - will be handled with base file\n")
                    continue
                
                # Load the YFT XML
                name = os.path.splitext(os.path.basename(xml_file))[0]
                if name.endswith(".yft"):
                    name = name[:-4]
                
                yft_xml = YFT.from_xml_file(xml_file)
                
                # Create the fragment object
                frag_obj = create_fragment_obj(yft_xml, xml_file, name)
                
                if frag_obj:
                    import_success = True
                    if log_path:
                        with open(log_path, 'a') as log_file:
                            log_file.write(f"Direct import succeeded, created object: {frag_obj.name}\n")
                else:
                    if log_path:
                        with open(log_path, 'a') as log_file:
                            log_file.write("Direct import returned None object\n")
                
                # Wait to ensure import completes
                if self.wait_time > 0:
                    if log_path:
                        with open(log_path, 'a') as log_file:
                            log_file.write(f"Waiting {self.wait_time} seconds for import to complete...\n")
                    time.sleep(self.wait_time)
                
                bpy.context.view_layer.update()
            
            except Exception as e:
                error_msg = f"Failed to import {xml_file}: {str(e)}"
                self.report({'ERROR'}, error_msg)
                if log_path:
                    with open(log_path, 'a') as log_file:
                        log_file.write(f"ERROR: {error_msg}\n")
                        log_file.write("TRACE: " + traceback.format_exc() + "\n")
                error_count += 1
                continue
            
            # Record what's new
            new_objs = [obj for obj in bpy.data.objects if obj not in existing_objs]
            new_meshes = [mesh for mesh in bpy.data.meshes if mesh not in existing_meshes]
            new_collections = [coll for coll in bpy.data.collections if coll not in existing_collections]
            
            if log_path:
                with open(log_path, 'a') as log_file:
                    log_file.write(f"After import - Objects: {len(bpy.data.objects)}, ")
                    log_file.write(f"Meshes: {len(bpy.data.meshes)}, ")
                    log_file.write(f"Collections: {len(bpy.data.collections)}\n")
                    log_file.write(f"New objects: {len(new_objs)}, ")
                    log_file.write(f"New meshes: {len(new_meshes)}, ")
                    log_file.write(f"New collections: {len(new_collections)}\n\n")
                    
                    # Log scene objects
                    log_file.write("Objects in scene:\n")
                    for obj in bpy.context.scene.objects:
                        log_file.write(f"  - {obj.name} (Type: {obj.type})\n")
                    
                    # Log collections
                    log_file.write("\nCollections:\n")
                    for coll in bpy.data.collections:
                        log_file.write(f"  - {coll.name}: {len(coll.objects)} objects\n")
                        for obj in coll.objects:
                            log_file.write(f"    * {obj.name} (Type: {obj.type})\n")
                    
                    # Mesh objects check
                    mesh_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']
                    log_file.write(f"\nMesh objects in data: {len(mesh_objs)}\n")
                    for obj in mesh_objs:
                        log_file.write(f"  - {obj.name} (Vertices: {len(obj.data.vertices)})\n")
            
            self.report({'INFO'}, f"After import of {xml_file}: {len(new_objs)} new objects detected.")
            
            # If we have new meshes but no objects, create objects for them
            if not new_objs and new_meshes:
                if log_path:
                    with open(log_path, 'a') as log_file:
                        log_file.write("No new objects but found new meshes. Creating objects for them...\n")
                for mesh in new_meshes:
                    obj = bpy.data.objects.new(f"{base_filename}_{mesh.name}", mesh)
                    bpy.context.scene.collection.objects.link(obj)
                    new_objs.append(obj)
            
            # Make sure objects in new collections are accounted for
            for coll in new_collections:
                for obj in coll.objects:
                    if obj not in new_objs:
                        new_objs.append(obj)
            
            if not new_objs:
                self.report({'WARNING'}, f"No objects imported from {xml_file}. Skipping export.")
                if log_path:
                    with open(log_path, 'a') as log_file:
                        log_file.write("WARNING: No objects imported. Skipping export.\n")
                error_count += 1
                continue
            
            # Make sure all objects are visible and selectable
            for obj in new_objs:
                obj.hide_set(False)
                obj.hide_viewport = False
                obj.hide_render = False
            
            # Select all new objects for export
            for obj in bpy.context.scene.objects:
                obj.select_set(obj in new_objs)
            
            # Set an active object
            if new_objs:
                context.view_layer.objects.active = new_objs[0]
            
            try:
                if log_path:
                    with open(log_path, 'a') as log_file:
                        log_file.write(f"Exporting to: {output_fbx}\n")
                        log_file.write(f"Selected objects: {len([obj for obj in bpy.context.scene.objects if obj.select_get()])}\n")
                
                # Export to FBX
                bpy.ops.export_scene.fbx(
                    filepath=output_fbx,
                    use_selection=True,
                    use_mesh_modifiers=False,
                    path_mode='COPY',
                    embed_textures=True,  # Attempt to embed textures
                    mesh_smooth_type='FACE'
                )
                
                self.report({'INFO'}, f"Converted {xml_file} to {output_fbx}")
                success_count += 1
                if log_path:
                    with open(log_path, 'a') as log_file:
                        log_file.write(f"SUCCESS: Exported to {output_fbx}\n")
            
            except Exception as e:
                error_msg = f"Failed to export {output_fbx}: {str(e)}"
                self.report({'ERROR'}, error_msg)
                if log_path:
                    with open(log_path, 'a') as log_file:
                        log_file.write(f"ERROR: {error_msg}\n")
                        log_file.write("TRACE: " + traceback.format_exc() + "\n")
                error_count += 1
        
        # Log summary
        if log_path:
            with open(log_path, 'a') as log_file:
                log_file.write(f"\n\nConversion Summary:\n")
                log_file.write(f"Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                log_file.write(f"Total files processed: {len(xml_files)}\n")
                log_file.write(f"Successful conversions: {success_count}\n")
                log_file.write(f"Failed conversions: {error_count}\n")
        
        self.report({'INFO'}, f"Batch conversion completed! {success_count} files converted, {error_count} failed.")
        return {'FINISHED'}


class ExportGLB(bpy.types.Operator):
    """Export model as GLB"""
    bl_idname = "jarvis.export_glb"
    bl_label = "Export GLB"

    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No export file path provided!")
            return {'CANCELLED'}

        try:
            bpy.ops.export_scene.gltf(filepath=self.filepath, export_format='GLB')
            self.report({'INFO'}, f"Successfully exported GLB to {self.filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export GLB: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

class SimplifyTransparency(bpy.types.Operator):
    """Fix transparency issues in materials by breaking transparency links"""
    bl_idname = "jarvis.simplify_transparency"
    bl_label = "Simplify Transparency"

    def execute(self, context):
        for material in bpy.data.materials:
            if material.use_nodes:
                node_tree = material.node_tree
                for node in node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        # Find the Alpha input
                        alpha_input = node.inputs['Alpha']

                        # Break any existing links to the Alpha input
                        for link in list(node_tree.links):
                            if link.to_socket == alpha_input:
                                node_tree.links.remove(link)

                        # Set Alpha to full opacity
                        alpha_input.default_value = 1.0
                        self.report({'INFO'}, f"Fixed transparency for {material.name}")

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
