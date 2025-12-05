import streamlit as st
import pandas as pd
from drag_coefficient import calcualte_CD
import numpy as np


st.set_page_config(page_title='Two Phase Separatro Design')
st.sidebar.header('2 Phase Separator Design')


st.write("Fluid Rates")
col1 = st.columns(2)
with col1[1]:
    col2 = st.columns(2)
    with col2[1]:
        st.space('small')
        Ql_dis = st.checkbox("", value=True)
with col1[0]:
    Qw = st.number_input(min_value=0, label="Water Rate", disabled=not Ql_dis)
    Qg = st.number_input(min_value=0., label="Gas Rate", value=1.)


with col2[0]:
    Qo = st.number_input(min_value=0, label="Oil Rate", disabled=not Ql_dis, value=1000)
    
    Ql = Qo+Qw
    if not Ql_dis:
        Qo = 0
        Qw = 0
    Ql = st.number_input(min_value=0, label="Liquid Rate", value=Ql, disabled=Ql_dis)



st.write("Conditions")
col3 = st.columns(2)
with col3[0]:
    Po = st.number_input(min_value=0, label="Pressure", value=500)
with col3[1]:
    To_F = st.number_input(min_value=0, label="Temperature in Fehrenhite", value=60)
To_R = To_F+460



st.write("Fluid Properties")
col4 = st.columns(3)
with col4[0]:
    Sg = st.number_input(min_value=0., label="Gas Specific Gravity", value=0.6)
    SG_o_api = st.number_input(min_value=0, label="Oil API Gravity", value=35)
with col4[1]:
    z = st.number_input(min_value=0., max_value=1., label="Compressibility Factor", value=1.,format="%.2f")
    SG_w = st.number_input(min_value=0., label="Water Specific Gravity", disabled=not Ql_dis, value=1.07)
with col4[2]:
    mu_g = st.number_input(min_value=0.000, label="Gas Viscosity", value=0.013, step=0.001, format="%.3f")

SG_o = 141.5/(131.5+SG_o_api)
rho_o = 62.4*SG_o
if Ql_dis:
    rho_w = 62.4*SG_w
    rho_l = (Qo*rho_o+Qw*rho_w)/Ql
else:
    rho_l = rho_o
rho_g = 2.7*Sg*Po/(To_R*z)

st.write('Design Specifications')
col5 = st.columns(3)
with col5[0]:
    dm_liquid = st.number_input(min_value=0, label="Droplet Size", value=100)
with col5[1]:
# (liquid_density, gas_density, droplet_diameter, gas_viscosity)
    CD = calcualte_CD(rho_l, rho_g, dm_liquid, mu_g)
    Cd = st.number_input(min_value=0., label="Drag Coefficient", value=CD)
with col5[2]:
    tr = st.number_input(min_value=0., label='Retention Time', value=2.)

diameter_list = [n for n in range(4, 25, 4)]+[n for n in range(30, 150, 6)]
values = st.slider('Range', 0, len(diameter_list)-1,(2,9))
Vertical, Horizontal = st.columns(2)
with Vertical:
    st.write('Vertical Design')
    # Dmin = (5040*Qg*To_R*z/Po*(rho_g/(rho_l-rho_g)*Cd/dm_liquid)**(1/2))**(1/2)
    # st.write(f'Minimum Diameter is {Dmin}')
    
    dsquared_h = tr*Ql/0.12
    Vertical_design_data = pd.DataFrame(columns=["Diameter (in)", "Height (in)", "Lss (ft)", "SR"])
    Vertical_design_data["Diameter (in)"] = diameter_list
    Vertical_design_data["Height (in)"] = dsquared_h/(Vertical_design_data["Diameter (in)"])**2
    Vertical_design_data["Lss (ft)"] = np.where(Vertical_design_data['Diameter (in)']<=36, (Vertical_design_data["Height (in)"] + 76)/12 , (Vertical_design_data["Height (in)"] + Vertical_design_data["Diameter (in)"] + 40)/12)
    Vertical_design_data["SR"] = 12*Vertical_design_data["Lss (ft)"]/Vertical_design_data["Diameter (in)"]

    def highlight(rows):
        if (rows["SR"]<=4 and rows["SR"]>=3):
            return ['background-color: green'] * len(rows)
        else:
            return [''] * len(rows)

    st.dataframe(Vertical_design_data.iloc[values[0]:values[1]+1].style.apply(highlight, axis=1), hide_index=True)

with Horizontal:
    st.write('Horizontal Design')

    LD = 420*Qg*To_R*z/Po*(rho_l/(rho_l-rho_g)*Cd/dm_liquid)**(1/2)
    dsquared_L = tr*Ql/0.7
    Horizontal_design_data = pd.DataFrame(columns=["Diameter (in)", "Leff (gas) (ft)", "Leff (liquid) (ft)", "Lss (ft)", "SR"])
    Horizontal_design_data["Diameter (in)"] = diameter_list
    Horizontal_design_data["Leff (gas) (ft)"] = LD/(Horizontal_design_data["Diameter (in)"])
    Horizontal_design_data["Leff (liquid) (ft)"] = dsquared_L/(Horizontal_design_data["Diameter (in)"])**2
    Horizontal_design_data["Lss (ft)"] = np.where(Horizontal_design_data['Leff (gas) (ft)']>Horizontal_design_data['Leff (liquid) (ft)'], (Horizontal_design_data['Leff (gas) (ft)'] + Horizontal_design_data["Diameter (in)"])/12 , 4/3*Horizontal_design_data["Leff (liquid) (ft)"])
    Horizontal_design_data["SR"] = 12*Horizontal_design_data["Lss (ft)"]/Horizontal_design_data["Diameter (in)"]


    st.dataframe(Horizontal_design_data.iloc[values[0]:values[1]+1].style.apply(highlight, axis=1), hide_index=True)
