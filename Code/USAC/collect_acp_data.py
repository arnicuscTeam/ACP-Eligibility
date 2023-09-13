import os

import pandas as pd
import requests
from bs4 import BeautifulSoup

from Code.ACS_PUMS.acs_pums import code_to_source_dict


def downloadFile(data_directory: str):
    """
    Function to download the ACP data from the usac website. Allows us to collect participation rate at the
    zip code level. The files are downloaded in xlsx format and then converted to csv format.
    :param data_directory: Path to the data directory
    :return: None
    """

    # Create directory for downloads
    download_directory = os.path.join(data_directory, "ACP_Households", "Middle_Files")
    os.makedirs(download_directory, exist_ok=True)

    # Webpage where all the data is located
    website = "https://www.usac.org/about/affordable-connectivity-program/acp-enrollment-and-claims-tracker/"

    # Main link for the website
    main_link = "https://www.usac.org"

    # Request the website
    response = requests.get(website)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links and the text associated with them
    links = soup.find_all("a")

    # Filter the links to only include the links that contain the text "ACP Households by Zip Code"
    links = [link for link in links if "ACP Households by Zip Code" in link.text]

    # Loop through all the links
    for link in links:

        # Store the download link
        download_link = link["href"]

        # In order to name the files dynamically
        file_name = download_link.split("/")[-1]

        # Download the file
        r = requests.get(main_link + download_link, allow_redirects=True)

        # Save the file
        excel_path = os.path.join(download_directory, file_name)
        open(excel_path, "wb").write(r.content)

        # Read the Excel file
        df = pd.read_excel(excel_path, engine="openpyxl")

        # Rename columns so that all the files have the same column names
        column_mapping = {
            "ZipCode": "zcta",
            "Zip Code": "zcta",
            "Net New Enrollments total": "Net New Enrollments Total",
        }
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)

        # Ensure the 'zcta' column is a string with five characters
        df["zcta"] = df["zcta"].astype(str).str.zfill(5)

        # Save the csv
        csv_name = file_name.replace(".xlsx", ".csv")
        csv_path = os.path.join(download_directory, csv_name)

        df.to_csv(csv_path, index=False)

        # Delete the xlsx file
        os.remove(excel_path)

        # Delete the df to save memory
        del df


def combineFiles(data_directory: str) -> str:
    """
    This function combines all the csv files that were downloaded from the usac website into one csv file.
    :param data_directory: Path to the data directory
    :return: Path to the final csv file
    """

    acp_folder = os.path.join(data_directory, "ACP_Households")
    final_folder = os.path.join(acp_folder, "Final_Files")

    # Check if the Final_Files folder exists
    if not os.path.exists(final_folder):
        os.makedirs(final_folder)

    # Path to the folder containing the csv files
    path = os.path.join(data_directory, "ACP_Households", "Middle_Files")

    # List of all the files in the folder
    files = [file for file in os.listdir(path) if "ACP-Households-by-Zip" in file]

    # Name of the final csv file
    final_name = os.path.join(final_folder, "Total-ACP-Households-by-zcta.csv")

    # Create a dataframe to store the data
    final_df = pd.DataFrame()

    # Loop through all the files
    for file in files:
        # Read the file
        df = pd.read_csv(os.path.join(path, file))

        # Add the data to the final dataframe using concat
        final_df = pd.concat([final_df, df])

        # Delete the file
        os.remove(os.path.join(path, file))

    # Zip Code column is a string with five characters
    final_df["zcta"] = final_df["zcta"].astype(str).str.zfill(5)

    # Group the data by Zip Code and sort by Data Month
    final_df = final_df.groupby("zcta").apply(lambda x: x.sort_values(["Data Month"], ascending=True)).reset_index(
        drop=True)

    # Drop the duplicates
    final_df.drop_duplicates(inplace=True)

    # Fill in the missing values with 0
    final_df.fillna(0, inplace=True)

    # Turn all the columns except for the Zip Code column into integers
    for col in final_df.columns:
        if col != "zcta" and col != "Data Month":
            final_df[col] = final_df[col].astype(int)

    # Drop the row where zcta is 00000
    final_df = final_df[final_df["zcta"] != "00000"]

    # Save the final dataframe as a csv file
    final_df.to_csv(final_name, index=False)

    # Return the path to the final csv file
    return final_name


def organizeDataByZip(df: pd.DataFrame) -> dict[str, list[list[str, float]]]:
    """
    This function organizes the data by Zip Code. The data is stored in a dictionary where the keys are the Zip Codes
    and the values are lists of lists. The inner lists contain the data for each month. The first item in the inner list
    is the data month, the second item is the Zip Code, and the rest of the items are the data.
    :param df: The dataframe containing the usac data for all the Zip Codes
    :return: A dictionary where the keys are the Zip Codes and the values are lists of lists
    """

    # Group the data by Zip Code
    data_groupby = df.groupby("zcta")

    # Create a dictionary to store the Zip Codes and the corresponding data
    zip_data_dict = {}

    # Loop through the Zip Codes
    for zip_code in df["zcta"].unique():
        # Get the data for the Zip Code
        data = data_groupby.get_group(zip_code)

        # Convert the data to a list
        data = data.values.tolist()

        # Add the Zip Code and data to the dictionary
        zip_data_dict[zip_code] = data

    return zip_data_dict


def crosswalkUSACData(data_directory: str, code_dict: dict[str, list[tuple[str, float]]],
                      zip_data_dict: dict[str, list[list[str, float]]], code_col: str):
    """
    This function crosswalks the ACP data to the target geography codes. The data is then aggregated by the target
    geography code and data month.
    :param data_directory: Path to the data directory
    :param code_dict: A dictionary where the keys are the target geography codes and the values are lists of tuples.
    :param zip_data_dict: A dictionary where the keys are the Zip Codes and the values are lists of lists.
    :param code_col: The name of the column containing the target geography codes
    :return: None, the data is saved to a csv file
    """

    # Create a string for the file to be saved to
    end_file = data_directory + "ACP_Households/Final_Files/Total-ACP-Households-by-" + code_col + ".csv"

    # Create a list to store the new data
    new_list = []

    # Loop through the keys in the zip_data_dict, which are zip codes
    for key in zip_data_dict.keys():
        # Loop through the keys in the code_dict, which are target geography codes
        # values are lists of tuples of zcta codes and their afact [(ZCTA, AF), (ZCTA, AF), ...]
        for middle_key, value in code_dict.items():
            # Loop through the tuples in the list
            for small_key in value:
                # If the zip code is in the list of zcta codes
                if key == small_key[0]:
                    # Add the target geography code, afact, and data to the new list
                    new_list.append([middle_key, small_key[1], zip_data_dict[key]])

    """
    EXAMPLE OF ONE ROW IN THE NEW_LIST:

    ['03730', 0.2696, [['2022-01-01', '90010', 0.0, 0.0, 2.0, 9.0, 11.0, 8.0, 0.0, 54.0, 39.0, 101.0],
     ['2022-02-01', '90010', 0.0, 0.0, 6.0, 7.0, 13.0, 8.0, 0.0, 60.0, 46.0, 114.0]]]

    """

    # Create a list to store the new data
    second_list = []

    # Loop through the items in the list of [target geography codes, afact, and [data]]
    for item in new_list:
        # Get the target geography code and afact
        target_geo_code = item[0]
        afact = item[1]
        # Loop through the data rows in the data list
        for ls in item[2]:
            # Create a new list with the target geography code and afact, which will be appended to second_list
            new_ls = [ls[0], target_geo_code]
            # Loop through the items in the data list, starting at the second item
            for item_two in ls[2:]:
                # Multiply the item by the afact and append it to the new list
                new_ls.append(int(round(item_two * afact)))
            # Append the new list to second_list
            second_list.append(new_ls)

    """
    EXAMPLE OF ONE ROW IN THE SECOND_LIST:

    ['2022-01-01', '03730', 0.0, 0.0, 0.5392, 2.4264, 2.9656000000000002, 2.1568, 0.0, 14.5584, 10.5144, 27.2296]

    Note: There can be multiple rows with the same puma22 code and data month, so the data needs to be aggregated
    """

    # Turn second_list into a dataframe, columns are the same as the columns in the original data file
    df = pd.DataFrame(second_list,
                      columns=['Data Month', code_col, 'Net New Enrollments Alternative Verification Process',
                               'Net New Enrollments Verified by School', 'Net New Enrollments Lifeline',
                               'Net New Enrollments National Verifier Application',
                               'Net New Enrollments Total', 'Total Alternative Verification Process',
                               'Total Verified by School', 'Total Lifeline',
                               'Total National Verifier Application', 'Total Subscribers'])

    # Aggregate the data if there are multiple rows with the same puma22 code and data month
    df = df.groupby(['Data Month', code_col]).sum()

    # Round the data to the nearest whole number
    df = df.round(0)

    # Reset the index
    df = df.reset_index()

    # Sort the dataframe by the target geography code and data month
    df = df.sort_values(by=[code_col, 'Data Month'])

    # Save the dataframe as a csv file
    df.to_csv(end_file, index=False)

    # Delete the dataframes to save memory
    del df
    del new_list
    del second_list
    del code_dict
    del zip_data_dict


def ZCTAtoTargetGeography(data_directory: str, target_geo: str, source_col: str = "zcta"):

    final_folder = os.path.join(data_directory, "ACP_Households", "Final_Files")
    final_zip_file = os.path.join(final_folder, "Total-ACP-Households-by-zcta.csv")
    df = pd.read_csv(final_zip_file)

    geocorr_folder = os.path.join(data_directory, "Geocorr")
    zcta_cw_folder = os.path.join(geocorr_folder, "ZIP_ZCTA")

    # Find the crosswalk file
    if target_geo == "Metropolitan division":
        cw_file = os.path.join(zcta_cw_folder, "United_States_Zip-Zcta_to_Metropolitan-Division.csv")
    elif target_geo == "Public-use microdata area (PUMA)":
        cw_file = os.path.join(zcta_cw_folder, "United_States_Zip-Zcta_to_Public-Use-Microdata-Area-(Puma).csv")
    elif target_geo == "County":
        cw_file = os.path.join(zcta_cw_folder, "United_States_Zip-Zcta_to_County.csv")
    elif target_geo == "State":
        cw_file = os.path.join(zcta_cw_folder, "United_States_ZIP-ZCTA_to_State.csv")




    dc, col_name = code_to_source_dict(cw_file, source_col)
    zip_data = organizeDataByZip(df)

    crosswalkUSACData(data_directory, dc, zip_data, col_name)

    if "cd" in col_name:
        addCDFlag(data_directory, col_name)


if __name__ == "__main__":
    # downloadFile("../../Data/")
    combineFiles("../../Data/")
    pass
