ift = None
import warnings
import sys
try:
    import pyift.pyift as ift
except:
    warnings.warn("PyIFT is not installed.", ImportWarning)

original_imgs_path = sys.argv[1]
input_mimgs_path = sys.argv[2]
output_dir = sys.argv[3]
nsuperpixels = int(sys.argv[4])
patch_size = int(sys.argv[5])

Z = ift.PatchesFromSuperpixels(original_imgs_path, input_mimgs_path, output_dir, nsuperpixels, patch_size)
print(Z.nsamples)