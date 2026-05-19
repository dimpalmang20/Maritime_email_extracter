import streamlit as st
import requests
import pandas as pd
import plotly.express as px


st.title("Maritime Email Extraction System")

st.subheader("Upload Maritime Email")

email_text = st.text_area(
    "Paste Maritime Email",
    height=250
)

if st.button("Extract Maritime Data"):

    payload = {
        "email": email_text
    }

    response = requests.post(
        "http://127.0.0.1:8000/extract",
        json=payload
    )

    if response.status_code == 200:

        try:

            result = response.json()

            st.subheader("Extraction Result")

            st.json(result)

        except Exception as e:

            st.error("JSON Parsing Failed")

            st.write(str(e))

            st.write(response.text)

    else:

        st.error("Backend Error")

        st.write(response.text)

    # VIEW DATABASE RECORDS

if st.button("View All Records"):

    response = requests.get(
        "http://127.0.0.1:8000/records"
    )

    data = response.json()

    st.subheader("Stored Maritime Records")

    st.write(data)


st.subheader("Advanced Maritime Search")

search_field = st.selectbox(

    "Search By",

    [

        "cargo",
        "vessel_type",
        "load_port",
        "discharge_port",
        "laycan",
        "dwt"

    ]

)

search_value = st.text_input(

    "Enter Search Value"

)

if st.button("Search Maritime Records"):

    response = requests.get(

        f"http://127.0.0.1:8000/search/{search_field}/{search_value}"

    )

    if response.status_code == 200:

        result = response.json()

        st.write(result)

    else:

        st.error("Search Failed")

        st.write(response.text)

st.subheader("Maritime Analytics Dashboard")

if st.button("Load Analytics"):

    response = requests.get(
        "http://127.0.0.1:8000/records"
    )

    data = response.json()

    records = data["records"]

    if len(records) > 0:

        columns = [

    "id",

    "cargo",

    "cargo_type",

    "load_port",

    "discharge_port",

    "open_port",

    "quantity",

    "dwt",

    "vessel_type",

    "template_type",

    "email_type",

    "laycan",

    "imo",

    "grain_capacity",

    "confidence_score",

    "extraction_status"

]

        df = pd.DataFrame(records)

        available_columns = [

              col for col in columns

              if col in df.columns

           ]

        df = df[available_columns]

        st.write(df)
                # Cargo Distribution Chart

        cargo_chart = px.bar(

            df,
            x="cargo",
            title="Cargo Distribution"

        )

        st.plotly_chart(cargo_chart)

                # Vessel Type Chart

        vessel_chart = px.pie(

            df,
            names="vessel_type",
            title="Vessel Type Distribution"

        )

        st.plotly_chart(vessel_chart)

                # Confidence Score Chart

        confidence_chart = px.histogram(

            df,
            x="confidence_score",
            title="Confidence Score Distribution"

        )

        st.plotly_chart(confidence_chart)

                # Vessel Type Distribution

        vessel_chart = px.bar(

            df,

            x="vessel_type",

            title="Vessel Type Distribution"

        )

        st.plotly_chart(vessel_chart)

        # Open Port Distribution

        if "open_port" in df.columns:

            port_chart = px.bar(

                df,

                x="open_port",

                title="Open Port Distribution"

            )

            st.plotly_chart(port_chart)

        # DWT Distribution

        if "dwt" in df.columns:

            dwt_chart = px.histogram(

                df,

                x="dwt",

                title="DWT Distribution"

            )

            st.plotly_chart(dwt_chart)