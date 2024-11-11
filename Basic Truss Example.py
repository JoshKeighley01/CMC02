#Units
m = 1
N = 1
Pa = 1

inches = 0.0254*m
ft = 12*inches
kip = 4.45*10**3*N
ksi = 6.89*10**6*Pa



#Input variables
x1 = 0.
y1 = 0.

x2 =12.*ft
y2 = 0.

x3 = 14.*ft
y3 = 0.

x4 = 6.*ft
y4= 8.*ft

A1 = 10.*inches**2
A2 = 5.*inches**2

E = 3000*ksi

Px = 100*ksi
Py = -50*ksi

"""The reason for the decimal place is that when you pass data into opensees it expects it as a certain type
for the node comands it expects float. Without the decimal place it is an integer"""



#Opensees Analysis

#Import openseespy 
import openseespy.opensees as ops
import opsvis as opsv
import numpy as np
import os

#Wipe model
ops.wipe()

#Create ModelBuilder (2 dimensions, 3 DOFs/nodes)
ops.model('basic', '-ndm', 2, '-ndf', 3)
"""Should use 3DoF for a 2D system, 6DoF for 3D system to keep consistent convention"""
if not os.path.exists('Data'):
    os.mkdir('Data')

# define materials
ops.uniaxialMaterial("Elastic", 1, E)
"""first part is a string that tells the command what type the materials is, the second
is an integer that is the material tag to keep track of materials in more complex models
the third part is the elastic modulus entred as a float """

# # create nodes
# ops.node(1, x1, y1)
# ops.node(2, x2, y2)
# ops.node(3, x3, y3)
# ops.node(4, x4, y4)
# """node tag, x-coordinate, y-coordinate"""

# create nodes
nodes = np.array([[x1,y1],[x2,y2],[x3,y3],[x4,y4]])
for i, n in enumerate(nodes):
    ops.node(i+1, float(n[0]), float(n[1]))
    print(f'Node {i+1} is defined')

# set boundary condition
ops.fix(1, 1, 1, 1)
ops.fix(2, 1, 1, 1)
ops.fix(3, 1, 1, 1)
ops.fix(4, 0, 0, 1)
"""node tag, x-dir, y-dir, rotation"""
"""1 is fixed, 0 is free"""
"""If your are using a truss element, you fix the rotational degree of freedom for 3DoF"""

# define elements
# element('TrussSection', eleTag, *eleNodes, secTag, <'-rho', rho>, <'-cMass', cFlag>, <'-doRayleigh', rFlag>)
ops.element("Truss", 1, 1, 4, A1, 1)
ops.element("Truss", 2, 2, 4, A2, 1)
ops.element("Truss", 3, 3, 4, A2, 1)

# create TimeSeries
ops.timeSeries("Linear", 1)
"""time series type, time series tag"""

# create a plain load pattern
ops.pattern("Plain", 1, 1)
"""pattern type, pattern tag, assign to time series 1"""

"""???"""
# Create the nodal load - command: load nodeID xForce yForce
ops.load(4, Px, Py, 0)
"""node, x-dir load, y-dir load, rotational DoF load"""


#Displacement, Reaction recorder, and element recorder
ops.recorder('Node', '-file', "Data/NodeDisp.out", '-time', '-node', 4, '-dof', 1,2,3, 'disp')
ops.recorder('Node', '-file', "Data/Reaction.out", '-time', '-node', 1,2,3, '-dof', 1,2,3, 'reaction')
ops.recorder('Element', '-file', "Data/Elements.out", '-time', '-ele', 1,2,3, 'forces')
#for node
"""what to record, save file, with this file name, for all time, record a node, node 4, these DoFs, the displacement"""

# create SOE
ops.system("BandSPD")
"""Creates the system of equations"""

# create DOF number
ops.numberer("RCM")
"""Now the DoFs are numbered """

# create constraint handler
ops.constraints("Plain")
"""how the constraints are handled"""

# create integrator
ops.integrator("LoadControl", 1.0)
"""Integrator type, the loads control what is going on from step to step"""

# create algorithm
ops.algorithm("Newton")

# create analysis object
ops.analysis("Static")
"""Type of analysis"""

#Initialise values
ops.initialize()

# perform the analysis
ok = ops.analyze(1)
"""how many times to analyze. If it works analyze returns 0"""

ops.wipe()

#Plotting the model
opsv.plot_model()


