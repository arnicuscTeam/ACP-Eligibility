import os
import urllib.request
import zipfile
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO

from pandas import Series, DataFrame


def downloadOldPumaNewPumaFile(data_dir: str):
    """
    This function will download the crosswalk file from the MCDC website, for the old puma to new puma crosswalk. It
    does so by using the requests and BeautifulSoup packages to parse the MCDC website and find the link to the file.
    It is important to do this because the pums files use the old puma codes, but the crosswalk files use the new puma codes.
    :param data_dir: The path to the data directory
    :return: None, but saves the file to the data directory
    """

    # Create the folder if it doesn't exist
    download_folder = data_dir + "GeoCorr/"

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    download_folder = download_folder + "Public-use microdata area (PUMA)/"

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # The website where the file is located
    main_site = "https://mcdc.missouri.edu"
    website = "https://mcdc.missouri.edu/geography/PUMAs.html"

    # Get the html from the website
    response = requests.get(website)

    # Parse the html
    soup = BeautifulSoup(response.text, "html.parser")
    new_link = ""

    # Find the link that has "2010 to 2020 PUMA equivalency file" as the text and get the link, and the lik ends in .csv
    links = soup.find_all("a", string="2010 to 2020 PUMA equivalency file")
    for link in links:
        if link["href"].endswith(".csv"):
            # Get the link
            new_link = link["href"]
        else:
            continue

    # Download the file
    urllib.request.urlretrieve(main_site + new_link, download_folder + "puma_equivalency.csv")

    # Clean the file
    df = pd.read_csv(download_folder + "puma_equivalency.csv")

    # Drop the first row
    df.drop(index=0, inplace=True)

    # Clean the columns
    df["state"] = df["state"].astype(str)
    df["state"] = df["state"].str.zfill(2)

    # Add the state code to the puma codes
    df["puma12"] = df["puma12"].astype(str)
    df["puma12"] = df["puma12"].str.zfill(5)
    df["puma12"] = df["state"] + df["puma12"]

    df["puma22"] = df["puma22"].astype(str)
    df["puma22"] = df["puma22"].str.zfill(5)
    df["puma22"] = df["state"] + df["puma22"]

    # Drop the state column
    df.drop(columns=["state"], inplace=True)

    # Save the file
    df.to_csv(download_folder + "puma_equivalency.csv", index=False)

    # Delete variables to save memory
    del df

    return download_folder + "puma_equivalency.csv"


def crossWalkOldPumaNewPuma(all_eligibility_df: pd.DataFrame, crosswalk_file: str) -> pd.DataFrame:
    """
    This function will crosswalk the PUMS data from 2012 pumas to 2020 pumas. It does so by reading the crosswalk file
    and creating a dictionary with the 2012 puma codes as keys and the 2020 puma codes as values. It then iterates
    through the dictionary and multiplies the data by the afact. It then aggregates the data by the 2020 puma code.
    :param all_eligibility_df: The dataframe with the eligibility data
    :param crosswalk_file: The path to the crosswalk file
    :return: A dataframe with the eligibility data crosswalked to 2020 pumas
    """

    # Clean the puma column
    df = all_eligibility_df
    df["puma22"] = df["puma22"].astype(str)
    df["puma22"] = df["puma22"].str.zfill(7)

    # Drop the percentage eligible column
    df = df.drop(columns=["Percentage Eligible"])

    # Store the columns in a list
    columns = df.columns.tolist()

    # Get the dictionary from the crosswalk file
    dictionary, col = code_to_source_dict(crosswalk_file, "puma12")
    # Dict: {puma22: [(puma12, afact), (puma12, afact), (puma12, afact)]}

    # Turn the df into a dictionary
    df_dict = df.set_index("puma22").T.to_dict("list")
    # dict: {puma12: [eligible]}

    new_df = pd.DataFrame()

    # Crosswalk the puma12 to puma22

    # Iterate through the dictionary keys
    for puma22 in dictionary.keys():

        # Iterate through the tuples in the dictionary
        for tup in dictionary[puma22]:
            # Initialize the new data list
            new_data = []
            # Get the puma12 and afact
            puma12 = tup[0]
            afact = tup[1]

            # Check if the puma12 is in the df_dict
            if puma12 in df_dict.keys():
                # Get the data
                data = df_dict[puma12]

                # Add the puma22 to the new data list
                new_data.append(puma22)

                # Iterate through the data and multiply it by the afact
                for d in data:
                    # Multiply the data by the afact and round it, then add it to the new data list
                    new_data.append(int(round(d * afact)))

                # Create a dataframe with the new data
                temp_df = pd.DataFrame([new_data], columns=columns)

                # Add the dataframe to the new dataframe
                new_df = pd.concat([new_df, temp_df], axis=0)

    # Aggregate the data by the puma
    new_df = new_df.groupby(["puma22"]).sum()

    # Reset the index
    new_df.reset_index(inplace=True)

    # Zero fill the code column
    new_df["puma22"] = new_df["puma22"].str.zfill(7)

    # Calculate the percentage eligible
    new_df["Percentage Eligible"] = new_df["Num Eligible"] / (new_df["Num Eligible"] + new_df["Num Ineligible"]) * 100

    # Round the percentage eligible to two decimal places
    new_df["Percentage Eligible"] = new_df["Percentage Eligible"].round(2)

    # Move the percentage eligible column to the 4th column
    cols = new_df.columns.tolist()
    cols = cols[:3] + cols[-1:] + cols[3:-1]
    new_df = new_df[cols]

    # Delete variables that are no longer needed
    del df_dict, dictionary, df, all_eligibility_df

    return new_df


def crosswalkPUMAData(df: pd.DataFrame, crosswalk_dict: dict, source_column: str, target_column: str) -> pd.DataFrame:
    """
    This function will crosswalk the pums data from puma to another geography. It does so by reading the crosswalk file
    and creating a dictionary with the puma codes as keys and the new geography codes as values. It then iterates
    through the dictionary and multiplies the data by the afact. It then aggregates the data by the new geography code.
    :param df: The dataframe with the puma data
    :param crosswalk_dict: The dictionary with the crosswalk data
    :param source_column: The column name for the source geography, which would be the puma column
    :param target_column: The column name for the target geography, which would be the new geography column
    :return: A dataframe with the puma data crosswalked to the new geography
    """

    columns = df.columns.tolist()

    # Replace the code column with the new code column
    columns[0] = target_column

    # Initialize a dictionary to store the original data
    puma_data = {}

    # Group the data by the code column
    data_groupby = df.groupby(source_column)

    # Iterate through every code in the crosswalk file
    for puma in df[source_column].unique():
        # Get the data for the puma Code
        data = data_groupby.get_group(puma)

        # Convert the data to a list
        data = data.values.tolist()

        # Get the data for the puma
        row = data[0][1:]

        # Remove the period from the puma
        try:
            puma = puma.split(".")[0]
        except:
            pass
        puma = puma.zfill(7)

        # Add the puma and data to the dictionary
        puma_data[puma] = row

    # Create a new list to store the new data
    new_list = []

    # Iterate through every code in the crosswalk file
    for key, value in crosswalk_dict.items():
        # Iterate through every value in the list
        for val in value:
            # Get the puma and afact
            puma = str(val[0])

            # Remove the period from the puma
            if "." in puma:
                puma = puma.split(".")[0]

            puma = puma.zfill(7)

            # Get the afact
            afact = val[1]

            # If the puma is in the dictionary, then calculate the new number eligible and ineligible
            if puma in puma_data.keys():
                temp_list = [key]
                for d in puma_data[puma]:
                    temp_list.append(int(round(d * afact)))
                new_list.append(temp_list)

    # Create a new dataframe with the new list
    new_df = pd.DataFrame(new_list, columns=columns)

    # Group the data by the code column
    new_df = new_df.groupby(target_column).sum()

    # Reset the index
    new_df.reset_index(inplace=True)

    # Return the new dataframe
    return new_df


def code_to_source_dict(crosswalk_file: str, source_col: str) \
        -> tuple[dict[str, list[tuple[str, Series | Series | DataFrame]]], str | Any]:
    """
    This function will create a dictionary with the target codes as keys and the source codes as values. It will also
    return the column name for the target codes. It does so by reading the crosswalk file and finding the column with
    the target codes. It then groups the source codes by the target codes, and creates a dictionary with the target
    codes as keys and the source codes as values.
    An example of the dictionary is:
    {puma22: [(zcta1, afact1), (zcta2, afact2), ...]}
    :param crosswalk_file: The path to the crosswalk file
    :param source_col: the column name for the source codes
    :return: a dictionary with the target codes as keys and the source codes as values, and the column name for the
    target codes
    """

    code_col = ""

    # Get the column name for the source geography
    df_zeros = pd.read_csv(crosswalk_file)
    for col in df_zeros.columns.tolist():
        if source_col in col:
            source_col = col
            break

    # Read the crosswalk file to get the column names
    df_zeros = pd.read_csv(crosswalk_file, dtype={source_col: str})

    # Read the column names
    col_names = df_zeros.columns.tolist()
    col_names.remove(source_col)

    # Find the column with the target codes
    for col in col_names:
        if "zcta" in col:
            code_col = col
            break
        elif "county" in col and "tract" not in col_names:
            code_col = col
            break
        elif "metdiv" in col:
            code_col = col
            break
        elif "puma" in col:
            code_col = col
            break
        elif "tract" in col:
            code_col = col
            break
        elif "cd" in col:
            code_col = col
            break
        elif "sdbest" in col:
            code_col = col
            break
        elif "sdelem" in col:
            code_col = col
            break
        elif "sdsec" in col:
            code_col = col
            break
        elif "sduni" in col:
            code_col = col
            break
        elif "state" in col:
            code_col = col
            break

    try:
        df = pd.read_csv(crosswalk_file, dtype={source_col: str, code_col: str})
    except:
        df = pd.read_csv(crosswalk_file, dtype={source_col: str})

    # Group the source by code
    cw_lists = df.groupby(code_col)[source_col].apply(list)

    # Initialize the dictionary to store the data
    code_zcta_dict = {}

    # Iterate through the target codes
    for index, row in cw_lists.items():
        data = []
        for item in row:
            # Find the afact on the crosswalk dataframe by the source code and the target code
            afact = df.loc[(df[source_col] == item) & (df[code_col] == index), 'afact'].iloc[0]

            # Create a tuple with the source code and the afact
            tup = (str(item), afact)

            # Add the tuple to the list
            data.append(tup)

        # Add the list to the dictionary
        code_zcta_dict[str(index)] = data

    # Return the dictionary and the column name for the target codes
    return code_zcta_dict, code_col


def downloadPUMSFiles(data_directory: str):
    """
    This function downloads the most recent 1-year PUMS files from the Census website, and saves them to the PUMS
    folder. It downloads both .zip files for household and person data for every state. It does so by using the
    requests and BeautifulSoup packages to parse the Census website and find the links to the files. It then uses
    urllib to download the files. The files are saved to the PUMS folder in the data directory into state folders.
    """

    # Path to the folder where the PUMS files will be saved
    pums_folder = data_directory + "ACS_PUMS"

    # Create the folder if it doesn't exist
    if not os.path.exists(pums_folder):
        os.makedirs(pums_folder)

    state_data_folder = pums_folder + "/state_data"

    if not os.path.exists(state_data_folder):
        os.makedirs(state_data_folder)

    pums_folder = state_data_folder + "/"

    acs_webpage = "https://www2.census.gov/programs-surveys/acs/data/pums/"

    year = "1"

    # Request the website
    response = requests.get(acs_webpage)

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table element
    table = soup.find("table")

    # Find all the links in the table
    links = table.find_all("a")

    # Get the most recent year, which is the last link in the table
    new_link = acs_webpage + links[-1]["href"] + year + "-Year/"

    # Request the website
    response = requests.get(new_link)

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table element
    table = soup.find("table")

    # Find all the links in the table
    links = table.find_all("a")

    # Download the zip files
    for link in links:

        # Do not download the US file
        if "us" not in link.text:

            # Only download the csv files
            if link.text.startswith("csv_"):

                # Get the state acronym from the file name
                period = link.text.find(".zip")
                state_acronym = link.text[period - 2:period]

                # Create the folder if it doesn't exist
                if not os.path.exists(pums_folder + state_acronym):
                    os.makedirs(pums_folder + state_acronym)

                # Download the file
                urllib.request.urlretrieve(new_link + link["href"], pums_folder + state_acronym + "/" + link.text)

    # Delete variables that are no longer needed
    del table
    del links
    del soup
    del response


def create_state_sheet(df_person: pd.DataFrame, df_household: pd.DataFrame, output_file: str, state_code: str):
    """

    :param df_person: the person dataframe from the PUMS person zip file
    :param df_household: the household dataframe from the PUMS household zip file
    :param output_file: the name of the file to save the data to
    :param state_code: the state code, used to create the full 7-digit puma code
    :return: None, but saves the data to a csv file

    This function will create a csv file containing the eligibility criteria for ACP for each SERIALNO in the PUMS data,
    as well as the PUMA code, the weight, and demographic information. This will be used later to determine eligibility
    depending on the projected criteria.

    """

    # Merge the two dataframes
    merged = pd.merge(df_person, df_household, on="SERIALNO", how="left", suffixes=('_person', '_household'),
                      indicator=True, validate="m:1")

    # Drop the RT column that came from the household file
    merged = merged.drop(columns=['RT_household'])

    # Drop the _merge column
    merged = merged.drop(columns=['_merge'])

    # Generate program eligibility variables
    merged["HINS4"] = merged["HINS4"].replace(2, 0)
    merged["number_hins4"] = merged.groupby("SERIALNO")["HINS4"].transform("sum")
    merged["has_hins4"] = (merged["number_hins4"] >= 1).astype(int)

    # Turn the pap variable into a binary variable of 0 or 1
    merged["number_pap"] = merged.groupby("SERIALNO")["PAP"].transform("sum")
    merged["has_pap"] = (merged["number_pap"] > 0).astype(int)

    # Turn the ssip variable into a binary variable of 0 or 1
    merged["number_ssip"] = merged.groupby("SERIALNO")["SSIP"].transform("sum")
    merged["has_ssip"] = (merged["number_ssip"] > 0).astype(int)

    # Turn the snap variable into a binary variable of 0 or 1
    merged["FS"] = merged["FS"].replace(2, 0)
    merged["number_fs"] = merged.groupby("SERIALNO")["FS"].transform("sum")
    merged["has_snap"] = (merged["number_fs"] > 0).astype(int)

    merged["PUMA_person"] = merged["PUMA_person"].astype(int)

    # Collect the demographic information
    merged["RACAIAN"] = merged["RACAIAN"].astype(int)
    merged["RACASN"] = merged["RACASN"].astype(int)
    merged["RACBLK"] = merged["RACBLK"].astype(int)
    merged["RACNH"] = merged["RACNH"].astype(int)
    merged["RACPI"] = merged["RACPI"].astype(int)
    merged["RACWHT"] = merged["RACWHT"].astype(int)
    merged["HISP"] = merged["HISP"].astype(int)
    merged["AGEP"] = merged["AGEP"].astype(int)
    merged["DIS"] = merged["DIS"].astype(int)
    merged["ENG"] = merged["ENG"].fillna(0)
    merged["ENG"] = merged["ENG"].astype(int)

    # Turn the hispanic variable into a binary variable. In the original file, one means not hispanic; anything else is
    # a specific hispanic origin. We want to turn this into a binary variable of zero or one, where one means hispanic.
    merged["HISP"] = merged["HISP"].replace(1, 0)
    merged["HISP"] = (merged["HISP"] > 0).astype(int)

    # Veteran period of service into a binary variable
    merged["VPS"] = merged["VPS"].fillna(0)
    merged["VPS"] = (merged["VPS"] > 0).astype(int)

    # Elderly variable
    merged["AGEP"] = merged["AGEP"].fillna(0)
    merged["Elderly"] = (merged["AGEP"] >= 60).astype(int)

    # People with disabilities variable
    merged["DIS"] = merged["DIS"].replace(2, 0)

    # People who speak English less than "very well"
    merged["ENG"] = (merged["ENG"] > 1).astype(int)

    # Rename the columns
    merged = merged.rename(columns={"RACAIAN": "American Indian and Alaska Native", "RACASN": "Asian",
                                    "RACBLK": "Black or African American", "RACNH": "Native Hawaiian",
                                    "RACPI": "Pacific Islander", "RACWHT": "White", "HISP": "Hispanic or Latino",
                                    "VPS": "Veteran", "ENG": "English less than very well"})

    # Create a new dataframe with the variables we need
    # First means we get that information from the first person in the household
    # Mean means we get that information from the mean of the household
    # Max means we keep the highest value for that variable in the household, being either 0 or 1 for binary variables
    collapsed = merged.groupby("SERIALNO").agg({
        "POVPIP": "first",
        "has_pap": "mean",
        "has_ssip": "mean",
        "has_hins4": "mean",
        "has_snap": "mean",
        "PUMA_person": "mean",
        "WGTP": "mean",
        "American Indian and Alaska Native": "max",
        "Asian": "max",
        "Black or African American": "max",
        "Native Hawaiian": "max",
        "Pacific Islander": "max",
        "White": "max",
        "Hispanic or Latino": "max",
        "Veteran": "max",
        "Elderly": "max",
        "DIS": "max",
        "English less than very well": "max"
    })

    # Multiply the race variables by the weight, rounded and converted to an integer, so that we can sum them later
    collapsed["American Indian and Alaska Native"] = (
            collapsed["American Indian and Alaska Native"] * collapsed["WGTP"]).round(0).astype(int)
    collapsed["Asian"] = (collapsed["Asian"] * collapsed["WGTP"]).round(0).astype(int)
    collapsed["Black or African American"] = (collapsed["Black or African American"] * collapsed["WGTP"]).round(
        0).astype(int)
    collapsed["Native Hawaiian"] = (collapsed["Native Hawaiian"] * collapsed["WGTP"]).round(0).astype(int)
    collapsed["Pacific Islander"] = (collapsed["Pacific Islander"] * collapsed["WGTP"]).round(0).astype(int)
    collapsed["White"] = (collapsed["White"] * collapsed["WGTP"]).round(0).astype(int)
    collapsed["Hispanic or Latino"] = (collapsed["Hispanic or Latino"] * collapsed["WGTP"]).round(0).astype(int)
    collapsed["Veteran"] = (collapsed["Veteran"] * collapsed["WGTP"]).round(0).astype(int)
    collapsed["Elderly"] = (collapsed["Elderly"] * collapsed["WGTP"]).round(0).astype(int)
    collapsed["DIS"] = (collapsed["DIS"] * collapsed["WGTP"]).round(0).astype(int)
    collapsed["English less than very well"] = (collapsed["English less than very well"] * collapsed["WGTP"]).round(
        0).astype(int)

    # Drop the rows where WGTP is 0, they will not be used regardless
    collapsed = collapsed[collapsed["WGTP"] != 0]

    # Round all the variables to integers
    collapsed["POVPIP"] = collapsed["POVPIP"].round(0).astype(int)
    collapsed["has_pap"] = collapsed["has_pap"].round(0).astype(int)
    collapsed["has_ssip"] = collapsed["has_ssip"].round(0).astype(int)
    collapsed["has_hins4"] = collapsed["has_hins4"].round(0).astype(int)
    collapsed["has_snap"] = collapsed["has_snap"].round(0).astype(int)
    collapsed["WGTP"] = collapsed["WGTP"].round(0).astype(int)

    # Add the state code to the puma code
    collapsed["PUMA_person"] = collapsed["PUMA_person"].astype(str)
    collapsed["PUMA_person"] = collapsed["PUMA_person"].str.split(".").str[0]
    collapsed["PUMA_person"] = collapsed["PUMA_person"].str.zfill(5)
    collapsed["PUMA_person"] = state_code + collapsed["PUMA_person"]

    # Save the data
    collapsed.to_csv(output_file)

    # Delete variables that are no longer needed
    del merged
    del collapsed


def everyStateEligibility(data_directory: str):
    """
    This function will determine eligibility for ACP for all states. It does so by iterating through all the states and
    calling the determineEligibility function for each state. It will save the data to a csv file in the state folder.
    :param data_directory: The path to the data directory which contains the ACS_PUMS folder
    :return: None, but saves the data to csv files
    """

    # Path to the folder where the PUMS files are saved
    data_dir = data_directory + "ACS_PUMS/"
    state_dir = data_dir + "state_data/"

    # Iterate through all folders in the ACS_PUMS folder
    for state in os.listdir(state_dir):
        # Initialize the dataframes
        person_df = pd.DataFrame()

        household_df = pd.DataFrame()

        # Create the file name
        end_file = state_dir + state + "/" + state + "-eligibility.csv"

        # Iterate through all zipped files in the state folder
        for zip_folder in os.listdir(state_dir + state):
            # Only unzip the zip files
            if zip_folder.endswith(".zip"):
                # Get the folder name
                folder_name = state_dir + state + "/" + zip_folder

                # Unzip the file
                with zipfile.ZipFile(folder_name, 'r') as zip_file:
                    # Iterate through all files in the zipped folder
                    for file in zip_file.namelist():
                        # Only read the csv files
                        if file.endswith("csv"):
                            # Get the state code from the file name
                            end = file.find(".csv")

                            state_code = str(file[end - 2:end])

                            state_code = state_code.zfill(2)

                            # Read the file
                            if file.startswith("psam_h"):
                                household_df = pd.concat(
                                    [household_df, pd.read_csv(zip_file.open(file), dtype={"PUMA": str})])
                            elif file.startswith("psam_p"):
                                person_df = pd.concat(
                                    [person_df, pd.read_csv(zip_file.open(file), dtype={"PUMA": str})])

        # Call the function to determine eligibility
        create_state_sheet(person_df, household_df, end_file, state_code)

    # Delete variables that are no longer needed
    del person_df
    del household_df


def downloadCoveredPopFile():
    """
    This function will get the covered population data from the Census website. It does so by using the requests and
    BeautifulSoup packages to parse the Census website and find the link to the file. It will store the data into a
    dataframe and return it. This will be used to determine if a county is rural or not.
    :return: A dataframe with the covered population data
    """

    # Website
    website = "https://www.census.gov/programs-surveys/community-resilience-estimates/partnerships/ntia/digital-equity.html"

    # Get the response from the website
    response = requests.get(website)

    # Parse the response
    soup = BeautifulSoup(response.content, "html.parser")

    # Search for all a tags
    a_tags = soup.find_all("a")

    # Initialize the new link
    link = ""

    # Iterate through all a tags
    for tag in a_tags:
        # If the text is "County and Census Tract Data," then get the link
        if "County and Census Tract Data" in tag.text:
            # Get the link
            link = tag["href"]
            break

    # Download the file from the link
    if link != "":
        # Download the file
        response = requests.get("https:" + link)

        # Save the file to a variable
        excel_data = BytesIO(response.content)

        # Read the Excel file
        # noinspection PyTypeChecker
        df = pd.read_excel(excel_data, sheet_name="county_total_covered_population", skiprows=0)

        # Drop all the columns that have MOE
        df = df.loc[:, ~df.columns.str.contains("MOE")]

        # Drop the geography_name column
        df.drop(columns=["geography_name"], inplace=True)

        # Turn the rural column into a 0 or 1
        df["rural"] = df["rural"].replace({"Rural": "1", "Not rural": "0"})

        # Drop the row if rural is null
        df = df[df["rural"].notnull()]

        # Turn geo_id into a string and zero fill it
        df["geo_id"] = df["geo_id"].astype(str)
        df["geo_id"] = df["geo_id"].str.zfill(11)
        df["geo_id"] = df["geo_id"].str[:5]

        # Return the dataframe
        return df

    # If there is no link
    else:
        print("No link found.")


def determine_eligibility(data_dir: str, povpip: int = 200, has_pap: int = 1, has_ssip: int = 1, has_hins4: int = 1,
                          has_snap: int = 1, geography: str = "Public-use microdata area (PUMA)",
                          aian: int = 0, asian: int = 0, black: int = 0, nhpi: int = 0, white: int = 0,
                          hispanic: int = 0, veteran: int = 0, elderly: int = 0, disability: int = 0,
                          eng_very_well: int = 0, end_folder: str = "Change_Eligibility/"):
    """
    This function will determine eligibility for ACP for all states. It does so by iterating through all the states and
    reading the eligibility data for each state. It will then aggregate the data by the geography specified. It will
    then save the data to a csv file in the state folder.
    :param data_dir: The path to the data directory which contains the ACS_PUMS folder
    :param povpip: The desired income threshold
    :param has_pap: Whether to use the PAP criteria 0|1
    :param has_ssip: Whether to use the SSIP criteria 0|1
    :param has_hins4: Whether to use the HINS4 criteria 0|1
    :param has_snap: Whether to use the SNAP criteria 0|1
    :param geography: The geography to aggregate the data by
    :param aian: Whether we want to see the effects to the American Indian and Alaska Native population 0|1
    :param asian: Whether we want to see the effects to the Asian population 0|1
    :param black: Whether we want to see the effects to the Black or African American population 0|1
    :param nhpi: Whether we want to see the effects to the Native Hawaiian population 0|1
    :param white: Whether we want to see the effects to the White population 0|1
    :param hispanic: Whether we want to see the effects to the Hispanic or Latino population 0|1
    :param veteran: Whether we want to see the effects to the Veteran population 0|1
    :param elderly: Whether we want to see the effects to the Elderly population 0|1
    :param disability: Whether we want to see the effects to the Disability population 0|1
    :param eng_very_well: Whether we want to see the effects to the population that speaks English very well 0|1
    :param end_folder: The folder to save the data to
    :return: None, but saves the data to csv files
    """

    # Path to relevant folders
    pums_folder = data_dir + "ACS_PUMS/"
    state_folder = pums_folder + "state_data/"
    current_data = pums_folder + "Current_Eligibility/"
    test_data = pums_folder + end_folder
    geocorr_folder = data_dir + "GeoCorr/"
    puma_cw_folder = geocorr_folder + "Public-use microdata area (PUMA)/"


    if not os.path.exists(current_data):
        os.makedirs(current_data)

    if not os.path.exists(test_data):
        os.makedirs(test_data)



    # Dictionary to map the geography to the code column and crosswalk file
    geography_mapping = {
        "Public-use microdata area (PUMA)": ("puma22", "puma_equivalency.csv"),
        "118th Congress (2023-2024)": (
            "cd118", "United_States_Public-Use-Microdata-Area-(Puma)_to_118Th-Congress-(2023-2024).csv"),
        "State": ("state", "United_States_Public-Use-Microdata-Area-(Puma)_to_State.csv"),
        "County": ("county", "United_States_Public-Use-Microdata-Area-(Puma)_to_County.csv"),
        "ZIP/ZCTA": ("zcta", "United_States_Public-Use-Microdata-Area-(Puma)_to_ZIP-ZCTA.csv"),
        "Unified school district": (
            "sduni20", "United_States_Public-Use-Microdata-Area-(Puma)_to_Unified-School-District.csv"),
        "Metropolitan division": (
            "metdiv20", "United_States_Public-Use-Microdata-Area-(Puma)_to_Metropolitan-Division.csv")
    }

    # Get the code column and crosswalk file
    code_column, cw_name = geography_mapping[geography]
    cw_file = puma_cw_folder + cw_name

    # Create the columns for the dataframe
    columns = ["puma22", "Num Eligible", "Num Ineligible", "Percentage Eligible"]

    # Initialize the variables for the columns of covered populations
    covered_populations = [
        ("American Indian and Alaska Native", "aian"),
        ("Asian", "asian"),
        ("Black or African American", "black"),
        ("Native Hawaiian", "nhpi"),
        ("White", "white"),
        ("Hispanic or Latino", "hispanic"),
        ("Veteran", "veteran"),
        ("Elderly", "elderly"),
        ("DIS", "disability"),
        ("English less than very well", "eng_very_well")
    ]

    # Add the columns for the covered populations if they are used
    for population_name, population_var in covered_populations:
        if locals()[population_var] == 1:
            columns.append(population_name + " Eligible")

    # Create a dataframe to store the results, which will first be stored in puma
    main_df = pd.DataFrame(columns=columns)

    # Iterate through all folders in the State data folder
    for state in os.listdir(state_folder):
        # Save the path to the state folder
        state_files = state_folder + state + "/"
        # Iterate through all files in the state folder
        for file in os.listdir(state_files):
            # Only read the csv files
            if file.endswith(".csv"):
                # Read the file
                temp_df = pd.read_csv(state_files + file, header=0)

                # Drop SERIALNO column
                temp_df = temp_df.drop(columns=["SERIALNO"])

                # Turn all acp_eligible values to 0
                temp_df["acp_eligible"] = 0

                # If the povpip is not 0, then use it as a criteria
                if povpip != 0:
                    # Turn all acp_eligible values to 1 if they meet the criteria and if we are using the criteria
                    temp_df.loc[(temp_df["POVPIP"] <= povpip) | ((temp_df["has_pap"] == 1) & (has_pap == 1)) |
                                ((temp_df["has_ssip"] == 1) & (has_ssip == 1)) |
                                ((temp_df["has_hins4"] == 1) & (has_hins4 == 1)) |
                                ((temp_df["has_snap"] == 1) & (has_snap == 1)), "acp_eligible"] = 1

                # If the povpip is 0, then use the other criteria
                else:
                    temp_df.loc[((temp_df["has_pap"] == 1) & (has_pap == 1)) |
                                ((temp_df["has_ssip"] == 1) & (has_ssip == 1)) |
                                ((temp_df["has_hins4"] == 1) & (has_hins4 == 1)) |
                                ((temp_df["has_snap"] == 1) & (has_snap == 1)), "acp_eligible"] = 1

                # Find the total number eligible for every PUMA_person
                unique_puma_person = temp_df["PUMA_person"].unique()

                # Iterate through every PUMA_person
                for puma_person in unique_puma_person:
                    # Create a dataframe for the PUMA_person
                    puma_df = temp_df.loc[temp_df["PUMA_person"] == puma_person]

                    # Find the number eligible and ineligible
                    eligible_df = puma_df.loc[puma_df["acp_eligible"] == 1]
                    ineligible_df = puma_df.loc[puma_df["acp_eligible"] == 0]

                    eligible = eligible_df["WGTP"].sum()
                    ineligible = ineligible_df["WGTP"].sum()

                    # Calculate the percentage eligible
                    percentage_eligible = eligible / (eligible + ineligible)

                    # Create a list to store the data
                    data = [puma_person, eligible, ineligible, percentage_eligible]

                    # If the covered populations are used, then add the number eligible for each population
                    for population_name, population_var in covered_populations:
                        if locals()[population_var] == 1:
                            data.append(eligible_df[population_name].sum())

                    # Add the puma_person and percentage eligible to the main dataframe
                    new_df = pd.DataFrame([data], columns=columns)

                    # If the main df is empty, set it equal to the new df
                    if main_df.empty:
                        main_df = new_df
                    else:
                        # Add the new dataframe to the main dataframe
                        main_df = pd.concat([main_df, new_df], axis=0)

    # Sort the main dataframe by puma22
    main_df.sort_values(by=["puma22"], inplace=True)

    # Round the percentage eligible column to two decimal places
    main_df["Percentage Eligible"] = (main_df["Percentage Eligible"] * 100).round(2)

    # PUMAs are seven digits, so add leading zeros
    main_df["puma22"] = main_df["puma22"].astype(str)
    main_df["puma22"] = main_df["puma22"].str.zfill(7)

    # If it is using 2010 PUMAs, then crosswalk the data to 2020 PUMAs
    if '0600102' in main_df['puma22'].values:
        cw_File = downloadOldPumaNewPumaFile(data_dir)
        main_df = crossWalkOldPumaNewPuma(main_df, cw_File)

    # Create the file name
    file_name = "percentage_eligible"

    # Boolean to determine if there was a change to see the difference in eligibility
    add_col = False

    # If all the criteria are used, then do not add anything to the file name
    if povpip == 200 and has_pap == 1 and has_ssip == 1 and has_hins4 == 1 and has_snap == 1:
        file_name = "eligibility-by"
        file_name = current_data + file_name
    # Else, add the criteria to the file name dynamically
    else:
        if povpip != 200:
            file_name += "_povpip_" + str(povpip)
        if has_pap == 1:
            file_name += "_has_pap"
        if has_ssip == 1:
            file_name += "_has_ssip"
        if has_hins4 == 1:
            file_name += "_has_hins4"
        if has_snap == 1:
            file_name += "_has_snap"
        add_col = True

    # Determine if any covered populations are used
    if (aian == 1 and asian == 1 and black == 1 and nhpi == 1 and white == 1 and hispanic == 1 and veteran == 1
            and elderly == 1 and disability == 1 and eng_very_well == 1):
        file_name += "-covered_populations"

        # Add the file name to the end file
        if add_col:
            file_name = test_data + file_name
    else:
        for population_name, population_var in covered_populations:
            if locals()[population_var] == 1:
                file_name += "_" + population_var

        # Add the file name to the end file
        if add_col:
            file_name = test_data + file_name

    # If the geography is PUMA, then do not crosswalk the data
    if code_column == "puma22":
        # If we are looking at changes, add the current percentage eligible column
        if add_col:
            # Read the original file
            if (aian == 1 or asian == 1 or black == 1 or nhpi == 1 or white == 1 or hispanic == 1 or veteran == 1 or
                    elderly == 1 or disability == 1 or eng_very_well == 1):
                original_file = current_data + "eligibility-by-covered_populations-puma22.csv"
            else:
                original_file = current_data + "eligibility-by-puma22.csv"
            original_df = pd.read_csv(original_file, header=0, dtype={"puma22": str})

            # Rename all the columns to have "Current" in front of them
            original_df = original_df.rename(columns={"Num Eligible": "Current Num Eligible",
                                                      "Num Ineligible": "Current Num Ineligible",
                                                      "Percentage Eligible": "Current Percentage Eligible"})

            # If covered populations are used, open that file and rename the columns
            if "covered_populations" in original_file:
                # Iterate through the covered populations
                for population_name, population_var in covered_populations:
                    if locals()[population_var] == 1:
                        original_df = original_df.rename(
                            columns={population_name + " Eligible": "Current " + population_name + " Eligible"})
                    else:
                        original_df = original_df.drop(columns=[population_name + " Eligible"])

            # Round the percentage eligible column to two decimal places
            main_df["Percentage Eligible"] = main_df["Percentage Eligible"].round(2)
            original_df["Current Percentage Eligible"] = original_df["Current Percentage Eligible"].round(2)

            # Reset the index
            original_df.reset_index(inplace=True)
            main_df.reset_index(inplace=True)
            original_df.drop(columns=["index"], inplace=True)
            main_df.drop(columns=["index"], inplace=True)

            # Add the current percentage eligible column to the main dataframe
            main_df = pd.concat([main_df, original_df], axis=1, join="outer", ignore_index=False, sort=True)

            # Calculate the difference between the two covered populations eligible columns
            for population_name, population_var in covered_populations:
                if locals()[population_var] == 1:
                    main_df["difference_" + population_var] = main_df[population_name + " Eligible"] - main_df[
                        "Current " + population_name + " Eligible"]
                    main_df["difference_percentage_" + population_var] = ((main_df["difference_" + population_var] /
                                                                           main_df["Current " + population_name +
                                                                                   " Eligible"]) * 100).round(2)
                    # Drop the columns that are no longer needed
                    main_df = main_df.drop(
                        columns=["Current " + population_name + " Eligible", "difference_" + population_var])

            # Combine duplicate columns
            main_df = main_df.loc[:, ~main_df.columns.duplicated()]

            # Move the current percentage eligible column to the second position
            columns = main_df.columns.tolist()

            # Remove the current percentage eligible column
            columns.remove("Current Percentage Eligible")

            # Add the current percentage eligible column to the second position
            columns.insert(1, "Current Percentage Eligible")

            # Remove the current percentage eligible column
            columns.remove("Current Num Ineligible")

            # Add the current percentage eligible column to the second position
            columns.insert(1, "Current Num Ineligible")

            # Remove the current percentage eligible column
            columns.remove("Current Num Eligible")

            # Add the current percentage eligible column to the second position
            columns.insert(1, "Current Num Eligible")

            # Reorder the columns
            main_df = main_df[columns]

        # Save the data
        file_name += "-puma22.csv"

        # Fill the null values with 0
        main_df = main_df.fillna(0)

        # Save the dataframe to a csv file
        main_df.to_csv(file_name, index=False)

    # Else, crosswalk the data
    else:
        # Drop the percentage eligible column
        main_df = main_df.drop(columns=["Percentage Eligible"])

        # Read the crosswalk file
        dc, col_name = code_to_source_dict(cw_file, "puma")

        # Add the geography to the file name
        file_name += f"-{col_name}.csv"

        # Crosswalk the data
        new_df = crosswalkPUMAData(main_df, dc, "puma22", col_name)

        # Make the percentage eligible column
        new_df["Percentage Eligible"] = new_df["Num Eligible"] / (
                new_df["Num Eligible"] + new_df["Num Ineligible"]) * 100

        # Round the percentage eligible column to two decimal places
        new_df["Percentage Eligible"] = new_df["Percentage Eligible"].round(2)

        # If we are looking at changes, add the current percentage eligible column
        if add_col:
            # Read the original file
            if (aian == 1 or asian == 1 or black == 1 or nhpi == 1 or white == 1 or hispanic == 1 or veteran == 1 or
                    elderly == 1 or disability == 1):
                original_file = current_data + f"eligibility-by-covered_populations-{col_name}.csv"
            else:
                original_file = current_data + f"eligibility-by-{col_name}.csv"
            original_df = pd.read_csv(original_file, header=0)

            # Rename all the columns to have "Current" in front of them
            original_df = original_df.rename(columns={"Num Eligible": "Current Num Eligible",
                                                      "Num Ineligible": "Current Num Ineligible",
                                                      "Percentage Eligible": "Current Percentage Eligible"})


            # If covered populations are used, open that file and rename the columns
            if "covered_populations" in original_file:
                # Iterate through the covered populations
                for population_name, population_var in covered_populations:
                    if locals()[population_var] == 1:
                        original_df = original_df.rename(
                            columns={population_name + " Eligible": "Current " + population_name + " Eligible"})
                    else:
                        original_df = original_df.drop(columns=[population_name + " Eligible"])


            # Round the percentage eligible column to two decimal places
            new_df["Percentage Eligible"] = new_df["Percentage Eligible"].round(2)
            original_df["Current Percentage Eligible"] = original_df["Current Percentage Eligible"].round(2)

            # Reset the index
            original_df.reset_index(inplace=True)
            new_df.reset_index(inplace=True)
            original_df.drop(columns=["index"], inplace=True)
            new_df.drop(columns=["index"], inplace=True)

            # Add the current percentage eligible column to the main dataframe
            new_df = pd.concat([new_df, original_df], axis=1, join="outer", ignore_index=False, sort=True)

            # Calculate the difference between the two covered populations eligible columns
            for population_name, population_var in covered_populations:
                # If the population is used, then calculate the difference
                if locals()[population_var] == 1:
                    # Calculate the difference between the two covered populations eligible columns
                    new_df["difference_" + population_var] = new_df[population_name + " Eligible"] - new_df[
                        "Current " + population_name + " Eligible"]

                    # Calculate the difference percentage
                    new_df["difference_percentage_" + population_var] = (new_df["difference_" + population_var] /
                                                                         new_df["Current " + population_name +
                                                                                " Eligible"] * 100).round(2)
                    new_df = new_df.drop(
                        columns=["Current " + population_name + " Eligible", "difference_" + population_var])

            # Combine duplicate columns
            new_df = new_df.loc[:, ~new_df.columns.duplicated()]

            # Move the current percentage eligible column to the second position
            columns = new_df.columns.tolist()

            # Remove the current percentage eligible column
            columns.remove("Current Percentage Eligible")

            # Add the current percentage eligible column to the second position
            columns.insert(1, "Current Percentage Eligible")

            # Remove the current percentage eligible column
            columns.remove("Current Num Ineligible")

            # Add the current percentage eligible column to the second position
            columns.insert(1, "Current Num Ineligible")

            # Remove the current percentage eligible column
            columns.remove("Current Num Eligible")

            # Add the current percentage eligible column to the second position
            columns.insert(1, "Current Num Eligible")

            # Reorder the columns
            new_df = new_df[columns]

        # If the code column is county, then add the rural column and county name column
        if code_column == "county":
            if "rural" not in new_df.columns.tolist():
                # Download the covered population file
                covered_pops_df = downloadCoveredPopFile()

                # Rename the columns
                covered_pops_df = covered_pops_df.rename(columns={"geo_id": "county"})

                # Turn the county column into a string and zero fill it
                covered_pops_df["county"] = covered_pops_df["county"].astype(str)
                covered_pops_df["county"] = covered_pops_df["county"].str.zfill(5)

                new_df["county"] = new_df["county"].astype(str)
                new_df["county"] = new_df["county"].str.zfill(5)

                # Only keep county and rural columns
                covered_pops_df = covered_pops_df[["county", "rural"]]

                # Merge the dataframes
                new_df = pd.merge(new_df, covered_pops_df, on="county", how="left")

            # Move the rural column to the second position
            columns = new_df.columns.tolist()

            # Move the rural column to the second position
            columns.remove("rural")

            # Add the rural column to the second position
            columns.insert(1, "rural")

            # Reorder the columns
            new_df = new_df[columns]
            if "CountyName" not in new_df.columns.tolist():
                # Read the crosswalk file
                df = pd.read_csv(cw_file, header=0, dtype={"county": str})

                # Drop the duplicate county rows
                df = df.drop_duplicates(subset=["county"])

                df["county"] = df["county"].astype(str)
                df["county"] = df["county"].str.zfill(5)

                new_df["county"] = new_df["county"].astype(str)
                new_df["county"] = new_df["county"].str.zfill(5)

                # Add the "CountyName" column to the new dataframe
                new_df = pd.merge(new_df, df[["county", "CountyName"]], on="county", how="left")

            # Move the CountyName column to the second position
            columns = new_df.columns.tolist()

            # Remove the CountyName column
            columns.remove("CountyName")

            # Add the CountyName column to the second position
            columns.insert(1, "CountyName")

            # Reorder the columns
            new_df = new_df[columns]

        # If the code column is metdiv, then add the metdiv name column
        if code_column == "metdiv20":
            if "MetDivName" not in new_df.columns.tolist():
                # Read the crosswalk file
                df = pd.read_csv(cw_file, header=0, dtype={"metdiv20": str})

                # Drop the duplicate metdiv rows
                df = df.drop_duplicates(subset=["metdiv20"])

                df["metdiv20"] = df["metdiv20"].astype(str)
                df["metdiv20"] = df["metdiv20"].str.zfill(5)

                new_df["metdiv20"] = new_df["metdiv20"].astype(str)
                new_df["metdiv20"] = new_df["metdiv20"].str.zfill(5)

                # Add the "MetDivName" column to the new dataframe
                new_df = pd.merge(new_df, df[["metdiv20", "MetDivName"]], on="metdiv20", how="left")

            # Move the MetDivName column to the second position
            columns = new_df.columns.tolist()

            # Remove the MetDivName column
            columns.remove("MetDivName")

            # Add the MetDivName column to the second position
            columns.insert(1, "MetDivName")

            # Reorder the columns
            new_df = new_df[columns]

        # Fill the null values with 0
        new_df = new_df.fillna(0)

        # Save the dataframe to a csv file
        new_df.to_csv(file_name, index=False)


def add_participation_rate_combined(data_dir: str):

    """
    This function will add the participation rate to the combined files. It does so by iterating through all the
    combined files and adding the most recent subscriber count for that geography. It then creates the participation rate
    by dividing the total subscribers by the total eligible.
    :param data_dir:
    :return: None, but saves the data to csv files
    """

    pums_folder = data_dir + "ACS_PUMS/"
    change_data = pums_folder + "Change_Eligibility/"
    acp_data = data_dir + "ACP_Households/"
    total_acp_folder = acp_data + "Final_Files/"

    # Get all the files in the change data folder
    combined_files = [f for f in os.listdir(change_data) if f.endswith(".csv") and "combined" in f]

    # Iterate through all the files
    for file in combined_files:
        # Get the geography
        geography = file.split("-")[-1].split(".")[0]

        # Read the file
        pums_df = pd.read_csv(os.path.join(change_data, file), header=0, dtype={geography: str})

        # Add the total subscribers column
        pums_df["Current Total Subscribers"] = 0

        # Look for the total acp file with the same geography
        total_acp_file = [f for f in os.listdir(total_acp_folder) if f.endswith(".csv") and geography in f]

        # If the file exists, then add the participation rate
        if len(total_acp_file) > 0:
            acp_df = pd.read_csv(os.path.join(total_acp_folder, total_acp_file[0]), header=0, dtype={geography: str})

            # Find unique values for the geography
            unique_geography = acp_df[geography].unique()

            # Iterate through all the unique values
            for area in unique_geography:
                area_df = acp_df.loc[acp_df[geography] == area].copy()

                # Sort them ascending by Data Month
                area_df.sort_values(by=["Data Month"], inplace=True)

                # Find the most recent month
                most_recent_month = area_df["Data Month"].iloc[-1]

                # Find the Total Subscribers column for the most recent month
                total_subscribers = area_df.loc[area_df["Data Month"] == most_recent_month, "Total Subscribers"].iloc[0]

                # Add the total subscribers to the pums dataframe
                pums_df.loc[pums_df[geography] == area, "Current Total Subscribers"] = total_subscribers

        # Current Participation Rate
        pums_df["Current Participation Rate"] = (
            ((pums_df["Current Total Subscribers"] / pums_df["Current Num Eligible"]) * 100).round(2))

        # Save the data
        pums_df.to_csv(os.path.join(change_data, file), index=False)


def cleanData(data_dir: str):
    """
    This function will clean the test data and combine it into one file. It does so by iterating through all the
    files in the test data folder and combining them into one file for each geography.
    :param data_dir:
    :return: None, but saves the data to csv files
    """

    # Path to relevant folders
    pums_folder = data_dir + "ACS_PUMS/"
    test_folder = pums_folder + "Change_Eligibility/"

    # Get all the files in the test folder
    all_files = [f for f in os.listdir(test_folder) if os.path.isfile(os.path.join(test_folder, f))]

    # Get all the geographies
    geographies = [f.split(".")[0].split("-")[-1] for f in all_files if f.endswith(".csv")]

    # Remove duplicates
    geographies = list(set(geographies))

    # Iterate through all the geographies
    for geography in geographies:

        # Initialize the main dataframe
        main_df = pd.DataFrame()

        # Iterate through all the files in the test folder
        for file in os.listdir(test_folder):

            # Only read the csv files that are for the current geography and are not the combined file
            if file.endswith(".csv") and geography in file and "combined" not in file:

                # Get the povpip
                povpip = file.split("_")[3]

                # Read the file
                df = pd.read_csv(test_folder + file, header=0, dtype={geography: str})

                # Rename the columns
                columns = df.columns.tolist()

                # For columns that are not the geography, add the povpip to the column name
                for column in columns:

                    # If the column is the geography, then do not add the povpip
                    if geography == column:
                        pass

                    # If the column is the current percentage eligible, then do not add the povpip to the column name
                    elif "Current" in column:
                        pass

                    # If the column is rural, then do not add the povpip to the column name
                    elif "rural" in column:
                        pass

                    # If the column is CountyName, then do not add the povpip to the column name
                    elif "Name" in column:
                        pass

                    # Else, add the povpip to the column name
                    else:
                        df = df.rename(columns={column: column + "_" + povpip})

                # If the main dataframe is empty, set it equal to the dataframe
                if main_df.empty:
                    main_df = df

                # Else, merge the dataframes
                else:
                    # If the geography is not county, then merge the dataframes on the geography and current percentage
                    if geography != "county" and geography != "metdiv20":
                        main_df = pd.merge(main_df, df, on=[geography, "Current Percentage Eligible",
                                                            "Current Num Eligible", "Current Num Ineligible"],
                                           how="outer")

                    # Else, merge the dataframes on the geography, current percentage, and rural
                    elif geography == "county":
                        main_df = pd.merge(main_df, df, on=[geography, "Current Percentage Eligible", "rural",
                                                            "Current Num Eligible", "Current Num Ineligible",
                                                            "CountyName"],
                                           how="outer")

                    elif geography == "metdiv20":
                        main_df = pd.merge(main_df, df, on=[geography, "Current Percentage Eligible",
                                                            "Current Num Eligible", "Current Num Ineligible",
                                                            "MetDivName"],
                                           how="outer")

        # Move the current percentage eligible column to the second position
        columns = main_df.columns.tolist()

        # Remove the current percentage eligible column
        columns.remove("Current Percentage Eligible")

        # Add the current percentage eligible column to the second position
        columns.insert(1, "Current Percentage Eligible")

        # Remove the current percentage eligible column
        columns.remove("Current Num Ineligible")

        # Add the current percentage eligible column to the second position
        columns.insert(1, "Current Num Ineligible")

        # Remove the current percentage eligible column
        columns.remove("Current Num Eligible")

        # Add the current percentage eligible column to the second position
        columns.insert(1, "Current Num Eligible")

        # Reassign the columns
        main_df = main_df[columns]

        # If the code column is county, make the rural column be the second column
        if geography == "county":
            # Get the columns
            columns = main_df.columns.tolist()

            # Remove the rural column
            columns.remove("rural")

            # Add the rural column to the second position
            columns.insert(1, "rural")

            # Reassign the columns
            main_df = main_df[columns]

        # Save the data
        main_df.to_csv(test_folder + f"combined-{geography}.csv", index=False)


def createDeliverableFiles(data_dir: str):
    pums_folder = data_dir + "ACS_PUMS/"

    deliverable_folder = pums_folder + "deliverable_file/"
    national_folder = pums_folder + "National_Changes/"

    # Turn the excel file into a csv file
    df = pd.read_excel(deliverable_folder + "State_135_v2.xlsx", header=0)

    df["state"] = df["state"].astype(str).str.zfill(2)

    df = df.dropna(subset=["Medicaid expansion (1)"])

    df = df[["state", " stusps", "Medicaid expansion (1)", "Party", "ACP Participation July 23 (2)",
             "Avg claim $ Jan-Jul 2023 (3)"]]

    for file in os.listdir(national_folder):
        if file.endswith(".csv"):
            df_change = pd.read_csv(national_folder + file, header=0, dtype={"state": str})

            if " stusps" not in df_change.columns.tolist():
                df_change["state"] = df_change["state"].astype(str).str.zfill(2)

                df_change = pd.merge(df_change, df, on="state", how="left")

                cols = df_change.columns.tolist()

                cols.remove(" stusps")

                cols.insert(1, " stusps")

                df_change = df_change[cols]

            df_change["Total dif"] = df_change["Current Num Eligible"] - df_change["Num Eligible"]

            df_change["Weighed dif"] = df_change["Total dif"] * df_change["ACP Participation July 23 (2)"]

            df_change["Saving in $"] = df_change["Weighed dif"] * df_change["Avg claim $ Jan-Jul 2023 (3)"]

            df_change.to_csv(national_folder + file, index=False)


def aggregateSavings(data_dir: str):
    pums_folder = data_dir + "ACS_PUMS/"
    national_folder = pums_folder + "National_Changes/"
    deliverable_folder = pums_folder + "deliverable_file/"

    main_df = pd.DataFrame(columns=["POVPIP", "National Saving"])

    for file in os.listdir(national_folder):
        povpip = file.split("_")[3]
        df = pd.read_csv(national_folder + file, header=0)

        total_savings = round((df["Saving in $"].sum()), 2)

        new_df = pd.DataFrame([[povpip, total_savings]], columns=["POVPIP", "National Saving"])

        main_df = pd.concat([main_df, new_df], axis=0)

    main_df = main_df.sort_values(by=["POVPIP"])


    main_df.to_csv(deliverable_folder + "national_savings.csv", index=False)




if __name__ == '__main__':
    # cleanData("../../Data/")
    # add_participation_rate_combined("../../Data/")
    createDeliverableFiles("../../Data/")
    aggregateSavings("../../Data/")
