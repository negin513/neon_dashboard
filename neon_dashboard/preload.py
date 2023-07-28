import os,sys,time
import pandas as pd
import numpy as np
from pyproj import Proj, transform

# //////////////////////////////////////////////////////////////////////////////////////
class Preload:

    neon_sites = ['ABBY','BART', 'HARV', 'BLAN',
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

    neon_sites_pft=None
    df_all=None
    us_lon1, us_lat1, us_lon2, us_lat2=[None,None,None,None]

    @staticmethod
    def run():

        neon_sites_pft = pd.read_csv('data/all_neon_sites.csv')

        print ('Total number of NEON sites for this demo:', len(Preload.neon_sites))

        failed_sites = []
        csv_dir = "data/preprocessed_data/"
        df_list =[]
        start_site = time.time()
        
        for it in Preload.neon_sites:
            try: 
                csv_file = "preprocessed_"+it+"_2021.csv"
                this_df = pd.read_csv(os.path.join(csv_dir, csv_file))
                print (os.path.join(csv_dir, csv_file))
                df_list.append(this_df)
            except:
                #print ('THIS SITE FAILED:', it)
                failed_sites.append(it)
                pass

        print (failed_sites)
        df_all = pd.concat(df_list)
        print (len(df_all))
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

        inProj  = Proj(init='epsg:3857')
        outProj = Proj(init='epsg:4326')
        us_lon1, us_lat1 = transform(outProj,inProj,-130,23)
        us_lon2, us_lat2 = transform(outProj,inProj,-65,49)

        x = neon_sites_pft['Lon']
        y = neon_sites_pft['Lat']
        x_transform, y_trasnform = transform(outProj,inProj,x,y)
        neon_sites_pft ['map_lat'] = y_trasnform
        neon_sites_pft ['map_lon'] = x_transform

            # reassign all variables
        Preload.neon_sites_pft=neon_sites_pft
        Preload.df_all=df_all
        Preload.us_lon1=us_lon1
        Preload.us_lat1=us_lat1
        Preload.us_lon2=us_lon2
        Preload.us_lat2=us_lat2