"""
Author: Negin Sobhani
Created on: 2022-10-01
Contact Info: negins@ucar.edu
"""

from bokeh.plotting import figure
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

# Importing required custom modules
from data_utils import *
from base_tab import *


freq_list = ["all", "hourly", "daily", "monthly"]

p_tools = "pan, wheel_zoom, box_zoom, box_select, undo, redo, save, reset, crosshair"
q_tools = "pan, box_zoom, box_select, lasso_select, crosshair"


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

        self.load_data()

    def load_data(self):
        """
        Function for creating ColumnDataSources.
        """
        self.df_new = get_data(
            self.df_all, self.default_var, self.default_freq, self.default_site
        )
        self.source = ColumnDataSource(self.df_new)

        self.this_site = get_neon_site(self.neon_sites_pft, self.default_site)
        print(self.this_site)
        print("!!!!")
        self.source2 = ColumnDataSource(self.this_site)
        print(self.this_site["site_name"].values[0].replace(r"[][]", " "))

        x_fit, y_fit = fit_func(self.df_new)
        print(x_fit)
        print(y_fit)
        print("!!!!!!!!!!!!!!!!!!!")
        df_fit = pd.DataFrame({"x": x_fit, "y": y_fit})
        df_fit.dropna(inplace=True)
        print(df_fit["x"])
        print(df_fit["y"])
        print("!!!!!!!!!!!!!!!!!!!")
        self.source_fit = ColumnDataSource(df_fit)

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

        print (self.this_site["Site"].values[0].replace(r"[][]", " "))
        print (self.this_site["state"].values[0].replace(r"[][]", " "))
        print(self.this_site["site_name"].values[0].replace(r"[][]", " "))
        print ('~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print ('~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print ('~~~~~~~~~~~~~~~~~~~~~~~~~~')
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "15pt"
        p.legend.label_text_font_style = "bold"

        # p.legend.label_text_font = "times"
        p.legend.label_text_color = "dimgray"
        p.legend.background_fill_alpha = 0.35

    # def scatter_plot(self, q):
    #     q.circle(
    #         "NEON",
    #         "CLM",
    #         source=self.source,
    #         alpha=0.8,
    #         color="navy",
    #         fill_alpha=0.4,
    #         size=13,
    #         hover_color="firebrick",
    #         selection_color="orange",
    #         nonselection_alpha=0.1,
    #         selection_alpha=0.5,
    #     )

    #     q.xaxis.major_label_text_color = "dimgray"
    #     q.xaxis.major_label_text_font_size = "13pt"
    #     q.xaxis.major_label_text_font_style = "bold"

    #     q.yaxis.major_label_text_color = "dimgray"
    #     q.yaxis.major_label_text_font_size = "13pt"
    #     q.yaxis.major_label_text_font_style = "bold"

    #     q.xaxis.axis_label_text_font_size = "13pt"
    #     q.yaxis.axis_label_text_font_size = "13pt"

    #     q.xaxis.axis_label_text_font_style = "bold"
    #     q.yaxis.axis_label_text_font_style = "bold"

    #     q.xaxis.axis_label_text_font = "Verdana"
    #     q.yaxis.axis_label_text_font = "Verdana"

    #     q.axis.axis_label_text_font_style = "bold"

    #     q.grid.grid_line_alpha = 0.35
    #     q.title.text_font_size = "12pt"

    #     q.xaxis.axis_label = "NEON"
    #     q.yaxis.axis_label = "CTSM"
    #     # df_new = get_diel_data(self.df_all, self.default_var, self.menu_season.value, self.menu_site.value)

    #     # q.xaxis.major_label_orientation = "vertical"
    #     q.xaxis.major_label_orientation = np.pi / 4

    #     print("++++++++++++++++++++")
    #     result = find_regline(self.df_new, "NEON", "CLM")
    #     print("df_new.NEON:", self.df_new["NEON"])
    #     print("df_new.CLM:", self.df_new["CLM"])
    #     print("slope:", result.slope)
    #     print("intercept:", result.intercept)
    #     print("new r_value:", result.rvalue**2)

    #     slope_label = (
    #         "y = "
    #         + "{:.2f}".format(result.slope)
    #         + "x"
    #         + " + "
    #         + "{:.2f}".format(result.intercept)
    #         + " (R² = "
    #         + "{:.3f}".format(result.rvalue**2)
    #         + ")"
    #     )
    #     print(slope_label)

    #     # mytext = Label(
    #     #    text=slope_label,
    #     #    x=0 + 20,
    #     #    y=q_height - 100,
    #     #    x_units="screen",
    #     #    y_units="screen",
    #     #    text_align="left",
    #     # )

    #     regression_line = Slope(
    #         gradient=result.slope,
    #         y_intercept=result.slope,
    #         line_color="navy",
    #         line_width=2,
    #         line_alpha=0.8,
    #     )

    #     # print (mytext)
    #     # q.add_layout(mytext)
    #     # q.add_layout(regression_line)
    #     q.title.text = slope_label

    #     # x = range(0,50)
    #     # y = slope*x+intercept
    #     oneone_line = Slope(
    #         gradient=1,
    #         y_intercept=0,
    #         line_color="gray",
    #         line_width=2,
    #         line_alpha=0.3,
    #         line_dash="dashed",
    #     )
    #     q.add_layout(oneone_line)

    #     # q.line(x, y,alpha=0.8, line_width=4, color="gray")

    #     # x = df_new['NEON']
    #     # y = df_new['CLM']

    #     # par = np.polyfit(x, y, 1, full=True)
    #     # slope=par[0][0]
    #     # intercept=par[0][1]
    #     # print ('------------')
    #     # print ('slope:', slope)
    #     # print ('intercept:', intercept)
    #     # Make the regression line
    #     # regression_line = Slope(gradient=slope, y_intercept=intercept, line_color="red")
    #     #q.add_layout(regression_line)
    #     q.line("x", "y", source=self.source_fit, alpha=0.8, color="red", line_width=3)

    def update_variable(self, attr, old, new):
        print("~~~~~~~~~~~~~~~~~~~~~~~~")
        print("calling update_variable :")
        print(" - freq: ", self.menu_freq.value)
        print(" - site: ", self.menu_site.value)
        print(" - var menu: ", self.menu_var.value)
        # new_var = rev_vars_dict[self.menu_var.value]
        print(" - var: ", rev_vars_dict[self.menu_var.value])

        df_new = get_data(
            self.df_all,
            rev_vars_dict[self.menu_var.value],
            self.menu_freq.value,
            self.menu_site.value,
        )

        self.source.data = df_new

        this_site = get_neon_site(self.neon_sites_pft, self.menu_site.value)
        self.source2.data = this_site

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
        self.q.title.text = slope_label
        # self.q.add_layout(regression_line)

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
        print(" - var menu: ", self.menu_var.value)
        # new_var = rev_vars_dict[self.menu_var.value]
        print(" - var: ", rev_vars_dict[self.menu_var.value])

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
        p_height = 600

        self.p = figure(
            tools="pan, wheel_zoom, box_zoom, box_select, undo, redo, save, reset, crosshair",
            x_axis_type="datetime",
            title="Neon Time-Series " + self.default_site,
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
        q_width = 370
        q_height = 350

        self.q = figure(
            tools=q_tools,
            width=q_width,
            height=q_height,
            toolbar_location="right",
            toolbar_sticky=False,
            active_drag="box_select",
            x_range=self.p.y_range,
            y_range=self.p.y_range,
            tooltips=[("NEON", "@NEON"), ("CLM", "@CLM")],
            margin=(30, 0, 0, 0),
        )
        self.scatter_plot(self.q)

        # -----------------------
        # -- adding map panel
        w_width = 375
        w_height = 225

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

        # -----------------------
        # -- adding menu options
        self.menu_var = Select(
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
                #args=dict(source=self.source, site_name=self.this_site["Site"].values[0].replace(r"[][]", " ")),
                args=dict(source=self.source, download_site=self.menu_site.value, download_freq=self.menu_freq.value, download_var=self.menu_var.value),
                code=open(os.path.join(os.path.dirname(__file__), "models", "download.js")
                ).read(),
            ),
        )

        # -----------------------------
        # adding menu behaviors:

        self.menu_var.on_change("value", self.update_variable)
        self.menu_var.on_change("value", self.update_yaxis)

        self.menu_freq.on_change("value", self.update_variable)

        # -- menu site change :
        self.menu_site.on_change("value", self.update_variable)
        self.menu_site.on_change("value", self.update_site)

        # layout = column(p, w)
        layout = column(
            row(
                self.menu_site,
                self.menu_var,
                self.menu_freq,
                sizing_mode="stretch_width",
            ),
            row(self.p, column(self.q, self.w, button)),
        )

        tab = Panel(child=layout, title="Time Series")
        return tab
