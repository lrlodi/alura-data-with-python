import pandas as pd
import plotly.express as px
import streamlit as st


# --- Page config --- #
# Set page title, icon and layout to fit whole width

st.set_page_config(
    page_title='Data Salary Dashboard',
    page_icon='📊',
    layout='wide'
)

# --- Data Load --- #

df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")


# --- Sidebar (filters) --- #
st.sidebar.header("Filters")

# --- Year Filter --- #
available_years = sorted(df['year'].unique())
selected_years = st.sidebar.multiselect("work_year", available_years, default=available_years)

# --- Seniority Filter --- #
available_seniority = sorted(df['seniority'].unique())
selected_seniority = st.sidebar.multiselect("Seniority", available_seniority, default=available_seniority)

# --- Contract Type Filter --- #
available_contract_types = sorted(df['employment_type'].unique())
selected_contract_types = st.sidebar.multiselect("Contract Type", available_contract_types, default=available_contract_types)

# --- Company Size Filter --- #
available_company_sizes = sorted(df['company_size'].unique())
selected_company_sizes = st.sidebar.multiselect("Company Size", available_company_sizes, default=available_company_sizes)

# ---Position Filter --- #
# available_positions = sorted(df['job_title'].unique())
# selected_positions = st.sidebar.multiselect("Position", available_positions, default=available_positions)


# --- Data Cleansing --- #
remote_ratios = {
    0: 'Not Remote',
    50: 'Partially Remote',
    100: 'Fully Remote'
}
df['remote_ratio'] = df['remote_ratio'].map(remote_ratios)



# --- Dataframe Filtering --- #
df_filtered = df[
    (df['work_year']).isin(selected_years) &
    (df['seniority']).isin(selected_seniority) &
    (df['employment_type']).isin(selected_contract_types) &
    (df['company_size']).isin(selected_company_sizes)
]

# --- Main Content --- #
st.title("Data Positions Salaries Dashboard")
st.markdown("Explore salary information for data positions in recent years. Use the filters on the sidebar to refine your research.")

# --- Main Metrics --- #
st.subheader("General Metrics")

if not df_filtered.empty:
    avg_salary = df_filtered['salary_in_usd'].mean()
    max_salary = df_filtered['salary_in_usd'].max()
    total_records = df_filtered.shape[0]
    most_common_position = df_filtered['job_title'].mode()[0]
else:
    avg_salary, max_salary, total_records, most_common_position = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Salary", f"US${avg_salary:,.0f} /y")
col2.metric("Max Salary", f"US${max_salary:,.0f} /y")
col3.metric("Total Records", f"{total_records:,}")
col4.metric("Most Common Position", f"{most_common_position}")

st.markdown("----------")

# --- Visual Analysis with Plotly --- #
st.subheader("Charts")

col_graf1, col_graf2, col_graf3, col_graf4 = st.columns(4)
with col_graf1:
    if not df_filtered.empty:
        top_positions = df_filtered.groupby('job_title')['salary_in_usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        positions_chart = px.bar(
            top_positions,
            x='salary_in_usd',
            y='job_title',
            orientation='h',
            title="Top best paid positions",
            labels={'salary_in_usd': 'Average anual salary in USD', 'position': ''}
        )
        positions_chart.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(positions_chart, use_container_width=True)
    else:
        st.warning("No Data Available")

with col_graf2:
    if not df_filtered.empty:
        hist_chart = px.histogram(
            df_filtered,
            x='salary_in_usd',
            nbins=30,
            title='Yearly Salaries Distribution',
            labels={'salary_in_usd': 'Salary Range (US$)', 'count': ''}
        )
        hist_chart.update_layout(title_x=0.1)
        st.plotly_chart(hist_chart, use_container_width=True)
    else:
        st.warning("No Data Available")


with col_graf3:
    if not df_filtered.empty:
        remote_count = df_filtered['remote_ratio'].value_counts().reset_index()
        remote_count.columns = ['remote_ratio', 'quantity']

        remote_chart = px.pie(
            remote_count,
            names='remote_ratio',
            values='quantity',
            title='Remote Ratio',
            hole=0.5
        )
        remote_chart.update_traces(textinfo='percent+label')
        remote_chart.update_layout(title_x=0.1)
        st.plotly_chart(remote_chart, use_container_width=True)
    else:
        st.warning("No Data Available")

with col_graf4:
    if not df_filtered.empty:
        df_ds = df_filtered[df_filtered['job_title'] == 'Data Scientist']
        country_avg = df_ds.groupby('employee_residence_iso3')['salary_in_usd'].mean().reset_index()

        map_chart = px.choropleth(
            country_avg,
            locations='employee_residence_iso3',
            color='salary_in_usd',
            color_continuous_scale='rdylgn',
            hover_name='employee_residence_iso3',
            title='Average Salary for Data Scientist by Country',
            labels={'salary_in_usd': 'Avg Salary', 'employee_residence_iso3': 'Country'}
        )
        map_chart.update_layout(title_x=0.1)
        st.plotly_chart(map_chart, use_container_width=True)
        map_chart.show()
    else:
        st.warning("No Data Available")

st.subheader("Detailed Data")
st.dataframe(df_filtered)
