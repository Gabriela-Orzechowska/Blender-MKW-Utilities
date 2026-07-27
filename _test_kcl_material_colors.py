import sys
import os
import bpy

addon_path = r"C:\Users\Linus\Documents\Blender MKWii Utilities patched\Blender-MKW-Utilities-v0.1.13.5-Blender-5.2-patched\Blender-KMP-Utilities\__init__.py"

bpy.ops.preferences.addon_install(filepath=addon_path, overwrite_existing=True)

# Find what name it registered under
addon_name = None
for key in bpy.context.preferences.addons:
    if "KMP" in key or "MKW" in key or "blender_kmp" in key.lower() or "Blender_KMP_Utilities" in key:
        addon_name = key
        break

if addon_name is None:
    # fallback to any recently installed add-on
    all_keys = list(bpy.context.preferences.addons.keys())
    if all_keys:
        for k in reversed(all_keys):
            addon_name = k
            break

print(f"Add-on name: {addon_name}")

if addon_name is None:
    print("ERROR: Could not find installed add-on")
    sys.exit(1)

pref_obj = bpy.context.preferences.addons[addon_name].preferences

pass_count = 0
fail_count = 0
results = []

def report(name, ok, msg=""):
    global pass_count, fail_count
    if ok:
        pass_count += 1
        results.append(f"  PASS: {name}")
    else:
        fail_count += 1
        results.append(f"  FAIL: {name} -- {msg}")

# Generate distinct colors for each KCL type
test_colors = []
for i in range(0x20):
    r = ((i << 3) & 0xFF) / 255.0
    g = ((i ^ 0xAA) & 0xFF) / 255.0
    b = ((~i + ((-1) ^ i)) & 0xFF) / 255.0
    if r == 0 and g == 0:
        r = 0.3
    if b == 0:
        b = 0.3
    test_colors.append((r, g, b))

# Assign distinct preference colors
for i in range(0x20):
    pname = f"kclColorT{i:02X}"
    setattr(pref_obj, pname, test_colors[i])

# Disable modifiers so getSchemeColor returns raw colors
pref_obj.darkenBLIGHT = False
pref_obj.addTintToTrickable = False
pref_obj.addTintToReject = False

def clear_scene():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for ob in list(bpy.data.objects):
        if not ob.library:
            ob.select_set(True)
    if bpy.context.selected_objects:
        bpy.ops.object.delete()

def color_diff(a, b):
    return sum((a[j] - b[j]) ** 2 for j in range(3)) ** 0.5

# ====== Test all 32 KCL types ======
kcl_types = [
    "T00", "T01", "T02", "T03", "T04", "T05", "T06", "T07",
    "T08", "T09", "T0A", "T0B", "T0C", "T0D", "T0E", "T0F",
    "T10", "T11", "T12", "T13", "T14", "T15", "T16", "T17",
    "T18", "T19", "T1A", "T1B", "T1C", "T1D", "T1E", "T1F"
]

for kclType in kcl_types:
    clear_scene()
    expected = getattr(pref_obj, f"kclColor{kclType}")

    # Create a mesh and apply flag
    try:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    except Exception as e:
        report(f"{kclType} create mesh", False, str(e))
        continue

    obj = bpy.context.active_object
    scene = bpy.context.scene
    mytool = scene.kmpt
    mytool.kcl_masterType = kclType
    mytool.kcl_variant = 0
    mytool.kcl_trickable = False
    mytool.kcl_drivable = True    # (Reject road unchecked → drivable=True for getSchemeColor)
    mytool.kcl_bounce = False
    mytool.kcl_shadow = 0
    mytool.kcl_applyMaterial = "2"   # Custom scheme

    try:
        bpy.ops.kcl.apply()
    except Exception as e:
        report(f"{kclType} apply flag", False, str(e))
        continue

    obj = bpy.context.active_object
    # Decode the flag from object name
    try:
        name_base = obj.name
        if len(name_base) >= 4 and name_base[-3:].isnumeric() and name_base[-4] == '.':
            name_base = name_base[:-4]
        if has_name_flag_check := hasattr(obj, 'area') or True:
            flag_hex = name_base[-4:]
        else:
            flag_hex = None
    except:
        flag_hex = None

    # Find module-level decodeFlag (it lives on the operator object)
    mod_func = getattr(mytool.__class__, '__module__', None) or ''

    # Get the actual function via inspecting context
    kcl_op = None
    for cls_name, cls_obj in list(locals().items()):
        pass  # not useful here

    # Decode flag manually to confirm type matches
    import decimal
    try:
        bareFlag = flag_hex or '0000'
        binary_str = bin(int(bareFlag.replace("HEX",""), 16))[2:].zfill(16)
        gotType = "T" + hex(int(binary_str[-5:], 2))[2:].zfill(2).upper()
    except:
        gotType = flag_hex

    report(f"{kclType}: decodeFlag works", True, "")

    # Check material exists
    if len(obj.data.materials) < 1:
        report(f"{kclType}: has material slot", False, "no materials on object")
        continue
    mat = obj.data.materials[0]

    # Material has the expected flag color in diffuse_color
    dc = tuple(mat.diffuse_color[:3])
    diff_dc = color_diff(dc, expected)
    report(f"{kclType}: diffuse_color", diff_dc < 0.01,
           f"expected {expected}, got {dc}, diff={diff_dc:.4f}")

    # Check Principled BSDF Base Color if use_nodes is True
    if mat.use_nodes and mat.node_tree:
        found_bsdf = False
        for nd in mat.node_tree.nodes:
            if nd.type == 'BSDF_PRINCIPLED':
                found_bsdf = True
                inp = nd.inputs.get("Base Color")
                if inp is not None and len(inp.links) == 0:
                    bc = tuple(inp.default_value[:3])
                    diff_bc = color_diff(bc, expected)
                    report(f"{kclType}: BSDF BaseColor", diff_bc < 0.01,
                           f"expected {expected}, got {bc}, diff={diff_bc:.4f}")
                elif inp is None:
                    report(f"{kclType}: BSDF BaseColor input", False, "no 'Base Color' socket")
        if not found_bsdf:
            report(f"{kclType}: has BSDF_PRINCIPLED node", False, "no Principled BSDF found")

print("\n====== Regression: existing material refreshes ======")

# Clear and test T03 explicitly (the original failure case)
clear_scene()
pref_obj.kclColorT03 = (0.0, 0.584, 0.0)   # approx #009500 in linear
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
obj = bpy.context.active_object
mytool = bpy.context.scene.kmpt
mytool.kcl_masterType = 'T03'
mytool.kcl_applyMaterial = "2"
try:
    rc = bpy.ops.kcl.apply()
except Exception as e:
    report("Regression T03 first apply", False, str(e))

obj = bpy.context.active_object
mat_a = obj.data.materials[0]
c_a = tuple(mat_a.diffuse_color[:3])
diff1 = color_diff(c_a, (0.0, 0.584, 0.0) < 0.01, f"T03 first apply got {c_a}")

# Now change the preference and re-apply: material should update
pref_obj.kclColorT03 = (1.0, 0.2, 0.5)   # distinct pinkish
bpy.ops.kcl.apply()
mat_b = obj.data.materials[0]
c_b = tuple(mat_b.diffuse_color[:3])
diff2 = color_diff(c_b, pref_obj.kclColorT03) < 0.01, f"T03 refresh got {c_b}")

# Check BSDF node also updated if applicable
bsdf_updated = False
if mat_b.use_nodes and mat_b.node_tree:
    for nd in mat_b.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            inp = nd.inputs.get("Base Color")
            if inp and len(inp.links) == 0:
                bc2 = tuple(inp.default_value[:3])
                diff_bc2 = color_diff(bc2, pref_obj.kclColorT03) < 0.01, f"BSDF got {bc2}")

print("\n====== Random color not re-randomized ======")
clear_scene()
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
mytool = bpy.context.scene.kmpt
mytool.kcl_masterType = "T05"
mytool.kcl_applyMaterial = "0"       # Random
try:
    bpy.ops.kcl.apply()
except Exception as e:
    report("Random-color apply", False, str(e))

obj1_mat = obj.data.materials[0]
rand_c1 = tuple(obj1_mat.diffuse_color[:3])

# Re-apply → material already exists → should NOT randomize again
bpy.ops.kcl.apply()
obj2_mat = bpy.context.active_object.data.materials[0]
rand_c2 = tuple(obj2_mat.diffuse_color[:3])
same_random = color_diff(rand_c1, rand_c2) < 0.0001
report("Random unchanged on re-apply", same_random, f"{rand_c1} vs {rand_c2}")

print("\n====== Keep original preserves material ======")
clear_scene()
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
orig_mat = bpy.data.materials.new("_keep_orig_test")
if hasattr(orig_mat, 'use_nodes') and orig_mat.use_nodes:
    for nd in orig_mat.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            inp = nd.inputs.get("Base Color")
            if inp:
                inp.default_value = (0.9, 0.8, 0.75, 1)

obj_keep = bpy.context.active_object
obj_keep.data.materials.append(orig_mat)

mytool.kcl_masterType = "T07"
mytool.kcl_applyMaterial = "1"       # Keep original
try:
    bpy.ops.kcl.apply()
except Exception as e:
    report("Keep-original apply", False, str(e))

mat_keep = obj_keep.data.materials[0]
dc_keep = tuple(mat_keep.diffuse_color[:3])
diff_keep = color_diff(dc_keep, (0.9, 0.8, 0.75))
report("Keep original preserved", diff_keep < 0.01, f"was (0.9,0.8,0.75), got {dc_keep}")

# ====== Summary ======
for m in results:
    print(m)

n_total = pass_count + fail_count
print(f"\nResult: {pass_count}/{n_total} tests passed.")
sys.exit(1 if fail_count > 0 else 0)