import streamlit as st
import pandas as pd
from pathlib import Path
import time

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = Path(r"C:\LAB_CODE\3rdsem\oilgas\output")

COLUMNS = [
    "Equipment",
    "Temperature",
    "Pressure",
    "Flow",
    "Vibration",
    "Timestamp"
]

# Normal operating limits
LIMITS = {
    "Temperature": (70, 95, "°C"),
    "Pressure": (130, 160, "bar"),
    "Flow": (280, 350, "m³/h"),
    "Vibration": (2, 7, "mm/s")
}

# ============================================================
# READ FLUME OUTPUT
# ============================================================

def read_flume_output():

    records = []

    if not OUTPUT_DIR.exists():
        return pd.DataFrame(columns=COLUMNS)

    files = sorted(
        [f for f in OUTPUT_DIR.iterdir() if f.is_file()],
        key=lambda f: f.stat().st_mtime
    )

    for file in files:

        try:

            with open(
                file,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                for line in f:

                    line = line.strip()

                    if not line:
                        continue

                    parts = line.split(",")

                    if len(parts) != 6:
                        continue

                    records.append(parts)

        except Exception:
            continue

    if not records:
        return pd.DataFrame(columns=COLUMNS)

    df = pd.DataFrame(records, columns=COLUMNS)

    # Convert numeric values
    for column in [
        "Temperature",
        "Pressure",
        "Flow",
        "Vibration"
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Convert timestamp
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        errors="coerce"
    )

    return df.dropna(subset=["Equipment"])


# ============================================================
# CHECK LIMITS
# ============================================================

def check_parameter(parameter, value):

    minimum, maximum, unit = LIMITS[parameter]

    if value < minimum:
        return True, f"Below normal limit ({minimum} {unit})"

    if value > maximum:
        return True, f"Above normal limit ({maximum} {unit})"

    return False, ""


def check_equipment(row):

    alerts = []

    for parameter in LIMITS:

        value = row[parameter]

        if pd.isna(value):
            continue

        abnormal, message = check_parameter(
            parameter,
            value
        )

        if abnormal:
            alerts.append(
                f"{parameter}: {value:.1f} "
                f"({message})"
            )

    return alerts


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Oil & Gas Equipment Monitoring",
    page_icon="🏭",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🏭 Oil & Gas Equipment Monitoring")

st.caption(
    "Real-time equipment monitoring using Apache Flume"
)

st.divider()


# ============================================================
# READ DATA
# ============================================================

df = read_flume_output()


if df.empty:

    st.warning(
        "Waiting for streaming data from Apache Flume..."
    )

else:

    # Get latest reading for each equipment
    latest = (
        df.sort_values("Timestamp")
        .groupby("Equipment")
        .tail(1)
        .reset_index(drop=True)
    )

    # ========================================================
    # OVERALL ALERT SUMMARY
    # ========================================================

    total_equipment = len(latest)

    alert_count = 0

    for _, row in latest.iterrows():

        alerts = check_equipment(row)

        if alerts:
            alert_count += 1

    normal_count = total_equipment - alert_count

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Equipment",
            total_equipment
        )

    with col2:
        st.metric(
            "Normal",
            normal_count
        )

    with col3:

        if alert_count > 0:

            st.error(
                f"🔴 {alert_count} Equipment Alert"
                if alert_count == 1
                else
                f"🔴 {alert_count} Equipment Alerts"
            )

        else:

            st.success(
                "🟢 No Active Alerts"
            )


    st.divider()


    # ========================================================
    # EQUIPMENT STATUS
    # ========================================================

    st.subheader("Equipment Status")

    columns = st.columns(len(latest))

    for column, (_, row) in zip(
        columns,
        latest.iterrows()
    ):

        equipment = row["Equipment"]

        alerts = check_equipment(row)

        is_abnormal = len(alerts) > 0


        with column:

            # ------------------------------------------------
            # CARD
            # ------------------------------------------------

            if is_abnormal:

                st.error(
                    f"🔴 ALERT\n\n"
                    f"**{equipment}**"
                )

            else:

                st.success(
                    f"🟢 NORMAL\n\n"
                    f"**{equipment}**"
                )


            # ------------------------------------------------
            # TEMPERATURE
            # ------------------------------------------------

            temperature = row["Temperature"]

            temp_alert, _ = check_parameter(
                "Temperature",
                temperature
            )

            if temp_alert:

                st.markdown(
                    f"🔴 **Temperature: "
                    f"{temperature:.1f} °C**"
                )

            else:

                st.write(
                    f"Temperature: "
                    f"{temperature:.1f} °C"
                )


            # ------------------------------------------------
            # PRESSURE
            # ------------------------------------------------

            pressure = row["Pressure"]

            pressure_alert, _ = check_parameter(
                "Pressure",
                pressure
            )

            if pressure_alert:

                st.markdown(
                    f"🔴 **Pressure: "
                    f"{pressure:.1f} bar**"
                )

            else:

                st.write(
                    f"Pressure: "
                    f"{pressure:.1f} bar"
                )


            # ------------------------------------------------
            # FLOW
            # ------------------------------------------------

            flow = row["Flow"]

            flow_alert, _ = check_parameter(
                "Flow",
                flow
            )

            if flow_alert:

                st.markdown(
                    f"🔴 **Flow: "
                    f"{flow:.1f} m³/h**"
                )

            else:

                st.write(
                    f"Flow: "
                    f"{flow:.1f} m³/h"
                )


            # ------------------------------------------------
            # VIBRATION
            # ------------------------------------------------

            vibration = row["Vibration"]

            vibration_alert, _ = check_parameter(
                "Vibration",
                vibration
            )

            if vibration_alert:

                st.markdown(
                    f"🔴 **Vibration: "
                    f"{vibration:.1f} mm/s**"
                )

            else:

                st.write(
                    f"Vibration: "
                    f"{vibration:.1f} mm/s"
                )


            # ------------------------------------------------
            # ALERT MESSAGE
            # ------------------------------------------------

            if alerts:

                st.warning(
                    "⚠ " + " | ".join(alerts)
                )


    # ========================================================
    # LATEST READINGS
    # ========================================================

    st.divider()

    st.subheader("Latest Streaming Readings")

    display_df = latest.copy()

    st.dataframe(
        display_df,
        hide_index=True,
        width="stretch"
    )


    # ========================================================
    # RECENT EVENTS
    # ========================================================

    st.subheader("Recent Streaming Events")

    recent = (
        df.sort_values(
            "Timestamp",
            ascending=False
        )
        .head(20)
    )

    st.dataframe(
        recent,
        hide_index=True,
        width="stretch"
    )


    # ========================================================
    # NORMAL OPERATING LIMITS
    # ========================================================

    st.subheader("Normal Operating Limits")

    limits_df = pd.DataFrame(
        [
            [
                "Temperature",
                "70 – 95 °C"
            ],
            [
                "Pressure",
                "130 – 160 bar"
            ],
            [
                "Flow",
                "280 – 350 m³/h"
            ],
            [
                "Vibration",
                "2 – 7 mm/s"
            ]
        ],
        columns=[
            "Parameter",
            "Normal Range"
        ]
    )

    st.dataframe(
        limits_df,
        hide_index=True,
        width="stretch"
    )


# ============================================================
# AUTO REFRESH
# ============================================================

time.sleep(2)

st.rerun()