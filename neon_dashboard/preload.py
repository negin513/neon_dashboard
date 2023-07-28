import os
import time
import numpy as np
import pandas as pd
from pyproj import Proj, transform

class Preload:
    """
    A class for preprocessing NEON site data and extracting relevant information.

    Attributes:
        neon_sites (list): A list of NEON site codes.
        neon_sites_pft (pd.DataFrame): A DataFrame containing NEON site data.
        df_all (pd.DataFrame): A DataFrame containing preprocessed data for all NEON sites.
        us_lon1, us_lat1, us_lon2, us_lat2 (float): Latitude and Longitude boundaries for the US.

    Note:
        This class assumes that the data files and 'all_neon_sites.csv' are present in the 'data' folder.
    """

    neon_sites = ['ABBY', 'BART', 'HARV', 'BLAN',
                  'SCBI', 'SERC', 'DSNY', 'JERC',
                  'OSBS', 'GUAN', 'LAJA', 'STEI',
                  'TREE', 'UNDE', 'KONA', 'KONZ',
                  'UKFS', 'GRSM', 'MLBS', 'ORNL',
                  'DELA', 'LENO', 'TALL', 'DCFS',
                  'NOGP', 'WOOD', 'CPER', 'RMNP',
                  'STER', 'CLBJ', 'OAES', 'YELL',
                  'MOAB', 'JORN', 'SRER', 'ONAQ',
                  'ABBY', 'WREF', 'SJER', 'SOAP',
                  'TEAK', 'TOOL', 'BARR', 'BONA',
                  'DEJU', 'HEAL']

    def __init__(self):
        """
        Initializes the Preload class.
        """
        pass

    @staticmethod
    def run():
        """
        Preprocesses NEON site data and extracts relevant information.

        This method reads preprocessed data files for each NEON site and combines them into a single DataFrame.
        It also extracts time-related information and adds additional columns to the DataFrame.

        Note:
            The method assumes that preprocessed data files are present in the 'data/preprocessed_data/' folder.
        """
        # Read NEON site data
        neon_sites_pft = pd.read_csv('data/all_neon_sites.csv')

        print('Total number of NEON sites for this demo:', len(Preload.neon_sites))

        failed_sites = []
        csv_dir = "data/preprocessed_data/"
        df_list = []
        start_site = time.time()

        for site_code in Preload.neon_sites:
            try:
                csv_file = f"preprocessed_{site_code}_2021.csv"
                this_df = pd.read_csv(os.path.join(csv_dir, csv_file))
                print(os.path.join(csv_dir, csv_file))
                df_list.append(this_df)
            except FileNotFoundError:
                # print('THIS SITE FAILED:', site_code)
                failed_sites.append(site_code)
                pass

        print("Failed sites:", failed_sites)
        df_all = pd.concat(df_list)
        print("Total records:", len(df_all))
        end_site = time.time()
        print("Reading all preprocessed files took:", end_site - start_site, "s.")

        print("Number of failed sites:", len(failed_sites))
        print(*failed_sites, sep="\n")

        # Fix time formatting
        df_all['time'] = pd.to_datetime(df_all['time'], errors='coerce')

        # Extract year, month, day, hour information from time
        df_all['year'] = df_all['time'].dt.year
        df_all['month'] = df_all['time'].dt.month
        df_all['day'] = df_all['time'].dt.day
        df_all['hour'] = df_all['time'].dt.hour
        df_all['season'] = ((df_all['month'] % 12 + 3) // 3).map({1: 'DJF', 2: 'MAM', 3: 'JJA', 4: 'SON'})

        df_all['ELAI'] = np.nan

        inProj = Proj(init='epsg:3857')
        outProj = Proj(init='epsg:4326')
        us_lon1, us_lat1 = transform(outProj, inProj, -130, 23)
        us_lon2, us_lat2 = transform(outProj, inProj, -65, 49)

        x = neon_sites_pft['Lon']
        y = neon_sites_pft['Lat']
        x_transform, y_transform = transform(outProj, inProj, x, y)
        neon_sites_pft['map_lat'] = y_transform
        neon_sites_pft['map_lon'] = x_transform

        # Reassign all variables
        Preload.neon_sites_pft = neon_sites_pft
        Preload.df_all = df_all
        Preload.us_lon1 = us_lon1
        Preload.us_lat1 = us_lat1
        Preload.us_lon2 = us_lon2
        Preload.us_lat2 = us_lat2