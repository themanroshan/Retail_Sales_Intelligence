"""RetailPulse — Dashboard Components"""

import streamlit as st
import pandas as pd


def download_csv(df: pd.DataFrame, filename: str = "retailpulse_data.csv") -> None:
    st.markdown("---")
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
    )
