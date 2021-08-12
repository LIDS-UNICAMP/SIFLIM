import warnings
ift = None

try:
    import pyift.pyift as ift
except:
    warnings.warn("PyIFT is not installed.", ImportWarning)

def load_opf_dataset(path):
    assert ift is not None, "PyIFT is not available"

    opf_dataset = ift.ReadDataSet(path)

    return opf_dataset