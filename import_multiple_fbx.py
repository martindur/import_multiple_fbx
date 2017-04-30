# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Import Multiple FBXs",
    "author": "Martin Durhuus",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Multiple FBX IO meshes, UV's, vertex colors, materials, textures, cameras, lamps and actions",
    "warning": "Early version, might give some errors",
    "category": "Import-Export",
}

import bpy
import os

from bpy_extras.io_utils import ImportHelper

from bpy.props import (
        StringProperty,
        BoolProperty,
        FloatProperty,
        EnumProperty,
        CollectionProperty,
        )

class ImportMultipleFbx(bpy.types.Operator, ImportHelper):
    """Load multiple FBX files"""
    bl_idname = "import_scene.multiple_fbx"
    bl_label = "Import FBXs"
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = ".fbx"
    filter_glob = StringProperty(default="*.fbx", options={'HIDDEN'})

    files = CollectionProperty(type=bpy.types.PropertyGroup)

    use_manual_orientation = BoolProperty(
            name="Manual Orientation",
            description="Specify orientation and scale, instead of using embedded data in FBX file",
            default=False,
            )

    ui_tab = EnumProperty(
            items=(('MAIN', "Main", "Main basic settings"),
                   ('ARMATURE', "Armatures", "Armature-related settings"),
                  ),
            name="ui_tab",
            description="Import options categories",
            )
    
    axis_forward = EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='Z',
            )

    axis_up = EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Y',
            )

    global_scale = FloatProperty(
            name="Scale",
            description="",
            min=0.0, max=1000.0,
            soft_min=0.0, soft_max=1000.0,
            default=1.0,
            )

    bake_space_transform = BoolProperty(
            name="!EXPERIMENTAL! Apply Transform",
            description="Bake space transform into object data, avoids getting unwanted rotations to objects when "
                        "target space is not aligned with Blender's space "
                        "(WARNING! experimental option, use at own risks, known broken with armatures/animations)",
            default=False,
            )

    use_custom_normals = BoolProperty(
            name="Import Normals",
            description="Import custom normals, if available (otherwise Blender will recompute them)",
            default=True,
            )

    use_anim = BoolProperty(
            name="Import Animation",
            description="Import FBX animation",
            default=True,
            )
    
    anim_offset = FloatProperty(
            name="Animation Offset",
            description="Offset to apply to animation during import, in frames",
            default=1.0,
            )

    use_custom_props = BoolProperty(
            name="Import User Properties",
            description="Import user properties as custom properties",
            default=True,
            )

    enum_as_string = BoolProperty(
            name="Import Enums As Strings",
            description="Store enumeration values as strings",
            default=True,
            )

    use_image_search = BoolProperty(
            name="Image Search",
            description="Search subdirs for any associated images(WARNING: may be slow)",
            default=True,
            )

    decal_offset = FloatProperty(
            name="Decal Offset",
            min=0.0, max=1.0,
            default=0.0,
            )

    use_prepost_rot = BoolProperty(
            name="Use Pre/Post Rotation",
            description="Use pre/post rotation from FBX transform (you may have to disable that in some cases)",
            default=True,
            )

    ignore_leaf_bones = BoolProperty(
            name="Ignore Leaf Bones",
            description="Ignore the last bone at the end of each chain (used to mark the length of the previous bone)",
            default=False,
            )

    force_connect_children = BoolProperty(
            name="Force Connect Children",
            description="Force connection of children bones to their parent, even if their computed head/tail",
            default=False,
            )

    automatic_bone_orientation = BoolProperty(
            name="Automatic Bone Orientation",
            description="Try to aign the major bone axis with the bone children",
            default=False,
            )

    primary_bone_axis = EnumProperty(
            name="Primary Bone Axis",
            items=(('X', "X Axis", ""),
                   ('Y', "Y Axis", ""),
                   ('Z', "Z Axis", ""),
                   ('-X', "-X Axis", ""),
                   ('-Y', "-Y Axis", ""),
                   ('-Z', "-Z Axis", ""),
                   ),
            default='Y',
            )


    secondary_bone_axis = EnumProperty(
            name="Secondary Bone Axis",
            items=(('X', "X Axis", ""),
                   ('Y', "Y Axis", ""),
                   ('Z', "Z Axis", ""),
                   ('-X', "-X Axis", ""),
                   ('-Y', "-Y Axis", ""),
                   ('-Z', "-Z Axis", ""),
                   ),
            default='X',
            )

    use_global_position = BoolProperty(
            name="Import Global Position",
            description="Use object's position in world space instead of world zero",
            default=False,
            )

    use_global_rotation = BoolProperty(
            name="Import Global Rotation",
            description="Use object's rotation in world space instead of zero",
            default=False,
            )

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "ui_tab", expand=True)
        if self.ui_tab == 'MAIN':
            layout.prop(self, "use_global_position"),
            layout.prop(self, "use_global_rotation"),
            layout.prop(self, "use_manual_orientation"),
            sub = layout.column()
            sub.enabled = self.use_manual_orientation
            sub.prop(self, "axis_forward")
            sub.prop(self, "axis_up")
            layout.prop(self, "global_scale")
            layout.prop(self, "bake_space_transform")

            layout.prop(self, "use_custom_normals")

            layout.prop(self, "use_anim")
            layout.prop(self, "anim_offset")

            layout.prop(self, "use_custom_props")
            sub = layout.row()
            sub.enabled = self.use_custom_props
            sub.prop(self, "enum_as_string")

            layout.prop(self, "use_image_search")
            layout.prop(self, "decal_offset")

            layout.prop(self, "use_prepost_rot")
        elif self.ui_tab == 'ARMATURE':
            layout.prop(self, "ignore_leaf_bones")
            layout.prop(self, "force_connect_children"),
            layout.prop(self, "automatic_bone_orientation"),
            sub = layout.column()
            sub.enabled = not self.automatic_bone_orientation
            sub.prop(self, "primary_bone_axis")
            sub.prop(self, "secondary_bone_axis")

    def execute(self, context):
        
        folder = (os.path.dirname(self.filepath))

        for j, i in enumerate(self.files):
                
                file_path = (os.path.join(folder, i.name))

                bpy.ops.import_scene.fbx(filepath = file_path,
                                        axis_forward = self.axis_forward,
                                        axis_up = self.axis_up,
                                        filter_glob = self.filter_glob,
                                        use_manual_orientation = self.use_manual_orientation,
                                        global_scale = self.global_scale,
                                        bake_space_transform = self.bake_space_transform,
                                        use_custom_normals = self.use_custom_normals,
                                        use_image_search = self.use_image_search,
                                        decal_offset = self.decal_offset,
                                        use_anim = self.use_anim,
                                        anim_offset = self.anim_offset,
                                        use_custom_props = self.use_custom_props,
                                        use_custom_props_enum_as_string = self.enum_as_string,
                                        ignore_leaf_bones = self.ignore_leaf_bones,
                                        force_connect_children = self.force_connect_children,
                                        automatic_bone_orientation = self.automatic_bone_orientation,
                                        primary_bone_axis = self.primary_bone_axis,
                                        secondary_bone_axis = self.secondary_bone_axis,
                                        use_prepost_rot = self.use_prepost_rot)
                if not self.use_global_position:
                        bpy.ops.object.location_clear()
                if not self.use_global_rotation:
                        bpy.ops.object.rotation_clear()
                bpy.ops.transform.resize(value=(self.global_scale, self.global_scale, self.global_scale), constraint_axis=(False, False, False))
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportMultipleFbx.bl_idname, text="Multiple FBXs (.fbx)")
        


def register():
    bpy.utils.register_class(ImportMultipleFbx)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    
    
def unregister():
    bpy.utils.unregister_class(ImportMultipleFbx)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    
if __name__ == "__main__":
    register()