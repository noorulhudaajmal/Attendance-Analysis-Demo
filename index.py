import streamlit as st
import pandas as pd

from utils import preprocess, calculate_team_attendance, summary_table, \
    filter_data

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
    data_file = './data/data.xlsx'
    file_data = pd.ExcelFile(data_file)

    avb_quarters = file_data.sheet_names
    avb_quarters = [sheet for sheet in avb_quarters if sheet.startswith('Q')]

    master_data = pd.read_excel(data_file, sheet_name='Employee Master Sheet', skiprows=3, usecols=['List of Teams'])
    master_data = master_data.dropna()
    avb_teams = master_data['List of Teams'].unique()

    quarters = st.sidebar.multiselect(label='Select Quarter', options=avb_quarters, placeholder="All")
    if len(quarters) == 0:
        quarters = avb_quarters

    teams = st.sidebar.multiselect(label='Choose Team', options=avb_teams, placeholder="All")
    if len(teams) == 0:
        teams = avb_teams

    for quarter in quarters:
        st.write(f"## {quarter}")
        header_df = pd.read_excel(data_file, sheet_name=quarter, nrows=1, skiprows=1)
        meetings = [col for col in header_df.columns if not col.startswith('Unnamed')]
        n_meetings = len(meetings)
        cols_to_read = 3 + (3 * n_meetings) + 4
        quarter_data = pd.read_excel(data_file, sheet_name=quarter, skiprows=2,
                                     usecols=list(range(1, cols_to_read + 1)))
        quarter_data = preprocess(quarter_data)

        # Find columns that start with 'Attendance'
        attendance_record = [col for col in quarter_data.columns if col.startswith('Attendance')]

        # Map meeting names to their respective Attendance columns
        meeting_to_attendance_map = dict(zip(meetings, attendance_record))

        kpis = st.columns((2, 1, 1, 1, 1))
        selected_meetings = kpis[0].multiselect(label='Select Meeting', options=meetings, placeholder="All")
        if len(selected_meetings) == 0:
            selected_meetings = meetings

        filtered_data = filter_data(quarter_data, meeting_to_attendance_map, selected_meetings)

        total_meetings, attended, attendance_percentage, working_period = calculate_team_attendance(filtered_data)
        kpis[1].metric(label="Total Meetings", value=int(total_meetings))
        kpis[2].metric(label="Total Attended Meetings", value=int(attended))
        kpis[3].metric(label="Attendance Percentage", value=f'{attendance_percentage:.1f}%')
        kpis[4].metric(label="Avg. Working Period", value=f'{working_period:.2f}')

        attendance_summary_table = summary_table(filtered_data)
        st.plotly_chart(attendance_summary_table, use_container_width=True)

        st.write("---")


# ----------------------------------- Helpers ----------------------------------

if __name__ == '__main__':
    main()
