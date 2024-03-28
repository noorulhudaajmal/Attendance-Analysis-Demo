import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils import preprocess, extract_teams, calculate_team_attendance, summary_table, create_working_period_plot

# ------------------------------ Page Configuration------------------------------
st.set_page_config(page_title="Attendance Analytics", page_icon="📊", layout="wide")

# ----------------------------------- Page Styling ------------------------------

with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.markdown("""
<style>
    [data-testid=block-container] {
        padding: 0px;
        margin-top:0px;
    }
</style>
""", unsafe_allow_html=True)


# ----------------------------------- App View -----------------------------
def main():
    data_file = './data/data.xlsx'  # st.sidebar.file_uploader(label="Upload data file", accept_multiple_files=False, type=["xlsx", "xls"])

    quarter_sheets = []

    if data_file is not None:
        st.title('Team Attendance Dashboard')
        # data_sheet = pd.read_excel(data_file, sheet_name='Data')
        quarter_sheets = [pd.read_excel(data_file, sheet_name=f'Q{i}', skiprows=2, usecols=['Employee Name', 'Team', 'Working period', 'Attended', 'Absent', 'Total Meetings']) for i in range(1, 5)]
        quarters_data = [preprocess(i) for i in quarter_sheets]

        quarter = st.sidebar.multiselect(label='Select Quarter', options=['Q1', 'Q2', 'Q3', 'Q4'], placeholder="All")
        if len(quarter) == 0:
            quarter = ['Q1', 'Q2', 'Q3', 'Q4']

        selected_quarter_index = sorted([int(i[1]) - 1 for i in quarter])

        # selected_quarter_data = quarters_data[0]
        selected_data = [quarters_data[i] for i in selected_quarter_index]

        all_departments = extract_teams(selected_data)
        departments = st.sidebar.multiselect(label='Choose Departments', options=all_departments, placeholder="All")
        if len(departments) == 0:
            departments = all_departments

        for i in range(len(selected_data)):
            st.write(f"## QTR-{selected_quarter_index[i]+1}")
            selected_quarter_data = selected_data[i]
            filtered_data = selected_quarter_data[selected_quarter_data['Team'].isin(departments)]

            total_meetings, attended, attendance_percentage, working_period = calculate_team_attendance(filtered_data)
            kpis = st.columns(4)
            kpis[0].metric(label="Total Meetings", value=int(total_meetings))
            kpis[1].metric(label="Total Attended Meetings", value=int(attended))
            kpis[2].metric(label="Attendance Percentage", value=f'{attendance_percentage:.1f}%')
            kpis[3].metric(label="Avg. Working Period", value=f'{working_period:.2f}')

            attendance_summary_table = summary_table(filtered_data)
            st.plotly_chart(attendance_summary_table, use_container_width=True)

        fig = create_working_period_plot(selected_data, departments)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Upload data file to see analytics.")


# ----------------------------------- Helpers ----------------------------------

if __name__ == '__main__':
    main()
