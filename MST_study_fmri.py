# MST - STUDY PHASE

# AT NEXT SUBIC PILOT: 
# 1. CHECK RESPONSE BUTTONS (1,3?)
# 2. UPDATE WIN: win = Window(fullscr=True, color='white', monitor='laptop', units='height')
# 3. DOUBLE-CHECK THE OLD SCRIPT TO SEE IF ANYTHING ELSE SHOULD BE CHANGED


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
    saveWideText=False,   # Otherwise it saves a .csv, but fmriprep wants .tsv (BIDS) 
    dataFileName=os.path.join(data_dir, f"sub-{exp_info['participant']}_encoding-MST_events"),
)

# --- Load condition files ---
# Main experiment stimuli
cond_df = pd.read_excel("MST_stimuli.xlsx")

# Filter only old stimuli for the main study loop
study_df = cond_df[cond_df["cond"].isin(["old", "old_similar_source"])]

# TrialHandler for main experiment (created once) 
study_trials = data.TrialHandler(
    trialList=study_df.to_dict('records'), 
    nReps=1,
    method='random',
    name='main'
)

# --- Window and input devices ---
win = Window(fullscr=True, color='white', monitor='laptop', units='height') # Set fullscr=True when actually testing
clock = Clock()
kb = Keyboard()

# --- Settings ---
DEBUG = True  # set to False when done testing

# If True: save all scanner triggers.
# If False: only use the first trigger to start the task, as in the original script.
SAVE_TRIGGERS = True

# Store scanner trigger times if trigger saving is enabled
scanner_triggers = []

# Wait for scanner text
wait_for_scanner_txt = TextStim(
    win,
    text='Vänligen vänta',
    font='Calibri',
    color="black",
    height=0.05
)

# "Thank you for playing" screen
exit_screen = TextStim(
    win,
    text='Klart',
    font='Calibri',
    color="black",
    height=0.05
)

# Judgment question text (static)
judge_txt = "Inomhus eller utomhus?"
stim_txt = TextStim(win, text=judge_txt, pos=(
    0, 0.4), height=0.07, color='black')

# Fixation cross (reuse same object)
fix_target = TextStim(win, text='+', height=0.07, color='black')

# Image stimulus (we only change image each trial)
stim_img = ImageStim(win, image=None, units='height')
stim_img.size = (None, 0.5) # None preserves aspect ratio, 0.5 is percentage of screen, height wise

# --- Timings ---
t_fix_options = [0.5, 1.0, 1.5]  # fixation cross duration options (ISI jitter)


# Wait for scanner trigger (testing: simulate with '5')
kb.clearEvents()
wait_for_scanner_txt.draw()
win.flip()
kb.waitKeys(keyList=['5'], waitRelease=False)  # simulate scanner trigger

# Reset clock so onsets are relative to scanner start
clock.reset()

# If triggers are being saved, the initial trigger is time 0
if SAVE_TRIGGERS:
    scanner_triggers.append(0.0)


for trial in study_trials:
        # trial is now a dict with the same columns as your dataframe
        idx = study_trials.thisN  # 0,1,2,... current trial number
    
        # Path to current image
        image_path = os.path.join(f"Set_{int(trial['set'])}", trial['stim'])

        # Update the ImageStim
        stim_img.image = image_path

        # Response variables
        resp_key = None
        resp_rt = None

        # Timing
        t_fix = random.choice(t_fix_options)   # 0.5–1.5 s fixation

        # stimulus duration
        stim_dur = 3.0
        
        # These are actual timing values from the global experiment clock.
        stim_onset = None
        stim_offset = None

        # Start trial clock
        #kb.clearEvents() # Clear keyboard events
        kb.clock.reset()

        # ---- FIXATION PERIOD ----
        # Present fixation for the selected jitter duration
        fix_target.draw()
        win.flip()

        if SAVE_TRIGGERS:
            # Check for scanner triggers throughout fixation
            fix_timer = Clock()

            while fix_timer.getTime() < t_fix:
                keys = kb.getKeys(
                    keyList=['5', 'escape'],
                    waitRelease=False,
                    clear=True
                )

                for key in keys:
                    if key.name == '5':
                        scanner_triggers.append(clock.getTime())

                    elif key.name == 'escape':
                        exp.saveAsWideText(
                            exp.dataFileName + ".tsv",
                            delim="\t",
                            fileCollisionMethod="overwrite",
                        )

                        # Save scanner triggers before quitting
                        if SAVE_TRIGGERS:
                            trigger_df = pd.DataFrame({
                                "trigger_index": range(1, len(scanner_triggers) + 1),
                                "onset": scanner_triggers
                            })

                            trigger_df.to_csv(
                                os.path.join(
                                    data_dir,
                                    f"sub-{exp_info['participant']}_encoding-MST_triggers.tsv"
                                ),
                                sep="\t",
                                index=False
                            )

                        win.close()
                        quit()

        else:
            # Original behaviour
            wait(t_fix)


        # ---- STIMULUS ONSET ----
        # Draw the image and judgment text
        stim_img.draw()
        stim_txt.draw()

        # Present the stimulus.
        # Use the reset experiment clock for onset timing
        win.flip()
        stim_onset = clock.getTime()

        # Remove any response-button presses that occurred before stimulus onset,
        # without clearing scanner triggers.
        kb.getKeys(
            keyList=['1', '3'],
            waitRelease=False,
            clear=True
        )

        # Reset the keyboard clock so RT is relative to stimulus onset.
        kb.clock.reset()
        #kb.clearEvents()

        # ---- RESPONSE COLLECTION DURING STIMULUS ----
        # Keep the stimulus on screen while collecting responses
        stim_timer = Clock()

        while stim_timer.getTime() < stim_dur:

            if SAVE_TRIGGERS:
                key_list = ['1', '3', '5', 'escape']
            else:
                key_list = ['1', '3', 'escape']

            keys = kb.getKeys(
                keyList=key_list,
                waitRelease=False,
                clear=True
            )

            for key in keys:

                # Scanner trigger
                if SAVE_TRIGGERS and key.name == '5':
                    scanner_triggers.append(clock.getTime())

                # Escape
                elif key.name == 'escape':
                    exp.saveAsWideText(
                        exp.dataFileName + ".tsv",
                        delim="\t",
                        fileCollisionMethod="overwrite",
                    )

                    # Save scanner triggers before quitting
                    if SAVE_TRIGGERS:
                        trigger_df = pd.DataFrame({
                            "trigger_index": range(1, len(scanner_triggers) + 1),
                            "onset": scanner_triggers
                        })

                        trigger_df.to_csv(
                            os.path.join(
                                data_dir,
                                f"sub-{exp_info['participant']}_encoding-MST_triggers.tsv"
                            ),
                            sep="\t",
                            index=False
                        )

                    win.close()
                    quit()

                # Participant response
                elif key.name in ['1', '3'] and resp_key is None:
                    resp_key = key.name
                    resp_rt = key.rt
            
        # ---- STIMULUS OFFSET ----
        # Clear the screen at the end of the stimulus period
        # Timestamp offset using the same reset experiment clock as onset
        win.flip()
        stim_offset = clock.getTime()

        # Actual displayed duration
        duration_actual = stim_offset - stim_onset
        
        if DEBUG:
            print("\n=== NEW TRIAL ===")
            print("response:", resp_key)
            print("idx:", idx)
            print("trial dict:", trial)
            print("stim:", trial.get("stim"))
            print("cond:", trial.get("cond"))
            print("set:", trial.get("set", "NA"))
            print("lure_bin:", trial.get("lure_bin", "NA"))
            print("image_path:", image_path)
            print("rt:", resp_rt)
            print("jitter:", t_fix)
            print("onset:", stim_onset)
            print("offset:", stim_offset)
            print("duration_actual:", duration_actual)

        # ---- LOG TRIAL DATA ----
        exp.addData('trial_index', idx + 1)        # 1-based indexing
        exp.addData('stim', trial.get('stim'))     # stim path
        exp.addData('cond', trial.get('cond'))     # condition
        exp.addData('set', trial.get('set', 'NA')) # which set the image belongs to 
        exp.addData('response', resp_key or 'NA')  # response (1 or 3)
        exp.addData('rt', resp_rt if resp_rt is not None else 'NA') # response-time
        exp.addData('onset', stim_onset)           # stim onset time 
        exp.addData('duration', stim_dur)           # stim dur we want 
        exp.addData('offset', stim_offset)          # any unintended offset
        exp.addData('duration_actual', duration_actual) # actual duration
        exp.addData('jitter', t_fix)                # Jitter 
        exp.addData('lure_bin', trial.get('lure_bin', 'NA')) # lure bin
        exp.nextEntry()


# Save the completed experiment data as a true tab-separated TSV.
exp.saveAsWideText(
    exp.dataFileName + ".tsv",
    delim="\t",
    fileCollisionMethod="overwrite",
)


# Save scanner triggers ONLY if SAVE_TRIGGERS = True
if SAVE_TRIGGERS:
    trigger_df = pd.DataFrame({
        "trigger_index": range(1, len(scanner_triggers) + 1),
        "onset": scanner_triggers
    })

    trigger_df.to_csv(
        os.path.join(
            data_dir,
            f"sub-{exp_info['participant']}_encoding-MST_triggers.tsv"
        ),
        sep="\t",
        index=False
    )


exit_screen.draw()
win.flip()
kb.waitKeys()

win.close()
quit()