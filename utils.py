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


def calculate_team_attendance(filtered_data):
    total_meetings = filtered_data['Total Meetings'].sum()
    attended = filtered_data['Attended'].sum()
    attendance_percentage = (attended / total_meetings) * 100 if total_meetings > 0 else 0
    working_period = filtered_data['Working period'].mean()
    return total_meetings, attended, attendance_percentage, working_period


def summary_table(data):
    unique_teams = data['Team'].unique()
    data = data.groupby('Team').agg({
        'Working period': 'mean',
        'Attended': 'sum',
        'Absent': 'sum',
        'Total Meetings': 'sum'
    }).reset_index()
    data['Total %age'] = ((data['Attended'] / data['Total Meetings']) * 100).round(1).astype(str) + '%'
    data['Working period'] = (data['Working period']).round(2)
    n_rows = len(data)
    fig = go.Figure(data=[go.Table(
        columnwidth=[2, 2, 1, 1, 1, 1, 1],
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
