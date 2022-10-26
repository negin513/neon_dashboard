#! /usr/bin/env python

# Import Libraries
import os
import sys
import glob
import time

from os.path import join
from glob import glob


import numpy as np
import pandas as pd
import xarray as xr
import yaml 

from bokeh.models import Panel, Tabs
from bokeh.io import curdoc

from scipy import stats
from bokeh.themes import Theme
from bokeh.models import ColumnDataSource, Slider , Dropdown, Select, PreText, Label, Slope, Band
from bokeh.models import (Button, ColumnDataSource, CustomJS, DataTable,
                          NumberFormatter, RangeSlider, TableColumn)
from bokeh.layouts import row,column
        
from bokeh.io import output_notebook, show, curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool

class NeonSite ():
  def __init__(self, name, long_name, lat, lon, state):
    self.site_code = name
    self.long_name = long_name
    self.lat = lat
    self.lon = lon
    self.state = state


def get_preprocessed_files(csv_dir, neon_site):
    fnames = glob(join(csv_dir, 'preprocessed_'+neon_site+'_'+'*.csv'))
    return fnames

def in_notebook():
    from IPython import get_ipython
    if get_ipython():
        return True
    else:
        return False  

ShowWebpage = True

if in_notebook():
    ShowWebpage = False

if ShowWebpage:
    pass
else:
    output_notebook()


neon_sites = ['BART', 'HARV', 'BLAN',
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
            
neon_sites_pft = pd.read_csv('data/all_neon_sites.csv')
#neon_sites = neon_sites_pft['Site'].to_list()

all_sites ={}
for index, this_row in neon_sites_pft.iterrows():
    this_site = NeonSite(this_row['Site'],this_row['site_name'],
                         this_row ['Lat'],this_row['Lon'],this_row['state'])
    all_sites[this_row['Site']]=this_site

print ('Total number of NEON sites for this demo:', len(neon_sites))

years =['2018','2019','2020','2021']

failed_sites = []
csv_dir = "/Users/negins/Desktop/Simulations/tutorials/will_runs/preprocessed_neon_v2/"
df_list =[]
start_site = time.time()
for neon_site in neon_sites:
    try: 
        csv_file = "preprocessed_"+neon_site+"_2021.csv"
        this_df = pd.read_csv(os.path.join(csv_dir, csv_file))
        df_list.append(this_df)
    except:
        #print ('THIS SITE FAILED:', neon_site)
        failed_sites.append(neon_site)
        pass

df_all = pd.concat(df_list)

end_site = time.time()
print("Reading all preprocessed files took:", end_site-start_site, "s.")

print ("Number of failed sites : ", len(failed_sites))
print (*failed_sites, sep=" \n")

# -- fix time formatting
df_all['time'] = pd.to_datetime(df_all['time'], errors='coerce')

#-- extract year, month, day, hour information from time
df_all['year'] = df_all['time'].dt.year
df_all['month'] = df_all['time'].dt.month
df_all['day'] = df_all['time'].dt.day
df_all['hour'] = df_all['time'].dt.hour
df_all['season'] = ((df_all['month']%12+3)//3).map({1:'DJF', 2: 'MAM', 3:'JJA', 4:'SON'})

df_all['ELAI'] = np.nan

#df_all ['NEE'] = df_all['NEE']*60*60*24
#df_all ['sim_NEE'] = df_all['sim_NEE']*60*60*24
#df_all ['GPP'] = df_all['GPP']*60*60*24
#df_all ['sim_GPP'] = df_all['sim_GPP']*60*60*24


freq_list = ['all','hourly','daily','monthly']


def get_data (df_all, var, freq, this_site):
    print ('this_site', this_site)
    df=df_all[df_all['site']==this_site]
    sim_var_name = "sim_"+var

    if freq=="monthly":
        df = df.groupby(['year','month']).mean().reset_index()
        df["day"]=15
        df['time']=pd.to_datetime(df[["year", "month","day"]])
        #if var=='NEE' or var=='GPP':
        #    df

    elif freq=="daily":
        df = df.groupby(['year','month','day']).mean().reset_index()
        df['time']=pd.to_datetime(df[["year", "month", "day"]])

    elif freq=="hourly":
        df = df.groupby(['year','month','day','hour']).mean().reset_index()
        df['time']=pd.to_datetime(df[["year", "month", "day","hour"]])
    
    elif freq=="all":
        df = df
    
    df_new = pd.DataFrame({'time':df['time'],'NEON':df[var],'CLM':df[sim_var_name]})
    
    #print(df_new)
    return df_new

def find_regline(df, var, sim_var_name):
        # find the trendline:
        #sim_var_name = "sim_"+var
        #print (var)
        #print (sim_var_name)

        df_temp = df[[var, sim_var_name]]#.dropna()
        
        #df_temp = pd.DataFrame(df, columns)
        df_temp.dropna(inplace=True)
        #print (df_temp)

        #z = np.polyfit(df_temp[var], df_temp[sim_var_name], 1)
        #p = np.poly1d(z)
        
        #-----
        slope, intercept, r_value, p_value, std_err = stats.linregress(df_temp[var], df_temp[sim_var_name])
        return slope, intercept, r_value, p_value, std_err

    

plot_vars =['FSH','EFLX_LH_TOT','Rnet','NEE','GPP','ELAI']
vars_dict = {'FSH': 'Sensible Heat Flux', 'EFLX_LH_TOT': 'Latent Heat Flux',\
     'GPP': 'Gross Primary Production','NEE': 'Net Ecosystem Exchange', \
     'ELAI': 'Effective Leaf Area Index'}

vars_dict2 = {y: x for x, y in vars_dict.items()}

# time-series with Dropdown menu for variables

# make a simple plot time-series


def simple_tseries():
    #-- default values:
    
    default_site = 'ABBY'
    default_freq = 'daily'
    defualt_var = 'EFLX_LH_TOT'
    
    df_new = get_data(df_all, defualt_var,default_freq,default_site)
    source = ColumnDataSource(df_new)

    #-- what are tools options
    #tools = "pan, wheel_zoom, box_zoom ,box_select,lasso_select, undo, redo, save, reset, hover, crosshair, tap"
    #tools = "tap"
    
    p_tools = "pan, wheel_zoom, box_zoom, box_select, undo, redo, save, reset, hover, crosshair"
    q_tools = "pan,  box_zoom, box_select, lasso_select, undo, redo, reset, crosshair"

    def tseries_plot(p):
        p.line('time', 'NEON', source=source, alpha=0.8, line_width=4, color="navy", legend_label="NEON")
        p.line('time', 'CLM',source=source , alpha=0.8, line_width=3, color="red", legend_label="CLM")
        p.circle('time', 'NEON', size=2, source=source, color=None, selection_color="navy")
        p.circle('time', 'CLM', size=2, source=source, color=None, selection_color="red")
        
        #p.circle('time', 'var', source=source, alpha=0.8, color="navy")

        p.xaxis.major_label_text_color = 'dimgray'
        p.xaxis.major_label_text_font_size = '18px'
        p.xaxis.major_label_text_font_style = "bold"

        p.yaxis.major_label_text_color = 'dimgray'
        p.yaxis.major_label_text_font_size = '18px'
        p.yaxis.major_label_text_font_style = "bold"

        p.xaxis.axis_label_text_font = 'Tahoma'
        p.yaxis.axis_label_text_font = 'Tahoma'
        p.xaxis.axis_label_text_font_size = "15pt"
        p.xaxis.axis_label_text_font_style = "bold"
        
        p.yaxis.axis_label_text_font_size = "15pt"
        p.yaxis.axis_label_text_font_style = "bold"
        
        p.axis.axis_label_text_font_style = "bold"
        
        p.grid.grid_line_alpha = 0.5
        p.title.text_font_size = '21pt'
        p.xaxis.axis_label = 'Time'
        p.yaxis.axis_label = 'Latent Heat Flux [W m⁻²]'

        p.title.text_font = 'Tahoma'
        p.title.text = "Time-Series Plot for Neon Site : " +default_site
        
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "15pt"
        p.legend.label_text_font_style = "bold"

        #p.legend.label_text_font = "times"
        p.legend.label_text_color = "dimgray"
        p.legend.background_fill_alpha = 0.25

    def scatter_plot(q):
        q.circle('NEON', 'CLM', source=source,
                alpha=0.8 , color="navy" , fill_alpha=0.2 , size=10, 
                hover_color = "firebrick" , selection_color="orange",
                nonselection_alpha=0.1 , selection_alpha=0.5)

        q.xaxis.major_label_text_color = 'dimgray'
        q.xaxis.major_label_text_font_size = '15px'
        q.xaxis.major_label_text_font_style = "bold"

        q.yaxis.major_label_text_color = 'dimgray'
        q.yaxis.major_label_text_font_size = '15px'
        q.yaxis.major_label_text_font_style = "bold"

        q.xaxis.axis_label_text_font_size = "13pt"
        q.yaxis.axis_label_text_font_size = "13pt"

        q.xaxis.axis_label_text_font = 'Verdana'
        q.yaxis.axis_label_text_font = 'Verdana'

        q.title.text_font = 'Verdana'
        q.axis.axis_label_text_font_style = "bold"
        q.grid.grid_line_alpha = 0.5
        q.title.text_font_size = '15pt'
        q.xaxis.axis_label = 'NEON'
        q.yaxis.axis_label = 'CLM'
        
        #q.xaxis.major_label_orientation = "vertical"
        q.xaxis.major_label_orientation = np.pi/4
    
        
    p_width = 900
    p_height = 550
    p = figure (tools=p_tools, x_axis_type="datetime",
                title= "Neon Time-Series "+neon_site , width = p_width, height =p_height)
    tseries_plot(p)
    
    q_width = 550
    q_height = 550
    q = figure(tools=q_tools,width=350, 
               height=350, x_range=p.y_range, y_range=p.y_range)
    scatter_plot(q)
    
    q.add_tools(
        HoverTool(
            tooltips=[
                      ("NEON", "$x"),
                      ("CLM", "$y")]
        )
    )
    
    
    #q.add_tools(
    #    HoverTool(tooltips=[('date', '@tooltip')],
    #      formatters={'@DateTime': 'datetime'})
    #)
    
    stats = PreText(text='', width=500)

    menu = Select(options=list(vars_dict2.keys()),value=vars_dict[defualt_var],
                  title='Variable', css_classes=['custom_select']) 
    menu_freq = Select(options=freq_list,value=default_freq, title='Frequency') 
    menu_site = Select(options=neon_sites,value=default_site, title='Neon Site') 

    def update_variable (attr, old, new):
        print ('updating plot for:')
        print (' - freq : ', menu_freq.value)
        print (' - site : ', menu_site.value)
        new_var = vars_dict2[menu.value]
        print (' - var  : ', new_var)

        df_new = get_data(df_all, new_var, menu_freq.value, menu_site.value)

        #q.add_layout(mytext)
        #q.add_layout(regression_line)
        
        #source = ColumnDataSource(df_new)
        source.data =df_new
        #source.stream(df_new)


    def update_site (attr, old, new):
        new_var =vars_dict2[menu.value]
        df_new = get_data(df_all, new_var, menu_freq.value, menu_site.value)
        source.data.update =df_new
        #source.stream(df_new)
        #print (menu.value)
        #print (menu_freq.value)
        print (menu_site.value)
        p.title.text = "Time-Series Plot for Neon Site : " +menu_site.value

    def update_yaxis (attr, old, new):
        new_var =vars_dict2[menu.value]

        if (new_var=='EFLX_LH_TOT'):
            p.yaxis.axis_label = 'Latent Heat Flux [W m⁻²]'
        elif (new_var=='FSH'):
            p.yaxis.axis_label = 'Sensible Heat Flux [W m⁻²]'
        elif (new_var=='Rnet'):
            p.yaxis.axis_label = 'Net Radiation [W m⁻²]'
        elif (new_var=='NEE'):
            p.yaxis.axis_label = 'Net Ecosystem Exchange [gC m⁻² day⁻¹]'
        elif (new_var=='GPP'):
            p.yaxis.axis_label = 'Gross Primary Production [gC m⁻² day⁻¹]'
        elif (new_var=='ELAI'):
            p.yaxis.axis_label = 'Exposed Leaf Area Index'


    menu.on_change('value', update_variable)
    menu.on_change('value', update_yaxis)

    menu_freq.on_change('value', update_variable)
    
    menu_site.on_change('value', update_variable)
    menu_site.on_change('value', update_site)
    
    
    #layout = row(column(menu, menu_freq, menu_site, q),  p)
    layout = row(p, column( menu, menu_freq, menu_site, q))
    #layout = gridplot([[p, q]])
    tab = Panel(child = layout, title = 'Time Series')

    #doc.add_root(layout)
    
    #doc.theme = Theme(json=yaml.load("""
    #    attrs:
    #        Figure:
    #            background_fill_color: "#FFFFFF"
    #            outline_line_color: grey
    #            toolbar_location: above
    #            height: 550
    #            width: 1100
    #        Grid:
    #            grid_line_dash: [6, 4]
    #            grid_line_color: grey
    #""", Loader=yaml.FullLoader))
    return tab


plot_vars =['FSH','EFLX_LH_TOT','Rnet','NEE','GPP']
valid_vars = plot_vars


def get_diel_data (df, var, season, this_site):

    print ('this site:', this_site)
    if (season != "Annual"):
        df = df[df['season']==season]

    df_this = df[df['site']==this_site]

    if var == 'NEE' or var == 'GPP':
        min_thresh = -100 * (12.01/1000000) *60*60*24
        max_thresh = 100 * (12.01/1000000) *60*60*24
    elif var == 'Rnet' or var == 'FSH' or var == 'EFLX_LH_TOT':
        min_thresh = -500
        max_thresh = 1000

    if var == 'ELAI':
        df = df_this
    else:
        #df, count = remove_outliers_manual (df_this, var, min_thresh, max_thresh)
        df = df_this




    diel_df_mean = df.groupby('hour').mean().reset_index()
    diel_df_std = df.groupby('hour').std().reset_index()

    print (diel_df_mean)

    sim_var_name = "sim_"+var
    bias_var_name = "bias_"+var
    std_var_name = "std_"+var

    diel_df_mean[bias_var_name] = diel_df_mean[sim_var_name]-diel_df_mean[var]

    df_new = pd.DataFrame({'hour':diel_df_mean['hour'],'NEON':diel_df_mean[var],'CLM':diel_df_mean[sim_var_name]})

   # df_new ['CLM'][-1] = diel_df_mean[sim_var_name][0]

    print (df_new['CLM'])
    df_new['Bias'] = diel_df_mean[sim_var_name] - diel_df_mean[var]
    df_new['NEON_lower'] = diel_df_mean[var]-diel_df_std[var]
    df_new['NEON_upper'] = diel_df_mean[var]+diel_df_std[var]

    df_new['CLM_lower'] = diel_df_mean[sim_var_name]-diel_df_std[sim_var_name]
    df_new['CLM_upper'] = diel_df_mean[sim_var_name]+diel_df_std[sim_var_name]

    return df_new


def find_regline(df, var, sim_var_name):

        df_temp = df[[var, sim_var_name]]
        #df_temp = pd.DataFrame(df, columns)
        #df_temp.dropna(inplace=True)
        #print (df_temp)

        #z = np.polyfit(df_temp[var], df_temp[sim_var_name], 1)
        #p = np.poly1d(z)

        #-----
        print (df_temp)
        slope, intercept, r_value, p_value, std_err = stats.linregress(df_temp[var], df_temp[sim_var_name])
        return slope, intercept, r_value, p_value, std_err

def fit_func(df):
    df_temp = df[['NEON', 'CLM']]
    print ('df_temp:')
    print (df_temp)
    print ('------------')
    print ('------------')
    print ('------------')
    print ('------------')
    print ('------------')
    print ('------------')
    slope, intercept, r_value, p_value, std_err = stats.linregress(df_temp['NEON'], df_temp['CLM'])

    x_fit = df_temp['NEON'].sort_values()

    min_x_fit = df_temp.min().min() - x_fit.mean()
    max_x_fit = df_temp.max().max() + 1.5*x_fit.mean()
    print ('max_x_fit',max_x_fit)
    print ('min_x_fit',min_x_fit)

    x_fit = np.arange(min_x_fit, max_x_fit)
    y_fit = slope*x_fit +intercept
    print ('======')
    print (y_fit)
    return x_fit, y_fit


def diel_doc():
    #-- default values:

    default_site = 'ABBY'
    default_season = 'DJF'
    default_var = 'EFLX_LH_TOT'
    default_var_desc = "Latent Heat Flux [W/m2]"

    df_new = get_diel_data (df_all, default_var,default_season, default_site)
    source = ColumnDataSource(df_new)
    x_fit, y_fit = fit_func(df_new)
    source_fit =  ColumnDataSource(data={'x': x_fit, 'y': y_fit})
    #-- what are tools options
    #tools = "hover, box_zoom, undo, crosshair"
    p_tools = "pan, wheel_zoom, box_zoom,  undo, redo, save, reset, crosshair,xbox_select"
    q_tools = "pan, wheel_zoom, box_zoom, box_select, lasso_select, reset, crosshair"
    def diel_shaded_plot(p):
        p.line('hour', 'NEON', source=source, alpha=0.8, line_width=4, color="navy", legend_label="NEON")
        p.line('hour', 'CLM',source=source , alpha=0.8, line_width=3, color="red", legend_label="CLM")

        p.circle('hour', 'NEON', size=7, source=source, color="navy", selection_color="navy")
        p.circle('hour', 'CLM', size=7, source=source, color="red", selection_color="red")

        p.line('hour', 'NEON_lower',source=source , alpha=0.5, line_width=3, color="#6495ED")
        p.line('hour', 'NEON_upper',source=source , alpha=0.5, line_width=3, color="#6495ED")

        band_neon = Band(base='hour', lower='NEON_lower', upper='NEON_upper', source=source,level='underlay',
                fill_alpha=0.3,fill_color='#6495ED')

        band_clm = Band(base='hour', lower='CLM_lower', upper='CLM_upper', source=source,level='underlay',
                fill_alpha=0.3,fill_color='#F08080')

        p.line('hour', 'CLM_lower',source=source , alpha=0.5, line_width=3, color="#F08080")
        p.line('hour', 'CLM_upper',source=source , alpha=0.5, line_width=3, color="#F08080")

        p.add_layout(band_neon)
        p.add_layout(band_clm)

        p.xaxis.major_label_text_color = 'dimgray'
        p.xaxis.major_label_text_font_size = '18px'
        p.xaxis.major_label_text_font_style = "bold"

        p.yaxis.major_label_text_color = 'dimgray'
        p.yaxis.major_label_text_font_size = '18px'
        p.yaxis.major_label_text_font_style = "bold"

        p.xaxis.axis_label_text_font_size = "15pt"
        p.xaxis.axis_label_text_font_style = "bold"

        p.yaxis.axis_label_text_font_size = "15pt"
        p.yaxis.axis_label_text_font_style = "bold"

        p.axis.axis_label_text_font_style = "bold"

        p.grid.grid_line_alpha = 0.5
        p.title.text_font_size = '18pt'

        p.xaxis.axis_label = 'Hour of Day'
        p.yaxis.axis_label = 'Latent Heat Flux [W m⁻²]'

        p.title.text = "Diurnal Cycle Plot for Neon Site : " +default_site

        p.legend.location = "top_right"
        p.legend.label_text_font_size = "13pt"
        p.legend.label_text_font_style = "bold"

        #p.legend.label_text_font = "times"
        p.legend.label_text_color = "dimgray"
        p.legend.background_fill_alpha = 0.25
        
        
    def diel_bias_plot (q):
        q.line('hour', 'Bias', source=source, alpha=0.8, line_width=4, color="green", legend_label="Bias")
        q.circle('hour', 'Bias', size=7, source=source, color="green")

        q.xaxis.major_label_text_color = 'dimgray'
        q.xaxis.major_label_text_font_size = '18px'
        q.xaxis.major_label_text_font_style = "bold"

        q.yaxis.major_label_text_color = 'dimgray'
        q.yaxis.major_label_text_font_size = '18px'
        q.yaxis.major_label_text_font_style = "bold"

        q.xaxis.axis_label_text_font_size = "15pt"
        q.xaxis.axis_label_text_font_style = "bold"

        q.yaxis.axis_label_text_font_size = "15pt"
        q.yaxis.axis_label_text_font_style = "bold"

        q.axis.axis_label_text_font_style = "bold"

        q.grid.grid_line_alpha = 0.5
        q.xaxis.axis_label = 'Hour of Day'
        q.yaxis.axis_label = 'Bias'

        q.legend.location = "top_right"
        q.legend.label_text_font_size = "13pt"
        q.legend.label_text_font_style = "bold"

        #p.legend.label_text_font = "times"
        q.legend.label_text_color = "dimgray"
        q.legend.background_fill_alpha = 0.25

        zeros = np.zeros(26)
        x= range(-1,25)
        #q.line (x, zeros,line_width=4, color="darkgray", alpha=0.8,line_dash="dashed")
        zero_line = Slope(gradient=0, y_intercept=0, line_color="gray",line_width=3, line_alpha = 0.8,line_dash="dashed")
        q.add_layout(zero_line)
        
    def scatter_plot(q):
        q.circle('NEON', 'CLM', source=source, alpha=0.8, color="navy",fill_alpha=0.4, size=13, hover_color = "firebrick", selection_color="orange", nonselection_alpha=0.1, selection_alpha=0.5)

        q.xaxis.major_label_text_color = 'dimgray'
        q.xaxis.major_label_text_font_size = '18px'
        q.xaxis.major_label_text_font_style = "bold"

        q.yaxis.major_label_text_color = 'dimgray'
        q.yaxis.major_label_text_font_size = '18px'
        q.yaxis.major_label_text_font_style = "bold"

        q.xaxis.axis_label_text_font_size = "15pt"
        q.xaxis.axis_label_text_font_style = "bold"

        q.yaxis.axis_label_text_font_size = "15pt"
        q.yaxis.axis_label_text_font_style = "bold"

        q.axis.axis_label_text_font_style = "bold"

        q.grid.grid_line_alpha = 0.5
        q.title.text_font_size = '13pt'
        q.xaxis.axis_label = 'NEON'
        q.yaxis.axis_label = 'CLM'

        slope, intercept, r_value, p_value, std_err = find_regline(df_new, 'NEON','CLM')
        print ('slope:', slope)
        print ('intercept:', intercept)
        #print ("new r_value:",r_value)
        slope_label = "y = "+"{:.2f}".format(slope)+"x"+" + "+"{:.2f}".format(intercept)+" (R² = "+"{:.2f}".format(r_value)+")"
        mytext = Label(text=slope_label , x=0+20, y=q_height-100,
                        x_units="screen", y_units='screen', text_align="left")

        regression_line = Slope(gradient=slope, y_intercept=intercept, line_color="navy",line_width=2, line_alpha = 0.8)

        #print (mytext)
        #q.add_layout(mytext)
        #q.add_layout(regression_line)
        q.title.text = slope_label

        #x = range(0,50)
        #y = slope*x+intercept
        oneone_line = Slope(gradient=1, y_intercept=0, line_color="gray",line_width=2, line_alpha = 0.3,line_dash="dashed")
        q.add_layout(oneone_line)

        #q.line(x, y,alpha=0.8, line_width=4, color="gray")

        #x = df_new['NEON']
        #y = df_new['CLM']

        #par = np.polyfit(x, y, 1, full=True)
        #slope=par[0][0]
        #intercept=par[0][1]
        #print ('------------')
        #print ('slope:', slope)
        #print ('intercept:', intercept)
        # Make the regression line
        #regression_line = Slope(gradient=slope, y_intercept=intercept, line_color="red")
        #q.add_layout(regression_line)
        q.line('x', 'y', source=source_fit, alpha=0.8, color="navy",line_width=3)
        
    p_width = 950
    p_height = 450
    p = figure(tools=p_tools, title= "Diurnal Cycle Plot for Neon Site : " +default_site, active_drag="xbox_select", width = p_width, height = p_height)
    diel_shaded_plot(p)


    q_width = 950
    q_height = 300
    q = figure(tools=p_tools,width=q_width, height=q_height, x_range=p.x_range, active_drag="xbox_select")
    diel_bias_plot(q)


    q.add_tools(
        HoverTool(
            tooltips=[
                      ("Hour", "$index"),
                      ("Bias", "@Bias")]
        )
    )
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

    q_width = 350
    q_height = 350
    qq = figure(tools=q_tools,width=350, height=350, toolbar_location="right",toolbar_sticky=False,active_drag="box_select",x_range=p.y_range,y_range=p.y_range)
    scatter_plot(qq)

    qq.add_tools(
        HoverTool(
            tooltips=[
                      ("NEON", "$x"),
                      ("CLM", "$y")]
        )
    )

    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    stat_summary = df_new[['NEON','CLM']].describe()
    title = 'Statistical Summary'
    line  = '-------------------'
    print (stat_summary)
    stats_text = title +  '\n'+str(stat_summary)

    stats = PreText(text=stats_text, width=500,sizing_mode='stretch_width',style={'color': 'dimgray','font-weight': 'bold','font-size':'11pt','font-family': 'Arial'})

    menu = Select(options=valid_vars,value='EFLX_LH_TOT', title='Variable')
    menu_season =  Select(options=["DJF","MAM", "JJA", "SON", "Annual"],value='DJF', title='Season')
    menu_site = Select(options=neon_sites,value=default_site, title='Neon Site')

    def update_stats(df_new):

        stat_summary = df_new[['NEON','CLM']].describe()
        print ('~~~~~~~~~~~~')
        title = 'Statistical Summary'
        line  = '-------------------'
        print (stat_summary)
        stats.text = title +  '\n'+str(stat_summary)

    def update_variable (attr, old, new):

        print ('updating plot for:')
        print (' - var  : ', menu.value)
        print (' - freq : ', menu_season.value)
        print (' - site : ', menu_site.value)

        df_new = get_diel_data(df_all, menu.value, menu_season.value, menu_site.value)
        update_stats(df_new)

        source.data =df_new
        #diel_shaded_plot(p)
        #scatter_plot(qq)
        #scatter_plot(q)
        #source.stream(df_new)
        var = menu.value
        sim_var_name = 'sim_'+var
        print ('***************')
        print (df_new)

        x_fit, y_fit = fit_func(df_new)
        source_fit.data =  {'x': x_fit, 'y': y_fit}

        slope, intercept, r_value, p_value, std_err = find_regline(df_new, 'NEON','CLM')
        #print (r_value)
        if intercept >0:
            slope_label = "y = "+"{:.2f}".format(slope)+"x"+" + "+"{:.2f}".format(intercept)+" (R² = "+"{:.2f}".format(r_value)+")"
        else:
            slope_label = "y = "+"{:.2f}".format(slope)+"x"+" "+"{:.2f}".format(intercept)+" (R² = "+"{:.2f}".format(r_value)+")"

        #mytext = Label(text=slope_label , x=0+20, y=q_height-100, 
        #                x_units="screen", y_units='screen', text_align="left")

        regression_line = Slope(gradient=slope, y_intercept=intercept, line_color="red")

        #qq.add_layout(mytext)
        #print (q)
        qq.title.text = slope_label
        #qq.add_layout(regression_line)
        
    def update_site (attr, old, new):
        df_new = get_diel_data(df_all, menu.value, menu_season.value, menu_site.value)
        print ('-----')
        print (df_new)
        source.data.update =df_new
        #source.stream(df_new)
        #print (menu.value)
        #print (menu_freq.value)
        print (menu_site.value)
        p.title.text = "Neon Diurnal Cycle " +menu_site.value

    def update_yaxis (attr, old, new):
        if (menu.value=='EFLX_LH_TOT'):
            p.yaxis.axis_label = 'Latent Heat Flux [W m⁻²]'
        elif (menu.value=='FSH'):
            p.yaxis.axis_label = 'Sensible Heat Flux [W m⁻²]'
        elif (menu.value=='Rnet'):
            p.yaxis.axis_label = 'Net Radiation [W m⁻²]'
        elif (menu.value=='NEE'):
            p.yaxis.axis_label = 'Net Ecosystem Exchange [gC m⁻² day⁻¹]'
        elif (menu.value=='GPP'):
            p.yaxis.axis_label = 'Gross Primary Production [gC m⁻² day⁻¹]'
        elif (menu.value=='ELAI'):
            p.yaxis.axis_label = 'Exposed Leaf Area Index'



    menu.on_change('value', update_variable)
    menu.on_change('value', update_yaxis)

    menu_season.on_change('value', update_variable)

    menu_site.on_change('value', update_site)
    menu_site.on_change('value', update_variable)

    #layout = row(column(menu, menu_freq, menu_site, q),  p)
    layout = row(column(p,q), column( menu, menu_season, menu_site, stats,qq))
    #doc.add_root(layout)
    tab = Panel(child = layout, title = 'Diurnal Cycle')
    return tab
    
    
    
    
        

# output_notebook()

#if ShowWebpage:
#    simple_tseries(curdoc())
#else:
#    #show(bkapp)
#    #show(simple_tseries)
    
    

tab_1 = simple_tseries()
tab_2 = diel_doc()
tabs=Tabs(tabs=[tab_1,tab_2])
#doc.add_root(tabs)

curdoc().add_root(tabs)
    
#make_doc(doc)