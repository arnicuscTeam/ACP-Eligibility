# Data Collection Process

## Data Sources

### American Community Survey PUMS (ACS PUMS)
https://www2.census.gov/programs-surveys/acs/data/pums/

The code that shows how the files were collected can be found: [downloadPUMSFiles](Code/ACS_PUMS/acs_pums.py). This 
downloads the .zip files for household and person data for each state.

Since the files are downloaded as .zip files, we need to unzip and extract the columns that will be used for data 
analysis. The code for this can be found: [everyStateEligibility](Code/ACS_PUMS/acs_pums.py). everyStateEligibility 
iterates over every state and calls the following function: [create_state_sheet](Code/ACS_PUMS/acs_pums.py).

create_state_sheet extracts the columns that will be used for data analysis and saves the data as a .csv file. It does 
so by merging the person file with the household file on the SERIALNO variable. This collapses the data to the 
household level. The variables that are important to us are the following: HINS4, PAP, SSIP, FS, RACAIAN, RACASN, 
RACBLK, RACNH, RACPI, RACWHT, HISP, VPS, AGEP, DIS, ENG, and WGTP. The variables are defined below:

- HINS4 - Medicaid, Medical Assistance, or any kind of government-assistance plan for those with low incomes or a
  disability. The values are 1 = Yes, 2 = No. We turn this into a binary variable where 1 = Yes and 0 = No.
- PAP - Public assistance income past 12 months. The values are -1 = N/A, 0 = None, 4-30000 = $4 to $30,000. 
We turn this into a binary variable where 1 = Yes and 0 = No by summing the PAP received by the household and if it is
more than 0, then we set the value to 1.
- SSIP - Supplementary Security Income past 12 months. The values are -1 = N/A, 0 = None, 4-30000 = $4 to $30,000. 
We turn this into a binary variable where 1 = Yes and 0 = No by summing the SSIP received by the household and if it is
more than 0, then we set the value to 1.
- FS - Yearly food stamp/Supplemental Nutrition Assistance Program (SNAP) recipiency. The values are 0 = N/A, 1 = Yes,
    2 = No. We turn this into a binary variable where 1 = Yes and 0 = No.
- RACAIAN - American Indian and Alaska Native recode (American Indian and Alaska Native alone or in combination with 
one or more other races). The values are 0 = No, 1 = Yes.
- RACASIAN - Asian recode (Asian alone or in combination with one or more other races). The values are 0 = No, 1 = Yes.
- RACBLK - Black or African American recode (Black alone or in combination with one or more other races). The values
are 0 = No, 1 = Yes.
- RACNH - Native Hawaiian recode (Native Hawaiian alone or in combination with one or more other races). The values
are 0 = No, 1 = Yes.
- RACPI - Other Pacific Islander recode (Other Pacific Islander alone or in combination with one or more other races).
The values are 0 = No, 1 = Yes.
- RACWHT - White recode (White alone or in combination with one or more other races). The values are 0 = No, 1 = Yes.
- HISP - Recoded detailed Hispanic origin. The values are 1 = Not Hispanic, 2-24 = Hispanic. We turn this into a binary
variable where 1 = Hispanic and 0 = Not Hispanic.
- VPS - Veteran period of service. The values are 0 = None, 1 = Gulf War (9/2001 or later), 2 = Gulf War (8/1990 to 
8/2001) and Gulf War (9/2001 or later), 3 = Gulf War (8/1990 to 8/2001) and Gulf War (9/2001 or later) and Vietnam era, 
4 = Gulf War (8/1990 to 8/2001), 5 = Gulf War (8/1990 to 8/2001) and Vietnam era, 6 = Vietnam era, 7 = Vietnam era and 
Korean War, 8 = Vietnam era and Korean War and World War II, 9 = Korean War, 10 = Korean War and World War II, 
11 = World War II, 12 = Between Gulf War and Vietnam era only, 13 = Between Vietnam era and Korean War only, 14 = 
Peacetime service before the Korean War only.
- AGEP - Age. The values are 0-99. We turn this into a binary variable where 1 = 65 and older and 0 = 64 and younger.
- DIS - Disability recode. The values are 1 = With a disability, 2 = Without a disability. We turn this into a binary 
variable where 1 = Yes and 0 = No.
- ENG - Ability to speak English. The values are 0 = N/A (Less than 5 years old or only speaks English), 1 = Very well,
2 = Well, 3 = Not well, 4 = Not at all. We turn this into a binary variable where 1 = People who speak less than very 
well.
- WGTP - PUMS household weights. This is used to weight the data.
