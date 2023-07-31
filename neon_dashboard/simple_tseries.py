from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, HoverTool, Select, Panel
from bokeh.tile_providers import get_provider, Vendors


from data_utils import *
from base_tab import *


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

freq_list = ["all", "hourly", "daily", "monthly"]
plot_vars = ["FSH", "EFLX_LH_TOT", "Rnet", "NEE", "GPP", "ELAI"]


class SimpleTseries:
    """
    Class for generating time series plots tabs.
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
        
        self.us_lat1=us_lat1
        self.us_lat2=us_lat2
        self.us_lon1=us_lon1
        self.us_lon2=us_lon2

        p_tools = (
            "pan, wheel_zoom, box_zoom, box_select, undo, redo, save, reset, crosshair"
        )
        q_tools = "pan,  box_zoom, box_select, lasso_select, crosshair"
        self.load_data()

    def load_data(self):
        """
        Function for creating ColumnDataSouces:
        """
        df_new = get_data(
            self.df_all, self.default_var, self.default_freq, self.default_site
        )
        self.source = ColumnDataSource(df_new)

        self.this_site = get_neon_site(self.neon_sites_pft, self.default_site)
        print(self.this_site)
        print("!!!!")
        self.source2 = ColumnDataSource(self.this_site)
        print(self.this_site["site_name"].values[0].replace(r"[][]", " "))

    def tseries_plot(self, p):
        p.line(
            "time",
            "NEON",
            source=self.source,
            alpha=0.8,
            line_width=4,
            color="navy",
            legend_label="NEON",
        )
        p.line(
            "time",
            "CLM",
            source=self.source,
            alpha=0.8,
            line_width=3,
            color="red",
            legend_label="CTSM",
        )
        p.circle(
            "time",
            "NEON",
            size=2,
            source=self.source,
            color=None,
            selection_color="navy",
        )
        p.circle(
            "time", "CLM", size=2, source=self.source, color=None, selection_color="red"
        )

        # p.circle('time', 'var', source=source, alpha=0.8, color="navy")

        p.xaxis.major_label_text_color = "dimgray"
        p.xaxis.major_label_text_font_size = "18px"
        p.xaxis.major_label_text_font_style = "bold"

        p.yaxis.major_label_text_color = "dimgray"
        p.yaxis.major_label_text_font_size = "18px"
        p.yaxis.major_label_text_font_style = "bold"

        p.xaxis.axis_label_text_font = "Tahoma"
        p.yaxis.axis_label_text_font = "Tahoma"
        p.xaxis.axis_label_text_font_size = "15pt"
        p.xaxis.axis_label_text_font_style = "bold"

        p.yaxis.axis_label_text_font_size = "15pt"
        p.yaxis.axis_label_text_font_style = "bold"

        p.axis.axis_label_text_font_style = "bold"

        p.grid.grid_line_alpha = 0.35
        p.title.text_font_size = "19pt"
        p.xaxis.axis_label = "Time"
        p.yaxis.axis_label = "Latent Heat Flux [W m⁻²]"

        p.title.text_font = "Tahoma"
        # p.title.text = "Time-Series Plot for Neon Site : " +default_site
        plot_title = (
            "NEON Site : "
            + self.this_site["site_name"].values[0].replace(r"[][]", " ")
            + ", "
            + self.this_site["state"].values[0].replace(r"[][]", " ")
            + " ("
            + self.default_site
            + ") "
        )

        p.title.text = plot_title

        p.legend.location = "top_right"
        p.legend.label_text_font_size = "15pt"
        p.legend.label_text_font_style = "bold"

        # p.legend.label_text_font = "times"
        p.legend.label_text_color = "dimgray"
        p.legend.background_fill_alpha = 0.35

    def scatter_plot(self, q):
        q.circle(
            "NEON",
            "CLM",
            source=self.source,
            alpha=0.8,
            color="navy",
            fill_alpha=0.2,
            size=10,
            hover_color="firebrick",
            selection_color="orange",
            nonselection_alpha=0.1,
            selection_alpha=0.5,
        )

        q.xaxis.major_label_text_color = "dimgray"
        q.xaxis.major_label_text_font_size = "15px"
        q.xaxis.major_label_text_font_style = "bold"

        q.yaxis.major_label_text_color = "dimgray"
        q.yaxis.major_label_text_font_size = "15px"
        q.yaxis.major_label_text_font_style = "bold"

        q.xaxis.axis_label_text_font_size = "13pt"
        q.yaxis.axis_label_text_font_size = "13pt"

        q.xaxis.axis_label_text_font = "Verdana"
        q.yaxis.axis_label_text_font = "Verdana"

        q.title.text_font = "Verdana"
        q.axis.axis_label_text_font_style = "bold"
        q.grid.grid_line_alpha = 0.35
        q.title.text_font_size = "15pt"
        q.xaxis.axis_label = "NEON"
        q.yaxis.axis_label = "CTSM"

        # q.xaxis.major_label_orientation = "vertical"
        q.xaxis.major_label_orientation = np.pi / 4

    def map_sites(self, w):
        from bokeh.tile_providers import get_provider, Vendors

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
        print ('~~~~~~~~~')
        print ('chosen tiles')
        print ( chosentile)
        w.add_tile(chosentile)
        w.xaxis.major_label_text_color = "white"
        w.yaxis.major_label_text_color = "white"
        w.grid.visible = False

    def update_variable(self, attr, old, new):
        print("updating plot for:")
        print(" - freq: ", self.menu_freq.value)
        print(" - site: ", self.menu_site.value)
        new_var = rev_vars_dict[self.menu.value]
        print(" - var: ", new_var)

        df_new = get_data(new_var, self.menu_freq.value, self.menu_site.value)
        self.source.data = df_new

        this_site = get_neon_site(self.neon_sites_pft, self.menu_site.value)
        self.source2.data = this_site

        plot_title = (
            "NEON Site: "
            + this_site["site_name"].values[0].replace(r"[][]", " ")
            + ", "
            + this_site["state"].values[0].replace(r"[][]", " ")
            + " ("
            + self.menu_site.value
            + ") "
        )
        self.p.title.text = plot_title

    def update_site(self, attr, old, new):
        new_var = rev_vars_dict[self.menu.value]
        df_new = get_data(new_var, self.menu_freq.value, new)
        this_site = get_neon_site(self.neon_sites_pft, new)

        self.source.data = df_new
        self.source2.data = this_site

        plot_title = (
            "NEON Site: "
            + this_site["site_name"].values[0].replace(r"[][]", " ")
            + ", "
            + this_site["state"].values[0].replace(r"[][]", " ")
            + " ("
            + new
            + ") "
        )
        self.p.title.text = plot_title

    def update_yaxis(self, attr, old, new):
        new_var = rev_vars_dict[self.menu.value]

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
        # -- adding time-series panel
        p_width = 1300
        p_height = 550
        neon_site = "ABBY"  # Default site for initial plot

        p = figure(
            tools="pan, wheel_zoom, box_zoom, box_select, undo, redo, save, reset, crosshair",
            x_axis_type="datetime",
            title="Neon Time-Series " + neon_site,
            width=p_width,
            height=p_height,
        )

        self.tseries_plot(p)

        hover = HoverTool(
            tooltips=[("Time", "@time{%F %T}"), ("NEON", "@NEON"), ("CLM", "@CLM")],
            formatters={"@time": "datetime"},
        )
        p.add_tools(hover)

        # -- adding scatter panel
        q_width = 350
        q_height = 350

        q = figure(
            tools="pan, box_zoom, box_select, lasso_select, crosshair",
            width=q_width,
            height=q_height,
            x_range=p.y_range,
            y_range=p.y_range,
            tooltips=[("NEON", "@NEON"), ("CLM", "@CLM")],
        )
        self.scatter_plot(q)

        # -- adding map panel
        w_width = 375
        w_height = 225

        w = figure(
            name="neon_map",
            plot_width=w_width,
            plot_height=w_height,
            x_range=(self.us_lon1, self.us_lon2),
            y_range=(self.us_lat1, self.us_lat2),
            x_axis_type="mercator",
            y_axis_type="mercator",
            x_axis_location=None,
            y_axis_location=None,
            match_aspect=True,
            max_height=w_height,
            max_width=w_width,
            margin=(-17, 0, 0, 53),
            tooltips=TOOLTIP,
            tools=["wheel_zoom", "pan"],
            toolbar_location="right",
        )

        self.map_sites(w)

        # -- adding menu options
        menu = Select(
            options=list(rev_vars_dict.keys()),
            value=self.default_var,
            title="Variable",
            css_classes=["custom_select"],
        )
        menu_freq = Select(
            options=freq_list,
            value=self.default_freq,
            title="Frequency",
        )
        menu_site = Select(
            options=self.neon_sites,
            value=self.default_site,
            title="Neon Site",
        )

        # adding menu behaviors:

        menu.on_change("value", self.update_variable)
        menu.on_change("value", self.update_yaxis)

        menu_freq.on_change("value", self.update_variable)

        menu_site.on_change("value", self.update_variable)
        menu_site.on_change("value", self.update_site)

        #layout = column(p, w)
        layout = column(row(p, column(menu, menu_freq, menu_site, q)), w)

        tab = Panel(child=layout, title="Time Series")
        return tab
