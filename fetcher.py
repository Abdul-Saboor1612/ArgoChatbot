from argopy import DataFetcher
import xarray as xr
import streamlit as st

@st.cache_data
def fetch_float_data(float_id: int) -> xr.Dataset:
    ArgoSet = DataFetcher().float([float_id])
    ds = ArgoSet.load().to_xarray()
    return ds
