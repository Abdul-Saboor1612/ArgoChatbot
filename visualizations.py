# visualizations.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def plot_float_profiles(float_data_dict, variable="TEMP"):
    """
    Plot profiles (TEMP, PSAL, PRES) for one or multiple floats.
    float_data_dict: {float_id: xarray dataset}
    variable: "TEMP", "PSAL", or "PRES"
    """
    fig = go.Figure()
    y_label = ""
    x_axis = ""
    
    for fid, ds in float_data_dict.items():
        if variable == "TEMP":
            x = ds['PRES'].values
            y = ds['TEMP'].values
            y_label = "Temperature (°C)"
            x_axis = "Pressure (dbar)"
        elif variable == "PSAL":
            x = ds['PRES'].values
            y = ds['PSAL'].values
            y_label = "Salinity (psu)"
            x_axis = "Pressure (dbar)"
        elif variable == "PRES":
            x = np.arange(len(ds['PRES'].values))
            y = ds['PRES'].values
            y_label = "Pressure (dbar)"
            x_axis = "Sample Index"
        else:
            continue
        
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f'Float {fid}'))
    
    fig.update_layout(
        xaxis_title=x_axis,
        yaxis_title=y_label,
        template='plotly_white'
    )
    return fig


def plot_map(float_data_dict):
    """
    Plot map of latest positions of floats.
    """
    info_list = []
    for fid, ds in float_data_dict.items():
        lat = float(ds['LATITUDE'].values[-1]) if 'LATITUDE' in ds and ds['LATITUDE'].size > 0 else np.nan
        lon = float(ds['LONGITUDE'].values[-1]) if 'LONGITUDE' in ds and ds['LONGITUDE'].size > 0 else np.nan
        info_list.append({
            'Float': fid,
            'Latitude': lat,
            'Longitude': lon
        })
    info_df = pd.DataFrame(info_list)
    fig = px.scatter_mapbox(
        info_df,
        lat='Latitude',
        lon='Longitude',
        color='Float',
        hover_data=['Float'],
        mapbox_style='open-street-map'
    )
    # Auto-fit to shown locations by computing bounds
    if not info_df.empty and info_df['Latitude'].notna().any() and info_df['Longitude'].notna().any():
        south = float(info_df['Latitude'].min())
        north = float(info_df['Latitude'].max())
        west = float(info_df['Longitude'].min())
        east = float(info_df['Longitude'].max())
        fig.update_layout(
            mapbox=dict(
                bounds=dict(west=west, east=east, south=south, north=north),
            ),
            margin=dict(l=0, r=0, t=0, b=0),
        )
    else:
        fig.update_layout(
            mapbox_zoom=2,
            margin=dict(l=0, r=0, t=0, b=0),
        )
    return fig


def compare_floats_plot(float_data_dict, float_ids):
    """
    Return dict of figures comparing multiple floats for TEMP, PSAL, PRES.
    """
    figs = {}
    for var, y_label in zip(["TEMP", "PSAL", "PRES"], ["Temperature (°C)", "Salinity (psu)", "Pressure (dbar)"]):
        fig = go.Figure()
        x_axis = ""
        for fid in float_ids:
            ds = float_data_dict[fid]
            if var == "TEMP":
                x = ds['PRES'].values
                y = ds['TEMP'].values
                x_axis = "Pressure (dbar)"
            elif var == "PSAL":
                x = ds['PRES'].values
                y = ds['PSAL'].values
                x_axis = "Pressure (dbar)"
            elif var == "PRES":
                x = np.arange(len(ds['PRES'].values))
                y = ds['PRES'].values
                x_axis = "Sample Index"
            else:
                continue
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f'Float {fid}'))
        fig.update_layout(
            xaxis_title=x_axis,
            yaxis_title=y_label,
            template='plotly_white'
        )
        figs[var] = fig
    return figs


def plot_trajectories(float_data_dict):
    """
    Plot full trajectories for one or multiple floats using Scattermapbox.
    Draws line+markers for the entire path and highlights the latest position in red.
    """
    fig = go.Figure()
    any_data = False
    floats_with_data = []

    for fid, ds in float_data_dict.items():
        if 'LATITUDE' in ds and 'LONGITUDE' in ds and ds['LATITUDE'].size > 0 and ds['LONGITUDE'].size > 0:
            lats = ds['LATITUDE'].values
            lons = ds['LONGITUDE'].values
            # Normalize longitudes to [-180, 180] to avoid dateline spanning
            lons = ((lons + 180) % 360) - 180
            # Full track
            fig.add_trace(go.Scattermapbox(
                lat=lats.tolist(),
                lon=lons.tolist(),
                mode='lines+markers',
                name=f'Track {fid}',
                marker=dict(size=6),
                line=dict(width=2)
            ))
            # Latest point
            fig.add_trace(go.Scattermapbox(
                lat=[float(lats[-1])],
                lon=[float(lons[-1])],
                mode='markers',
                name=f'Latest {fid}',
                marker=dict(size=12, color='red')
            ))
            any_data = True
            floats_with_data.append(fid)

    # Auto-fit view to the data by computing bounds
    fig.update_layout(
        mapbox_style='open-street-map',
        margin=dict(l=0, r=0, t=0, b=0),
    )

    # Collect all lat/lon points from traces to set bounds
    all_lats = []
    all_lons = []
    for tr in fig.data:
        if isinstance(tr, go.Scattermapbox):
            if hasattr(tr, 'lat') and hasattr(tr, 'lon') and tr.lat is not None and tr.lon is not None:
                all_lats.extend([float(x) for x in tr.lat])
                all_lons.extend([float(x) for x in tr.lon])

    if all_lats and all_lons:
        south = float(np.nanmin(all_lats))
        north = float(np.nanmax(all_lats))
        west = float(np.nanmin(all_lons))
        east = float(np.nanmax(all_lons))
        # If only one float is provided, center on latest point with a sensible zoom
        if len(floats_with_data) == 1:
            center_lat = float(all_lats[-1])
            center_lon = float(all_lons[-1])
            # Simple heuristic for zoom based on span
            lat_span = max(1e-6, north - south)
            lon_span = max(1e-6, east - west)
            span = max(lat_span, lon_span)
            # Rough mapping: smaller span -> larger zoom
            if span < 0.5:
                zoom = 6
            elif span < 1.0:
                zoom = 5
            elif span < 5:
                zoom = 4
            else:
                zoom = 3
            fig.update_layout(mapbox=dict(center=dict(lat=center_lat, lon=center_lon), zoom=zoom))
        else:
            fig.update_layout(
                mapbox=dict(
                    bounds=dict(west=west, east=east, south=south, north=north),
                )
            )
    else:
        fig.update_layout(mapbox_zoom=2)

    return fig
