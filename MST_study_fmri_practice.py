# MST - STUDY PHASE - PRACTICE

from psychopy.gui import DlgFromDict
from psychopy.visual import Window, TextStim, ImageStim
from psychopy.core import Clock, quit, wait
from psychopy.hardware.keyboard import Keyboard
from psychopy import data
import pandas as pd
import os
import random

# --- Participant info dialog ---
exp_info = {'participant': '001'}
dlg = DlgFromDict(exp_info)
if not dlg.OK:
    quit()

# --- Experiment handler for saving data ---
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

exp = data.ExperimentHandler(
    name='MST',
    version='1.0',
    extraInfo=exp_info,
    savePickle=True,
    saveWideText=True,
    dataFileName=os.path.join(data_dir, f"MST_study_practice_{exp_info['participant']}")
)


# Practice stimuli (e.g. Set 6)
practice_cond_df = pd.read_excel("MST_practice_stimuli.xlsx")

# TrialHandler for main experiment (created once) 
trials = data.TrialHandler(
    trialList=practice_cond_df.to_dict('records'), 
    nReps=1,
    method='random',
    name='main'
)

# --- Window and input devices ---
win = Window(fullscr=True, color='white', monitor='laptop', units='height') # Set fullscr=True when actually testing
clock = Clock()
kb = Keyboard()

# --- Text stimuli ---

# General instructions
instructions_txt_stim = TextStim(
    win,
    text="""Du kommer nu att få se några bilder.\n
    Bedöm om du tycker att föremålet i bilden passar bäst inomhus eller utomhus\n
    
    Vänster: Inomhus
    
    Höger: Utomhus
""",
    font='Calibri',
    color= "black",
    height=0.05
)

# After practice: repeat or continue
practice_continue_stim = TextStim(
    win,
    text="""Övningsomgången är nu klar.'""",
    font='Calibri',
    color="black",
    height=0.05
)

# Judgment question text (static)
judge_txt = "Inomhus (Vänster) eller utomhus (Höger)?"
stim_txt = TextStim(win, text=judge_txt, pos=(
    0, 0.4), height=0.07, color='black')

# Fixation cross (reuse same object)
fix_target = TextStim(win, text='+', height=0.07, color='black')

# Image stimulus (we only change image each trial)
stim_img = ImageStim(win, image=None, units='height')
stim_img.size = (None, 0.5) # precentage of screen height, None preserves aspect ratio

# --- Timings ---
t_fix_options = [0.5, 1.0, 1.5]  # fixation cross duration options (ISI jitter)
DEBUG = True  # set to False when done testing

# General instructions
instructions_txt_stim.draw()
win.flip()
kb.waitKeys(keyList=['return'])


# Main loop
for trial in trials:
        idx = trials.thisN  # 0,1,2,...
        
        image_path = os.path.join("Set_4", trial['stim'])
        
        # Update the ImageStim
        stim_img.image = image_path

        # Response variables
        resp_key = None
        resp_rt = None

        # Timing
        t_fix = random.choice(t_fix_options)   # 0.5–1.5 s fixation
        # stimulus duration (change if you want)
        stim_dur = 3.0
        total_dur = t_fix + stim_dur           # total trial time

        if DEBUG:
            print("\n=== NEW TRIAL ===")
            print("response:", resp_key)
            print("idx:", idx)
            print("trial dict:", trial)
            print("trial duration", trial.get(total_dur))
            print("stim:", trial.get("stim"))
            print("cond:", trial.get("cond"))
            print("set:", trial.get("set", "NA"))
            print("lure_bin:", trial.get("lure_bin", "NA"))
            print("image_path:", image_path)

        
        # Clear keyboard events and start trial clock
        kb.clearEvents()
        kb.clock.reset()
        trial_clock = Clock()

        # --- Single loop controlling fixation + stimulus ---
        while True:
            t = trial_clock.getTime()

            if t < t_fix:
                # Fixation period
                fix_target.draw()
            elif t < t_fix + stim_dur:
                # Stimulus period
                stim_img.draw()
                stim_txt.draw()
            else:
                # Trial is over
                break

            win.flip()

            # Collect response *only* during stimulus period
            if t >= t_fix and t < t_fix + stim_dur and resp_key is None:
                keys = kb.getKeys(keyList=['1', '2', 'escape'], # Set keys according to fMRI needs?
                                  waitRelease=False,
                                  clear=False)
                if keys:
                    key = keys[0]
                    if key.name == 'escape':
                        win.close()
                        quit()
                    resp_key = key.name
                    resp_rt = key.rt  # time since last clearEvents()

        # ---- LOG TRIAL DATA ----
        exp.addData('trial_index', idx + 1)  # 1-based indexing
        exp.addData('stim', trial.get('stim'))
        exp.addData('cond', trial.get('cond'))
        exp.addData('set', trial.get('set', 'NA'))
        exp.addData('response', resp_key or 'NA')
        exp.addData('rt', resp_rt or 'NA')
        exp.nextEntry()
        
# Data is saved automatically when the ExperimentHandler closes
win.close()
quit()
