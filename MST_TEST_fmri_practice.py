# MST - TEST PHASE - PRACTICE

from psychopy.gui import DlgFromDict
from psychopy.visual import Window, TextStim, ImageStim
from psychopy.core import Clock, quit, wait
from psychopy.hardware.keyboard import Keyboard
from psychopy import data
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
    dataFileName=os.path.join(data_dir, f"MST_test_practice_{exp_info['participant']}")
)

# --- Exactly three practice images ---
practice_trials = [
    {'stim': '001a.jpg', 'cond': 'GAMMAL', 'direction': 'Vänster', 'correct_key': '1'},
    {'stim': '001b.jpg', 'cond': 'LIK',     'direction': 'Upp',     'correct_key': '2'},
    {'stim': '011a.jpg', 'cond': 'NY',      'direction': 'Höger',   'correct_key': '3'}
]

# --- Window and input devices ---
win = Window(fullscr=True, color='white', monitor='laptop', units='height')
kb = Keyboard()

# --- Stimuli ---
stim_img = ImageStim(win, image=None, units='height')
stim_img.size = (None, 0.5)

top_txt = TextStim(win, text='', pos=(0, 0.4), height=0.055, color='black')
bottom_txt = TextStim(
    win,
    text='',
    pos=(0, -0.38),
    height=0.04,
    color='black',
    wrapWidth=1.5
)

fix_target = TextStim(win, text='+', height=0.07, color='black')

# --- Timings ---
stim_dur = 3.0
t_fix_options = [0.5, 1.0, 1.5]
feedback_dur = 1.5

# --- Instructions ---
# Response box: 1 = Vänster, 2 = Upp, 3 = Höger
instruction_screens = [
    (
        '001a.jpg',
        'GAMMAL – VÄNSTER',
        'Den här bilden är exakt samma som en bild du såg i den tidigare '
        'övningsomgången.\n\nGAMMAL svarar du med VÄNSTER.',
        '1'
    ),
    (
        '001b.jpg',
        'LIK – UPP',
        'Den här bilden liknar bilden du såg tidigare, men är inte exakt samma.\n\n'
        'LIK svarar du med UPP.',
        '2'
    ),
    (
        '011a.jpg',
        'NY – HÖGER',
        'Den här bilden visades inte i den tidigare övningsomgången.\n\n'
        'NY svarar du med HÖGER.',
        '3'
    )
]

run_instructions = True

while True:

    # --- Instructions ---
    if run_instructions:
        for image, title, text, correct_key in instruction_screens:
            stim_img.image = os.path.join('Set_4', image)
            top_txt.text = title
            top_txt.pos = (0, 0.4)
            bottom_txt.text = text
            bottom_txt.pos = (0, -0.38)

            top_txt.draw()
            stim_img.draw()
            bottom_txt.draw()
            win.flip()

            keys = kb.waitKeys(keyList=[correct_key, 'escape'])
            if keys[0].name == 'escape':
                win.close()
                quit()

        # Fixation only:
        # Enter = continue to practice
        # Space = restart instructions
        fix_target.draw()
        win.flip()

        keys = kb.waitKeys(keyList=['return', 'space', 'escape'])

        if keys[0].name == 'escape':
            win.close()
            quit()

        if keys[0].name == 'space':
            continue

        run_instructions = False

    # --- Practice ---
    random.shuffle(practice_trials)

    for idx, trial in enumerate(practice_trials):

        stim_img.image = os.path.join('Set_4', trial['stim'])
        resp_key = None
        resp_rt = None
        t_fix = random.choice(t_fix_options)

        kb.clearEvents()
        kb.clock.reset()
        trial_clock = Clock()

        while True:
            t = trial_clock.getTime()

            if t < stim_dur:
                top_txt.text = 'Gammal, lik eller ny?'
                top_txt.pos = (0, 0.4)

                stim_img.draw()
                top_txt.draw()

            elif t < stim_dur + t_fix:
                fix_target.draw()

            else:
                break

            win.flip()

            if resp_key is None:
                keys = kb.getKeys(
                    keyList=['1', '2', '3', 'escape'],
                    waitRelease=False,
                    clear=False
                )

                if keys:
                    key = keys[0]

                    if key.name == 'escape':
                        win.close()
                        quit()

                    resp_key = key.name
                    resp_rt = key.rt

        correct = resp_key == trial['correct_key']

        if resp_key is None:
            top_txt.text = f"Inget svar.\n\nRätt svar: {trial['cond']} ({trial['direction']})"
        elif correct:
            top_txt.text = 'Rätt!'
        else:
            top_txt.text = f"Fel.\n\nRätt svar: {trial['cond']} ({trial['direction']})"

        top_txt.pos = (0, 0)
        top_txt.draw()
        win.flip()
        wait(feedback_dur)

        exp.addData('trial_index', idx + 1)
        exp.addData('stim', trial['stim'])
        exp.addData('cond', trial['cond'])
        exp.addData('response', resp_key or 'NA')
        exp.addData('correct', correct)
        exp.addData('rt', resp_rt if resp_rt is not None else 'NA')
        exp.addData('fixation_duration', t_fix)
        exp.nextEntry()

    # Fixation only:
    # Enter = repeat practice
    # Space = restart instructions
    fix_target.draw()
    win.flip()

    keys = kb.waitKeys(keyList=['return', 'space', 'escape'])

    if keys[0].name == 'escape':
        win.close()
        quit()

    if keys[0].name == 'space':
        run_instructions = True
    else:
        run_instructions = False
