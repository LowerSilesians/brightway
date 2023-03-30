import bw2data as bd
import bw2calc as bc
import bw2io as bi
import numpy as np
from tqdm import tqdm
from pathlib import Path
import pandas as pd
import json


bd.projects.set_current("to_dataframe USEEIO")

datadir = Path("data")
datadir.mkdir(exist_ok=True)

bi.useeio11()

df = bd.Database("USEEIO-1.1").nodes_to_dataframe()


def safe_joiner(x):
    try:
        if not x or np.isnan(x):
            return None
    except TypeError:
        pass
    return "::".join(x)


df['categories'] = df['categories'].apply(safe_joiner)


def safe_converter(x):
    try:
        return str(int(x))
    except:
        return None

