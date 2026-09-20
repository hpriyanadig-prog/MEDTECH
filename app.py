import streamlit as st
import pandas as pd

from hospital1 import (
    hospital,
    Patient,
    PatientCondition,
    PatientLocation,
    NormalBed,
    ICUBed,
    SpecialWardBed,
    BloodGroup
)

st.set_page_config(page_title="MEDTECH", page_icon="🏥", layout="wide")

st.title("🏥 MEDTECH")
st.subheader("Hospital Resource Management Dashboard")

st.caption("Hospital resource and patient management")

# Hospital details
st.header("Hospital Overview")
st.write("Hospital: ",hospital.name)

total_beds = len(hospital.beds)
available_beds = sum(
    bed.status.value == "available"
    for bed in hospital.beds
)

total_doctors = len(hospital.doctors)
available_doctors = sum(
    doctor.status.value == "available"
    for doctor in hospital.doctors
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Beds", total_beds)
col2.metric("Available Beds", available_beds)
col3.metric("Total Doctors", total_doctors)
col4.metric("Available Doctors", available_doctors)

st.divider()

# -----------------------------
# Register patient
# -----------------------------

st.header("👤 Register a patient")

with st.form("patient_form"):
    patient_id = st.text_input("Patients ID")
    patient_name = st.text_input("Patient name")
    age = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        step=1,
    )

    condition_label = st.selectbox(
        "Patient condition",
        ["Stable", "Serious","Critical"],
    )

    location_label = st.selectbox(
        "Patient location",
        ["Emergency", "ICU", "Ward", "Operating Theatre"],
    )

    blood_group = st.selectbox(
        "Blood group",
        ["Not specified", "A+", "A-", "B+", "B-",
         "AB+", "AB-", "O+", "O-"],
    )

    waiting_time = st.number_input(
        "Waiting time (minutes)",
        min_value=0,
        step=1
    )
    required_oxygen = st.checkbox("Requires oxygen")
    surgery_required = st.checkbox("Surgery required")

    register_clicked = st.form_submit_button("Register Patient")

if register_clicked:
    if not patient_id.strip() or not patient_name.strip():
        st.warning("Please enter both patient ID and name.")

    elif any(
        p.patient_id == patient_id.strip()
        for p in hospital.patients
    ):
        st.warning("That patient ID already exists.")

    else:
        condition = PatientCondition[condition_label.upper()]
        location = PatientLocation[
            location_label.upper().replace(" ", "_")
        ]

        selected_blood_group = None
        if blood_group != "Not specified":
            selected_blood_group = BloodGroup(blood_group)
        new_patient = Patient(
            patient_id=patient_id.strip(),
            name=patient_name.strip(),
            age=int(age),
            condition=condition,
            location=location,
            blood_group=selected_blood_group,
            required_oxygen=required_oxygen,
            surgery_required=surgery_required,
        )

        hospital.register_patient(new_patient)
        st.success(f"Registered {patient_name}!")

# -----------------------------
# Assign resources
# -----------------------------

st.divider()
st.header("Assign Resources")

patient_ids = [p.patient_id for p in hospital.patients]

if patient_ids:
    selected_patient_id = st.selectbox(
        "Choose patient",
        patient_ids,
    )
    bed_choice = st.selectbox(
        "Bed type",
        ["Normal Bed", "ICU Bed", "Special Ward Bed"],
    )

    if st.button("Assign Doctor"):
        success = hospital.assign_doctor(selected_patient_id)

        if success:
            st.success("Doctor assigned.")
        else:
            st.warning("No suitable available doctor found.")

    if st.button("Assign Bed"):
        bed_types = {
            "Normal Bed": NormalBed,
            "ICU Bed": ICUBed,
            "Special Ward Bed": SpecialWardBed,
        }

        success = hospital.assign_bed(
            selected_patient_id,
            bed_types[bed_choice],
        )

        if success:
            st.success("Bed assigned.")
        else:
            st.warning("No suitable available bed found.")
    if st.button("Assign Ventilator"):
        success = hospital.assign_ventilator(
            selected_patient_id
        )

        if success:
            st.success("Ventilator assigned.")
        else:
            st.warning("No available ventilator found.")

else:
    st.info("Register a patient first to assign resources.")

# -----------------------------
# Patient table
# -----------------------------

st.divider()
st.header("Patient Records")

if hospital.patients:
    patient_rows = []

    for p in hospital.patients:
        patient_rows.append({
            "Patient ID": p.patient_id,
            "Name": p.name,
            "Age": p.age,
            "Condition": p.condition.value,
            "Location": p.location.value,
            "Doctor": p.assigned_doctor or "Not assigned",
            "Bed": p.assigned_bed or "Not assigned",
            "Ventilator": p.assigned_ventilator or "Not assigned",
        })

    st.dataframe(
        pd.DataFrame(patient_rows),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No patients registered yet.")

# -----------------------------
# Resource status
# -----------------------------

st.divider()
st.header("Resource Status")

with st.expander("View beds"):
    if hospital.beds:
        st.dataframe(
            [
                {
                    "Bed ID": bed.resource_id,
                    "Name": bed.name,
                    "Ward": bed.ward_name or "—",
                    "Status": bed.status.value,
                }
                for bed in hospital.beds
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No beds available in the system.")

with st.expander("View doctors"):
    if hospital.doctors:
        st.dataframe(
            [
                {
                    "Doctor ID": doctor.resource_id,
                    "Name": doctor.name,
                    "Specialization": doctor.specialization or "—",
                    "Shift": doctor.shift or "—",
                    "Status": doctor.status.value,
                }
                for doctor in hospital.doctors
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No doctors listed in the system.")


st.divider()

st.caption("Developed by Haripriya, Krithika & Harika — BMSCE Sem 1")


  
