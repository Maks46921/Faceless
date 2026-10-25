import bpy,mathutils
for n in("chair","lamp","table"):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=f"D:/Faceless/models/{n}_noir.glb")
    for o in bpy.data.objects:
        if o.type=='MESH':
            print("OBJ",n,o.name,[ (m.name,tuple(round(x,2) for x in m.node_tree.nodes['Principled BSDF'].inputs[0].default_value[:3]),round(m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value,1)) for m in o.data.materials])
            vs=[o.matrix_world@v.co for v in o.data.vertices]
            print("BB",n,[(round(min(v[i] for v in vs),3),round(max(v[i] for v in vs),3)) for i in range(3)])
