# Standard Library Imports
import os

# Related Third-Party Imports
import numpy as np

from bokeh import models, events
from bokeh.layouts import column, row
from bokeh.models import (
    Band,
    Button,
    ColumnDataSource,
    CustomJS,
    DataTable,
    Div,
    DatetimeTickFormatter,
    HoverTool,
    Label,
    Panel,
    Select,
    Slope,
    TableColumn,
)

from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, Vendors

# Importing required custom modules
from base_tab import *
from data_utils import *

# ----------------- #
# -- default values
# ----------------- #

# default_site = "ABBY"
# default_freq = "daily"
# default_var = "EFLX_LH_TOT"
# default_season = "Annual"


class DielCycle(BaseTab):
    """
    Creates and returns a Bokeh Panel containing the Diel Cycle tab.

    Returns:
        bokeh.models.Panel: The Diel Cycle tab panel.
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
        default_season="Annual",
    ):
        """
        Initializes the DielCycle class.

        Args:
            df_all : DataFrame
                The DataFrame containing all the data.
            neon_sites_pft : DataFrame
                The DataFrame containing NEON site data.
            neon_sites : list
                List of all NEON sites.
            default_var : str
                The default variable to plot.
            default_freq : str
                The default frequency.
            default_site : str
                The default site.
            us_lat1, us_lat2, us_lon1, us_lon2 : float
                The boundaries for US latitudes and longitudes.
            default_season : str, optional
                The default season.
        """
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
        self.default_season = default_season

        self.load_data()

    def load_data(self):
        """
        Function for creating ColumnDataSouces.
        """
        self.df_new = get_diel_data(
            self.df_all, self.default_var, self.default_season, self.default_site
        )
        self.source = ColumnDataSource(self.df_new)

        self.this_site = get_neon_site(self.neon_sites_pft, self.default_site)
        self.source2 = ColumnDataSource(self.this_site)

        x_fit, y_fit = fit_func(self.df_new)
        self.source_fit = ColumnDataSource(data={"x": x_fit, "y": y_fit})

        print(self.this_site["site_name"].values[0].replace(r"[][]", " "))

    def diel_shaded_plot(self, p):
        p.line(
            "local_hour_dt",
            "NEON",
            source=self.source,
            alpha=0.8,
            line_width=4,
            color="navy",
            legend_label="NEON",
        )
        p.line(
            "local_hour_dt",
            "CLM",
            source=self.source,
            alpha=0.8,
            line_width=3,
            color="red",
            legend_label="CTSM",
        )

        p.circle(
            "local_hour_dt",
            "NEON",
            size=7,
            source=self.source,
            color="navy",
            selection_color="navy",
        )
        p.circle(
            "local_hour_dt",
            "CLM",
            size=7,
            source=self.source,
            color="red",
            selection_color="red",
        )

        p.line(
            "local_hour_dt",
            "NEON_lower",
            source=self.source,
            alpha=0.5,
            line_width=3,
            color="#6495ED",
        )
        p.line(
            "local_hour_dt",
            "NEON_upper",
            source=self.source,
            alpha=0.5,
            line_width=3,
            color="#6495ED",
        )

        band_neon = Band(
            base="local_hour_dt",
            lower="NEON_lower",
            upper="NEON_upper",
            source=self.source,
            level="underlay",
            fill_alpha=0.3,
            fill_color="#6495ED",
        )

        band_clm = Band(
            base="local_hour_dt",
            lower="CLM_lower",
            upper="CLM_upper",
            source=self.source,
            level="underlay",
            fill_alpha=0.3,
            fill_color="#F08080",
        )

        p.line(
            "local_hour_dt",
            "CLM_lower",
            source=self.source,
            alpha=0.5,
            line_width=3,
            color="#F08080",
        )
        p.line(
            "local_hour_dt",
            "CLM_upper",
            source=self.source,
            alpha=0.5,
            line_width=3,
            color="#F08080",
        )

        p.add_layout(band_neon)
        p.add_layout(band_clm)

        p.xaxis.major_label_text_color = "dimgray"
        p.xaxis.major_label_text_font_size = "15px"
        p.xaxis.major_label_text_font_style = "bold"

        p.yaxis.major_label_text_color = "dimgray"
        p.yaxis.major_label_text_font_size = "15px"
        p.yaxis.major_label_text_font_style = "bold"

        p.xaxis.axis_label_text_font = "Tahoma"
        p.yaxis.axis_label_text_font = "Tahoma"

        p.xaxis.axis_label_text_font_size = "15pt"
        p.xaxis.axis_label_text_font_style = "bold"

        p.yaxis.axis_label_text_font_size = "15pt"
        p.yaxis.axis_label_text_font_style = "bold"

        p.axis.axis_label_text_font_style = "bold"

        p.grid.grid_line_alpha = 0.35
        p.title.text_font_size = "15pt"

        # p.xaxis.axis_label = 'Hour of Day'
        p.yaxis.axis_label = "Latent Heat Flux [W m⁻²]"
        p.title.text_font = "Tahoma"

        # plot_title = ('NEON Site : '+
        #              this_site['site_name'].values[0].replace(r'[][]', ' ') +', '+
        #              this_site['state'].values[0].replace(r'[][]', ' ') +
        #              ' ('+default_site+') ')

        plot_title = (
            "Diurnal Cycle \n"
            + "NEON Site : "
            + self.this_site["site_name"].values[0].replace(r"[][]", " ")
            + ", "
            + self.this_site["state"].values[0].replace(r"[][]", " ")
            + " ("
            + self.default_site
            + ") "
            + " -- "
            + self.default_season
            + " "
            + "Average"
        )

        p.title.text = plot_title

        p.legend.location = "top_right"
        p.legend.label_text_font_size = "13pt"
        p.legend.label_text_font_style = "bold"

        p.legend.label_text_font = "Tahoma"
        p.legend.label_text_color = "dimgray"
        p.legend.background_fill_alpha = 0.35
        p.toolbar_location = "right"
        p.xaxis.formatter = DatetimeTickFormatter(days="%H:%M", hours="%H:%M")
        p.xaxis.major_label_text_color = "white"
        p.xaxis[0].ticker.desired_num_ticks = 12

    def diel_bias_plot(self, q):
        q.line(
            "local_hour_dt",
            "Bias",
            source=self.source,
            alpha=0.8,
            line_width=4,
            color="green",
            legend_label="Bias",
        )
        q.circle("local_hour_dt", "Bias", size=7, source=self.source, color="green")

        q.xaxis.major_label_text_color = "dimgray"
        q.xaxis.major_label_text_font_size = "15px"
        q.xaxis.major_label_text_font_style = "bold"

        q.yaxis.major_label_text_color = "dimgray"
        q.yaxis.major_label_text_font_size = "15px"
        q.yaxis.major_label_text_font_style = "bold"

        q.xaxis.axis_label_text_font_size = "15pt"
        q.xaxis.axis_label_text_font_style = "bold"

        q.yaxis.axis_label_text_font_size = "15pt"
        q.yaxis.axis_label_text_font_style = "bold"

        q.axis.axis_label_text_font_style = "bold"

        q.grid.grid_line_alpha = 0.35
        q.xaxis.axis_label = "Local Time"
        q.yaxis.axis_label = "Bias"

        q.legend.location = "top_right"
        q.legend.label_text_font_size = "13pt"
        q.legend.label_text_font_style = "bold"

        # p.legend.label_text_font = "times"
        q.legend.label_text_color = "dimgray"
        q.legend.background_fill_alpha = 0.25

        zeros = np.zeros(26)
        x = range(-1, 25)
        # q.line (x, zeros,line_width=4, color="darkgray", alpha=0.8,line_dash="dashed")
        zero_line = Slope(
            gradient=0,
            y_intercept=0,
            line_color="gray",
            line_width=3,
            line_alpha=0.8,
            line_dash="dashed",
        )
        q.add_layout(zero_line)
        q.xaxis.formatter = DatetimeTickFormatter(days="%H:%M", hours="%H:%M")
        q.xaxis.major_label_orientation = np.pi / 4
        q.xaxis[0].ticker.desired_num_ticks = 12

    def update_variable(self, attr, old, new):
        print("~~~~~~~~~~~~~~~~~~~~~~~~")
        print("calling update_variable :")
        print(" - freq : ", self.menu_season.value)
        print(" - site : ", self.menu_site.value)
        print(" - var menu: ", self.menu_var.value)
        new_var = rev_vars_dict[self.menu_var.value]
        print(" - var: ", rev_vars_dict[self.menu_var.value])

        df_new = get_diel_data(
            self.df_all,
            rev_vars_dict[self.menu_var.value],
            self.menu_season.value,
            self.menu_site.value,
        )
        self.update_stats(df_new)

        self.source.data = df_new
        # diel_shaded_plot(p)
        # scatter_plot(qq)
        # scatter_plot(q)
        # self.source.stream(df_new)
        sim_var_name = "sim_" + new_var

        x_fit, y_fit = fit_func(df_new)
        self.source_fit.data = {"x": x_fit, "y": y_fit}

        result = find_regline(df_new, "NEON", "CLM")
        print("~~~~~~~~~~~~~~~~~~~~~")
        print("~~~~~~~~~~~~~~~~~~~~~")
        print("df_new:")
        print(df_new["NEON"])
        print(df_new["CLM"])
        print("~~~~~~~~~~~~~~~~~~~~~")
        print(result)
        slope = result.slope
        intercept = result.intercept
        r_value = result.rvalue**2

        # print (r_value)
        if intercept > 0:
            slope_label = (
                "y = "
                + "{:.2f}".format(slope)
                + "x"
                + " + "
                + "{:.2f}".format(intercept)
                + " (R² = "
                + "{:.3f}".format(r_value)
                + ")"
            )
        else:
            slope_label = (
                "y = "
                + "{:.2f}".format(slope)
                + "x"
                + " "
                + "{:.2f}".format(intercept)
                + " (R² = "
                + "{:.3f}".format(r_value)
                + ")"
            )

        # mytext = Label(text=slope_label , x=0+20, y=q_height-100,
        #                x_units="screen", y_units='screen', text_align="left")

        regression_line = Slope(gradient=slope, y_intercept=intercept, line_color="red")

        # qq.add_layout(mytext)
        # print (q)
        self.qq.title.text = slope_label
        # qq.add_layout(regression_line)

    def update_site(self, attr, old, new):
        new_var = rev_vars_dict[self.menu_var.value]
        df_new = get_diel_data(
            self.df_all, new_var, self.menu_season.value, self.menu_site.value
        )
        print("-----")
        print(df_new)
        self.source.data.update = df_new
        # self.source.stream(df_new)
        # print (self.menu.value)
        # print (menu_freq.value)

        this_site = get_neon_site(self.neon_sites_pft, self.menu_site.value)
        print(this_site)
        # self.source.data.update =df_new
        self.source2.data.update = this_site
        self.source2.data = this_site
        self.update_stats(df_new)

    def update_title(self, attr, old, new):
        this_site = get_neon_site(self.neon_sites_pft, self.menu_site.values)
        plot_title = (
            "Diurnal Cycle \n"
            + "NEON Site : "
            + self.this_site["site_name"].values[0].replace(r"[][]", " ")
            + ", "
            + self.menu_site.value["state"].values[0].replace(r"[][]", " ")
            + " ("
            + self.menu_site.value
            + ") "
            + " -- "
            + self.menu_season.value
            + " "
            + "Average"
        )

        self.p.title.text = plot_title

    def update_stats(self, df_new):
        stat_summary = (
            df_new[["NEON", "CLM"]].describe().applymap(lambda x: f"{x:0.3f}")
        )

        print("~~~~~~~~~~~~")
        title = "Statistical Summary"
        line = "-------------------"
        print(stat_summary)
        self.source3.data = stat_summary
        # source3.stream(df_new)
        print("done with stats")

    def create_tab(self):
        # -----------------------
        TOOLTIP = [
            ("Hour", "$index" + ":00"),
            ("NEON", "@NEON"),
            ("CLM", "@CLM"),
            ("Bias", "@Bias"),
        ]

        # -- what are tools options
        p_tools = (
            "pan, wheel_zoom, box_zoom, undo, redo, save, reset, crosshair,xbox_select"
        )

        q_tools = "pan, box_zoom, box_select, lasso_select, crosshair"

        p_width = 950
        p_height = 500

        q_width = p_width
        q_height = 275

        qq_width = 375
        qq_height = qq_width

        w_width = qq_width
        w_height = 275

        # -- adding shaded time-series panel
        self.p = figure(
            tools=p_tools,
            active_drag="xbox_select",
            width=p_width,
            height=p_height,
            toolbar_location="right",
            x_axis_type="datetime",
            # margin=(-30, 0, 0, 0),
            min_border_left=50,
            min_border_right=30,
        )
        self.diel_shaded_plot(self.p)

        # -----------------------
        # -- adding bias plot
        self.q = figure(
            tools=p_tools,
            width=q_width,
            height=q_height,
            x_range=self.p.x_range,
            active_drag="xbox_select",
            toolbar_location="right",
            x_axis_type="datetime",
            margin=(-30, 0, 0, 0),  # moving bias higher and closer to the tseries plot
            min_border_left=50,
            min_border_right=30,
        )
        self.diel_bias_plot(self.q)

        # -----------------------
        # -- adding scatter plot

        self.qq = figure(
            tools=q_tools,
            width=qq_width,
            height=qq_width,
            toolbar_location="right",
            toolbar_sticky=False,
            active_drag="box_select",
            x_range=self.p.y_range,
            y_range=self.p.y_range,
            margin=(55, 0, 0, 0),
            min_border_left=55,
            # min_border_top=30,
            align="center",
        )
        self.scatter_plot(self.qq)

        # -----------------------
        # -- adding map panel
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
            tooltips=tooltip,
            tools=["wheel_zoom", "pan"],
            toolbar_location="right",
            margin=(-5, 0, 0, 0),
            min_border_left=55,
        )
        self.map_sites(self.w)

        self.p.add_tools(
            HoverTool(
                tooltips=[
                    ("Hour", "$index" + ":00"),
                    ("NEON", "@NEON"),
                    ("CLM", "@CLM"),
                    ("Bias", "@Bias"),
                ]
            )
        )

        self.q.add_tools(
            HoverTool(tooltips=[("Hour", "$index" + ":00"), ("Bias", "@Bias")])
        )

        self.qq.add_tools(HoverTool(tooltips=[("NEON", "$x"), ("CLM", "$y")]))

        pd.set_option("display.float_format", lambda x: "%.3f" % x)

        stat_summary = (
            self.df_new[["NEON", "CLM"]].describe().applymap(lambda x: f"{x:0.3f}")
        )
        self.source3 = ColumnDataSource(stat_summary)

        # title = 'Statistical Summary'
        # print (stat_summary)
        # stats_text = title +  '\n'+str(stat_summary)

        title = Div(
            text='<h3 style="text-align: center">Summary Statistics</h3>',
            width=350,
            margin=(20, 0, 0, 55),
        )

        # stats = PreText(text=stats_text, width=500,sizing_mode='stretch_width',style={'color': 'dimgray','font-weight': 'bold','font-size':'11pt','font-family': 'Arial'})

        columns = [
            TableColumn(field="index", title=" ", width=50),
            TableColumn(field="NEON", title="NEON", width=75),
            TableColumn(field="CLM", title="CTSM", width=75),
        ]

        myTable = DataTable(
            source=self.source3,
            columns=columns,
            index_position=None,
            fit_columns=False,
            width=350,
            margin=(0, 0, 0, 55),
        )

        # -----------------------
        # -- adding menu options
        self.menu_var = Select(
            options=list(rev_vars_dict.keys()),
            value=vars_dict[self.default_var],
            title="Variable",
            css_classes=["custom_select"],
        )
        self.menu_season = Select(
            options=[
                "Annual",
                "MAM",
                "JJA",
                "SON",
                "DJF",
            ],
            value=self.default_season,
            title="Season",
        )
        self.menu_site = Select(
            options=self.neon_sites,
            value=self.default_site,
            title="Neon Site",
        )

        # -----------------------
        # -- adding download button
        button = Button(
            label="Download",
            css_classes=["btn_style"],
            width=275,
            margin=(0, 0, 0, 75),
        )
        button.js_on_event(
            "button_click",
            CustomJS(
                args=dict(source=self.source),
                code=open(
                    os.path.join(os.path.dirname(__file__), "models", "download.js")
                ).read(),
            ),
        )

        # -----------------------------
        # adding menu behaviors:

        # -----------------------------
        # --variable
        self.menu_var.on_change("value", self.update_variable)
        self.menu_var.on_change("value", self.update_yaxis)

        # -- season
        self.menu_season.on_change("value", self.update_variable)
        self.menu_var.on_change("value", self.update_yaxis)
        self.menu_season.on_change("value", self.update_title)

        # -- neon site
        self.menu_site.on_change("value", self.update_variable)
        self.menu_site.on_change("value", self.update_site)
        # self.menu.on_change("value", self.update_yaxis)
        self.menu_site.on_change("value", self.update_title)

        # -- create a layout
        layout = column(
            row(
                self.menu_site,
                self.menu_var,
                self.menu_season,
                sizing_mode="stretch_width",
            ),
            row(
                column(self.p, self.q),
                column(self.qq, self.w, button),
                column(
                    title,
                    myTable,
                ),
                sizing_mode="stretch_width",
            ),
        )

        # doc.add_root(layout)
        tab = Panel(child=layout, title="Diurnal Cycle")
        return tab
