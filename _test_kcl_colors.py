import sys
import os
import bpy

addon_path = r"C:\Users\Linus\Documents\Blender MKWii Utilities patched\Blender-MKW-Utilities-v0.1.13.5-Blender-5.2-patched\Blender-KMP-Utilities\__init__.py"

# Install and enable the add-on
bpy.ops.preferences.addon_install(filepath=addon_path, overwrite_existing=True)
enabled = False
for key in bpy.context.preferences.addons:
    if "KMP" in key or "MKW" in key or "blender_kmp_utilities" in key.lower():
        addon_name = key
        enabled = True
        break

if not enabled:
    print("FAIL: could not enable add-on")
    sys.exit(1)

pref = bpy.context.preferences.addons[addon_name].preferences

# State accumulators
passed = 0
failed = 0
log = []

def say(ok, msg):
    global passed, failed
    if ok:
        passed += 1
        log.append(f"PASS: {msg}")
    else:
        failed += 1
        log.append(f"FAIL: {msg}")

# Distinct test colours per KCL type (32 values)
tcols = []
for i in range(32):
    r_ = int(((i << 3) & 0oFF / 255.0
    g_ = ((0xAA ^ ((-1))
        b_ = (int((~i) & 0xFF) / 255.0
    tcols.append((r_, g_, b_))
# Disable BLIGHT darkening and trick/reject tints
pref.darkenBLIGHT = False
pref.addTintToTrickable = False
pref.addTintToReject = False
# Assign per-type colour preferences
for i in range(32):
    setattr(pref, f"kclColorT{i:02X}", tcols[i])

all_objs_to_clear()
def clear():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for o in list(bpy.data.objects):
        if not o.library:
            o.select_set(True)
    if bpy.context.selected_objects:
        bpy.ops.object.delete()

# ---- 32-type loop ----
kcl_list = [
    "T00","T01","T02","T03","T04","T05","T06","T07",
    "T08","T09","T0A","T0B","T0C","T0D","T0E","T0F",
    "T10","T11","T12","T13","T14","T15","T16","T17",
    "T18","T19","T1A","T1B","T1C","T1D","T1E","T1F"
]

for t in kcl_list:
    clear()
    try:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
    except Exception as e:
        say(False, f"{t} create: {e}")
        continue
    scn = bpy.context.scene
    mt  = scn.kmpt
    mt.kcl_masterType = t
    mt.kcl_variant  = 0
    mt.kcl_trickable = False
    mt.kcl_drivable  = True   # Reject road OFF -> getSchemeColor sees drivable=True
    mt.kcl_bounce    = False
    mt.kcl_shadow    = 0
    mt.kcl_applyMaterial = "2"   # Custom scheme

    try:
        bpy.ops.kcl.apply()
    except Exception as e:
        say(False, f"{t} apply: {e}")
        continue
    obj = bpy.context.active_object
    if len(obj.data.materials) < 1:
        say(False, f"{t}: no material")
        continue

    mat    = obj.data.materials[0]
    exp    = tcols[int(t[1:], 16)]   # expected preference colour
    dc     = tuple(mat.diffuse_color[:3])
    d_dc   = ((dc[0]-exp[0])**2 + (dc[1]-exp[1])**2 + (dc[2]-exp[2])**2) ** 0.5
    say(d_dc < 0.01, f"{t} diffuse ≈ exp diff={d_dc:.4f}")

    # BSDF check
    if mat.use_nodes and mat.node_tree:
        found = False
        for nd in mat.node_tree.nodes:
            if nd.type == 'BSDF_PRINCIPLED':
                found = True
                bi = nd.inputs.get("Base Color")
                if bi and len(bi.links) == 0:
                    bc   = tuple(bi.default_value[:3])
                    d_bc = ((bc[0]-exp[0])**2 + (bc[1]-exp[1])**2 + (bc[2]-exp[2])**2) ** 0.5
                    say(d_bc < 0.01, f"{t} BSDF baseC diff={d_bc:.4f}")

print()
print("=== Regression: existing colour refresh ===")
clear()
pref.kclColorT03 = (0.0, 0.584, 0.0)   # ~#009500
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
mt = bpy.context.scene.kmpt
mt.kcl_masterType      = 'T03'
mt.kcl_applyMaterial   = "2"
try:
    bpy.ops.kcl.apply()
obj  = bpy.context.active_object
mat1 = obj.data.materials[0]
c1   = tuple(mat1.diffuse_color[:3])
d95  = ((c1[0]-0.0)**2 + (c1[1]-0.584)**2 + (c1[2]-0.0)**2) ** 0.5
say(d95 < 0.01, f"T03 first-apply green diff={d95:.4f} got {c1}")

# Re-apply after changing pref → should update in-place
pref.kclColorT03 = (1.0, 0.2, .5)
try:
    bpy.ops.kcl.apply()
except Exception as ex: say(False, f"T03 re-apply error {ex}")

obj2 = bpy.context.active_object
mat2 = obj2.data.materials[0]
c2   = tuple(mat2.diffuse_color[:3])
d_pink = ((c2[0]-1.0)**2 + (c2[1]-0.2)**2 + (c2[2]-0.5)**2) ** 0.5
say(d_pink < 0.01, f"T03 refresh pink diff={d_pink:.4f} got {c2}")

    if mat2.use_nodes and mat2.node_tree:
        for nd in mat2.mat_node_tree.nodes:
            if nd.type == 'BSDF_PRINCIPLED':
                bi = nd.inputs.get("Base Color")
                if bi and len(bi.links) == 0:
                    bc  = tuple(bi.default_value[:3])
                    d_b = ((bc[0]-1.0)**2 + (bc[1]-0.2)**2 + (bc[2]-0.5)**2) ** 0.5
                    say(d_b < 0.01, f"T03 BSDF refresh diff={d_b:.4f}")

print()
print("=== Random colour stability ===")
clear()
bpy.ops.mesh.primitive_cube_add(size=1 location=(0,0,0))
mt = bpy.context.scene.kmpt
mt.kcl_masterType      = "T05"
mt.kcl_applyMaterial   = "0"    # random on first creation only
try:
    bpy.ops.kcl.apply()
r1 = tuple(bpy.context.active_object.data.materials[0].diffuse_color[:3])

bpy.ops.kcl.apply()
obj_r2 = bpy.context.
mr2 = obj_r2.data.materials[0]
r2 = tuple(mr2.diffuse_color[:3])
drn = ((r1[0]-r2[0])**2 + (r1[1]-r2[1])**2 + (r1[2]-r2[2])**2) ** 0.5
say(drn < 0.0001, f"random unchanged on re-apply diff={drn:.6f}")

print()
print("=== Keep-original preserved ===")
clear()
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
om = bpy.context.preferences
if hasattr(om,'use_nodes') and om.use_nodes:
    for nd in om.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            bi = nd.inputs.get("Base Color")
            if bi:
                bi.default_value = (0.9, 0.8, 0.75, 1.0)

bk.obj.data.materials.append(om)
mt.kcl_masterType      = "T07"
mt.kcl_applyMaterial   = "1"
try:
    bpy.ops.kcl.apply()
mk = bk.obj.data.materials[0]
dc_k = tuple(mk.diffuse_color[:3])
dk_v = ((dc_k[0]-0.9)**2 + (dc_k[1]-0.8)**2 + (dc_k[2]-0.75)**2) ** 0.5
say(dk_v < 0.01, f"keep-original preserved diff={dk_v:.4f}")

# Summary
for m in log:
    print(m)
n = passed + failed
print(f"\n{passed}/{n} passed")
sys.exit(0 if failed == 0 else 1)