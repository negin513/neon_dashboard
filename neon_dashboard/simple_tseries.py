from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, HoverTool, Select, Panel
from bokeh.tile_providers import get_provider, Vendors


from data_utils import *
from base_tab import *



freq_list = ["all", "hourly", "daily", "monthly"]
plot_vars = ["FSH", "EFLX_LH_TOT", "Rnet", "NEE", "GPP", "ELAI"]


class SimpleTseries(BaseTab):
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
        super().__init__(
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

        p_tools = (
            "pan, wheel_zoom, box_zoom, box_select, undo, redo, save, reset, crosshair"
        )
        q_tools = "pan, box_zoom, box_select, lasso_select, crosshair"

        self.load_data()

    def load_data(self):
        """
        Function for creating ColumnDataSources.
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

    def update_variable(self, attr, old, new):
        print("~~~~~~~~~~~~~~~~~~~~~~~~")
        print("calling update_variable :")
        print(" - freq: ", self.menu_freq.value)
        print(" - site: ", self.menu_site.value)
        print(" - var menu: ", self.menu.value)
        #new_var = rev_vars_dict[self.menu.value]
        print(" - var: ", rev_vars_dict[self.menu.value])

        df_new = get_data(self.df_all, rev_vars_dict[self.menu.value], self.menu_freq.value, self.menu_site.value)
        
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
        print("~~~~~~~~~~~~~~~~~~~~~~~~")
        print("calling update_site :")
        print(" - freq: ", self.menu_freq.value)
        print(" - site: ", self.menu_site.value)
        print(" - var menu: ", self.menu.value)
        #new_var = rev_vars_dict[self.menu.value]
        print(" - var: ", rev_vars_dict[self.menu.value])

        this_site = get_neon_site(self.neon_sites_pft, new)

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

    def create_tab(self):
        
        # -----------------------
        # -- adding time-series panel
        p_width = 1300
        p_height = 550
        neon_site = "ABBY"  # Default site for initial plot

        self.p = figure(
            tools="pan, wheel_zoom, box_zoom, box_select, undo, redo, save, reset, crosshair",
            x_axis_type="datetime",
            title="Neon Time-Series " + neon_site,
            width=p_width,
            height=p_height,
        )

        self.tseries_plot(self.p)

        hover = HoverTool(
            tooltips=[("Time", "@time{%F %T}"), ("NEON", "@NEON"), ("CLM", "@CLM")],
            formatters={"@time": "datetime"},
        )
        self.p.add_tools(hover)

        # -----------------------
        # -- adding scatter panel
        q_width = 350
        q_height = 350

        self.q = figure(
            tools="pan, box_zoom, box_select, lasso_select, crosshair",
            width=q_width,
            height=q_height,
            x_range=self.p.y_range,
            y_range=self.p.y_range,
            tooltips=[("NEON", "@NEON"), ("CLM", "@CLM")],
        )
        self.scatter_plot(self.q)

        # -----------------------
        # -- adding map panel
        w_width = 375
        w_height = 225

        self.w = figure(
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

        self.map_sites(self.w)

        # -----------------------
        # -- adding menu options
        self.menu = Select(
            options=list(rev_vars_dict.keys()),
            value=vars_dict[self.default_var],
            title="Variable",
            css_classes=["custom_select"],
        )
        self.menu_freq = Select(
            options=freq_list,
            value=self.default_freq,
            title="Frequency",
        )
        self.menu_site = Select(
            options=self.neon_sites,
            value=self.default_site,
            title="Neon Site",
        )

        # -----------------------------
        # adding menu behaviors:

        self.menu.on_change("value", self.update_variable)
        self.menu.on_change("value", self.update_yaxis)

        self.menu_freq.on_change("value", self.update_variable)

        # -- menu site change :
        self.menu_site.on_change("value", self.update_variable)
        self.menu_site.on_change("value", self.update_site)

        #layout = column(p, w)
        layout = column(row(self.p, column(self.menu, self.menu_freq, self.menu_site, self.q)), self.w)

        tab = Panel(child=layout, title="Time Series")
        return tab
