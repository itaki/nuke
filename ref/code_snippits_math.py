#MATH FUNCTIONS AND WAVE GENERATOR
#PYTHON
#--------------------------------------------------------

#IMPORT THE MATH LIBRARY
import math

#--------------------------------------------------------
#WAVE GENERATOR

#RANDOM WAVE
random((frame+offset)/waveLength) * (maxVal-minVal) + minVal

#NOISE WAVE
(noise((frame+offset)/waveLength)+1)/2 * (maxVal-minVal) + minVal

#SINE WAVE
(sin(2*pi*(frame+offset)/waveLength)+1)/2 * (maxVal-minVal) + minVal

#TRIANGLE WAVE
(asin(sin(2*pi*(frame+offset)/waveLength))/pi+0.5) * (maxVal-minVal) + minVal

#SQUARE WAVE
int(sin(2*pi*(frame+offset)/waveLength)+1) * (maxVal-minVal) + minVal

#SAWTOOTH WAVE
((frame+offset) % waveLength)/waveLength * (maxVal-minVal) + minVal

#SAWTOOTH (PARABOLIC) WAVE
sin((pi*(frame+offset)/(2*waveLength)) % (pi/2)) * (maxVal-minVal) + minVal

#SAWTOOTH (PARABOLIC REVERSED) WAVE
cos((pi*(frame+offset)/(2*waveLength)) % (pi/2)) * (maxVal-minVal) + minVal

#SAWTOOTH (EXPONENTIAL) WAVE
(exp(2*pi*((frame+offset) % waveLength)/waveLength)-1)/exp(2*pi) * (maxVal-minVal) + minVal

#BOUNCE WAVE
abs(sin(pi*(frame + offset)/waveLength))* (maxVal-minVal) + minVal

#BLIP
((frame+(offset+waveLength)) % (waveLength+blipLength)/(waveLength)) *(waveLength/blipLength) - (waveLength/blipLength) >= 0 ? maxVal : minVa

#SINEBLIP
((int((frame+offset) % waveLength)) >= 0 ? ((int((frame+offset) % waveLength)) <= (0+(blipLength-1)) ? ((sin(pi*((frame+offset) % waveLength)/blipLength)/2+1/2) * (2*maxVal-2*minVal) + (2*minVal-maxVal)) : minVal)  : minVal)
