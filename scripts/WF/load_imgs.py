"""
This script is used to load images.
"""
import sys
sys.path.append('../DeepAPL/')
from DeepAPL.DeepAPL import DeepAPL_WF
import warnings
warnings.filterwarnings('ignore')

DAPL = DeepAPL_WF('load_data')
DAPL.Import_Data(directory=r"C:\Users\npotu1\DataScience\DeepAPL\Data\All", Load_Prev_Data=False)




