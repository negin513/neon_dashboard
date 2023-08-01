from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import (
    HoverTool,
    ColumnDataSource,
    Band,
    Slope,
    DataTable,
    TableColumn,
    Div,
    Label,
    Select,
    Button,
    DatetimeTickFormatter,
)
from bokeh.tile_providers import get_provider, Vendors
import pandas as pd
import numpy as np
import os
from bokeh.models import Panel
from bokeh.events import ButtonClick
from bokeh import models
from bokeh import events
from bokeh.models import CustomJS

from data_utils import *
from base_tab import *

# ----------------- #
# -- default values
# ----------------- #

default_site = "ABBY"
default_freq = "daily"
default_var = "EFLX_LH_TOT"
default_season = "Annual"

plot_vars = ["FSH", "EFLX_LH_TOT", "Rnet", "NEE", "GPP"]
valid_vars = plot_vars


# --------------------------- #
def diel_doc(df_all, neon_sites_pft, us_lat1, us_lat2, us_lon1, us_lon2):
    """
    Creates and returns a Bokeh Panel containing the Diel Cycle tab.

    Returns:
        bokeh.models.Panel: The Diel Cycle tab panel.
    """

    df_new = get_diel_data(df_all, default_var, default_season, default_site)
    source = ColumnDataSource(df_new)

    this_site = get_neon_site(neon_sites_pft, default_site)
    source2 = ColumnDataSource(this_site)

    x_fit, y_fit = fit_func(df_new)
    source_fit = ColumnDataSource(data={"x": x_fit, "y": y_fit})

    # -- what are tools options
    # tools = "hover, box_zoom, undo, crosshair"
    p_tools = (
        "pan, wheel_zoom, box_zoom,  undo, redo, save, reset, crosshair,xbox_select"
    )
    q_tools = "pan,  box_zoom, box_select, lasso_select, crosshair"

    def diel_shaded_plot(p):
        p.line(
            "local_hour_dt",
            "NEON",
            source=source,
            alpha=0.8,
            line_width=4,
            color="navy",
            legend_label="NEON",
        )
        p.line(
            "local_hour_dt",
            "CLM",
            source=source,
            alpha=0.8,
            line_width=3,
            color="red",
            legend_label="CTSM",
        )

        p.circle(
            "local_hour_dt",
            "NEON",
            size=7,
            source=source,
            color="navy",
            selection_color="navy",
        )
        p.circle(
            "local_hour_dt",
            "CLM",
            size=7,
            source=source,
            color="red",
            selection_color="red",
        )

        p.line(
            "local_hour_dt",
            "NEON_lower",
            source=source,
            alpha=0.5,
            line_width=3,
            color="#6495ED",
        )
        p.line(
            "local_hour_dt",
            "NEON_upper",
            source=source,
            alpha=0.5,
            line_width=3,
            color="#6495ED",
        )

        band_neon = Band(
            base="local_hour_dt",
            lower="NEON_lower",
            upper="NEON_upper",
            source=source,
            level="underlay",
            fill_alpha=0.3,
            fill_color="#6495ED",
        )

        band_clm = Band(
            base="local_hour_dt",
            lower="CLM_lower",
            upper="CLM_upper",
            source=source,
            level="underlay",
            fill_alpha=0.3,
            fill_color="#F08080",
        )

        p.line(
            "local_hour_dt",
            "CLM_lower",
            source=source,
            alpha=0.5,
            line_width=3,
            color="#F08080",
        )
        p.line(
            "local_hour_dt",
            "CLM_upper",
            source=source,
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
        p.title.text_font_size = "18pt"

        # p.xaxis.axis_label = 'Hour of Day'
        p.yaxis.axis_label = "Latent Heat Flux [W m⁻²]"
        p.title.text_font = "Tahoma"

        # plot_title = ('NEON Site : '+
        #              this_site['site_name'].values[0].replace(r'[][]', ' ') +', '+
        #              this_site['state'].values[0].replace(r'[][]', ' ') +
        #              ' ('+default_site+') ')

        p.title.text = (
            "Diurnal Cycle for Neon Site : "
            + default_site
            + " ("
            + default_season
            + " Average)"
        )

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

    def diel_bias_plot(q):
        q.line(
            "local_hour_dt",
            "Bias",
            source=source,
            alpha=0.8,
            line_width=4,
            color="green",
            legend_label="Bias",
        )
        q.circle("local_hour_dt", "Bias", size=7, source=source, color="green")

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

    def scatter_plot(q):
        q.circle(
            "NEON",
            "CLM",
            source=source,
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

        print("++++++++++++++++++++")
        result = find_regline(df_new, "NEON", "CLM")
        print("df_new.NEON:", df_new["NEON"])
        print("df_new.CLM:", df_new["CLM"])
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

        mytext = Label(
            text=slope_label,
            x=0 + 20,
            y=q_height - 100,
            x_units="screen",
            y_units="screen",
            text_align="left",
        )

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
        q.line("x", "y", source=source_fit, alpha=0.8, color="navy", line_width=3)

    def map_site(w):
        w.circle(
            x="map_lon",
            y="map_lat",
            size=10,
            fill_color="dimgray",
            line_color="darkslategray",
            fill_alpha=0.7,
            source=neon_sites_pft,
        )
        w.circle(
            x="map_lon",
            y="map_lat",
            size=10,
            fill_color="darkorange",
            line_color="darkorange",
            fill_alpha=0.9,
            source=source2,
        )
        chosentile = get_provider(Vendors.ESRI_IMAGERY)
        w.add_tile(chosentile)
        w.xaxis.major_label_text_color = "white"
        w.yaxis.major_label_text_color = "white"
        w.grid.visible = False

    p_width = 950
    p_height = 450

    q_width = 950
    q_height = 275

    qq_width = 375
    qq_height = 375

    w_width = 375
    w_height = 275

    p = figure(
        tools=p_tools,
        active_drag="xbox_select",
        width=p_width,
        height=p_height,
        toolbar_location="right",
        x_axis_type="datetime",
    )
    diel_shaded_plot(p)

    q = figure(
        tools=p_tools,
        width=q_width,
        height=q_height,
        x_range=p.x_range,
        active_drag="xbox_select",
        toolbar_location="right",
        x_axis_type="datetime",
        margin=(-30, 0, 0, 0),
    )
    diel_bias_plot(q)

    qq = figure(
        tools=q_tools,
        width=qq_width,
        height=qq_width,
        toolbar_location="right",
        toolbar_sticky=False,
        active_drag="box_select",
        x_range=p.y_range,
        y_range=p.y_range,
        margin=(17, 0, 0, 0),
    )
    scatter_plot(qq)

    w = figure(
        name="neon_map",
        plot_width=w_width,
        plot_height=w_height,
        x_range=(us_lon1, us_lon2),
        y_range=(us_lat1, us_lat2),
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
    )
    map_site(w)

    p.add_tools(
        HoverTool(
            tooltips=[
                ("Hour", "$index"),
                ("NEON", "@NEON"),
                ("CLM", "@CLM"),
                ("Bias", "@Bias"),
            ]
        )
    )

    q.add_tools(HoverTool(tooltips=[("Hour", "$index" + ":00"), ("Bias", "@Bias")]))

    qq.add_tools(HoverTool(tooltips=[("NEON", "$x"), ("CLM", "$y")]))

    pd.set_option("display.float_format", lambda x: "%.3f" % x)

    stat_summary = df_new[["NEON", "CLM"]].describe().applymap(lambda x: f"{x:0.3f}")
    source3 = ColumnDataSource(stat_summary)

    # title = 'Statistical Summary'
    # print (stat_summary)
    # stats_text = title +  '\n'+str(stat_summary)

    title = Div(
        text='<h3 style="text-align: center">Summary Statistics</h3>',
        width=350,
        margin=(0, 0, 0, 10),
    )

    # stats = PreText(text=stats_text, width=500,sizing_mode='stretch_width',style={'color': 'dimgray','font-weight': 'bold','font-size':'11pt','font-family': 'Arial'})

    columns = [
        TableColumn(field="index", title=" ", width=50),
        TableColumn(field="NEON", title="NEON", width=75),
        TableColumn(field="CLM", title="CTSM", width=75),
    ]

    myTable = DataTable(
        source=source3,
        columns=columns,
        index_position=None,
        fit_columns=False,
        width=350,
        margin=(0, 0, 0, 10),
    )

    menu = Select(
        options=list(vars_dict2.keys()),
        value=vars_dict[default_var],
        title="Variable",
        css_classes=["custom_select"],
    )
    menu_season = Select(
        options=["DJF", "MAM", "JJA", "SON", "Annual"],
        value=default_season,
        title="Season",
    )
    menu_site = Select(options=neon_sites, value=default_site, title="Neon Site")

    button = Button(label="Download", css_classes=["btn_style"], width=300)
    button.js_on_event(
        "button_click",
        CustomJS(
            args=dict(source=source),
            code=open(
                os.path.join(os.path.dirname(__file__), "models", "download.js")
            ).read(),
        ),
    )

    def update_stats(df_new):
        stat_summary = (
            df_new[["NEON", "CLM"]].describe().applymap(lambda x: f"{x:0.3f}")
        )

        print("~~~~~~~~~~~~")
        title = "Statistical Summary"
        line = "-------------------"
        print(stat_summary)
        source3.data = stat_summary
        # source3.stream(df_new)
        print("done with stats")

    def update_variable(attr, old, new):
        print("Updating variable")

        print("updating plot for:")
        print(" - freq : ", menu_season.value)
        print(" - site : ", menu_site.value)
        new_var = vars_dict2[menu.value]
        print(" - var  : ", new_var)

        df_new = get_diel_data(df_all, new_var, menu_season.value, menu_site.value)
        update_stats(df_new)

        source.data = df_new
        # diel_shaded_plot(p)
        # scatter_plot(qq)
        # scatter_plot(q)
        # source.stream(df_new)
        sim_var_name = "sim_" + new_var

        x_fit, y_fit = fit_func(df_new)
        source_fit.data = {"x": x_fit, "y": y_fit}

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
        qq.title.text = slope_label
        # qq.add_layout(regression_line)

    def update_site(attr, old, new):
        new_var = vars_dict2[menu.value]
        df_new = get_diel_data(df_all, new_var, menu_season.value, menu_site.value)
        print("-----")
        print(df_new)
        source.data.update = df_new
        # source.stream(df_new)
        # print (menu.value)
        # print (menu_freq.value)

        this_site = get_neon_site(neon_sites_pft, menu_site.value)
        print(this_site)
        # source.data.update =df_new
        source2.data.update = this_site
        source2.data = this_site
        update_stats(df_new)

    def update_title(attr, old, new):
        p.title.text = (
            "Diurnal Cycle for Neon Site : "
            + menu_site.value
            + " ("
            + menu_season.value
            + " Average)"
        )

    def update_yaxis(attr, old, new):
        new_var = vars_dict2[menu.value]

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

    # -----------------------------
    # --variable
    menu.on_change("value", update_variable)
    menu.on_change("value", update_yaxis)

    # -- season
    menu_season.on_change("value", update_variable)
    menu.on_change("value", update_yaxis)
    menu_season.on_change("value", update_title)

    # -- neon site
    menu_site.on_change("value", update_site)
    menu_site.on_change("value", update_variable)
    menu.on_change("value", update_yaxis)
    menu_site.on_change("value", update_title)

    # -- create a layout
    layout = column(
        row(menu, menu_season, menu_site),
        row(column(p, q), column(qq, w), column(title, myTable, button)),
    )

    # doc.add_root(layout)
    tab = Panel(child=layout, title="Diurnal Cycle")
    return tab
