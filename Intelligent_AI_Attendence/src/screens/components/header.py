

import streamlit as st


def header_home():

    logo_url = "https://cdn-icons-png.magnific.com/256/18492/18492086.png"

    st.html(f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-bottom: 30px;
            margin-top: 30px;
        ">

            <img src="{logo_url}" style="height: 100px;">

            <h1 style="
                text-align: center;
                color: #E0E3FF;
                margin: 10px 0 0 0;
            ">
                Apani <br> Hazari
            </h1>

        </div>
    """)


def header_dashboard():

    logo_url = "https://cdn-icons-png.magnific.com/256/18492/18492086.png"

    st.html(f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            
        ">

            <img src="{logo_url}" style="height: 85px;">

            <h2 style="
                text-align: Right;
                color: #5865F2;
                margin: 0;
            ">
                Apani <br> Hazari
            </h2>

        </div>
    """)