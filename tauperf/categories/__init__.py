from .offline import *
from .hlt import *

CATEGORIES = {
    'nocut': [
        Category_NoCut
        ],
    'offline': [
        Category_Preselection,
        Category_1P,
        Category_2P,
        Category_3P,
        Category_MP,
        ],
    'hlt': [
        Category_Preselection,
        Category_1P_HLT,
        Category_2P_HLT,
        Category_3P_HLT,
        Category_MP_HLT,
        Category_HLT,
        ],
    'plotting': [
        # Category_Preselection,
        Category_1P,
        Category_3P,
        # Category_MP,
        ],
    'plotting_hlt': [
        Category_1P_HLT,
        Category_MP_HLT,
        # Category_HLT,
        ],
    'presel': [
        Category_Preselection
        ],
    'training': [
        Category_1P,
        Category_3P,
        ],
    'training_hlt': [
        Category_1P_HLT,
        Category_3P_HLT,
        ],
    



}
