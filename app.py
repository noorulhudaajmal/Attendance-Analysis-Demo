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
    [data-testid=stSidebar] {
        padding-top: 10px;
    }
    [data-testid=block-container] {
        padding-top: 0px;
    }
   [data-testid=stSidebarUserContent]{
      margin-top: -75px;
      margin-top: -75px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------- Data Loading -----------------------------

data_file = st.sidebar.file_uploader(label="Upload data file", accept_multiple_files=False, type=["xlsx", "xls"])

quarter_sheets = []

if data_file is not None:
    # data_sheet = pd.read_excel(data_file, sheet_name='Data')
    quarter_sheets = [pd.read_excel(data_file, sheet_name=f'Q{i}',
                                    usecols=['Employee Name', 'Team', 'Working period', 'Attended', 'Absent',
                                             'Total Meetings'],
                                    skiprows=2) for i in range(1, 5)]


# ----------------------------------- App View ----------------------------------


def preprocess(data):
    data['Attended'] = pd.to_numeric(data['Attended'], errors='coerce')
    data['Absent'] = pd.to_numeric(data['Absent'], errors='coerce')
    data['Total Meetings'] = pd.to_numeric(data['Total Meetings'], errors='coerce')
    data['Working period'] = pd.to_numeric(data['Working period'], errors='coerce')

    return data


def calculate_team_attendance_percentage(quarter_data, department):
    filtered_data = []
    for i in range(len(quarter_data)):
        filtered_quarter_data = quarter_data[i][quarter_data[i]['Team'] == department]
        total_meetings, attended, attendance_percentage = calculate_team_attendance(filtered_quarter_data)
        filtered_data.append({
            'Quarter': f'Q{i + 1}',
            'Total Meetings': total_meetings,
            'Attended': attended,
            'Attendance Percentage': attendance_percentage
        })
    return pd.DataFrame(filtered_data)


def calculate_team_attendance(filtered_quarter_data):
    total_meetings = filtered_quarter_data['Total Meetings'].sum()
    attended = filtered_quarter_data['Attended'].sum()
    attendance_percentage = (attended / total_meetings) * 100 if total_meetings > 0 else 0
    return total_meetings, attended, attendance_percentage


def create_workingperiod_plot(quarter_data):
    # Plot for Working Period
    fig_working_period = px.bar(
        quarter_data,
        x='Employee Name',
        y='Working period',
        title='Working Period by Employee'
    )
    return fig_working_period


def create_attendance_chart(filtered_attendance_df):
    # Create a figure with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add the bar charts for Attended and Total Meetings
    fig.add_trace(
        go.Bar(x=filtered_attendance_df['Quarter'], y=filtered_attendance_df['Attended'], name='Attended'),
        secondary_y=False,
    )

    fig.add_trace(
        go.Bar(x=filtered_attendance_df['Quarter'], y=filtered_attendance_df['Total Meetings'], name='Total Meetings'),
        secondary_y=False,
    )

    # Add the scatter line for Attendance Percentage
    fig.add_trace(
        go.Scatter(x=filtered_attendance_df['Quarter'], y=filtered_attendance_df['Attendance Percentage'],
                   name='Attendance Percentage', mode='lines+markers'),
        secondary_y=True,
    )

    # Set the axis titles
    fig.update_layout(
        title="Team Attendance Analysis",
        xaxis_title="Quarter",
        yaxis_title="Meetings",
        yaxis2_title="Attendance Percentage (%)",
    )

    return fig


def main():
    # Streamlit app setup
    st.title('Team Attendance Dashboard')

    if quarter_sheets:
        quarter_data = [preprocess(i) for i in quarter_sheets]
        q_1 = quarter_data[0]
        q_2 = quarter_data[1]
        q_3 = quarter_data[2]
        q_4 = quarter_data[3]
        all_departments = set((list(q_1['Team'].unique()) + list(q_2['Team'].unique()) +
                               list(q_3['Team'].unique()) + list(q_4['Team'].unique())))

        # Select box for Department
        department = st.sidebar.selectbox('Choose Departments', options=all_departments)

        filtered_attendance_df = calculate_team_attendance_percentage(quarter_data, department)
        st.dataframe(filtered_attendance_df, hide_index=True)

        fig = create_attendance_chart(filtered_attendance_df)
        fig.update_layout(title=f'Attendance Analysis for {department}')
        st.plotly_chart(fig, use_container_width=True)

        row_2 = st.columns((1, 5))
        quarter_index = 0
        with row_2[0]:
            st.write("#")
            st.write("#")
            quarter = st.selectbox("Select Quarter", options=['Q1', 'Q2', 'Q3', 'Q4'])
            quarter_index = int(quarter[1]) - 1

        selected_quarter_data = quarter_data[quarter_index]
        selected_quarter_data = selected_quarter_data[selected_quarter_data['Team'] == department]
        fig = create_workingperiod_plot(selected_quarter_data)
        row_2[1].plotly_chart(fig, use_container_width=True)

    else:
        st.info("Upload data file to see analytics.")



if __name__ == '__main__':
    main()
