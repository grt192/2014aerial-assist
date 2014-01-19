"""
Config File for Robot

#TODO: Setup for Constants File
"""

__author__ = "Sidd Karamcheti"

import wpilib
from grt.sensors.attack_joystick import Attack3Joystick
from grt.core import SensorPoller
from grt.mechanism.drivetrain import DriveTrain
from grt.mechanism.drivecontroller import ArcadeDriveController
#from grt.sensors.ticker import ticker
from grt.macro.drive_macro import DriveMacro
from grt.sensors.encoder import Encoder

# Joysticks
lstick = Attack3Joystick(1)

sp = SensorPoller((lstick, ))

#Solenoids (PINS TENTATIVE)
#solenoid = wpilib.Solenoid(7, 1)

#Motors (PINS TENTATIVE)
lfm = wpilib.Talon(6)
lmm = wpilib.Talon(7)
lrm = wpilib.Talon(8)
rfm = wpilib.Talon(3)
rmm = wpilib.Talon(4)
rrm = wpilib.Talon(5)
import math
pi = math.pi
dist_per_pulse = .01 #(pi * (1.75 * 2))/128
left_encoder=Encoder(2, 3, dist_per_pulse, reverse=True)
right_encoder=Encoder(4, 5, dist_per_pulse, reverse=True)

dt = DriveTrain(lfm, rfm, lmm, rmm, lrm, rrm, left_encoder = left_encoder, right_encoder = right_encoder)

ac = ArcadeDriveController(dt, lstick)

# Autonomous
auto_sp = SensorPoller((dt.right_encoder, dt.left_encoder))
drive_macro = DriveMacro(dt, 20, 10)
