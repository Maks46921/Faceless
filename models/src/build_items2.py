"""P2 hand/ground items: pass card, ID booklet, documents folder, key ring, notebook, portable radio, briefcase, videotape.
Run: D:\Cosmoteer\blender.exe -b -P D:\Faceless\models\src\build_items2.py"""
_src = open("D:/Faceless/models/src/build_items.py", encoding="utf-8").read()
exec(_src[:_src.index("# ---------------- knife (kitchen)")])
def extra_mats():
    mat("card_white", (.55, .55, .5), .5); mat("card_blue", (.05, .12, .28), .5); mat("photo_gray", (.25, .25, .27), .7); mat("red_cloth", (.28, .02, .02), .8)
    mat("paper", (.62, .6, .55), .9); mat("cardboard", (.38, .28, .16), .9); mat("brass", (.55, .4, .12), .4, .8); mat("notebook_blue", (.08, .12, .2), .8)
    mat("radio_body", (.18, .17, .13), .6); mat("radio_dial", (.5, .45, .3), .4); mat("leather_tan", (.2, .11, .05), .6); mat("tape_black", (.015, .015, .02), .5)
_orig_palette = palette
def palette():
    r = _orig_palette(); extra_mats(); return r

def pass_card():
    P = []
    P.append(box((.0856, .0008, .054), MATS["card_white"], loc=(0, 0, 0), bev=.0008, seg=1, name="card"))
    P.append(box((.02, .0004, .024), MATS["photo_gray"], loc=(-.026, -.0005, .003), bev=0, name="photo"))
    P.append(box((.0856, .0004, .01), MATS["card_blue"], loc=(0, -.0005, .022), bev=0, name="stripe"))
    P.append(box((.012, .0004, .003), MATS["black_paint"] if "black_paint" in MATS else MATS["rubber"], loc=(.018, -.0005, -.004), bev=0, name="line"))
    return P
def id_booklet():
    P = []
    P.append(box((.098, .009, .068), MATS["red_cloth"], loc=(0, 0, 0), bev=.002, seg=2, name="cover"))
    P.append(box((.093, .006, .064), MATS["paper"], loc=(.002, 0, 0), bev=0, name="pages"))
    P.append(cyl(.012, .0008, MATS["brass"], loc=(0, -.0049, .008), seg=12, rot=(math.pi / 2, 0, 0), name="emblem"))
    P.append(box((.05, .0006, .008), MATS["brass"], loc=(0, -.0049, -.016), bev=0, seg=1, name="title"))
    return P
def folder_docs():
    P = []
    P.append(box((.31, .026, .222), MATS["cardboard"], loc=(0, 0, 0), bev=.003, seg=1, name="folder"))
    P.append(box((.29, .02, .21), MATS["paper"], loc=(.004, .002, .004), bev=0, name="papers"))
    P.append(box((.22, .0012, .09), MATS["paper"], loc=(.03, -.015, .13), bev=0, rot=(0, .1, 0), name="loose_sheet"))
    P.append(box((.29, .004, .02), MATS["black_paint"] if "black_paint" in MATS else MATS["rubber"], loc=(0, -.014, -.05), bev=0, seg=1, name="tie"))
    return P
def keys_ring():
    P = []
    P.append(lathe([(.017, .0), (.0185, .0015), (.017, .003), (.0155, .0015)], MATS["steel"], loc=(0, 0, .0), seg=14, name="ring", rot=(math.pi / 2, 0, 0)))
    for k, (ln, mm) in enumerate(((.06, "steel"), (.052, "brass"), (.045, "steel"))):
        ang = (k - 1) * .5
        o1 = box((.012, .002, ln), MATS[mm], loc=(0, 0, -ln / 2 - .008), bev=.0006, seg=1, name="key_blade")
        o2 = cyl(.011, .002, MATS[mm], loc=(0, 0, .002), seg=10, rot=(math.pi / 2, 0, 0), name="key_head")
        o3 = box((.008, .002, .006), MATS[mm], loc=(.006, 0, -ln - .004), bev=0, seg=1, name="key_teeth")
        for o in (o1, o2, o3): o.rotation_euler[1] = ang + o.rotation_euler[1]
        P += [o1, o2, o3]
    return P
def notebook():
    P = []
    P.append(box((.1, .012, .14), MATS["notebook_blue"], loc=(0, 0, 0), bev=.002, seg=1, name="cover"))
    P.append(box((.094, .008, .134), MATS["paper"], loc=(.002, 0, 0), bev=0, name="pages"))
    for i in range(8): P.append(cyl(.0035, .016, MATS["steel"], loc=(-.04 + i * .0115, 0, .072), seg=6, rot=(math.pi / 2, 0, 0), name="spiral"))
    P.append(box((.01, .005, .1), MATS["wood"], loc=(.04, -.009, 0), bev=.001, seg=1, name="pencil"))
    return P
def radio():
    P = []
    P.append(box((.22, .08, .13), MATS["radio_body"], loc=(0, 0, .065), bev=.008, seg=2, name="body"))
    for i in range(7): P.append(box((.085, .002, .004), MATS["steel_dark"], loc=(-.05, -.0405, .035 + i * .012), bev=0, seg=1, name="grille"))
    P.append(box((.07, .002, .04), MATS["radio_dial"], loc=(.055, -.0405, .09), bev=0, seg=1, name="dial"))
    P.append(box((.062, .0016, .002), MATS["black_paint"] if "black_paint" in MATS else MATS["rubber"], loc=(.055, -.0415, .09), bev=0, seg=1, name="needle"))
    for x in (.035, .08, .12): P.append(cyl(.011, .012, MATS["plastic_black"], loc=(x, -.045, .04), seg=10, rot=(math.pi / 2, 0, 0), name="knob"))
    P.append(box((.14, .015, .018), MATS["plastic_black"], loc=(0, 0, .14), bev=.005, seg=2, name="handle"))
    a = tube_pts = None
    o = cyl(.003, .32, MATS["steel"], loc=(.095, .03, .27), seg=6, rot=(-.5, 0, .0), name="antenna"); P.append(o)
    P.append(sphere(.006, MATS["steel"], loc=(.095, .107, .41), seg=6, rings=4, name="antenna_tip"))
    return P
def briefcase():
    P = []
    P.append(box((.46, .11, .31), MATS["leather_tan"], loc=(0, 0, 0), bev=.012, seg=3, name="body"))
    P.append(box((.46, .006, .012), MATS["leather"], loc=(0, 0, .0), bev=0, seg=1, name="seam"))
    P.append(box((.12, .03, .03), MATS["leather"], loc=(0, 0, .17), bev=.01, seg=2, name="handle_grip"))
    for sx in (-.05, .05): P.append(box((.012, .02, .035), MATS["leather"], loc=(sx, 0, .15), bev=.003, seg=1, name="handle_post"))
    for sx in (-.15, .15):
        P.append(box((.04, .012, .035), MATS["brass"], loc=(sx, -.057, .1), bev=.003, seg=1, name="latch"))
        P.append(box((.012, .014, .012), MATS["steel_dark"], loc=(sx, -.062, .1), bev=0, seg=1, name="latch_lock"))
    for sx in (-1, 1):
        for sz in (-1, 1): P.append(box((.03, .114, .03), MATS["brass"], loc=(sx * .215, 0, sz * .14), bev=.004, seg=1, name="corner"))
    return P
def videotape():
    P = []
    P.append(box((.187, .025, .103), MATS["tape_black"], loc=(0, 0, 0), bev=.002, seg=1, name="shell"))
    P.append(box((.16, .0008, .042), MATS["paper"], loc=(0, -.0128, -.018), bev=0, seg=1, name="label"))
    P.append(box((.09, .0006, .006), MATS["black_paint"] if "black_paint" in MATS else MATS["rubber"], loc=(0, -.0132, -.012), bev=0, seg=1, name="label_line"))
    for sx in (-.036, .036): P.append(cyl(.015, .001, MATS["glass"], loc=(sx, -.0128, .025), seg=14, rot=(math.pi / 2, 0, 0), name="reel_window"))
    P.append(box((.14, .02, .008), MATS["steel_dark"], loc=(0, 0, -.052), bev=0, seg=1, name="front_flap"))
    return P

build_item("pass_card", pass_card, ground_rot=(math.pi / 2, 0, 0), ground_yaw=.4)
build_item("id_booklet", id_booklet, ground_rot=(math.pi / 2, 0, 0), ground_yaw=-.5)
build_item("folder_docs", folder_docs, ground_rot=(math.pi / 2, 0, 0), ground_yaw=.2)
build_item("keys_ring", keys_ring, ground_rot=(math.pi / 2, 0, 0), ground_yaw=.9)
build_item("notebook", notebook, ground_rot=(math.pi / 2, 0, 0), ground_yaw=.3)
build_item("radio", radio, ground_rot=(0, 0, 0), ground_yaw=0)
build_item("briefcase", briefcase, ground_rot=(0, 0, 0), ground_yaw=0)
build_item("videotape", videotape, ground_rot=(math.pi / 2, 0, 0), ground_yaw=.6)
