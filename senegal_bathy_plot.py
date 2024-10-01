#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 09:52:01 2023
bathymetry grid from GEBCO https://download.gebco.net/

@author: epoirier1
https://download.gebco.net/

Created on Sat Feb 18 06:46:41 2023
map with bathy from GEBCO
as in https://notebook.community/ueapy/ueapy.github.io/content/notebooks/2019-05-30-cartopy-map
had to change variable to "elevation"
@author: user
"""


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import xarray as xr
import cartopy
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.io import shapereader
plt.rcParams.update({'font.size': 20})


# extracted from https://download.gebco.net/
# choose your correct path on your computer here
bathy_file_path = Path(
    'your_path_on_your_machine/gebco_2023_n16.4839_s10.5513_w-20.0759_e-14.4289.nc')

# bordures pour rufisque
# s_lim = 14
# n_lim = 15
# w_lim = -16.5
# e_lim = -17.7

# bordures pour joal
s_lim = 13.65
n_lim = 14.71
w_lim = -16.5
e_lim = -17.7

bathy_ds = xr.open_dataset(bathy_file_path)

# had to specify "elevation" instead of "bathy"
bathy_lon, bathy_lat, bathy_h = bathy_ds.elevation.lon, bathy_ds.elevation.lat, bathy_ds.elevation.values
bathy_h[bathy_h > 0] = 0  # removes land

# Ici attention check the bathy_h.min() value, specify steps in colormap (-100,3,3) très raffiné
# the gebco model is cut at specified depth
bathy_conts = np.arange(-100, 5, 5)

# Create random sampling locations within our map area
lons = w_lim + (e_lim-w_lim) * np.random.random_sample(10)
lats = s_lim + (n_lim-s_lim) * np.random.random_sample(10)

# Subset of sampling locations
sample_lon = lons[:3]
sample_lat = lats[:3]

# Import the points of interest we want to display on the map
marker_path = '/home/epoirier1/Documents/PROJETS/2023/rapport_scopes/source/points_gps_mouillages.csv'
df_marker = pd.read_csv(marker_path)

# on rentre la projection ici
# plate carre, je ne sasi pas à quoi ç asert
coord = ccrs.Mercator()
pc = ccrs.PlateCarree()
fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(111, projection=coord)
ax.set_extent([e_lim, w_lim, s_lim, n_lim], crs=pc);

bathy = ax.contourf(bathy_lon, bathy_lat, bathy_h,
                    bathy_conts, transform=pc, cmap="Spectral_r")

gl = ax.gridlines(crs=pc, draw_labels=True, linewidth=1,
                  color="k", alpha=0.5, linestyle="--")
gl.xlabels_top = False
gl.ylabels_right = False
gl.ylines = True
gl.xlines = True

# adjust the cmpa settings, colorbar stuff
fig.colorbar(bathy, ax=ax, orientation="vertical",
             label="Depth (m)", shrink=1, pad=0.03, aspect=40);

# hig res coastline
shp = shapereader.Reader(
    '/home/epoirier1/Documents/PROJETS/2023/rapport_scopes/source/shapefile/land-polygons-complete-4326/hidf_land.shp')
for record, geometry in zip(shp.records(), shp.geometries()):
    ax.add_geometries([geometry], pc, edgecolor='0.5', facecolor='0.8')

# we work here on the small map in the corner sub_ax
# Here we add the inset map sub axes in the top right, note the different projection
tr2 = ccrs.Stereographic(central_latitude=14, central_longitude=-17)
sub_ax = plt.axes([0.6, 0.65, 0.2, 0.2], projection=tr2)
# Try changing the extent of our inset map here
sub_ax.set_extent([w_lim-10, e_lim+10, s_lim-10, n_lim+10], crs=pc)

# Here we make a line that plots the vertices of our main plot to put on the inset map
x_co = [w_lim, e_lim, e_lim, w_lim, w_lim]
y_co = [s_lim, s_lim, n_lim, n_lim, s_lim]

# add the coastline to the small map
# 10 m resolution coastline
feature = cartopy.feature.NaturalEarthFeature(
    name="coastline", category="physical", scale="10m", edgecolor="0.5", facecolor="0.8")
sub_ax.add_feature(feature)
sub_ax.plot(x_co, y_co, transform=pc, zorder=10, color='red');

# Finally we add a couple of text labels for the cities
# ax.text(-17.56, 14.81, 'Dakar', fontsize=14, transform=pc)
# ax.text(-17.23, 14.71, 'Rufisque', fontsize=14, transform=pc)
ax.text(-16.97, 14.42, "M'bour", fontsize=14, transform=pc)
ax.text(-16.82, 14.18, 'Joal Fadiouth', fontsize=14, transform=pc)


# # we plot here the positions of the moorings

# Coordonnées mouillage m3
m3_lat = df_marker['latitude'][df_marker['marker_name'] == 'M3 lest'][0]
m3_lon = df_marker['longitude'][df_marker['marker_name'] == 'M3 lest'][0]
m3_name = df_marker['marker_name'][df_marker['marker_name'] == 'M3 lest'][0]

# display text close to M3 mooring
ax.text(m3_lon-0.05, m3_lat-0.05, 'M3', fontsize=16, transform=pc)

# Coordonnées mouillage M4
m4_lat = df_marker['latitude'][df_marker['marker_name'] == 'M4 lest'][3]
m4_lon = df_marker['longitude'][df_marker['marker_name'] == 'M4 lest'][3]
m4_name = df_marker['marker_name'][df_marker['marker_name'] == 'M4 lest'][3]

# display text close to M4 mooring
ax.text(m4_lon-0.05, m4_lat-0.05, 'M4', fontsize=16, color='blue', transform=pc)

# display a marker for the two moorings with different colors
ax.scatter(m3_lon,m3_lat, zorder=10, color="k",
         marker="D", s=50, label='Mouillage M3', transform = pc);

ax.scatter(m4_lon,m4_lat, zorder=10, color="blue",
         marker="D", s=50, label='Mouillage M4', transform = pc);

# Add the legend, try changing its position
fig.legend( bbox_to_anchor=(0.32,0.8),loc='lower left')