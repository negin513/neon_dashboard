# ----------------------------------


from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, HoverTool, Select, Panel
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models import (Band, Button, ColumnDataSource, CustomJS, DataTable, 
                          Div, DatetimeTickFormatter, HoverTool, Label, 
                          Panel, Select, Slope, TableColumn)

from data_utils import *
from base_tab import *

# ----------------------------------
# --------default values------------
# ----------------------------------

neon_sites = [
    "ABBY",
    "BART",
    "HARV",
    "BLAN",
    "SCBI",
    "SERC",
    "DSNY",
    "JERC",
    "OSBS",
    "GUAN",
    "LAJA",
    "STEI",
    "TREE",
    "UNDE",
    "KONA",
    "KONZ",
    "UKFS",
    "GRSM",
    "MLBS",
    "ORNL",
    "DELA",
    "LENO",
    "TALL",
    "DCFS",
    "NOGP",
    "WOOD",
    "CPER",
    "RMNP",
    "STER",
    "CLBJ",
    "OAES",
    "YELL",
    "MOAB",
    "JORN",
    "SRER",
    "ONAQ",
    "ABBY",
    "WREF",
    "SJER",
    "SOAP",
    "TEAK",
    "TOOL",
    "BARR",
    "BONA",
    "DEJU",
    "HEAL",
]

vars_dict = {
    "FSH": "Sensible Heat Flux ",
    "EFLX_LH_TOT": "Latent Heat Flux ",
    "Rnet": "Net Radiation ",
    "GPP": "Gross Primary Production",
    "NEE": "Net Ecosystem Exchange",
    "ELAI": "Effective Leaf Area Index",
}

# -- reverse keys and values...
rev_vars_dict = {y: x for x, y in vars_dict.items()}

# ----------------------------------
# -- Tooltips for our plots
tooltip = (
    '<div class="plot-tooltip">'
    "    <div>"
    '        <h3 style="text-align:center">@Site</h3>'
    '        <span style="font-weight: bold;">@site_name, @state </span><br>'
    "    </div>"
    "    <div>"
    '        <span style="font-weight: bold;">Lon , Lat : </span> @Lon , @Lat <br>'
    '        <span style="font-weight: bold;">Dominant PFT : </span>@pft'
    "    </div>"
    "</div>"
)

q_TOOLTIP = (
    '<div class="plotq-tooltip">'
    "    <div>"
    '        <span style="font-weight: bold;">NEON : </span> @NEON <br>'
    '        <span style="font-weight: bold;">CTSM : </span> @CLM <br>'
    "    </div>"
    "</div>"
)

p_TOOLTIP = (
    '<div class="plotq-tooltip">'
    "    <div>"
    '        <span style="font-weight: bold;">Time : </span> @time <br>'
    '        <span style="font-weight: bold;">NEON : </span> @NEON <br>'
    '        <span style="font-weight: bold;">CTSM : </span> @CLM <br>'
    "    </div>"
    "</div>"
)

COL_TPL = "<%= get_icon(type.toLowerCase()) %> <%= type %>"


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

    def scatter_plot(self, q):
        q.circle(
            "NEON",
            "CLM",
            source=self.source,
            alpha=0.8,
            color="navy",
            fill_alpha=0.4,
            size=13,
            hover_color="firebrick",
            selection_color="orange",
            nonselection_alpha=0.1,
            selection_alpha=0.5,
        )

        q.xaxis.major_label_text_color = "dimgray"
        q.xaxis.major_label_text_font_size = "13pt"
        q.xaxis.major_label_text_font_style = "bold"

        q.yaxis.major_label_text_color = "dimgray"
        q.yaxis.major_label_text_font_size = "13pt"
        q.yaxis.major_label_text_font_style = "bold"

        q.xaxis.axis_label_text_font_size = "13pt"
        q.yaxis.axis_label_text_font_size = "13pt"

        q.xaxis.axis_label_text_font_style = "bold"
        q.yaxis.axis_label_text_font_style = "bold"

        q.xaxis.axis_label_text_font = "Verdana"
        q.yaxis.axis_label_text_font = "Verdana"

        q.axis.axis_label_text_font_style = "bold"

        q.grid.grid_line_alpha = 0.35
        q.title.text_font_size = "12pt"

        q.xaxis.axis_label = "NEON"
        q.yaxis.axis_label = "CTSM"
        # df_new = get_diel_data(self.df_all, self.default_var, self.menu_season.value, self.menu_site.value)

        # q.xaxis.major_label_orientation = "vertical"
        q.xaxis.major_label_orientation = np.pi / 4

        print("++++++++++++++++++++")
        result = find_regline(self.df_new, "NEON", "CLM")
        print("df_new.NEON:", self.df_new["NEON"])
        print("df_new.CLM:", self.df_new["CLM"])
        print("slope:", result.slope)
        print("intercept:", result.intercept)
        print("new r_value:", result.rvalue**2)

        slope_label = (
            "y = "
            + "{:.2f}".format(result.slope)
            + "x"
            + " + "
            + "{:.2f}".format(result.intercept)
            + " (R² = "
            + "{:.3f}".format(result.rvalue**2)
            + ")"
        )
        print(slope_label)

        # mytext = Label(
        #    text=slope_label,
        #    x=0 + 20,
        #    y=q_height - 100,
        #    x_units="screen",
        #    y_units="screen",
        #    text_align="left",
        # )

        regression_line = Slope(
            gradient=result.slope,
            y_intercept=result.slope,
            line_color="navy",
            line_width=2,
            line_alpha=0.8,
        )

        # print (mytext)
        # q.add_layout(mytext)
        # q.add_layout(regression_line)
        q.title.text = slope_label

        # x = range(0,50)
        # y = slope*x+intercept
        oneone_line = Slope(
            gradient=1,
            y_intercept=0,
            line_color="gray",
            line_width=2,
            line_alpha=0.3,
            line_dash="dashed",
        )
        q.add_layout(oneone_line)

        # q.line(x, y,alpha=0.8, line_width=4, color="gray")

        # x = df_new['NEON']
        # y = df_new['CLM']

        # par = np.polyfit(x, y, 1, full=True)
        # slope=par[0][0]
        # intercept=par[0][1]
        # print ('------------')
        # print ('slope:', slope)
        # print ('intercept:', intercept)
        # Make the regression line
        # regression_line = Slope(gradient=slope, y_intercept=intercept, line_color="red")
        # q.add_layout(regression_line)
        q.line("x", "y", source=self.source_fit, alpha=0.8, color="navy", line_width=3)

        # q.add_layout(regression_line)

    def map_sites(self, w):
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

    def update_yaxis(self, attr, old, new):
        print("----------------------------")
        print(self.menu_var.value)
        new_var = rev_vars_dict[self.menu_var.value]

        if new_var == "EFLX_LH_TOT":
            self.p.yaxis.axis_label = "Latent Heat Flux [W m⁻²]"
        elif new_var == "FSH":
            self.p.yaxis.axis_label = "Sensible Heat Flux [W m⁻²]"
        elif new_var == "Rnet":
            self.p.yaxis.axis_label = "Net Radiation [W m⁻²]"
        elif new_var == "NEE":
            self.p.yaxis.axis_label = "Net Ecosystem Exchange [gC m⁻² day⁻¹]"
        elif new_var == "GPP":
            self.p.yaxis.axis_label = "Gross Primary Production [gC m⁻² day⁻¹]"
        elif new_var == "ELAI":
            self.p.yaxis.axis_label = "Exposed Leaf Area Index"

    def create_tab(self):
        """
        Function for creating ColumnDataSources.
        """
        raise NotImplementedError("Subclasses must implement this method.")
