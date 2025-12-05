import streamlit as st
from drag_coefficient import calcualte_CD
import pandas as pd
import numpy as np
import math

st.set_page_config(page_title='Three Phase Separatro Design')
st.sidebar.header('3 Phase Separator Design')



st.write("Fluid Rates")
col1 = st.columns(2)
with col1[1]:
    Qo = st.number_input(min_value=0, label="Oil Rate", value=1000)


with col1[0]:
    Qw = st.number_input(min_value=0, label="Water Rate", value=1000)
    Qg = st.number_input(min_value=1., label="Gas Rate")

Ql = Qo+Qw





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
    z = st.number_input(min_value=0., max_value=1., label="Compressibility Factor", value=1.,format="%.2f")
    rho_g = rho_o = st.number_input(min_value=0., label="Gas Density", value=2.7*Sg*Po/(To_R*z))
with col4[1]:
    mu_g = st.number_input(min_value=0., label="Gas Viscosity", value=0.013, step=0.001, format="%.3f")
    SG_w = st.number_input(min_value=0., label="Water Specific Gravity", value=1.07)
    mu_w = st.number_input(min_value=0, label="Water Viscosity", value=1)
with col4[2]:
    SG_o_api = st.number_input(min_value=0, label="Oil API Gravity", value=35)
    mu_o = st.number_input(min_value=0, label="Oil Viscosity", value=10)
    SG_o = 141.5/(131.5+SG_o_api)
    rho_o = st.number_input(min_value=0., label="Oil Density", value=62.4*SG_o)

    deltaSG = SG_w-SG_o

rho_w = 62.4*SG_w
rho_l = (Qo*rho_o+Qw*rho_w)/Ql




st.write('Design Specifications')
col5 = st.columns(3)
with col5[0]:
    dm_liquid = st.number_input(min_value=0, label="Liquid Droplet Size in Gas Section", value=100)
    CD = calcualte_CD(rho_l, rho_g, dm_liquid, mu_g)
    Cd = st.number_input(min_value=0., label="Drag Coefficient CD", value=CD)
with col5[1]:
    dm_water = st.number_input(min_value=0, label="Water Droplet Size in Oil Section", value=500)
    tr_w = st.number_input(min_value=0., label='Water Retention Time', value=10.)
# (liquid_density, gas_density, droplet_diameter, gas_viscosity)
with col5[2]:
    dm_oil = st.number_input(min_value=0, label="Oil Droplet Size in Water Section", value=200)
    tr_o = st.number_input(min_value=0., label='Oil Retention Time', value=10.)


dmin_gas = (5040*Qg*To_R*z/Po*(rho_g/(rho_l-rho_g)*Cd/dm_liquid)**(1/2))**(1/2)
dmin_oil = (6690*Qw*mu_w/(deltaSG*dm_oil**2))**(1/2)
dmin_water = (6690*Qo*mu_o/(deltaSG*dm_water**2))**(1/2)


def generate_vertical_diameter(n, count=25):

    start = n if n % 4 == 0 else int(n + (4 - n % 4))
    
    result = []
    current = start


    while len(result) < count:
        result.append(current)

        if current < 24:
            step = 4
        else:
            step = 6
        
        current += step

    return result


dmin = max([dmin_gas, dmin_oil, dmin_water])

def highlight(rows):
        if (rows["SR"]<=3 and rows["SR"]>=1.5):
            return ['background-color: green'] * len(rows)
        else:
            return [''] * len(rows)



def Aw_over_A(beta):
    return (1/math.pi) * ( math.acos(1-2*beta) - 2*(1-2*beta)*math.sqrt(max(0,beta-beta*beta)) )

def find_beta(target, tol=1e-8):
    lo, hi = 0.0, 0.5
    for _ in range(200):
        mid = 0.5*(lo+hi)
        if Aw_over_A(mid) < target:
            lo = mid
        else:
            hi = mid
        if hi-lo < tol:
            break
    return 0.5-0.5*(lo+hi)

vertical_diameter_list = generate_vertical_diameter(dmin)
values = st.slider('Range', 0, len(vertical_diameter_list)-1,(0,10))

Vertical, Horizontal = st.columns(2)

with Vertical:
    st.write("Vertical Separator")
    
    Vertical_design_data = pd.DataFrame(columns=["Diameter (in)", "Liquid Height (in)", "Lss (ft)", "SR"])
    Vertical_design_data["Diameter (in)"] = vertical_diameter_list
    Vertical_design_data["Liquid Height (in)"] = (tr_o*Qo+tr_w*Qw)/(0.12*(Vertical_design_data["Diameter (in)"])**2)
    Vertical_design_data["Lss (ft)"] = np.where(Vertical_design_data['Diameter (in)']<=36, (Vertical_design_data["Liquid Height (in)"] + 76)/12 , (Vertical_design_data["Liquid Height (in)"] + Vertical_design_data["Diameter (in)"] + 40)/12)
    Vertical_design_data["SR"] = 12*Vertical_design_data["Lss (ft)"]/Vertical_design_data["Diameter (in)"]

    st.dataframe(Vertical_design_data.iloc[values[0]:values[1]+1].style.apply(highlight, axis=1), hide_index=True)

def generate_horizontal_diameters(max_value):
    # first multiple of 4 ≥ n
    start = 4

    result = []
    current = start

    while current <= max_value:
        result.append(current)

        # step changes after reaching 24
        step = 4 if current < 24 else 6

        current += step

    return result

with Horizontal:
    st.write('Horizontal Separator')

    homax = 0.00128*tr_o*deltaSG*dm_water**2/mu_o
    hwmax = 0.00128*tr_w*deltaSG*dm_oil**2/mu_w
    AwA = 0.5*Qw*tr_w/(tr_o*Qo+tr_w*Qw)
    beta = find_beta(AwA)
    dmax_o = homax/beta
    dmax_w = hwmax/beta
    dmax = min([dmax_o, dmax_w])
    LD = 420*Qg*To_R*z/Po*(rho_l/(rho_l-rho_g)*Cd/dm_liquid)**(1/2)
    dsquared_L = 1.42*(tr_o*Qo+tr_w*Qw)

    Horizontal_design_data = pd.DataFrame(columns=["Diameter (in)", "Leff (gas) (ft)", "Leff (liquid) (ft)", "Lss (ft)", "SR"])
    Horizontal_design_data["Diameter (in)"] = generate_horizontal_diameters(dmax)
    Horizontal_design_data["Leff (gas) (ft)"] = LD/(Horizontal_design_data["Diameter (in)"])
    Horizontal_design_data["Leff (liquid) (ft)"] = dsquared_L/(Horizontal_design_data["Diameter (in)"])**2
    Horizontal_design_data["Lss (ft)"] = np.where(Horizontal_design_data['Leff (gas) (ft)']>Horizontal_design_data['Leff (liquid) (ft)'], (Horizontal_design_data['Leff (gas) (ft)'] + Horizontal_design_data["Diameter (in)"])/12 , 4/3*Horizontal_design_data["Leff (liquid) (ft)"])
    Horizontal_design_data["SR"] = 12*Horizontal_design_data["Lss (ft)"]/Horizontal_design_data["Diameter (in)"]
    

    st.dataframe(Horizontal_design_data.iloc[values[0]:values[1]+1].style.apply(highlight, axis=1), hide_index=True)
