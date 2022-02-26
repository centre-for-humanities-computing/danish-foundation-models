"""
pip install pand
"""
import pandas as pd

pd.read_parquet('example_pa.parquet', engine='pyarrow')