import streamlit as st
import pandas as pd
from drag_coefficient import calcualte_CD
import numpy as np

st.set_page_config(
    page_title="Separators Design Calculator",
    page_icon="👋",
)

st.sidebar.success("Select a Demo Above.")


st.markdown('''
# Production Facilities Design
## Separators Design
#### Supervised by: Eng. Mohammed Hussain
#### Done by: Ahmed Zuhair
            ''')



