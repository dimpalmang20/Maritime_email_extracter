import streamlit as st
import requests
import os
import json


LOCAL_API_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_RENDER_API_BASE_URL = "https://maritime-email-extracter-3.onrender.com"


def _get_secret(name):
    try:
        return st.secrets.get(name)
    except Exception:
        return None


def _truthy(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "local", "development", "dev"}


def _get_api_base_url():
    configured = (
        os.environ.get("MARITIME_API_BASE_URL")
        or _get_secret("MARITIME_API_BASE_URL")
        or os.environ.get("API_BASE_URL")
        or _get_secret("API_BASE_URL")
    )
    if configured:
        return str(configured).rstrip("/")

    if _truthy(os.environ.get("MARITIME_USE_LOCAL_API")) or _truthy(os.environ.get("MARITIME_ENV")):
        return LOCAL_API_BASE_URL

    return DEFAULT_RENDER_API_BASE_URL


API_BASE_URL = _get_api_base_url()


def _api_request(method, path, **kwargs):
    url = f"{API_BASE_URL}{path}"
    try:
        response = requests.request(method, url, timeout=30, **kwargs)
        response.raise_for_status()
        return response, None
    except requests.exceptions.RequestException:
        return None, "Backend unavailable. Please check API server."


def _response_json(response):
    try:
        return response.json(), None
    except ValueError:
        return None, "Backend returned an invalid response."


def _load_analytics_libs():
    try:
        import pandas as pd
        import plotly.express as px
        return pd, px, None
    except Exception as exc:
        return None, None, exc


def _confidence_label(score):
    try:
        score = float(score or 0)
    except (TypeError, ValueError):
        score = 0
    if 0 < score <= 1:
        score *= 100
    if score >= 80:
        return "HIGH", "green"
    if score >= 50:
        return "MEDIUM", "orange"
    return "LOW", "red"


def _render_extraction_result(result):
    rows = result if isinstance(result, list) else [result]
    st.download_button(
        "Export JSON",
        data=json.dumps(result, indent=2, ensure_ascii=False),
        file_name="maritime_extraction.json",
        mime="application/json",
    )
    for idx, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            st.json(row)
            continue
        label, color = _confidence_label(row.get("confidence_score"))
        title = row.get("vessel_name") or row.get("cargo") or row.get("template_type") or f"Record {idx}"
        with st.expander(f"{idx}. {title}", expanded=True):
            st.markdown(f":{color}[**{label} CONFIDENCE**]  `{row.get('confidence_score', 0)}`")
            cols = st.columns(4)
            cols[0].metric("Template", row.get("template_type") or "-")
            email_type_value = row.get("email_type")

            if isinstance(email_type_value, dict):
                email_type_value = email_type_value.get("email_type", "-")

            cols[1].metric("Email Type", str(email_type_value or "-"))
            cols[2].metric("Cargo", str(row.get("cargo") or "-"))
            cols[3].metric("DWT", str(row.get("dwt") or "-"))
            issues = row.get("validation_issues") or []
            if issues:
                st.warning("Validation issues: " + ", ".join(map(str, issues)))
            legs = row.get("cargo_legs") or []
            if legs:
                st.subheader("Cargo Legs")
                for leg_no, leg in enumerate(legs, start=1):
                    with st.expander(f"Leg {leg_no}: {leg.get('cargo_name') or 'Cargo'}", expanded=False):
                        st.json(leg)
            vessels = row.get("vessel_data") or []
            if vessels:
                st.subheader("Vessel Data")
                for vessel_no, vessel in enumerate(vessels, start=1):
                    with st.expander(f"Vessel {vessel_no}: {vessel.get('vessel_name') or 'Vessel'}", expanded=False):
                        st.json(vessel)
            st.subheader("Structured Record")
            st.json(row.get("structured_record") or row)


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

    response, error = _api_request("POST", "/extract", json=payload)

    if error:
        st.error(error)
    else:
        result, json_error = _response_json(response)
        if json_error:
            st.error(json_error)
        elif isinstance(result, list) and not result:
            st.error("Backend returned no extraction records.")
        else:
            st.subheader("Extraction Result")
            _render_extraction_result(result)

    # VIEW DATABASE RECORDS

if st.button("View All Records"):

    response, error = _api_request("GET", "/records")

    if error:
        st.error(error)
    else:
        data, json_error = _response_json(response)
        if json_error:
            st.error(json_error)
        else:
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

    response, error = _api_request("GET", f"/search/{search_field}/{search_value}")

    if error:
        st.error(error)
    else:
        result, json_error = _response_json(response)
        if json_error:
            st.error(json_error)
        else:
            st.write(result)

st.subheader("Maritime Analytics Dashboard")

if st.button("Load Analytics"):

    response, error = _api_request("GET", "/records")

    if error:
        st.error(error)
        st.stop()

    data, json_error = _response_json(response)
    if json_error:
        st.error(json_error)
        st.stop()

    records = data.get("records", [])

    if len(records) > 0:
        pd, px, analytics_error = _load_analytics_libs()
        if analytics_error:
            st.warning("Analytics libraries are unavailable in this environment.")
            st.write(str(analytics_error))
            st.write(records)
            st.stop()

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
