#! /usr/bin/env python
"""
Author: Negin Sobhani
Created on: 2022-10-01
Contact Info: negins@ucar.edu
"""

# Standard Library Imports
import os

# Related Third-Party Imports
from bokeh.io import curdoc, output_notebook, show
from bokeh.models import Tabs

from simple_tseries import SimpleTseries
from diel_cycle import DielCycle
from .preload import Preload

# ----------------------------------
# -- start a dask cluster

# from dask.distributed import Client

# client = Client(n_workers=2)
# client

# ----------------- #
# -- default values
# ----------------- #
default_site = "ABBY"
default_freq = "daily"
default_var = "EFLX_LH_TOT"
default_season = "Annual"


neon_sites_file = "data/all_neon_sites.csv"
csv_dir = "data/preprocessed_data"

years = ["2018", "2019", "2020", "2021"]
freq_list = ["all", "hourly", "daily", "monthly"]

#plot_vars = ["FSH", "EFLX_LH_TOT", "Rnet", "NEE", "GPP", "ELAI"]

#all_sites, neon_sites_pft = generate_sites(neon_sites_file)

if __name__.startswith("bokeh"):
    print(" -----------------------------  ")
    print(" Starting bokeh application ... ")


    neon_sites = Preload.neon_sites
    neon_sites_pft = Preload.neon_sites_pft
    df_all = Preload.df_all
    us_lon1, us_lat1, us_lon2, us_lat2 = (
        Preload.us_lon1,
        Preload.us_lat1,
        Preload.us_lon2,
        Preload.us_lat2,
    )

    # ----------------- #
    tseries_doc = SimpleTseries(
        df_all,
        neon_sites_pft,
        neon_sites,
        default_var,
        default_freq,
        default_site,
        us_lat1,
        us_lat2,
        us_lon1,
        us_lon2,
    )
    tab_1 = tseries_doc.create_tab()

    diel_doc = DielCycle(
        df_all,
        neon_sites_pft,
        neon_sites,
        default_var,
        default_freq,
        default_site,
        us_lat1,
        us_lat2,
        us_lon1,
        us_lon2,
        default_season,
    )

    # ----- DielCycle
    tab_2 = diel_doc.create_tab()

    # tabs = Tabs(tabs=[tab_1, tab_2])
    tabs = Tabs(tabs=[tab_1, tab_2])

    curdoc().add_root(tabs)
