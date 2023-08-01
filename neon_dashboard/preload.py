import os
import time
import numpy as np
import pandas as pd
from pyproj import Proj, transform
import dask.dataframe as dd

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

    csv_dir = os.path.join(os.path.dirname(__file__), "data/preprocessed_data")
    
    neon_sites_file = os.path.join(os.path.dirname(__file__),"data/all_neon_sites.csv")


    def __init__(self):
        """
        Initializes the Preload class.
        """
        pass

    @staticmethod
    def load_and_preprocess_data(neon_sites, csv_dir):
        """
        Load and preprocess data from CSV files.

        Args:
            neon_sites (list): List of NEON sites.
            csv_dir (str): Directory containing the CSV files.

        Returns:
            df_all (pd.DataFrame): DataFrame containing the processed data.
            failed_sites (list): List of sites that failed to load.
        """
        df_list = []
        failed_sites = []

        for neon_site in neon_sites:
            try:
                csv_file = f"preprocessed_{neon_site}_2021.csv"
                df = pd.read_csv(os.path.join(csv_dir, csv_file), parse_dates=["time"])
                df_list.append(df)
            except Exception as e:
                print(f"Error loading data for site {neon_site}: {str(e)}")
                failed_sites.append(neon_site)

        df_all = pd.concat(df_list)

        # Fix time formatting
        # df_all['time'] = pd.to_datetime(df_all['time'], errors='coerce')

        # Extract year, month, day, hour information from time
        df_all["year"] = df_all["time"].dt.year
        df_all["month"] = df_all["time"].dt.month
        df_all["day"] = df_all["time"].dt.day
        df_all["hour"] = df_all["time"].dt.hour
        df_all["season"] = ((df_all["month"] % 12 + 3) // 3).map(
            {1: "DJF", 2: "MAM", 3: "JJA", 4: "SON"}
        )

        df_all["ELAI"] = np.nan

        return df_all, failed_sites

    @staticmethod
    def load_neon_sites(neon_sites_file):
        """
        Load NEON site data from a CSV file.

        Args:
            neon_sites_file (str): File path to the 'all_neon_sites.csv' file.

        Returns:
            neon_sites_pft (pd.DataFrame): DataFrame containing NEON site data.
        """
        neon_sites_pft = pd.read_csv(neon_sites_file)
        return neon_sites_pft

    @staticmethod
    def transform_neon_sites(neon_sites_pft):
        """
        Transform NEON site data coordinates from EPSG:3857 to EPSG:4326.

        Args:
            neon_sites_pft (pd.DataFrame): DataFrame containing NEON site data.

        Returns:
            transformed_neon_sites (pd.DataFrame): DataFrame with transformed coordinates.
        """
        inProj = Proj(init='epsg:3857')
        outProj = Proj(init='epsg:4326')

        us_lon1, us_lat1 = transform(outProj,inProj,-130,23)
        us_lon2, us_lat2 = transform(outProj,inProj,-65,49)

        x = neon_sites_pft['Lon']
        y = neon_sites_pft['Lat']
        x_transform, y_transform = transform(outProj, inProj, x, y)

        neon_sites_pft['map_lat'] = y_transform
        neon_sites_pft['map_lon'] = x_transform

        return neon_sites_pft, us_lat1, us_lat2, us_lon1, us_lon2



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
        

        print('Total number of NEON sites for this demo:', len(Preload.neon_sites))

        start_time = time.time()
        df_all, failed_sites = Preload.load_and_preprocess_data(Preload.neon_sites, Preload.csv_dir)
        elapsed_time = time.time() - start_time

        print(f"Reading all preprocessed files took: {elapsed_time:.2f} seconds.")
        print(f"Number of failed sites: {len(failed_sites)}")
        print("\n".join(failed_sites))

        neon_sites_pft = Preload.load_neon_sites(Preload.neon_sites_file)

        neon_sites_pft, us_lat1, us_lat2, us_lon1, us_lon2, = Preload.transform_neon_sites(neon_sites_pft)


        # Reassign all variables
        Preload.neon_sites_pft = neon_sites_pft
        Preload.df_all = df_all
        Preload.us_lon1 = us_lon1
        Preload.us_lat1 = us_lat1
        Preload.us_lon2 = us_lon2
        Preload.us_lat2 = us_lat2