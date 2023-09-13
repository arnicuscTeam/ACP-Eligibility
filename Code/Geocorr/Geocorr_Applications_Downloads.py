import os
import time
import urllib.request

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def getMostRecentGeoCorrApplication(data_directory: str, link_year: int = 0) -> str:
    """
    This function gets the link to the most recent GeoCorr Application using requests. It is useful when the user wants
    to download the crosswalk files for a specific year. If the user does not specify a year, the function will use the
    link to the most recent application.
    :param data_directory: The path to the data directory
    :param link_year: The year of the application that the user wants to download the crosswalk files for
    :return: The link to the most recent GeoCorr Application
    """

    directory = data_directory + "GeoCorr"

    # Create directory for downloads
    if not os.path.exists(directory):
        os.makedirs(directory)

    # GeoCorr Applications website
    website = "https://mcdc.missouri.edu/applications/geocorr.html"

    # Main link for the website
    main_link = "https://mcdc.missouri.edu"

    # Request the website
    response = requests.get(website)

    # Parse the website
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links
    links = soup.find_all("a")

    # Filter the links to only include the links that contain the text "Geocorr"
    links = [link for link in links if "Geocorr" in link.text]

    # The second link is the most recent application
    if link_year != 0:
        for link in links:
            if str(link_year) in link.text:
                newest_link = main_link + link["href"]
    else:
        newest_link = main_link + links[1]["href"]

    return newest_link


def downloadCrossWalkFile(weblink: str, data_directory: str, source_geography: str,
                          target_geography: str, state_name: str = "0") -> tuple[str, str]:
    """
    This function downloads the crosswalk file for the specified source and target geographies. It also cleans the
    crosswalk file by calling the cleanCrossWalkFile function.
    :param weblink: The link to the GeoCorr Application
    :param data_directory: The path to the data directory
    :param state_name: The name of the state in case the user wants to download the crosswalk file for a specific state
    :param source_geography: The source geography
    :param target_geography: The target geography
    :return: The path to the crosswalk file and the name of the source geography column
    """

    options = ["state", "county", "county subdivision (township, mcd)",
               "place (city, town, village, cdp, etc.)", "census tract", "census block group", "census block",
               "zip/zcta", "public-use microdata area (puma)", "core-based statistical area (cbsa)",
               "cbsa type (metro or micro)", "metropolitan division", "combined statistical area",
               "necta (new england only)", "necta division (new england only)", "combined necta (new england only)",
               "american indian / alaska native / native hawaiian areas", "state legislative district — upper chamber",
               "state legislative district — lower chamber", "unified school district", "elementary school district",
               "secondary school district", "best school district", "best school district type", "county size category",
               "place size category", "within-a-place code", "state legislative district — upper chamber",
               "state legislative district — lower chamber", "urban-rural portion", "urban Area",
               "118th congress (2023-2024)", "117th congress (2021-2022)", "116th congress (2019-2020)",
               "puma (2012)", "voting tabulation district", "hospital service area (2019)",
               "hospital referral region (2019)", "library district (2022)", "regional planning commissions",
               "u. of missouri extension regions", "mo dept. of economic development regions",
               "mo dept. of transportation districts", "mo area agencies on aging", "mo brfss regions"]

    optionsBeforeSource = options[:options.index(source_geography.lower())]

    temp_geo = source_geography[:]
    temp_geo = temp_geo.replace("/", "_")

    directory = data_directory + "GeoCorr/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory += temp_geo

    # Create directory for downloads
    if not os.path.exists(directory):
        os.makedirs(directory)

    # List of states
    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
              "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
              "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
              "Mississippi", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
              "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
              "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
              "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

    # download the chrome driver from                     https://chromedriver.chromium.org/downloads

    # Open the Chrome browser
    chrome_options = Options()

    # Run the browser in headless mode
    chrome_options.add_argument("--headless")

    # Create the driver
    driver = webdriver.Chrome(options=chrome_options)

    # Go to the website
    driver.get(weblink)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "leftBox")))

    # Clicker variable to only click the source geography once on the left side
    clicker = 0

    # Select the state_name, source geography, and target geography
    selectable_options = driver.find_elements(By.TAG_NAME, "option")

    for option in selectable_options:

        # To set the state(s)
        if state_name == "0":
            if option.text in states:
                option.click()
        else:
            # Click the state_name and unclick the auto-selected Missouri
            if option.text == state_name or option.text == "Missouri":
                option.click()

        # To set the targe geography and source geography
        if target_geography.lower() not in optionsBeforeSource:
            # Only click the source geography once on the left side
            if option.text.lower() == source_geography.lower() and clicker == 0:
                option.click()
                clicker += 1

            # To click and unclick the left side target geography
            elif target_geography.lower() == option.text.lower() and (clicker == 1):
                option.click()
                option.click()
                clicker += 1

            elif target_geography.lower() == option.text.lower() and clicker == 2:
                option.click()
                clicker += 1
        else:
            # Only click the source geography once on the left side
            if option.text.lower() == source_geography.lower() and clicker == 0:
                option.click()
                clicker += 1

            # To click and unclick the left side target geography
            elif target_geography.lower() == option.text.lower() and (clicker == 1):
                option.click()
                clicker += 1

    # Click the submit button
    submit_button = driver.find_elements(By.TAG_NAME, "input")
    submit_button[-2].click()

    # Wait for the page to load by looking for the tag h1 and the text associated with it is "Query Output"
    WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Query Output"))

    time.sleep(3)

    # Find the link to download the file
    download_link = driver.find_element(By.TAG_NAME, "a")

    # Rename source and target geographies
    source_geography = source_geography.replace("/", "-").title()
    source_geography = source_geography.replace(" ", "-").title()

    target_geography = target_geography.replace("/", "-").title()
    target_geography = target_geography.replace(" ", "-").title()

    if "18" in weblink:
        target_geography = target_geography + "_2018"

    # Rename state_name if it is the United States
    if state_name == "0":
        state_name = "United_States"

    # File name
    file_name = state_name + "_" + source_geography + "_to_" + target_geography + ".csv"

    # Final file path
    file_path = directory + "/" + file_name

    # Download the file to the current directory
    urllib.request.urlretrieve(download_link.get_attribute("href"), file_path)

    # Close the browser
    driver.quit()

    source_col = ""
    if source_geography == "Zip-Zcta":
        source_col = "zcta"
    elif source_geography == "Census Tract":
        source_col = "tract"
    elif source_geography == "County":
        source_col = "county"
    elif source_geography == "Metropolitan Division":
        source_col = "metdiv"
    elif source_geography == "Public-Use-Microdata-Area-(Puma)":
        source_col = "puma"
    elif source_geography == "118Th Congress (2023-2024)":
        source_col = "cd"
    elif source_geography == "Unified School District":
        source_col = "sduni"

    # Clean the crosswalk file
    file_path, source_col = cleanCrossWalkFile(file_path, source_col)

    return file_path, source_col


def cleanCrossWalkFile(file_name: str, source_col: str) -> tuple[str, str]:
    """
    This function cleans the crosswalk file. This is necessary because the crosswalk files have an extra row at the top
    :param file_name: The name of the crosswalk file
    :param source_col: The name of the source geography column
    :return: The name of the crosswalk file and the name of the source geography column
    """

    df = pd.read_csv(file_name, encoding="ISO-8859-1", dtype=str, skiprows=[1])

    columns = df.columns.tolist()

    for column in columns:
        if source_col.lower() in column.lower():
            source_col = column
            break

    # Standardize 'zcta' column
    if 'zcta' in df:
        df['zcta'] = df['zcta'].astype(str).str.zfill(5)

    # Standardize 'state' column
    if 'state' in df:
        df['state'] = df['state'].astype(str).str.zfill(2)

    # Standardize 'puma' column
    if 'puma' in source_col:
        print(source_col)
        df[source_col] = df[source_col].astype(str).str.zfill(5)
        df[source_col] = df['state'] + df[source_col]

    # Standardize 'sduni20' column (Unified School District)
    if 'sduni20' in df:
        df['sduni20'] = df['sduni20'].astype(str).str.zfill(5)
        df['state'] = df['state'].astype(str).str.zfill(2)
        df['sduni20'] = df['state'] + df['sduni20']
        df = df.drop(columns=['state'])

    # Standardize 'metdiv20' column (Metropolitan Division)
    if 'metdiv20' in df:
        df['metdiv20'] = df['metdiv20'].astype(str).str.zfill(5)
        df = df[df['metdiv20'] != '99999']

    # Standardize 'county' column
    if 'county' in df:
        df['county'] = df['county'].astype(str).str.zfill(5)

    # Standardize 'tract' column (Census Tract)
    if 'tract' in df:
        df['tract'] = df['tract'].astype(str).str.replace(".", "", regex=False)
        df['tract'] = df['tract'].str.pad(width=6, side='right', fillchar='0')
        df['county'] = df['county'].astype(str).str.zfill(5)
        df['tract'] = df['county'] + df['tract']
        df = df.drop(columns=['county'])
        if '2018' in file_name:
            df = df.rename(columns={"tract": "tract10"})

    # Standardize 'cd118' column (118th Congress)
    if 'cd118' in df:
        df['cd118'] = df['cd118'].astype(str).str.zfill(2)
        df['state'] = df['state'].astype(str).str.zfill(2)
        df['cd118'] = df['state'] + df['cd118']
        df = df.drop(columns=['state'])

    # Standardize 'puma22' column (Public-Use Microdata Area)
    if 'puma22' in df:
        df['puma22'] = df['puma22'].astype(str).str.zfill(5)
        df['state'] = df['state'].astype(str).str.zfill(2)
        df['puma22'] = df['state'] + df['puma22']

        # Drop the state column if it is not the source or target geography
        temp_name = file_name.split("States")[1]

        if "State" not in temp_name:
            df = df.drop(columns=["state"])

    # Drop rows with '00000' in the source column (e.g., zip code)
    df = df[df[source_col] != "00000"]

    # Save the cleaned file
    df.to_csv(file_name, index=False)

    return file_name, source_col
