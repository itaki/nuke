#*****************************************************************
#*****************************************************************
#*****************************************************************
#*****************PARTICLES COLLECTION FOR NUKE******************
#******************v1.0 compatible with Nuke 13*******************
#*****************************************************************
#******************ADD THIS TO YOUR FILE INIT.PY******************
#***************DON'T DELETE THE r BEFORE THE PATH****************
#nuke.pluginAddPath(r"/Users/yourPath/.nuke/ParticlesCollection")
#*****************************************************************
#*****************************************************************




import sys
import nuke
import os
import webbrowser


#Read Particles folder path
Particles_path = os.path.dirname(__file__)
print ("Particles path: " + Particles_path)


toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("Particles Nodes", icon = os.path.join(Particles_path, "icon/particles_logo.png"))

m.addMenu( 'Animals', icon = os.path.join(Particles_path, "icon/particles01.png") )
m.addMenu( 'Expression and Blinkscript', icon = os.path.join(Particles_path, "icon/particles03.png") )
m.addMenu( 'Modelling', icon = os.path.join(Particles_path, "icon/particles04.png") )
m.addMenu( 'Pyro and Sparks', icon = os.path.join(Particles_path, "icon/particles05.png") )
m.addMenu( 'Utilities', icon = os.path.join(Particles_path, "icon/particles06.png") )
m.addMenu( 'Various Setup', icon = os.path.join(Particles_path, "icon/particles08.png") )
m.addMenu( 'Weather', icon = os.path.join(Particles_path, "icon/particles02.png") )




#ANIMALS
m.addCommand('Animals/P_flockOfBirds', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Animals/flockOfBirds.nk").replace('\\', '/') + "\")")     # in Windows I need to convert \ to / with --> replace('\\', '/'),
m.addCommand('Animals/P_Bird', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Animals/P_Bird.nk").replace('\\', '/') + "\")")
m.addCommand('Animals/P_Bugs', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Animals/P_Bugs.nk").replace('\\', '/') + "\")")
m.addCommand('Animals/P_Flies', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Animals/P_Flies.nk").replace('\\', '/') + "\")")



#ExpressionAndBlinkscript
m.addCommand('Expression and Blinkscript/Basic Particles BlinkScript Gizmos', "nuke.nodePaste(\"" + os.path.join(Particles_path, "ExpressionAndBlinkscript/BasicBlinkscriptGizmos.nk").replace('\\', '/') + "\")")
m.addCommand('Expression and Blinkscript/Particle Expression Node', "nuke.nodePaste(\"" + os.path.join(Particles_path, "ExpressionAndBlinkscript/ParticleExpressionNode.nk").replace('\\', '/') + "\")")
m.addCommand('Expression and Blinkscript/ParticleKiller', "nuke.nodePaste(\"" + os.path.join(Particles_path, "ExpressionAndBlinkscript/ParticleKiller.nk").replace('\\', '/') + "\")")
m.addCommand('Expression and Blinkscript/Particle Constrain To Sphere', "nuke.nodePaste(\"" + os.path.join(Particles_path, "ExpressionAndBlinkscript/ParticleConstrainToSphereMY.nk").replace('\\', '/') + "\")")
m.addCommand('Expression and Blinkscript/Particles Attract To Sphere', "nuke.nodePaste(\"" + os.path.join(Particles_path, "ExpressionAndBlinkscript/ParticlesAttractToSphereMY.nk").replace('\\', '/') + "\")")
m.addCommand('Expression and Blinkscript/ParticleWorldP_color', "nuke.nodePaste(\"" + os.path.join(Particles_path, "ExpressionAndBlinkscript/worldP_color.nk").replace('\\', '/') + "\")")




#MODELLING
m.addCommand('Modelling/P_LEGO', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Modelling/LEGO.nk").replace('\\', '/') + "\")")
m.addCommand('Modelling/ParticleEnvironment', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Modelling/ParticleEnvironment.nk").replace('\\', '/') + "\")")





#PYRO and SPARKS
m.addCommand('Pyro and Sparks/P_Embers', "nuke.nodePaste(\"" + os.path.join(Particles_path, "PyroAndSparks/Embers.nk").replace('\\', '/') + "\")")
m.addCommand('Pyro and Sparks/P_Fire and Sparks', "nuke.nodePaste(\"" + os.path.join(Particles_path, "PyroAndSparks/FireAndSparks.nk").replace('\\', '/') + "\")")
m.addCommand('Pyro and Sparks/P_Smoke', "nuke.nodePaste(\"" + os.path.join(Particles_path, "PyroAndSparks/smoke.nk").replace('\\', '/') + "\")")
m.addCommand('Pyro and Sparks/P_Sparks', "nuke.nodePaste(\"" + os.path.join(Particles_path, "PyroAndSparks/Sparks.nk").replace('\\', '/') + "\")")
m.addCommand('Pyro and Sparks/P_Sparky', "nuke.nodePaste(\"" + os.path.join(Particles_path, "PyroAndSparks/Sparky.nk").replace('\\', '/') + "\")")
m.addCommand('Pyro and Sparks/P_TrailSparks', "nuke.nodePaste(\"" + os.path.join(Particles_path, "PyroAndSparks/TrailSparks/TrailSparks/.nk").replace('\\', '/') + "\")")





#UTILITIES
m.addCommand('Utilities/PARTICLE NODES', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/PARTICLE_NODES.nk").replace('\\', '/') + "\")")
m.addCommand('Utilities/Particles Adjust size over time', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/adjust_size_over_time.nk").replace('\\', '/') + "\")")
m.addCommand('Utilities/P_Bounce and Friction', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/bounce_and_friction.nk").replace('\\', '/') + "\")")
m.addCommand('Utilities/P_Directional Force', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/directionalForce.nk").replace('\\', '/') + "\")")
m.addCommand('Utilities/P_Drag', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/drag.nk").replace('\\', '/') + "\")")
m.addCommand('Utilities/P_Gravity', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/gravity.nk").replace('\\', '/') + "\")")
m.addCommand('Utilities/P_LookAt', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/lookAt.nk").replace('\\', '/') + "\")")
m.addCommand('Utilities/P_MotionAlign', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/motionAlign.nk").replace('\\', '/') + "\")")
m.addCommand('Utilities/P_PointForce', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/pointForce.nk").replace('\\', '/') + "\")")
m.addCommand('Utilities/P_Turbulence', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/turbulence.nk").replace('\\', '/') + "\")")
m.addCommand('Utilities/P_Vortex', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/Vortex.nk").replace('\\', '/') + "\")")
m.addCommand('Utilities/P_Wind', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Utilities/wind.nk").replace('\\', '/') + "\")")





#VARIOUS SETUP
m.addCommand('VariousSetup/P_BloodHit', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/BloodHit.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_blueTrail', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/blueTrail.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_BouncingBalls', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/BouncingBalls.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_CollisionAndGravity', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/CollisionAndGravity.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_confettiExplosion', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/confettiExplosion.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_DNA', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/DNA.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_disintegrationEffect', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/disintegrationEffect.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_drStrangePortal', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/drStrangePortal.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_electricityBall', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/electricityBall.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_fireworks', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/fireworks.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_FootageAsParticles', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/FootageAsParticles.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_particleSystem', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/particleSystem.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_PathLines', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/PathLines.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/P_SpritePath', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/SpritePath.nk").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/Leaves/FallingLeaves', "nuke.createNode(\"" + os.path.join(Particles_path, "VariousSetup/Leaves/FallingLeaves.gizmo").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/Leaves/LeavesRender', "nuke.createNode(\"" + os.path.join(Particles_path, "VariousSetup/Leaves/LeavesRender.gizmo").replace('\\', '/') + "\")")
m.addCommand('VariousSetup/Leaves/FallingLeaves Example', "nuke.nodePaste(\"" + os.path.join(Particles_path, "VariousSetup/Leaves/LeavesExample.nk").replace('\\', '/') + "\")")






#WEATHER
m.addCommand('Weather/P_Clouds', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Weather/Clouds.nk").replace('\\', '/') + "\")")
m.addCommand('Weather/P_DustAtmos', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Weather/dustAtmos.nk").replace('\\', '/') + "\")")
m.addCommand('Weather/P_DustHit', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Weather/dustHit/DustHit.nk").replace('\\', '/') + "\")")
m.addCommand('Weather/P_Fog01', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Weather/FogSnowRain/FogExample.nk").replace('\\', '/') + "\")")
m.addCommand('Weather/P_Fog02', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Weather/Fog.nk").replace('\\', '/') + "\")")
m.addCommand('Weather/P_SnowRain', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Weather/FogSnowRain/SnowRainExample.nk").replace('\\', '/') + "\")")
m.addCommand('Weather/P_Raindrops', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Weather/Raindrops/Raindrops.nk").replace('\\', '/') + "\")")
m.addCommand('Weather/P_RainMaker', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Weather/RainMaker.nk").replace('\\', '/') + "\")")
m.addCommand('Weather/P_Lightning', "nuke.nodePaste(\"" + os.path.join(Particles_path, "Weather/Lightning.nk").replace('\\', '/') + "\")")




m.addSeparator()


#INFO
m.addCommand('Info e Tutorial', "nuke.tcl('start', 'http://www.andreageremia.it/tutorial_particles_collection.html')", icon = os.path.join(Particles_path, "icon/question_mark.png"))
