def calcualte_CD(liquid_density, gas_density, droplet_diameter, gas_viscosity):
    rho_l = liquid_density
    rho_g = gas_density
    dm = droplet_diameter
    mu_g = gas_viscosity
    Cd=0.34
    vt0=0
    vt1=0.01186*((rho_l-rho_g)/rho_g*dm/Cd)**(1/2)
    while (abs(vt0-vt1))>0.001:
        Re=0.0049*rho_g*dm*vt1/mu_g
        Cd=0.34+3/(Re)**0.5+24/Re
        vt0=vt1
        vt1=0.01186*((rho_l-rho_g)/rho_g*dm/Cd)**(1/2)
    return Cd

