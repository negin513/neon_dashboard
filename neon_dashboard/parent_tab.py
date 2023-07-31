from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, HoverTool, Select, Panel
from bokeh.tile_providers import get_provider, Vendors


from data_utils import *
from base_tab import *


class BaseTab:
    """
    Base class for generating time series plots tabs.
    """

    def __init__(
        self,
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
    ):
        self.df_all = df_all
        self.neon_sites_pft = neon_sites_pft
        self.neon_sites = neon_sites
        self.default_var = default_var
        self.default_freq = default_freq
        self.default_site = default_site
        self.us_lat1 = us_lat1
        self.us_lat2 = us_lat2
        self.us_lon1 = us_lon1
        self.us_lon2 = us_lon2

    def load_data(self):
        """
        Function for creating ColumnDataSources.
        """
        raise NotImplementedError("Subclasses must implement this method.")


    def map_site(self,w):
            w.circle(
                x="map_lon",
                y="map_lat",
                size=10,
                fill_color="dimgray",
                line_color="darkslategray",
                fill_alpha=0.7,
                source=self.neon_sites_pft,
            )
            w.circle(
                x="map_lon",
                y="map_lat",
                size=10,
                fill_color="darkorange",
                line_color="darkorange",
                fill_alpha=0.9,
                source=self.source2,
            )
            chosentile = get_provider(Vendors.ESRI_IMAGERY)
            w.add_tile(chosentile)
            w.xaxis.major_label_text_color = "white"
            w.yaxis.major_label_text_color = "white"
            w.grid.visible = False
            
    def update_yaxis(self,attr, old, new):
        new_var = vars_dict[self.menu.value]

        if new_var == "EFLX_LH_TOT":
            p.yaxis.axis_label = "Latent Heat Flux [W m⁻²]"
        elif new_var == "FSH":
            p.yaxis.axis_label = "Sensible Heat Flux [W m⁻²]"
        elif new_var == "Rnet":
            p.yaxis.axis_label = "Net Radiation [W m⁻²]"
        elif new_var == "NEE":
            p.yaxis.axis_label = "Net Ecosystem Exchange [gC m⁻² day⁻¹]"
        elif new_var == "GPP":
            p.yaxis.axis_label = "Gross Primary Production [gC m⁻² day⁻¹]"
        elif new_var == "ELAI":
            p.yaxis.axis_label = "Exposed Leaf Area Index"