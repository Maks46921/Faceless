"""blender -b -P contact_sheet.py -- out.png cols cell_px img1 img2 ... ; tiles images into a grid (no PIL needed)."""
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index("--") + 1:]; out, cols, cell = a[0], int(a[1]), int(a[2]); files = a[3:]
rows = (len(files) + cols - 1) // cols
canvas = np.full((rows * cell, cols * cell, 4), [.1, .1, .12, 1], np.float32)
for i, f in enumerate(files):
    im = bpy.data.images.load(f); w, h = im.size
    k = cell / max(w, h); im.scale(max(1, int(w * k)), max(1, int(h * k))); w, h = im.size
    px = np.array(im.pixels[:], np.float32).reshape(h, w, 4)
    r, c = divmod(i, cols); y = (rows - 1 - r) * cell + (cell - h) // 2; x = c * cell + (cell - w) // 2
    canvas[y:y + h, x:x + w] = px
im = bpy.data.images.new("sheet", cols * cell, rows * cell); im.pixels = canvas.ravel(); im.filepath_raw = out; im.file_format = 'PNG'; im.save()
print("OK", out, cols * cell, rows * cell)
