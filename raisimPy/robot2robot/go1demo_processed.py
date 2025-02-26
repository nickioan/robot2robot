import os
import numpy as np
import raisimpy as raisim
import time
from arguments import arg_parser

args = arg_parser()

raisim.World.setLicenseFile(os.path.dirname(
    os.path.abspath(__file__)) + "/../../rsc/activation.raisim")
go1_urdf_file = os.path.dirname(os.path.abspath(
    __file__)) + "/../../rsc/go1/urdf/go1_v2.urdf"

world = raisim.World()
world.setTimeStep(0.001)
server = raisim.RaisimServer(world)
ground = world.addGround()

path = "go1_motions_processed/preprocessed_" + args.name + ".csv"
data = np.loadtxt(path, delimiter=",")
print(f"The shape of the trajectory is size:{data.shape[0]}, features:{data.shape[1]}.")
# data front right --> sim rear left


go1 = world.addArticulatedSystem(go1_urdf_file)
go1.setName("Go1")

go1_nominal_joint_config = np.array([0, 0, 0.30, 1.0, 0.0, 0.0, 0.0, 0.0, 0.8, -1.7,
                                        0.00, 0.8, -1.7, 0.0, 0.8, -1.7, 0.00, 0.8, -1.7])


kp = 100
kd = 10
go1.setGeneralizedCoordinate(go1_nominal_joint_config)
go1.setPdGains(kp * np.ones([18]), kd * np.ones([18]))

server.launchServer(8080)

ep_length = len(data)
run_time = ep_length*20+1

def updateTargets(index):
    p_targets = np.zeros(19)
    d_targets = np.zeros(18)
    p_targets = data[index,:19]
    d_targets = data[index,19:]

    go1.setPdTarget(p_targets,d_targets)
    world.integrate()

time.sleep(2)
world.integrate1()
counter = 1

for i in range(1000000000):
    time.sleep(0.001)
    world.integrate()
    if i % 20 == 0:
        updateTargets(counter)
        counter+=1
    if counter >= ep_length:
        counter = 0

server.killServer()
