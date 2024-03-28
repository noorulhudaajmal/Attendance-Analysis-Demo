import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def extract_teams(quarter_data):
    all_teams = set()
    for data in quarter_data:
        unique_teams = data['Team'].unique()
        all_teams.update(unique_teams)  # Adds each unique team to the set
    return all_teams


def preprocess(data):
    data['Attended'] = pd.to_numeric(data['Attended'], errors='coerce')
    data['Absent'] = pd.to_numeric(data['Absent'], errors='coerce')
    data['Total Meetings'] = pd.to_numeric(data['Total Meetings'], errors='coerce')
    data['Working period'] = pd.to_numeric(data['Working period'], errors='coerce')

    data = data.dropna(subset='Team')
    data = data[~((data['Employee Name'] == 1) & (data['Team'] == 1))]

    return data


def filter_data(data, meeting_to_attendance_map, selected_meetings):
    # Filter columns based on selected meetings and map
    columns_to_keep = ['Employee Name', 'Team', 'Working period']
    for meeting in selected_meetings:
        if meeting in meeting_to_attendance_map:
            columns_to_keep.append(meeting_to_attendance_map[meeting])

    filtered_data = data[columns_to_keep]

    # Rename columns and map values
    for meeting in selected_meetings:
        if meeting in meeting_to_attendance_map:
            attendance_col = meeting_to_attendance_map[meeting]
            filtered_data = filtered_data.rename(columns={attendance_col: f"{meeting}-Attended"})
            filtered_data[f"{meeting}-Attended"] = filtered_data[f"{meeting}-Attended"].map({'Yes': 1, 'No': 0})

    # Add 'Attended' and 'Absent' columns
    attended_columns = [col for col in filtered_data.columns if col.endswith('-Attended')]
    filtered_data['Attended'] = filtered_data[attended_columns].sum(axis=1)
    filtered_data['Absent'] = filtered_data[attended_columns].apply(lambda row: len(row) - row.sum(), axis=1)

    # Group by 'Team' and aggregate
    aggregation_dict = {
        'Working period': 'mean',
    }

    # Update aggregation dictionary with sums of attended_columns
    for col in attended_columns:
        aggregation_dict[col] = 'sum'

    # Add the other aggregations
    aggregation_dict.update({
        'Attended': 'sum',
        'Absent': 'sum'
    })

    # Group by 'Team' and aggregate
    grouped_data = filtered_data.groupby('Team').agg(aggregation_dict).reset_index()

    # Add 'Total Meetings' and 'Attendance Percentage' columns
    grouped_data['Total Meetings'] = grouped_data['Absent'] + grouped_data['Attended']
    grouped_data['Attendance Percentage'] = (grouped_data['Attended'] / grouped_data['Total Meetings']) * 100

    return grouped_data


def calculate_team_attendance(filtered_data):
    total_meetings = filtered_data['Total Meetings'].sum()
    attended = filtered_data['Attended'].sum()
    attendance_percentage = (attended / total_meetings) * 100 if total_meetings > 0 else 0
    working_period = filtered_data['Working period'].mean()
    return total_meetings, attended, attendance_percentage, working_period


def summary_table(data):
    data['Attendance Percentage'] = (data['Attendance Percentage']).round(1).astype(str) + '%'
    data['Working period'] = (data['Working period']).round(2)
    n_rows = len(data)
    fig = go.Figure(data=[go.Table(
        # columnwidth=[2, 2, 1, 1, 1, 1, 1],
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
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), height=(n_rows * 40) + 80)
    return fig


def create_working_period_plot(quarters_data, departments):
    # Merge the list of dataframes into a single dataframe
    selected_data = pd.concat(quarters_data, ignore_index=True)

    # Filter the data for the selected departments
    data = selected_data[selected_data['Team'].isin(departments)]

    # Calculate Total %age and format it with a percentage sign and one decimal place
    data['Total %age'] = ((data['Attended'] / data['Total Meetings']) * 100).map(lambda x: '{:.1f}%'.format(x))

    # Plot for Working Period
    fig_working_period = px.bar(
        data,
        x='Employee Name',
        y='Working period',
        color='Team',
        title='Working Period by Employee'
    )
    return fig_working_period
