ift = None
import warnings
import sys
import shutil
try:
    import pyift.pyift as ift
except:
    warnings.warn("PyIFT is not installed.", ImportWarning)

original_imgs_path = sys.argv[1]
output_dir = sys.argv[2]
nsuperpixels = int(sys.argv[3])
patch_size = int(sys.argv[4])

Z = ift.PatchesFromSuperpixels(original_imgs_path, output_dir, nsuperpixels, patch_size)
print(Z.nsamples)

try:
    shutil.rmtree(output_dir.split('.')[0])
except OSError as e:
    print("Error: %s - %s." % (e.filename, e.strerror))