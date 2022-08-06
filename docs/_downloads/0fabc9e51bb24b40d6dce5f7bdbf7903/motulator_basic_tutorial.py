"""
Motulator basic tutorial
========================

This is a basic tutorial on how to use the motulator. In order to plot matlab figures on to the jupyter notebook
interface, first run the jupyter notebook magic command below:

"""


get_ipython().run_line_magic('matplotlib', 'inline')


#%%
# Usage
# -----
# Install motulator by using the pip command:


get_ipython().system('pip install motulator')


#%%
# After installation, motulator can be used by creating a continuous-time system model, a discrete-time controller,
# and a simulation object, as shown below:


import motulator as mt

# Continuous-time model for the drive system
motor = mt.InductionMotor()     # Motor model
mech = mt.Mechanics()           # Mechanics model
conv = mt.Inverter()            # Converter model
mdl = mt.InductionMotorDrive(motor, mech, conv)

# Discrete-time controller
pars = mt.InductionMotorVectorCtrlPars()    # Dataclass of control parameters
ctrl = mt.InductionMotorVectorCtrl(pars)    # Sensorless controller

# Create a simulation object, simulate, and plot example figures
sim = mt.Simulation(mdl, ctrl)
sim.simulate()
mt.plot(sim)


#%%
# Configuration of parameters
# ---------------------------
# Motulator simulation tool is based on the control of an induction motor or synchronous motor drive. Motulator
# includes scalar control (or Volts-per-Hertz-control) and rotor-flux-oriented vector control. In order to build
# the link between the continuous-time design and discrete-time implementation, all the control algorithms are
# implemented in the discrete-time domain based on forward Euler approximation.
# 
# The module motulator/model/im.py describes the induction motor model data according to the Γ model (Gamma model).
# The Γ model is chosen, since it can be extended with the magnetic saturation model in a staightforward manner.
# If the magnetic saturation is omitted, the Γ model is mathematically identical to the inverse-Γ model of the
# induction motor, which is shown below:
# 
# .. image:: ../../parts/Inverse-gamma_model.png
# 
# Motor model can be created by constructing the induction motor object as shown below:


import motulator as mt

# Motor model with custom parameters
motor = mt.InductionMotor(R_s=3.7, R_r=2.5, L_ell=.023, L_s=.245, p=2)


#%%
# Here the motor parameters mean the following: R_s is stator resistance, R_r is rotor resistance, L_ell is leakage
# inductance, L_s is stator inductance and p is the number of pole pairs. The value of parameters R_s, R_r, L_ell, L_s
# and p can be configured by changing their values when passing to mt.InductionMotor constructor.
# 
# The rated values of the motor are important for configuring how figures are plotted:


# Compute base values based on the nominal values (just for figures)
base = mt.BaseValues(U_nom=400,        # Line-line rms voltage
                     I_nom=5,          # Rms current
                     f_nom=50,         # Frequency
                     tau_nom=14.6,     # Torque
                     P_nom=2.2e3,      # Power
                     p=2)              # Number of pole pairs


#%%
# To configure the mechanics model and converter model parameters,
# the following parameters are passed into their class constructors:


mech = mt.Mechanics(J=.015)         # Mechanics model with custom parameters
conv = mt.Inverter(u_dc0=540)       # Inverter model with custom parameters


#%%
# Here J is the total moment of inertia of the motor and u_dc0 is the DC-bus voltage of inverter.
# After all of that has been configured, the continuous-time model for an induction motor drive
# can be constructed with the following command:


mdl = mt.InductionMotorDrive(motor, mech, conv)  # System model


#%%
# This interconnects the subsystems of an induction motor drive and provides an interface for the solver.
# More complicated systems could be modeled using a similar template.
# 
# Motulator includes Volts-per-Hertz-control and rotor-flux-oriented vector control, which are configured similarly
# to how the system model is configured. In the case of vector control, the configuration for the parameters of the
# control system can look something like this:


import numpy as np

# Control system
ctrl = mt.InductionMotorVectorCtrl(mt.InductionMotorVectorCtrlPars(
    sensorless=True,                # Enable sensorless mode
    T_s=250e-6,                     # Sampling period
    delay=1,                        # Amount of computational delay
    alpha_c=2*np.pi*200,            # Current-control bandwidth
    alpha_o=2*np.pi*40,             # Observer bandwidth
    alpha_s=2*np.pi*4,              # Speed-control bandwidth
    psi_R_nom=.9,                   # Nominal rotor flux
    i_s_max=1.5*base.i,             # Current limit
    tau_M_max=1.5*base.tau_nom,     # Torque limit (for the speed ctrl)
    J=.015,                         # Inertia estimate (for the speed ctrl)
    p=2,                            # Number of pole pairs
    # Inverse-Gamma model parameter estimates
    R_s=3.7, R_R=2.1, L_sgm=.021, L_M=.224))


#%%
# Speed reference and the external load torque for the induction motors can be configured in this way:


# Set the speed reference and the external load torque
ctrl.w_m_ref = lambda t: (t > .2)*(.5*base.w)
mdl.mech.tau_L_ext = lambda t: (t > .75)*base.tau_nom


#%%
# Simulation object has a simulate function, that solves the continuous-time model and calls the discrete-time
# controller. Base values for plotting figures is determined by base parameter and the simulation stop time is
# determined by t_stop parameter (which is 1 by default). Simulation object is created as follows:


# Create the simulation object
sim = mt.Simulation(mdl, ctrl, base=base, t_stop=1.5)


#%%
# To simulate the simulation object, run the command:


sim.simulate()


#%%
# Plotting can be done either by plotting figures in SI units:


mt.plot(sim)


#%%
# Or alternatively plotting figures in per units:


mt.plot_pu(sim)


#%%
# In this tutorial, induction motor was used to simulate the model. However, motulator also supports functionality for
# synchronous motors and more. More detailed information on configuration parameters can be found from the motulator
# documentation API reference.