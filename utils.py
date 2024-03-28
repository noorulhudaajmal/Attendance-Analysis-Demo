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


def filter_data(data, meeting_to_attendance_map, selected_meetings, teams):
    data = data[data['Team'].isin(teams)]
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

    return filtered_data, grouped_data


def calculate_team_attendance(filtered_data):
    total_meetings = filtered_data['Total Meetings'].sum()
    attended = filtered_data['Attended'].sum()
    attendance_percentage = (attended / total_meetings) * 100 if total_meetings > 0 else 0
    working_period = filtered_data['Working period'].mean()
    return total_meetings, attended, attendance_percentage, working_period


def summary_table(data):
    data['Attendance Percentage'] = (data['Attendance Percentage']).round(1).astype(str) + '%'
    data['Working period'] = (data['Working period']).round(2)
    col_to_display = ['Team', 'Working period', 'Total Meetings', 'Attended', 'Attendance Percentage']
    data = data[col_to_display]
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
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), height=(n_rows * 40) + 100)
    return fig


def attendance_plot(data, meetings):
    # Create a subplot with 1 row and 1 column, with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add bar traces for Total Meetings and each meeting's attendance
    fig.add_trace(
        go.Bar(
            x=data['Team'],
            y=data['Total Meetings'],
            name='Total Meetings'
        ),
        secondary_y=False
    )
    for meeting in meetings:
        fig.add_trace(
            go.Bar(
                x=data['Team'],
                y=data[f'{meeting}-Attended'],
                name=f'{meeting}'
            ),
            secondary_y=False
        )

    # Add scatter trace for Attendance Percentage on the secondary y-axis
    fig.add_trace(
        go.Scatter(
            x=data['Team'],
            y=data['Attendance Percentage'],
            mode='markers+lines',
            name='Attendance Percentage'
        ),
        secondary_y=True
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Team")

    # Set y-axes titles
    fig.update_yaxes(title_text="Meetings", secondary_y=False)
    fig.update_yaxes(title_text="Attendance Percentage", secondary_y=True)

    fig.update_layout(title='Summary Analytics', height=500)

    return fig


def working_period_plot(data):
    data['Total Meetings'] = data['Absent'] + data['Attended']
    data['Attendance Percentage'] = (data['Attended'] / data['Total Meetings']) * 100

    # Create a subplot with 1 row and 1 column, with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add bar trace for Working Period
    fig.add_trace(
        go.Bar(
            x=data['Employee Name'],
            y=data['Working period'],
            name='Working Period',
            # marker_color=data['Team'],  # Use Team as color
        ),
        secondary_y=False
    )

    # Add scatter trace for Attendance Percentage on the secondary y-axis
    fig.add_trace(
        go.Scatter(
            x=data['Employee Name'],
            y=data['Attendance Percentage'],
            name='Attendance Percentage',
            mode='markers+lines',
        ),
        secondary_y=True
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Employee Name")

    # Set y-axes titles
    fig.update_yaxes(title_text="Working Period", secondary_y=False)
    fig.update_yaxes(title_text="Attendance Percentage", secondary_y=True)

    # Set plot title
    fig.update_layout(title_text="Working Period by Employee")

    return fig