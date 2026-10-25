"""Faceless grey mannequins on the same 40-bone skeleton as human_noir_v4 (poses/animations transfer 1:1).
Run: MQ_KIND=male|female|child D:\Cosmoteer\blender.exe -b -P build_mannequin.py   -> models/mannequin_<kind>.glb"""
import os, math
exec(open("D:/Faceless/models/src/lib_props.py", encoding="utf-8").read())
KIND = os.environ.get("MQ_KIND", "male")
cfg = dict(male=dict(h=1.80, sh=1.0, hip=1.0, bust=0), female=dict(h=1.68, sh=.86, hip=1.12, bust=1), child=dict(h=1.22, sh=.9, hip=.95, bust=0))[KIND]
os.environ["TARGET_H"] = str(cfg["h"]); os.environ["MANN"] = "1"
os.environ["OUTGLB"] = f"D:/Faceless/models/mannequin_{KIND}.glb"; os.environ["OUTBLEND"] = f"D:/Faceless/models/src/mannequin_{KIND}.blend"
fresh(); palette()
G = MATS["mannequin_gray"]; objs = []
def chain(name, pts, edges, sub=2):
    me = bpy.data.meshes.new(name); me.from_pydata([p[:3] for p in pts], edges, [])
    o = bpy.data.objects.new(name, me); collection().objects.link(o); set_active(o)
    o.modifiers.new("skin", "SKIN"); sv = me.skin_vertices[0].data
    for i, p in enumerate(pts): sv[i].radius = (p[3], p[4])
    adj = {i: [] for i in range(len(pts))}
    for a, b in edges: adj[a].append(b); adj[b].append(a)
    seen = set()
    for i in range(len(pts)):
        if i in seen: continue
        sv[i].use_root = True; st = [i]
        while st:
            k = st.pop()
            if k in seen: continue
            seen.add(k); st += adj[k]
    o.modifiers.new("sub", "SUBSURF").levels = sub
    bpy.ops.object.modifier_apply(modifier="skin"); bpy.ops.object.modifier_apply(modifier="sub")
    me.materials.append(G)
    for p in o.data.polygons: p.use_smooth = True
    objs.append(o); return o
sh, hp = cfg["sh"], cfg["hip"]
# body: one skin chain (torso + arms + legs + neck) so all joints are smooth
P_ = [(0, 0, .93, .125 * hp, .09), (0, 0, 1.06, .105, .08), (0, 0, 1.27, .15 * sh, .095), (0, 0, 1.39, .16 * sh, .09), (0, 0, 1.47, .06, .06), (0, 0, 1.6, .045, .05),      # 0-5 spine up to neck
      (-.18 * sh, 0, 1.43, .05, .05), (-.31 * sh, 0, 1.2, .04, .04), (-.365 * sh, .04, .93, .033, .033),                                                                    # 6-8 arm R(pre-x<0)
      (.18 * sh, 0, 1.43, .05, .05), (.31 * sh, 0, 1.2, .04, .04), (.365 * sh, .04, .93, .033, .033),                                                                       # 9-11 arm L
      (-.09 * hp, 0, .88, .09 * hp, .085), (-.095, 0, .5, .062, .06), (-.1, 0, .09, .042, .042), (-.1, .12, .045, .038, .034),                                                # 12-15 leg
      (.09 * hp, 0, .88, .09 * hp, .085), (.095, 0, .5, .062, .06), (.1, 0, .09, .042, .042), (.1, .12, .045, .038, .034)]                                                   # 16-19 leg
E_ = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (3, 6), (6, 7), (7, 8), (3, 9), (9, 10), (10, 11), (0, 12), (12, 13), (13, 14), (14, 15), (0, 16), (16, 17), (17, 18), (18, 19)]
body = chain("mq_body", P_, E_, 2)
# hands: palm + 4 fingers merged + thumb (same joint positions as the human hands)
for sx in (-1, 1):
    hx = sx * .372 * sh
    chain("mq_hand", [(hx, .048, .975, .04, .03), (hx, .058, .86, .034, .024), (hx, .06, .79, .026, .02), (hx + sx * .008, .095, .9, .014, .014), (hx + sx * .012, .112, .855, .012, .012)], [(0, 1), (1, 2), (0, 3), (3, 4)], 1)
# head: smooth egg (no face)
hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=24, v_segments=16, radius=.1)
for v in hb.verts:
    v.co.x *= .82; v.co.y *= .92; v.co.z *= 1.17
    if v.co.z < 0: s_ = 1 + v.co.z * 1.4; v.co.x *= s_; v.co.y *= (1 + v.co.z * .7)
ho = mesh_obj("head", hb, G, (0, .005, 1.67)); objs.append(ho)
ho.vertex_groups.new(name="f_head").add(list(range(len(ho.data.vertices))), 1.0, 'REPLACE')
# plinth-less feet (shoe-like blocks for readability)
for sx in (-1, 1): objs.append(box((.085, .24, .035), G, loc=(sx * .1, .05, .018), bev=.012, name="foot_block", seg=3))
exec(compile(open("D:/Faceless/models/src/build_human_v4_rig.py", encoding="utf-8").read(), "v4_rig", "exec"), globals())
