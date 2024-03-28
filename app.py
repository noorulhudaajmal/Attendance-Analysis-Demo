import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# ----------------------------------- Data Loading -----------------------------
def main():
    data_file = './data/data.xlsx' #st.sidebar.file_uploader(label="Upload data file", accept_multiple_files=False, type=["xlsx", "xls"])

    quarter_sheets = []

    if data_file is not None:
        st.title('Team Attendance Dashboard')
        # data_sheet = pd.read_excel(data_file, sheet_name='Data')
        quarter_sheets = [pd.read_excel(data_file, sheet_name=f'Q{i}',
                                        usecols=['Employee Name', 'Team', 'Working period', 'Attended', 'Absent',
                                                'Total Meetings'],
                                        skiprows=2,
                                        # header=[0,1], index_col=[0]
                                        ) for i in range(1, 5)]
        quarters_data = [preprocess(i) for i in quarter_sheets]
        
        quarter = st.sidebar.selectbox(label='Select Quarter', options=['Q1', 'Q2', 'Q3', 'Q4'])
        selected_quarter_data = quarters_data[int(quarter[1])-1]
        
        all_departments = extract_teams(selected_quarter_data)
        department = st.sidebar.selectbox('Choose Departments', options=all_departments)
        
        filtered_data = selected_quarter_data[selected_quarter_data['Team'] == department]

        total_meetings, attended, attendance_percentage, working_period = calculate_team_attendance(filtered_data)
        kpis = st.columns(4)
        kpis[0].metric(label="Total Meetings", value=int(total_meetings))
        kpis[1].metric(label="Total Attended Meetings", value=int(attended))
        kpis[2].metric(label="Attendance Percentage", value=f'{attendance_percentage:.1f}%')
        kpis[3].metric(label="Avg. Working Period", value=f'{working_period:.2f}')

        attendance_summary_table = summary_table(filtered_data)
        st.plotly_chart(attendance_summary_table, use_container_width=True)

        fig = create_working_period_plot(filtered_data)
        st.plotly_chart(fig, use_container_width=True)
        
        
    else:
        st.info("Upload data file to see analytics.")


# ----------------------------------- App View ----------------------------------

def extract_teams(quarter_data):
    all_departments = set((list(quarter_data['Team'].unique())))
        
    return all_departments


def preprocess(data):
    data['Attended'] = pd.to_numeric(data['Attended'], errors='coerce')
    data['Absent'] = pd.to_numeric(data['Absent'], errors='coerce')
    data['Total Meetings'] = pd.to_numeric(data['Total Meetings'], errors='coerce')
    data['Working period'] = pd.to_numeric(data['Working period'], errors='coerce')

    data = data.dropna(subset='Team')
    data = data[~((data['Employee Name'] == 1) & (data['Team'] == 1))]

    return data


def calculate_team_attendance(filtered_data):
    total_meetings = filtered_data['Total Meetings'].sum()
    attended = filtered_data['Attended'].sum()
    attendance_percentage = (attended / total_meetings) * 100 if total_meetings > 0 else 0
    working_period = filtered_data['Working period'].mean()
    return total_meetings, attended, attendance_percentage, working_period


def summary_table(data):
    n_rows = len(data)
    fig = go.Figure(data=[go.Table(
        columnwidth=[2,2,1,1,1,1],
        header=dict(
            values=list(data.columns),
            font=dict(size=14, color='white'),
            fill_color='#264653',
            align=['left', 'center'],
            height=40
        ),
        cells=dict(
            values=[data[K].tolist() for K in data.columns],
            font=dict(size=12, color="black"),
            fill_color='#f5ebe0',
            height=40
        ))]
    )
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), height=(n_rows*40)+80)
    return fig


def create_working_period_plot(data):
    # Plot for Working Period
    fig_working_period = px.bar(
        data,
        x='Employee Name',
        y='Working period',
        title='Working Period by Employee'
    )
    return fig_working_period


if __name__ == '__main__':
    main()
