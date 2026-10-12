# Fixation cross only 

from psychopy.gui import DlgFromDict
from psychopy.visual import Window, TextStim, ImageStim
from psychopy.hardware.keyboard import Keyboard

# Window and input devices
win = Window(fullscr=True, color='white', monitor='laptop', units='height')
kb = Keyboard()

# Fixation cross
fixation_cross = TextStim(win, text='+', height=0.07, color='black')

fixation_cross.draw()
win.flip()
kb.waitKeys(keyList=['escape']) # Escape to exit 
