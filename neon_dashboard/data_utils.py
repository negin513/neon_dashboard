# ----------------------------------
# -- Functions and objects for this code

import os
import glob
import time
import numpy as np
import pandas as pd
from scipy import stats
from pyproj import Proj, transform
import dask.dataframe as dd


class NeonSite:
    """
    Class to hold NEON Site Information.

    Attributes:
        site_code (str): The code representing the NEON site.
        long_name (str): The long name of the site.
        lat (float): The latitude coordinate of the site.
        lon (float): The longitude coordinate of the site.
        state (str): The state where the site is located.
        map_lat (float): The transformed latitude coordinate.
        map_lon (float): The transformed longitude coordinate.
    """

    def __init__(self, site_code, long_name, lat, lon, state):
        """
        Initializes a new instance of the NeonSite class.

        Args:
            site_code (str): The code representing the NEON site.
            long_name (str): The long name of the site.
            lat (float): The latitude coordinate of the site.
            lon (float): The longitude coordinate of the site.
            state (str): The state where the site is located.
        """
        self.site_code = site_code
        self.long_name = long_name
        self.lat = lat
        self.lon = lon
        self.state = state
        self.add_xy_transform()

    def add_xy_transform(
        self, inProj=Proj(init="epsg:3857"), outProj=Proj(init="epsg:4326")
    ):
        """
        Adds the transformed latitude and longitude coordinates to the NeonSite instance.

        Args:
            inProj (pyproj.Proj, optional): The input projection. Defaults to EPSG:3857.
            outProj (pyproj.Proj, optional): The output projection. Defaults to EPSG:4326.
        """
        self.map_lon, self.map_lat = transform(outProj, inProj, self.lon, self.lat)


def generate_sites(file_path):
    """
    Generate site information from a CSV file containing the relevant information.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        all_sites (dict): Dictionary of all site objects.
        neon_sites_pft (pd.DataFrame): DataFrame containing the NEON site information.
    """
    neon_sites_pft = pd.read_csv(file_path)
    all_sites = {}

    for _, row in neon_sites_pft.iterrows():
        site = NeonSite(
            row["Site"], row["site_name"], row["Lat"], row["Lon"], row["state"]
        )
        all_sites[row["Site"]] = site

    print(f"Total number of NEON sites for this demo: {len(neon_sites_pft)}")

    return all_sites, neon_sites_pft


def get_preprocessed_files(csv_dir, neon_site):
    """
    Get preprocessed files.

    Args:
        csv_dir (str): Directory containing the CSV files.
        neon_site (str): NEON site.

    Returns:
        fnames (list): List of preprocessed file names.
    """
    fnames = glob.glob(os.path.join(csv_dir, f"preprocessed_{neon_site}_*.csv"))
    return fnames


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
    start_site = time.time()

    for neon_site in neon_sites:
        try:
            csv_file = f"preprocessed_{neon_site}_2021.csv"
            df = dd.read_csv(os.path.join(csv_dir, csv_file), parse_dates=["time"])
            df_list.append(df)
        except Exception as e:
            print(f"Error loading data for site {neon_site}: {str(e)}")
            failed_sites.append(neon_site)

    df_all = dd.concat(df_list)
    end_site = time.time()
    print("Reading all preprocessed files took:", end_site - start_site, "s.")

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

    print("Number of failed sites:", len(failed_sites))
    print(*failed_sites, sep=" \n")

    return df_all, failed_sites


def get_data(df_all, var, freq, this_site):
    """
    Get data from a DataFrame based on the specified variable, frequency, and site.

    Args:
        df_all (pd.DataFrame): DataFrame containing the data.
        var (str): Variable to retrieve.
        freq (str): Frequency of the data ('monthly', 'daily', 'hourly', 'all').
        this_site (str): Site name.

    Returns:
        df_new (pd.DataFrame): DataFrame containing the selected data.
    """
    start_time = time.time()

    print("this_site", this_site)
    df = df_all[df_all["site"] == this_site]  # .compute()
    sim_var_name = "sim_" + var

    if freq == "monthly":
        df = df.groupby(["year", "month"]).mean().reset_index()  # .compute()
        df["day"] = 15
        df["time"] = dd.to_datetime(df[["year", "month", "day"]])

    elif freq == "daily":
        df = df.groupby(["year", "month", "day"]).mean().reset_index()  # .compute()
        df["time"] = dd.to_datetime(df[["year", "month", "day"]])

    elif freq == "hourly":
        df = (
            df.groupby(["year", "month", "day", "hour"]).mean().reset_index()
        )  # .compute()
        df["time"] = dd.to_datetime(df[["year", "month", "day", "hour"]])

    elif freq == "all":
        df = df  # .compute()

    df_new = pd.DataFrame(
        {"time": df["time"], "NEON": df[var], "CLM": df[sim_var_name]}
    )

    end_time = time.time()
    print("Computing all data took:", end_time - start_time, "s.")
    return df_new


def get_diel_data(df, var, season, this_site):
    """
    This function gets and manipulates data related to diel cycles.

    Parameters:
    df (DataFrame): The original DataFrame to work on.
    var (str): The variable of interest.
    season (str): The season of interest, can be "Annual".
    this_site (str): The site of interest.

    Returns:
    df_new (DataFrame): The manipulated DataFrame ready for output.
    """

    # Print site information
    print(f"This site: {this_site}")

    # -- Filter DataFrame by season if it's not "Annual"
    if season != "Annual":
        df = df[df["season"] == season]

    # -- Filter DataFrame by site
    df = df[df["site"] == this_site]  # .compute()

    # Group the DataFrame by 'local_hour' and calculate the mean and standard deviation
    diel_df_mean = df.groupby("local_hour").mean().reset_index()
    diel_df_std = df.groupby("local_hour").std().reset_index()

    # Variable names for simulation, bias and standard deviation
    sim_var_name = "sim_" + var
    bias_var_name = "bias_" + var
    std_var_name = "std_" + var

    # Calculate bias for each local hour
    diel_df_mean[bias_var_name] = diel_df_mean[sim_var_name] - diel_df_mean[var]

    # Create a new DataFrame with the calculated mean values
    df_new = pd.DataFrame(
        {
            "hour": diel_df_mean["local_hour"],
            "NEON": diel_df_mean[var],
            "CLM": diel_df_mean[sim_var_name],
        }
    )

    # Convert 'hour' to datetime format
    df_new["local_hour_dt"] = pd.to_datetime(df_new["hour"], format="%H")

    # Calculate bias for the new DataFrame
    df_new["Bias"] = diel_df_mean[sim_var_name] - diel_df_mean[var]

    # Calculate the lower and upper bounds for 'NEON'
    df_new["NEON_lower"] = diel_df_mean[var] - diel_df_std[var]
    df_new["NEON_upper"] = diel_df_mean[var] + diel_df_std[var]

    # Calculate the lower and upper bounds for 'CLM'
    df_new["CLM_lower"] = diel_df_mean[sim_var_name] - diel_df_std[sim_var_name]
    df_new["CLM_upper"] = diel_df_mean[sim_var_name] + diel_df_std[sim_var_name]

    return df_new


def find_regline(df, var, sim_var_name):
    """
    Find the regression line between two variables in a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing the variables.
        var (str): Variable name.
        sim_var_name (str): Simulated variable name.

    Returns:
        result (scipy.stats.linregress): Regression line statistics.
    """
    df_temp = df[[var, sim_var_name]]
    df_temp.dropna(inplace=True)

    result = stats.linregress(df_temp[var], df_temp[sim_var_name])
    print("result:", result)
    return result


def fit_func(df):
    """
    This function fits a linear regression model on the 'NEON' and 'CLM' columns of the DataFrame.

    Parameters:
    df (DataFrame): The DataFrame on which to perform linear regression.

    Returns:
    x_fit (Series): The sorted 'NEON' values.
    y_fit (Series): The predicted 'CLM' values using the linear regression model.
    """

    # Subset DataFrame
    df_subset = df[["NEON", "CLM"]]
    df_subset.dropna(inplace=True)
    # Perform linear regression
    slope, intercept, _, _, _ = stats.linregress(df_subset["NEON"], df_subset["CLM"])

    # Sort 'NEON' values
    neon_sorted = df_subset["NEON"].sort_values()

    # Compute min and max 'NEON' values with adjustments
    min_neon = df_subset.min().min() - neon_sorted.mean()
    max_neon = df_subset.max().max() + 1.5 * neon_sorted.mean()

    # Generate 'NEON' values in the computed range
    x_fit = np.arange(min_neon, max_neon)

    # Calculate 'CLM' predictions using the linear regression model
    print("slope", slope)
    print("intercept", intercept)
    print("x_fit", x_fit)
    y_fit = slope * x_fit + intercept
    print("y_fit", y_fit)
    return x_fit, y_fit


def get_neon_site(neon_sites_pft, site_name):
    """
    Get the NEON site information for a given site name.

    Args:
        neon_sites_pft (pd.DataFrame): DataFrame containing the NEON site information.
        site_name (str): Site name.

    Returns:
        this_site (pd.DataFrame): NEON site information for the specified site name.
    """
    this_site = neon_sites_pft[neon_sites_pft["Site"] == site_name]
    return this_site
