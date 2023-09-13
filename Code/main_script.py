from ACS_PUMS.acs_pums import downloadPUMSFiles, everyStateEligibility, determine_eligibility
from Geocorr.Geocorr_Applications_Downloads import downloadCrossWalkFile, getMostRecentGeoCorrApplication


def main():
    data_dir = "../Data/"

    # downloadPUMSFiles(data_dir)
    #
    # everyStateEligibility(data_dir)
    #
    # The different target geographies
    county = "County"
    congressional_district = "118th Congress (2023-2024)"
    metro = "Metropolitan division"
    zcta = "ZIP/ZCTA"
    state = "State"
    #
    # Download the crosswalk files
    link = getMostRecentGeoCorrApplication(data_dir)

    # source_geography = "Public-use microdata area (PUMA)"
    #
    # county_cw_file, source_col_1 = downloadCrossWalkFile(link, data_dir, source_geography, county)
    # congressional_dist_cw_file, source_col_2 = downloadCrossWalkFile(link, data_dir, source_geography,
    #                                                                  congressional_district)
    # metro_cw_file, source_col_3 = downloadCrossWalkFile(link, data_dir, source_geography, metro)
    #
    # zcta_cw_file, source_col_4 = downloadCrossWalkFile(link, data_dir, source_geography, zcta)
    # state_cw_file, source_col_5 = downloadCrossWalkFile(link, data_dir, source_geography, state)
    #
    # determine_eligibility(data_dir)
    # determine_eligibility(data_dir, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1, veteran=1, disability=1,
    #                       elderly=1)
    # determine_eligibility(data_dir, geography=county)
    # determine_eligibility(data_dir, geography=county, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1, veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=congressional_district)
    # determine_eligibility(data_dir, geography=congressional_district, aian=1, asian=1, black=1, hispanic=1, white=1,
    #                       nhpi=1, veteran=1, disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=metro)
    # determine_eligibility(data_dir, geography=metro, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1, veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=zcta)
    # determine_eligibility(data_dir, geography=zcta, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1, veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=state)
    # determine_eligibility(data_dir, geography=state, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1, veteran=1,
    #                       disability=1, elderly=1)
    #
    # determine_eligibility(data_dir, povpip=150, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1, veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, povpip=135, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1, veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, povpip=120, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1, veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=county, povpip=150, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=county, povpip=135, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=county, povpip=120, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=congressional_district, povpip=150, aian=1, asian=1, black=1, hispanic=1,
    #                       white=1, nhpi=1, veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=congressional_district, povpip=135, aian=1, asian=1, black=1, hispanic=1,
    #                       white=1, nhpi=1, veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=congressional_district, povpip=120, aian=1, asian=1, black=1, hispanic=1,
    #                       white=1, nhpi=1, veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=metro, povpip=150, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=metro, povpip=135, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=metro, povpip=120, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=zcta, povpip=150, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=zcta, povpip=135, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=zcta, povpip=120, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=state, povpip=150, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=state, povpip=135, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)
    # determine_eligibility(data_dir, geography=state, povpip=120, aian=1, asian=1, black=1, hispanic=1, white=1, nhpi=1,
    #                       veteran=1,
    #                       disability=1, elderly=1)

    downloadCrossWalkFile(link, data_dir, zcta, county)
    downloadCrossWalkFile(link, data_dir, zcta, congressional_district)
    downloadCrossWalkFile(link, data_dir, zcta, metro)
    downloadCrossWalkFile(link, data_dir, zcta, state)



if __name__ == '__main__':
    main()
