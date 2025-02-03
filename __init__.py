# script to make rigify compatible with unity humanoid
# HOWTO: right after generating rig using rigify
#   press armature -> Rigify To Unity Converter -> (Prepare rig for unity) button
bl_info = {
    "name": "Rigify to Unity",
    "category": "Rigging",
    "description": "Change Rigify rig into Mecanim-ready rig for Unity",
    "location": "At the bottom of Rigify rig data/armature tab",
    "blender": (4, 0, 0)
}

import bpy
import re


class UnityMecanim_Panel(bpy.types.Panel):
    bl_label = "Rigify to Unity converter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(self, context):
        return context.object and context.object.type == 'ARMATURE' and "DEF-upper_arm.L.001" in context.object.data.bones

    def draw(self, context):
        self.layout.operator("rig4mec.convert2unity")


class UnityMecanim_Convert2Unity(bpy.types.Operator):
    bl_idname = "rig4mec.convert2unity"
    bl_label = "Prepare rig for unity"

    def execute(self, context):
        ob = context.object

        bpy.ops.object.mode_set(mode='OBJECT')

        def set_use_deform(bone_name, value):
            if bone_name in ob.data.bones:
                ob.data.bones[bone_name].use_deform = value

        set_use_deform('DEF-breast.L', False)
        set_use_deform('DEF-breast.R', False)
        set_use_deform('DEF-pelvis.L', False)
        set_use_deform('DEF-pelvis.R', False)

        bpy.ops.object.mode_set(mode='EDIT')

        def set_parent(child, parent):
            ob.data.edit_bones[child].parent = ob.data.edit_bones[parent]

        set_parent('DEF-shoulder.L', 'DEF-spine.003')
        set_parent('DEF-shoulder.R', 'DEF-spine.003')
        set_parent('DEF-upper_arm.L', 'DEF-shoulder.L')
        set_parent('DEF-upper_arm.R', 'DEF-shoulder.R')
        set_parent('DEF-thigh.L', 'DEF-spine')
        set_parent('DEF-thigh.R', 'DEF-spine')

        def set_tail(bone, target_bone):
            ob.data.edit_bones[bone].tail = ob.data.edit_bones[target_bone].tail

        def set_parent_and_tail(bone, target_bone):
            set_tail(bone, target_bone)
            ob.data.edit_bones[bone].parent = ob.data.edit_bones[target_bone].parent

        set_parent_and_tail('DEF-forearm.L', 'DEF-upper_arm.L.001')
        set_parent_and_tail('DEF-hand.L', 'DEF-forearm.L.001')
        ob.data.edit_bones.remove(ob.data.edit_bones['DEF-upper_arm.L.001'])
        ob.data.edit_bones.remove(ob.data.edit_bones['DEF-forearm.L.001'])

        set_parent_and_tail('DEF-forearm.R', 'DEF-upper_arm.R.001')
        set_parent_and_tail('DEF-hand.R', 'DEF-forearm.R.001')
        ob.data.edit_bones.remove(ob.data.edit_bones['DEF-upper_arm.R.001'])
        ob.data.edit_bones.remove(ob.data.edit_bones['DEF-forearm.R.001'])

        set_parent_and_tail('DEF-shin.L', 'DEF-thigh.L.001')
        set_parent_and_tail('DEF-foot.L', 'DEF-shin.L.001')
        ob.data.edit_bones.remove(ob.data.edit_bones['DEF-thigh.L.001'])
        ob.data.edit_bones.remove(ob.data.edit_bones['DEF-shin.L.001'])

        set_parent_and_tail('DEF-shin.R', 'DEF-thigh.R.001')
        set_parent_and_tail('DEF-foot.R', 'DEF-shin.R.001')
        ob.data.edit_bones.remove(ob.data.edit_bones['DEF-thigh.R.001'])
        ob.data.edit_bones.remove(ob.data.edit_bones['DEF-shin.R.001'])

        def remove_edit_bone(bone_name):
            if bone_name in ob.data.bones:
                ob.data.edit_bones.remove(ob.data.edit_bones[bone_name])

        remove_edit_bone('DEF-pelvis.L')
        remove_edit_bone('DEF-pelvis.R')
        remove_edit_bone('DEF-breast.L')
        remove_edit_bone('DEF-breast.R')

        bpy.ops.object.mode_set(mode='OBJECT')

        namelist = [("DEF-spine.006", "DEF-head"), ("DEF-spine.005", "DEF-neck")]

        for name, newname in namelist:
            pb = ob.pose.bones.get(name)
            if pb is not None:
                pb.name = newname

        self.report({'INFO'}, 'Unity ready rig!')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(UnityMecanim_Panel)
    bpy.utils.register_class(UnityMecanim_Convert2Unity)


def unregister():
    bpy.utils.unregister_class(UnityMecanim_Panel)
    bpy.utils.unregister_class(UnityMecanim_Convert2Unity)