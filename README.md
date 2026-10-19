This is the repository for the MST study-test phase which will be performed in the fMRI machine.

Folder Set_1 and Set_2 contain the images that will be studied, as well as the foils and lures that will be shown during the test phase.

Folder Set_4 contains images used for the practice phases.

The "data" folder contains saved data from the MST scripts.

MST_practice_stimuli.xlsx contains the paths to the practice-stimuli images in Set_4.

MST_stimuli.xlsx contains the stimuli used in the main MST study and test phases. Only lure bins 2–5 are used. Lure bin 1 is excluded since those lures are almost indistinguishable from the targets.

Sets1_6_Rankings_Named.xlsx contains the stimulus rankings and names for Sets 1–6.

MST_STUDY_fmri.py is the actual study-phase program the participants will view while in the MRI machine.
    Right now the stim_dur is set to 3.0 s and the fixation cross varies between 0.5, 1.0, and 1.5 s.

MST_STUDY_fmri_practice.py contains the instructions and practice trials for the MST study phase.

MST_TEST_fmri.py is the actual test-phase program the participants will view while in the MRI machine.
    Right now the stim_dur is set to 3.0 s and the fixation cross varies between 0.5, 1.0, and 1.5 s.

MST_TEST_fmri_practice.py contains the instructions and practice version of MST_TEST_fmri.py. It includes three practice trials with feedback and allows the instructions or practice trials to be repeated.

Stimulus change reasoning.txt is a text document explaining why we changed some of the stimuli (arachnophobia and cultural relevance).

create_MST_stimuli.R is a script used to create MST_stimuli.xlsx.

fixation_cross_only.py is a program that only shows a fixation cross to be used during resting-state fMRI.