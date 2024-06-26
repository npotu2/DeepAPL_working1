"""
This script is used to assess the prediction of the train MIL model on the clinical case vignette in the manuscript.
"""
import sys
sys.path.append('../DeepAPL/')
from DeepAPL.DeepAPL import DeepAPL_WF
import warnings
warnings.filterwarnings('ignore')
import pickle
import warnings
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import matplotlib.pyplot as plt
import numpy as np

DAPL = DeepAPL_WF('cc')
DAPL.Import_Data(directory=r"C:\Users\npotu1\DataScience\DeepAPL\Data\Clinical_Case", Load_Prev_Data=False)

name = 'discovery_all'
gpu=0
DAPL_train = DeepAPL_WF(name,gpu)
DAPL_train.imgs = DAPL.imgs
DAPL_train.patients = DAPL.patients
DAPL_train.cell_type = DAPL.cell_type
DAPL_train.files = DAPL.files
DAPL_train.smears = DAPL.smears
label_dict = {'cc':'AML'}
DAPL_train.labels = np.array([label_dict[x] for x in DAPL_train.patients])
DAPL_train.lb = LabelEncoder().fit(['AML','APL','out'])
DAPL_train.Y = DAPL_train.lb.transform(DAPL_train.labels)
DAPL_train.Y = OneHotEncoder(sparse_output= False).fit_transform(DAPL_train.Y.reshape(-1,1))
DAPL_train.predicted = np.zeros((len(DAPL_train.Y), len(DAPL_train.lb.classes_)))
predicted,sample_list = DAPL_train.Ensemble_Inference()
DAPL_train.Get_Cell_Predicted()

name_out = 'clinical_case'
with open(name_out+'.pkl','wb') as f:
    pickle.dump([DAPL_train.Cell_Pred,DAPL_train.DFs_pred,DAPL_train.imgs,
                DAPL_train.patients,DAPL_train.cell_type,DAPL_train.files,DAPL_train.smears,
                DAPL_train.labels,DAPL_train.Y,DAPL_train.predicted,DAPL_train.lb],f,protocol=4)
DAPL = DAPL_train
import seaborn as sns
blasts = False
cl = 'AML'
if blasts:
    fig, ax = plt.subplots(figsize=(5, 5))
    order = ['Blast, no lineage spec', 'Promonocyte', 'Promyelocyte', 'Myelocyte', 'Metamyelocyte']
else:
    fig, ax = plt.subplots(figsize=(15, 8))
    order = DAPL.Cell_Pred.groupby(['Cell_Type']).agg({cl:'mean'}).sort_values(by=cl).index
sns.violinplot(data=DAPL.Cell_Pred,x='Cell_Type',y=cl,cut=0,ax=ax,order=order,width=5)
# sns.boxplot(data=DAPL.Cell_Pred,x='Cell_Type',y='AML',ax=ax,order=order)
plt.xlabel('Cellavision Cell Type',fontsize=24)
plt.ylabel('P('+cl+')',fontsize=24)
ax.xaxis.set_ticks_position('top')
plt.xticks(rotation=-45,fontsize=16)
plt.yticks(fontsize=16)
plt.ylim([0,1])
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.tick_params(axis='x', which=u'both',length=0)
plt.tight_layout()
plt.savefig(name_out+'_celltype.eps',transparent=True)

plt.hist(DAPL.Cell_Pred['AML'],100)
DAPL.Cell_Pred.sort_values(by='AML',inplace=True,ascending=False)

