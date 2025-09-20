import streamlit as st
import pandas as pd
import io

def calculate_attendance(total_days, absent_hours):
    total_hours = total_days * 5  # Each day has 5 hours
    present_hours = total_hours - absent_hours
    present_percentage = (present_hours / total_hours) * 100
    
    if present_percentage >= 74:
        exam_status = "🟢 Eligible to write the exam"
    elif 65 <= present_percentage <= 75:
        exam_status = "🟡 Should pay fine to write the exam"
    elif 50 <= present_percentage < 65:
        exam_status = "🔴 Arrear "
    else:
        exam_status = "⚫ Redo"
    
    # Round to two decimal places
    present_percentage = round(present_percentage, 2)
    
    return present_percentage, present_hours, exam_status

# Initialize session state for calculator mode
if "calculator_mode" not in st.session_state:
    st.session_state.calculator_mode = "normal"

st.set_page_config(
    page_icon="🧮",
    page_title="Student Attendance Calculator",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .css-1d391kg {text-align: center;}
    .stButton>button {background-color: #87CEFA; color: black; padding: 10px; border-radius: 10px; font-weight: bold;}
    .stFileUploader {text-align: center;}
    .uploadedFile {color: green;}
    .stDownloadButton>button {background-color: #4682B4; color: white; padding: 10px; border-radius: 10px; font-weight: bold;}
    .stNumberInput>div>div>input {border-radius: 5px;}
    </style>
    """, unsafe_allow_html=True)

st.subheader("Student Attendance Calculator")
st.markdown("______")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Normal Calculator"):
            st.session_state.calculator_mode = "normal"
    with col2:
        if st.button("Excel Calculator"):
            st.session_state.calculator_mode = "excel"

# Display the appropriate calculator based on session state
if st.session_state.calculator_mode == "normal":
    with st.container():
        st.subheader("Enter Details Below")
        col1, col2 = st.columns(2)
        with col1:
            total_days = st.number_input("Total Working Days", min_value=1, max_value=365, value=5)
        with col2:
            absent_hours = st.number_input("Absent Hours of the Student", min_value=0, step=1)
            
    if st.button("Calculate Attendance"):
        if absent_hours > total_days*5:
            st.write("Enter valid Absent Hours!")
        else:
            present_percentage, present_hours, exam_status = calculate_attendance(total_days, absent_hours)
            
            st.write(f"**Present Percentage**: {present_percentage:.2f}%")
            st.write(f"**Present Hours**: {present_hours}")
            st.write(f"**Exam Status**: {exam_status}")

elif st.session_state.calculator_mode == "excel":
    st.subheader("Upload an Excel or CSV File")
    st.write("""Your file should contain "Student Name" and their "Absent Hours" as columns.""")

    with st.container():
        uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            # Read the file correctly
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file, engine='openpyxl')

            # Ensure required columns exist
            required_columns = {"Student Name", "Absent Hours"}
            if not required_columns.issubset(df.columns):
                st.error(f"Error: The uploaded file must contain the following columns: {required_columns}")
            else:
                with st.container():
                    total_days = st.number_input("Enter Total Days", min_value=1, step=1)

                if st.button("Process File"):
                    # Calculate attendance details
                    df["Total Hours"] = total_days * 5
                    df["Present Hours"] = df["Total Hours"] - df["Absent Hours"]
                    df["Present Percentage"] = (df["Present Hours"] / df["Total Hours"]) * 100
                    df["Exam Status"] = df["Present Percentage"].apply(
                        lambda x: "Eligible" if x >= 74 else "Fine Required" if x >= 65 else "Arrear" if x >= 50 else "Redo"
                    )

                    # Round to two decimal places
                    df["Present Percentage"] = df["Present Percentage"].round(2)

                    # Calculate class present percentage
                    class_present_percentage = df["Present Percentage"].mean()

                    # Display results in Streamlit
                    st.write("✅ **File Processed Successfully!**")
                    st.write(f"📊 **Class Present Percentage:** {class_present_percentage:.2f}%")
                    st.dataframe(df)

                    # Convert DataFrame to Excel for download
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name="Attendance")

                        # Access workbook and worksheet
                        workbook = writer.book
                        worksheet = writer.sheets["Attendance"]

                        # Add summary row at the bottom
                        row_num = len(df) + 2
                        worksheet.cell(row=row_num, column=1, value="Class Present Percentage")
                        worksheet.cell(row=row_num, column=2, value=class_present_percentage)

                        # Save and close writer
                        writer.close()
                        processed_data = output.getvalue()

                    # Download button for processed Excel file
                    st.download_button(
                        "Download Processed File",
                        data=processed_data,
                        file_name="processed_attendance.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e:
            st.error(f"⚠️ Error processing file: {e}")

# Footer
st.write(" ")
st.write(" ")
st.write(" ")
footer_html = """
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #E7EBF3;
            text-align: center;
            padding: 10px;
            font-size: 12px;
            color: #333;
        }
    </style>
    <div class="footer">
       Made By balafromtn 😉
    </div>
"""

st.markdown(footer_html, unsafe_allow_html=True)