# Creating MST stimuli
#
# Goal:
# - Start from the 192 stimulus pairs in Set 1.
# - Select 64 items that will later be tested as OLD.
# - Select another 64 studied items whose corresponding "b" images will later
#   be tested as SIMILAR.
# - Use the remaining 64 stimulus identities as NEW items.
#
# Study phase:
# - "old" + "old_similar_source" = 128 studied images
#
# Test phase:
# - "old" = 64 old images
# - "similar" = 64 lure images corresponding to the old_similar_source items
# - "new" = 64 previously unseen images


library(readxl)
library(dplyr)
library(stringr)
library(writexl)


# -------------------------------------------------------------------------
# Load and prepare the original MST stimulus information
# -------------------------------------------------------------------------

# Load the original MST file containing stimulus identities, set assignments,
# and lure-bin information.
df <- read_excel("Sets1_6_Rankings_Named.xlsx")

# Keep only stimuli belonging to Set 1.
# Retain only the variables needed for stimulus selection.
df <- df %>%
  filter(`Set Assignment` == 1) %>%
  select(`Set Assignment`, `Stim #`, `Lure Bin`)


# Rename columns to simpler names used throughout the script.
colnames(df) <- c("set", "stim", "lure_bin")

# At this point:
# df contains 192 rows and 3 columns:
# set, stim, lure_bin


# -------------------------------------------------------------------------
# Remove image-version suffixes
# -------------------------------------------------------------------------

# Each MST stimulus has an "a" and "b" image version.
# Remove these suffixes temporarily so that selection is performed using the
# underlying stimulus identity rather than the specific image version.

df <- df %>%
  mutate(stim = str_remove(stim, "b\\.jpg$"))

df <- df %>%
  mutate(stim = str_remove(stim, "a\\.jpg$"))


# -------------------------------------------------------------------------
# Helper function for sampling equal numbers from specified lure bins
# -------------------------------------------------------------------------

# This function samples the requested number of stimuli separately within
# each lure bin.
#
# dat        = data frame containing the available stimuli
# target_vec = named vector specifying how many stimuli to select from each bin
# seed       = optional random seed so that the same stimuli are selected
#              every time the script is run

sample_by_bin <- function(dat, target_vec, seed = NULL) {
  if (!is.null(seed)) set.seed(seed)
  
  dat %>%
    group_by(lure_bin) %>%
    group_split() %>%
    lapply(function(g) {
      bin <- as.character(g$lure_bin[1])
      n_here <- target_vec[bin]
      slice_sample(g, n = n_here)
    }) %>%
    bind_rows() %>%
    ungroup()
}


# -------------------------------------------------------------------------
# Select the 128 stimuli that will be shown during the study phase
# -------------------------------------------------------------------------

# Only lure bins 2-5 are used for stimuli that can later contribute to
# the OLD and SIMILAR test conditions.
df_25 <- df %>% filter(lure_bin %in% 2:5)

# Select 16 stimuli from each of lure bins 2, 3, 4, and 5.
# This gives 64 stimuli in total for each of the two studied stimulus groups.
target_old <- c(`2` = 16, `3` = 16, `4` = 16, `5` = 16)


# -------------------------------------------------------------------------
# First studied group: later tested as OLD
# -------------------------------------------------------------------------

# Randomly select 64 stimuli:
# 16 from each lure bin 2-5.
#
# These stimuli are labelled "old" because the same "a" image will later
# be presented again in the OLD condition at test.
df_old1 <- sample_by_bin(df_25, target_old, seed = 1) %>%
  mutate(cond = "old")


# Remove the 64 selected OLD stimuli from the full Set-1 pool.
# This ensures that the next group contains different stimulus identities.
df_rem1 <- anti_join(df, df_old1, by = c("set", "stim", "lure_bin"))


# Restrict the remaining pool again to lure bins 2-5 before selecting
# the second studied group.
df_25_rem1 <- df_rem1 %>% filter(lure_bin %in% 2:5)


# -------------------------------------------------------------------------
# Second studied group: source items for the later SIMILAR condition
# -------------------------------------------------------------------------

# Select another 64 stimuli:
# 16 from each lure bin 2-5.
#
# These are labelled "old_similar_source" because their "a" images are shown
# during study, while their corresponding "b" images will later be presented
# as SIMILAR items at test.
df_old2 <- sample_by_bin(df_25_rem1, target_old, seed = 2) %>%
  mutate(cond = "old_similar_source")


# Remove both studied groups from the available stimulus pool.
# The remaining stimulus identities are candidates for the NEW condition.
df_rem2 <- anti_join(df_rem1, df_old2, by = c("set", "stim", "lure_bin"))


# -------------------------------------------------------------------------
# Create the 64 NEW test stimuli
# -------------------------------------------------------------------------

# Keep all remaining lure-bin-1 stimuli.
# Bin 1 is not used for the OLD or SIMILAR conditions above.
bin1_pool  <- df_rem2 %>% filter(lure_bin == 1)

# The remaining stimuli from other lure bins can be used to fill any
# additional NEW slots needed.
other_pool <- df_rem2 %>% filter(lure_bin != 1)


# Calculate how many additional stimuli are needed to obtain exactly
# 64 NEW stimuli.
n_need <- 64 - nrow(bin1_pool)


# Safety checks:
# - Stop if there are already more than 64 remaining bin-1 stimuli.
# - Stop if there are not enough remaining stimuli to reach 64 NEW items.
if (n_need < 0) stop("More than 64 items in lure_bin==1 left; cannot include them all in new_1.")
if (nrow(other_pool) < n_need) stop("Not enough remaining items to fill new_1 to 64.")


# Combine:
# - all remaining lure-bin-1 stimuli
# - a random sample of the additional remaining stimuli needed to reach 64
#
# NEW items are assigned lure_bin = 0 because lure-bin difficulty is relevant
# to similar lures, not to previously unseen NEW images.
set.seed(3)

df_new1 <- bind_rows(
  bin1_pool,
  other_pool %>% slice_sample(n = n_need)
) %>%
  mutate(cond = "new", lure_bin = 0)


# -------------------------------------------------------------------------
# Combine the three underlying stimulus groups
# -------------------------------------------------------------------------

# At this stage there are 192 unique stimulus identities:
#
# 64 "old"
#     Studied as the "a" image and later tested with the same "a" image.
#
# 64 "old_similar_source"
#     Studied as the "a" image; their corresponding "b" images will later
#     become the SIMILAR test stimuli.
#
# 64 "new"
#     Not shown during study; presented for the first time at test.
df_cond <- bind_rows(df_old1, df_old2, df_new1)


# Check that there are 64 items in each of the three source groups.
table(df_cond$cond)

# Check the lure-bin distribution within each source group.
table(df_cond$cond, df_cond$lure_bin)


# Keep the combined source table for the next step.
df_final <- df_cond


# -------------------------------------------------------------------------
# Create the SIMILAR test condition
# -------------------------------------------------------------------------

# Copy the 64 "old_similar_source" rows.
#
# These have the same underlying stimulus identities and lure-bin values,
# but the condition label is changed to "similar".
#
# Later, these rows will receive the "b.jpg" image version, whereas the
# original old_similar_source rows retain the "a.jpg" version used at study.
df_sim1 <- df_final %>%
  filter(cond == "old_similar_source") %>%
  mutate(cond = "similar",
         lure_bin = lure_bin)  # keep same lure bin as the corresponding studied item


# -------------------------------------------------------------------------
# Create the complete master stimulus table
# -------------------------------------------------------------------------

# Combine:
# - the 64 OLD items
# - the 64 OLD_SIMILAR_SOURCE study items
# - the 64 NEW items
# - the 64 corresponding SIMILAR lure images
#
# Total = 256 rows.
#
# Study phase uses:
#   old + old_similar_source = 128 images
#
# Test phase uses:
#   old + similar + new = 192 images
df_full <- bind_rows(df_final, df_sim1)


# Check the number of rows in each condition.
table(df_full$cond)


# -------------------------------------------------------------------------
# Assign the actual image filenames
# -------------------------------------------------------------------------

# SIMILAR trials use the "b" version of each stimulus.
#
# All other rows use the "a" version:
# - old
# - old_similar_source
# - new
#
# Example:
# 011a.jpg = studied image
# 011b.jpg = corresponding similar lure
df_full <- df_full %>%
  mutate(
    stim = if_else(
      cond == "similar",
      paste0(stim, "b.jpg"),   # e.g. 011 → 011b.jpg
      paste0(stim, "a.jpg")    # e.g. 011 → 011a.jpg
    )
  )


# -------------------------------------------------------------------------
# Save the final master stimulus table
# -------------------------------------------------------------------------

write_xlsx(df_full, "MST_stimuli.xlsx")