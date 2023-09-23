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
household level. The variables that are important to us are the following: POVPIP, HINS4, PAP, SSIP, FS, RACAIAN, RACASN, 
RACBLK, RACNH, RACPI, RACWHT, HISP, VPS, AGEP, DIS, ENG, WGTP, SERIALNO, and PUMA. The variables are defined below:

- POVPIP - Ratio of income to poverty level in the past 12 months. The values range from 0-501. 
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
one or more other races). The values are 0 = No, 1 = Yes. This is set to 1 if anyone in the household falls into this.
Then we multiply this by the household weight (WGTP) to get the total number of households that identify as American
Indian and Alaska Native. This makes it easier to aggregate the data.
- RACASIAN - Asian recode (Asian alone or in combination with one or more other races). The values are 0 = No, 1 = Yes.
This is set to 1 if anyone in the household falls into this. Then we multiply this by the household weight (WGTP) to get
the total number of households that identify as Asian. This makes it easier to aggregate the data.
- RACBLK - Black or African American recode (Black alone or in combination with one or more other races). The values
are 0 = No, 1 = Yes.nThis is set to 1 if anyone in the household falls into this. Then we multiply this by the household
weight (WGTP) to get the total number of households that identify as Black or African American. This makes it easier to
aggregate the data.
- RACNH - Native Hawaiian recode (Native Hawaiian alone or in combination with one or more other races). The values
are 0 = No, 1 = Yes. This is set to 1 if anyone in the household falls into this. Then we multiply this by the household
weight (WGTP) to get the total number of households that identify as Native Hawaiian. This makes it easier to aggregate
the data.
- RACPI - Other Pacific Islander recode (Other Pacific Islander alone or in combination with one or more other races).
The values are 0 = No, 1 = Yes. This is set to 1 if anyone in the household falls into this. Then we multiply this by
the household weight (WGTP) to get the total number of households that identify as Other Pacific Islander. This makes it
easier to aggregate the data.
- RACWHT - White recode (White alone or in combination with one or more other races). The values are 0 = No, 1 = Yes.
This is set to 1 if anyone in the household falls into this. Then we multiply this by the household weight (WGTP) to get
the total number of households that identify as White. This makes it easier to aggregate the data.
- HISP - Recoded detailed Hispanic origin. The values are 1 = Not Hispanic, 2-24 = Hispanic. We turn this into a binary
variable where 1 = Hispanic and 0 = Not Hispanic. This is set to 1 if anyone in the household falls into this. Then we
multiply this by the household weight (WGTP) to get the total number of households that identify as Hispanic. This makes
it easier to aggregate the data.
- VPS - Veteran period of service. The values are 0 = None, 1 = Gulf War (9/2001 or later), 2 = Gulf War (8/1990 to 
8/2001) and Gulf War (9/2001 or later), 3 = Gulf War (8/1990 to 8/2001) and Gulf War (9/2001 or later) and Vietnam era, 
4 = Gulf War (8/1990 to 8/2001), 5 = Gulf War (8/1990 to 8/2001) and Vietnam era, 6 = Vietnam era, 7 = Vietnam era and 
Korean War, 8 = Vietnam era and Korean War and World War II, 9 = Korean War, 10 = Korean War and World War II, 
11 = World War II, 12 = Between Gulf War and Vietnam era only, 13 = Between Vietnam era and Korean War only, 14 = 
Peacetime service before the Korean War only. This is set to 1 if anyone in the household is a veteran from any period.
Then we multiply this by the household weight (WGTP) to get the total number of households that identify as a veteran.
This makes it easier to aggregate the data.
- AGEP - Age. The values are 0-99. We turn this into a binary variable where 1 = 65 and older and 0 = 64 and younger.
This is set to 1 if anyone in the household falls into this. Then we multiply this by the household weight (WGTP) to get
the total number of households that identify as someone who is 65 and older. This makes it easier to aggregate the data.
- DIS - Disability recode. The values are 1 = With a disability, 2 = Without a disability. We turn this into a binary 
variable where 1 = Yes and 0 = No. This is set to 1 if anyone in the household falls into this. Then we multiply this 
by the household weight (WGTP) to get the total number of households that identify as someone having a disability. This 
makes it easier to aggregate the data.
- ENG - Ability to speak English. The values are 0 = N/A (Less than 5 years old or only speaks English), 1 = Very well,
2 = Well, 3 = Not well, 4 = Not at all. We turn this into a binary variable where 1 = People who speak less than very 
well. This is then set to 1 if anyone in the household falls into this. Then we multiply this by the household weight
(WGTP) to get the total number of households that identify as someone who speaks less than very well. This makes it
easier to aggregate the data.
- WGTP - PUMS household weights. This is used to weight the data.
- SERIALNO - Housing unit/GQ person serial number. This is used to merge the person and household data.
- PUMA - Public use microdata area code. This is the level of geography the data is collected at.

We then use these variables to determine eligibility for ACP with different criteria. The function used to do this is:
[determine_eligibility](Code/ACS_PUMS/acs_pums.py). The function takes in the data and the criteria to determine the 
number of people eligible for ACP at different geographic levels. The function also allows us to see how certain covered
populations are affected by these changes. The criteria are the following:

- povpip -  An integer that represents the ratio of income to poverty level in the past 12 months. By default, this is 
set to 200, which is the current value for ACP.
- has_pap - An integer that represents whether the household received public assistance income past 12 months. By 
default, this is set to 1, meaning that the household did receive public assistance income past 12 months.
- has_ssip - An integer that represents whether the household received supplementary security income past 12 months. 
By default, this is set to 1, meaning that the household did receive supplementary security income past 12 months. 
- has_hins4 - An integer that represents whether the household received Medicaid, Medical Assistance, or any kind of
government-assistance plan for those with low incomes or a disability. By default, this is set to 1, meaning that the 
household did receive Medicaid, Medical Assistance, or any kind of government-assistance plan for those with low incomes
or a disability.
- has_snap - An integer that represents whether the household received food stamps/Supplemental Nutrition Assistance
Program (SNAP) in the past 12 months. By default, this is set to 1, meaning that the household did receive food stamps/Supplemental
Nutrition Assistance Program (SNAP) in the past 12 months.

The function also takes in the level of geography that the data is analyzed at. The levels of geography are the 
following: State, County, Zip, Congressional District, Metropolitan Division, and PUMA. Along with this, we can also
see the effects of the criteria on certain covered populations. The covered populations are the following:

- aian - An integer that represents whether the household has anyone who identifies as American Indian or Alaska Native.
By default, this is set to 0, meaning that we do not want to see the effects of the changes in criteria on this 
population.
- asian - An integer that represents whether the household has anyone who identifies as Asian. By default, this is set
to 0, meaning that we do not want to see the effects of the changes in criteria on this population.
- black - An integer that represents whether the household has anyone who identifies as Black or African American. By
default, this is set to 0, meaning that we do not want to see the effects of the changes in criteria on this population.
- nhpi - An integer that represents whether the household has anyone who identifies as Native Hawaiian or Other Pacific
Islander. By default, this is set to 0, meaning that we do not want to see the effects of the changes in criteria on this
population.
- white - An integer that represents whether the household has anyone who identifies as White. By default, this is set
to 0, meaning that we do not want to see the effects of the changes in criteria on this population.
- hispanic - An integer that represents whether the household has anyone who identifies as Hispanic. By default, this is
set to 0, meaning that we do not want to see the effects of the changes in criteria on this population.
- veteran - An integer that represents whether the household has anyone who identifies as a veteran. By default, this is
set to 0, meaning that we do not want to see the effects of the changes in criteria on this population.
- elderly - An integer that represents whether the household has anyone who is 65 and older. By default, this is set to 
0, meaning that we do not want to see the effects of the changes in criteria on this population.
- disability - An integer that represents whether the household has anyone who has a disability. By default, this is set
to 0, meaning that we do not want to see the effects of the changes in criteria on this population.
- eng_very_well - An integer that represents whether the household has anyone who speaks English less than very well.
By default, this is set to 0, meaning that we do not want to see the effects of the changes in criteria on this 
population.

In the function, we filter out the households that do not meet the criteria. Then, we sum the household weights (WGTP)
to get the total number of households that meet the criteria per PUMA. The PUMAs used by the ACS PUMS data are 2010
PUMA codes, so we have to crosswalk the eligibility to 2020 PUMAs. In order to do this, we download the PUMA equivalency
file from Missouri Census Data Center. The link is: https://mcdc.missouri.edu/geography/PUMAs.html. The code that does 
this can be found: [downloadOldPumaNewPumaFile](Code/ACS_PUMS/acs_pums.py). 

After downloading the file, we use [crossWalkOldPumaNewPuma](Code/ACS_PUMS/acs_pums.py) to crosswalk the eligibility to 
2020 PUMAs. The function takes in the eligibility data and the equivalency file. The function then calls the following 
function: [code_to_source_dict](Code/ACS_PUMS/acs_pums.py). This function allows us to allocate the 2010 pumas to the 2020 pumas 
using the allocation factor estimated by the Census Bureau. This function will also be called when crosswalking the ACP
eligibility data to other geographies. It returns a dictionary that maps the 2010 PUMA to the 2020 PUMA. An example
of this is {puma22: [(puma1, afact1), (puma2, afact2), ...]}. 

After crosswalking the eligibility data to 2020 PUMAs, the determine_eligibility function has the option to crosswalk
the data to other geographies. The geographies that the data can be crosswalked to are the following: ZCTA, County,
Congressional District, and Metropolitan Division. The code that does this can be found: 
[crosswalkPUMAData](Code/ACS_PUMS/acs_pums.py). The function takes in the eligibility data, the crosswalk dictionary
returned from code_to_source_dict, the source geography, and the target geography. The function returns the eligibility
data crosswalked to the target geography. 

The crosswalk files for PUMA to ZCTA, PUMA to County, PUMA to Congressional District, PUMA to Metropolitan Division,
and PUMA to State, are downloaded from the Missouri Census Data Center. The link to download the crosswalk files is:
https://mcdc.missouri.edu/applications/geocorr.html. We use the Geocorr 2022 application. The code that downloads the
files can be found: [downloadCrossWalkFile](Code/Geocorr/Geocorr_Applications_Downloads.py). We also use 
[getMostRecentGeoCorrApplication](Code/Geocorr/Geocorr_Applications_Downloads.py) to get the most recent application 
number. getMostRecentGeoCorrApplication returns the most recent application link. We then use this link in 
downloadCrossWalkFile to download the crosswalk files. downloadCrossWalkFile takes in the application link, source
geo, target geo, and the state name. By default, state name is set to 0, meaning that it downloads for all the states
and DC. We also clean up the crosswalk files by removing the first row since the first row is an explanation of the 
columns.

If the target geography is County, we call the following function: [downloadCoveredPopFile](Code/ACS_PUMS/acs_pums.py).
This function allows us to label the counties as urban or rural. The file that contains this information is downloaded
from the Census Bureau. The link is: 
https://www.census.gov/programs-surveys/community-resilience-estimates/partnerships/ntia/digital-equity.html. The sheet
that we use for this is called "county_total_covered_population." The function returns a dataframe that contains the 
county codes and a code for whether the county is urban or rural. Then the dataframe is merged with the ACP eligibility
dataframe.

For Metropolitan Division and County crosswalk, we add the names of each area by using the crosswalk files. 


Finally, we add the participation rate to the data. The participation rate is the number of people who are participating
in ACP divided by the number of people who are eligible for ACP. 


### ACP Enrollment and Claims Tracker (ACP Tracker)

In order to collect the number of people who are participating in ACP, we use the ACP Enrollment and Claims Tracker
provided by USAC. The link to the tracker is: 
https://www.usac.org/about/affordable-connectivity-program/acp-enrollment-and-claims-tracker/. The code that collects
the data can be found: [downloadFile](Code/USAC/collect_acp_data.py). The function downloads all the .xlsx files that 
contain ACP Households by ZIP code and turns them into .csv files.

We then use [combineFiles](Code/USAC/collect_acp_data.py) to combine the .csv files into one file.

Using the same Geocorr application as the ACS PUMS data, we download the crosswalk files for ZCTA to PUMA, ZCTA to 
County, ZCTA to Congressional District, ZCTA to Metropolitan Division, and ZCTA to State 
[downloadCrossWalkFile](Code/Geocorr/Geocorr_Applications_Downloads.py). 

After downloading the crosswalk files, we use the [code_to_source_dict](Code/ACS_PUMS/acs_pums.py) function to map the
ZCTAs to the different geographies. 

We then organize the data by Zip code to make it easier to crosswalk to the different geographies. The code that does
this can be found: [organizeDataByZip](Code/USAC/collect_acp_data.py). The function takes in the data frame of the 
combined ACP Tracker data. 

Finally, we crosswalk the data to the different geographies by calling the 
[crosswalkUSACData](Code/USAC/collect_acp_data.py). 

If the target geography is Congressional District, we add a flag indicating if the district is Democratic or Republican.
1 means that the district is Democratic and 0 means that the district is Republican. The code that does this can be
found: [addCDFlag](Code/USAC/collect_acp_data.py). 
