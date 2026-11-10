import streamlit as st
from db_connection import get_connection

st.set_page_config(
    page_title="Organ Donation Registry",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
/* Sidebar background */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102b4e, #9BE5AA);
}

/* Sidebar headings */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
}

/* Sidebar labels */
section[data-testid="stSidebar"] label {
    color: #eaf4ff !important;
    font-weight: 600;
}

/* Navigation dropdown */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: white;
    border-radius: 10px;
    border: 1px solid #bfd3e6;
}

section[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #17365d !important;
}

/* Sidebar divider */
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.3);
}
</style>
""", unsafe_allow_html=True)


st.title("🏥 Organ Donation Registry Management System")

st.write("Welcome to the Organ Donation Registry Management System.")

st.sidebar.markdown("""
<div style="text-align:center; padding:15px 5px;">
    <h1 style="color:white; font-size:25px;">🏥 OrganCare</h1>
    <p style="color:#dbeafe; font-size:13px;">
        Registry Management Portal
    </p>
</div>
<hr>
""", unsafe_allow_html=True)

st.sidebar.subheader("Navigation")

menu = st.sidebar.selectbox(
    "Choose an option",
   ["Home", "Donor Registration", "Donor Records",
 "Recipient Registration", "Recipient Records",
 "Organ Availability", "Hospital Details",
 "Coordinator Details", "Medical Compatibility",
 "Transplant Records"]
)


if menu == "Home":
    st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem;
    }
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e1e8f0;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.04);
    }
    [data-testid="stMetricLabel"] {
        color: #52647a;
    }
    [data-testid="stMetricValue"] {
        color: #17365d;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background: linear-gradient(120deg, #12345a, #1877a8);
        padding: 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;">
        <p style="font-size:13px; letter-spacing:2px;">
            ORGAN DONATION MANAGEMENT
        </p>
        <h1 style="color:white; margin:0;">
            Dashboard Overview
        </h1>
        <p style="color:#e1efff; margin-top:10px;">
            Monitor donor registrations, recipients,
            available organs and hospital information.
        </p>
    </div>
    """, unsafe_allow_html=True)

    conn = get_connection()

    if conn:
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    (SELECT COUNT(*) FROM donor) AS total_donors,
                    (SELECT COUNT(*) FROM recipient) AS total_recipients,
                    (SELECT COUNT(*) FROM organ
                     WHERE Availability_Status = 'Available')
                    AS available_organs,
                    (SELECT COUNT(*) FROM hospital) AS total_hospitals,
                    (SELECT COUNT(*) FROM organ) AS total_organs,
                    (SELECT COUNT(*) FROM medical_compatibility)
                    AS total_compatibility,
                    (SELECT COUNT(*) FROM transplant)
                    AS total_transplants
            """

            cursor.execute(query)
            data = cursor.fetchone()

            st.subheader("System Statistics")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Donors", data["total_donors"])
            col2.metric("Total Recipients", data["total_recipients"])
            col3.metric("Available Organs", data["available_organs"])
            col4.metric("Hospitals", data["total_hospitals"])

            st.divider()

            st.subheader("Registry Overview")

            left, right = st.columns(2)

            with left:
                st.markdown("#### Organ Availability")

                total = data["total_organs"]
                available = data["available_organs"]

                if total > 0:
                    st.progress(available / total)
                    st.caption(
                        f"{available} of {total} organs marked available"
                    )
                else:
                    st.info("No organ records available.")

                st.write(
                    f"**Compatibility Records:** "
                    f"{data['total_compatibility']}"
                )
                st.write(
                    f"**Transplant Records:** "
                    f"{data['total_transplants']}"
                )

            with right:
                st.markdown("#### Recent Donor Registrations")

                cursor.execute("""
                    SELECT Name, Registration_Date
                    FROM donor
                    ORDER BY Registration_Date DESC
                    LIMIT 3
                """)

                recent_donors = cursor.fetchall()

                if recent_donors:
                    for donor in recent_donors:
                        st.write(
                            f"**{donor['Name']}** — "
                            f"{donor['Registration_Date']}"
                        )
                        st.divider()
                else:
                    st.info("No recent registrations.")

            st.caption(
                "Live statistics retrieved from the MySQL database."
            )

        except Exception as e:
            st.error(f"Unable to load dashboard: {e}")

        finally:
            cursor.close()
            conn.close()


elif menu == "Donor Registration":
    st.subheader("Donor Registration")

    with st.form("donor_form"):
        donor_id = st.number_input("Donor ID", min_value=1, step=1)
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        blood_group = st.selectbox(
            "Blood Group",
            ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        )
        phone = st.text_input("Phone Number")
        address = st.text_input("Address")
        registration_date = st.date_input("Registration Date")

        submitted = st.form_submit_button("Register Donor")

    if submitted:
        if not name.strip():
            st.error("Please enter the donor name.")
        else:
            conn = get_connection()

            if conn:
                cursor = conn.cursor()
                try:
                    query = """
                        INSERT INTO donor
                        (Donor_ID, Name, Age, Gender, Blood_Group,
                         Phone, Address, Registration_Date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    values = (
                        donor_id, name, age, gender, blood_group,
                        phone, address, registration_date
                    )

                    cursor.execute(query, values)
                    conn.commit()
                    st.success("Donor registered successfully!")

                except Exception as e:
                    st.error(f"Registration failed: {e}")

                finally:
                    cursor.close()
                    conn.close()
elif menu == "Donor Records":
    st.subheader("Registered Donor Records")

    search = st.text_input("Search by Donor Name or ID")

    conn = get_connection()

    if conn:
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM donor")
            donors = cursor.fetchall()

            if search.strip():
                donors = [
                    donor for donor in donors
                    if search.lower() in str(donor["Name"]).lower()
                    or search in str(donor["Donor_ID"])
                ]

            if donors:
                for donor in donors:
                    for key, value in donor.items():
                        st.write(f"**{key}:** {value}")
                    st.divider()
            else:
                st.info("No matching donor records found.")

        except Exception as e:
            st.error(f"Unable to load donor records: {e}")

        finally:
            cursor.close()
            conn.close()       
elif menu == "Recipient Records":
    st.subheader("Registered Recipient Records")

    search = st.text_input("Search by Recipient Name or ID")

    conn = get_connection()

    if conn:
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM recipient")
            recipients = cursor.fetchall()

            if search.strip():
                recipients = [
                    recipient for recipient in recipients
                    if search.lower() in str(recipient["Name"]).lower()
                    or search in str(recipient["Recipient_ID"])
                ]

            if recipients:
                for recipient in recipients:
                    for key, value in recipient.items():
                        st.write(f"**{key}:** {value}")
                    st.divider()
            else:
                st.info("No matching recipient records found.")

        except Exception as e:
            st.error(f"Unable to load recipient records: {e}")

        finally:
            cursor.close()
            conn.close()             
elif menu == "Recipient Registration":
    st.subheader("Recipient Registration")

    with st.form("recipient_form"):
        recipient_id = st.number_input("Recipient ID", min_value=1, step=1)
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        blood_group = st.selectbox(
            "Blood Group",
            ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        )
        organ_required = st.selectbox(
            "Organ Required", ["Kidney", "Liver", "Heart", "Lungs", "Other"]
        )
        priority = st.selectbox(
            "Priority", ["High", "Medium", "Low"]
        )
        registration_date = st.date_input("Registration Date")

        submitted = st.form_submit_button("Register Recipient")

    if submitted:
        if not name.strip():
            st.error("Please enter the recipient name.")
        else:
            conn = get_connection()

            if conn:
                cursor = conn.cursor()
                try:
                    query = """
                        INSERT INTO recipient
                        (Recipient_ID, Name, Age, Gender, Blood_Group,
                         Organ_Required, Priority, Registration_Date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    values = (
                        recipient_id, name, age, gender, blood_group,
                        organ_required, priority, registration_date
                    )

                    cursor.execute(query, values)
                    conn.commit()
                    st.success("Recipient registered successfully!")

                except Exception as e:
                    st.error(f"Registration failed: {e}")

                finally:
                    cursor.close()
                    conn.close()

elif menu == "Organ Availability":
    st.subheader("Organ Availability")

    conn = get_connection()

    if conn:
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM available_organ_view")
            organs = cursor.fetchall()

            if organs:
                st.success("Organ records loaded successfully!")
                for organ in organs:
                 st.text(" | ".join(f"{key}: {value}" for key, value in organ.items()))
                 st.divider()
            else:
                st.info("No organ records available.")

        except Exception as e:
            st.error(f"Unable to load organ records: {e}")

        finally:
            cursor.close()
            conn.close()

elif menu == "Hospital Details":
    st.subheader("Hospital Details")

    conn = get_connection()

    if conn:
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM hospital")
            hospitals = cursor.fetchall()

            if hospitals:
                for hospital in hospitals:
                    for key, value in hospital.items():
                        st.write(f"**{key}:** {value}")
                    st.divider()
            else:
                st.info("No hospital records available.")

        except Exception as e:
            st.error(f"Unable to load hospital details: {e}")

        finally:
            cursor.close()
            conn.close()
elif menu == "Coordinator Details":
    st.subheader("Coordinator Details")

    conn = get_connection()

    if conn:
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    c.Coordinator_ID,
                    c.Name,
                    c.Phone,
                    h.Hospital_Name
                FROM coordinator c
                LEFT JOIN hospital h
                ON c.Hospital_ID = h.Hospital_ID
            """

            cursor.execute(query)
            coordinators = cursor.fetchall()

            if coordinators:
                for coordinator in coordinators:
                    for key, value in coordinator.items():
                        st.write(f"**{key}:** {value}")
                    st.divider()
            else:
                st.info("No coordinator records available.")

        except Exception as e:
            st.error(f"Unable to load coordinator details: {e}")

        finally:
            cursor.close()
            conn.close()
elif menu == "Medical Compatibility":
    st.subheader("Medical Compatibility Records")

    conn = get_connection()

    if conn:
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    mc.Compatibility_ID,
                    d.Name AS Donor_Name,
                    r.Name AS Recipient_Name,
                    mc.Compatibility_Status,
                    mc.Remarks
                FROM medical_compatibility mc
                LEFT JOIN donor d
                    ON mc.Donor_ID = d.Donor_ID
                LEFT JOIN recipient r
                    ON mc.Recipient_ID = r.Recipient_ID
            """

            cursor.execute(query)
            records = cursor.fetchall()

            if records:
                for record in records:
                    for key, value in record.items():
                        st.write(f"**{key}:** {value}")
                    st.divider()
            else:
                st.info("No compatibility records available.")

        except Exception as e:
            st.error(f"Unable to load compatibility records: {e}")

        finally:
            cursor.close()
            conn.close()
elif menu == "Transplant Records":
    st.subheader("Transplant Records")

    conn = get_connection()

    if conn:
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    t.Transplant_ID,
                    d.Name AS Donor_Name,
                    r.Name AS Recipient_Name,
                    o.Organ_Type,
                    h.Hospital_Name,
                    t.Transplant_Date,
                    t.Status
                FROM transplant t
                LEFT JOIN donor d ON t.Donor_ID = d.Donor_ID
                LEFT JOIN recipient r ON t.Recipient_ID = r.Recipient_ID
                LEFT JOIN organ o ON t.Organ_ID = o.Organ_ID
                LEFT JOIN hospital h ON t.Hospital_ID = h.Hospital_ID
            """

            cursor.execute(query)
            records = cursor.fetchall()

            if records:
                for record in records:
                    for key, value in record.items():
                        st.write(f"**{key}:** {value}")
                    st.divider()
            else:
                st.info("No transplant records available.")

        except Exception as e:
            st.error(f"Unable to load transplant records: {e}")

        finally:
            cursor.close()
            conn.close()

