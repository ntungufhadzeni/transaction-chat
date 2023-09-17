import pandas as pd
import streamlit as st

from helper import format_data, create_agent, query_agent

st.set_page_config(page_title="TNS Robot", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>TNS Robot</h1>", unsafe_allow_html=True)

st.write("Please upload your Excel file below.")
data = st.file_uploader("Upload a Excel")

tab1, tab2, tab3 = st.tabs(["Generate Consumption Data", "Chat With Consumption Data", "Chat With Any Data"])

with tab1:
    st.header("📈 Generate Data")
    container = st.container()
    response_container = st.container()

    with container:
        generate = st.button(label='Generate')
    with response_container:
        if generate and data:
            df = format_data(data)
            df_success = df[df['Transaction Status'].eq('success')].reset_index()
            df_fail = df[df['Transaction Status'].eq('fail')].reset_index()
            lst_success = df_success['Unique Id'].to_list()
            # lst_fail = df_fail.slug.to_list()
            df_failed_duplicates = df_fail[df_fail['Comment'].eq('DUPLICATE TX') & ~df_fail['Unique Id'].isin(lst_success)].reset_index()
            df_failed_duplicates.loc[:, 'Transaction Status'] = 'duplicates not in success (failed)'
            df_success_duplicates = df_fail[df_fail['Comment'].eq('DUPLICATE TX') & df_fail['Unique Id'].isin(lst_success)].reset_index()
            df_success_duplicates['Transaction Status'] = 'duplicates in success (failed)'
            df_fail_other = df_fail[~df_fail['Comment'].eq('DUPLICATE TX')].reset_index()
            df_fail_other.loc[:, 'Transaction Status'] = 'other failed'
            df_undischarged_0 = df[df['Transaction Status'].eq('undischarged-00')].reset_index()
            df_undischarged_1 = df[df['Transaction Status'].eq('undischarged-01')].reset_index()

            # Concatenate all DataFrames
            merged_df = pd.concat(
                [df_success, df_failed_duplicates, df_success_duplicates, df_fail_other, df_undischarged_0,
                 df_undischarged_1])

            # Optionally, reset the index if needed
            merged_df.reset_index(drop=True, inplace=True)

            # Group the DataFrame by 'Transaction Status' and calculate the total transaction count and total
            # transaction amount for each status
            result = merged_df.groupby(['Month', 'Transaction Status']).agg({
                'Transaction Status': 'count',  # Count the occurrences of each status
                'Transaction Amount': 'sum'  # Sum the transaction amounts for each status
            }).rename(columns={'Transaction Status': 'Total Transactions', 'Transaction Amount': 'Total Amount (R)'})

            # Reset the index to make the 'Transaction Status' a column
            result = result.reset_index()

            st.write(result)

with tab2:
    st.header("👨‍💻 Chat With Consumption Data")

    container = st.container()
    response_container = st.container()

    with container:
        api_key = st.text_input("Openai API KEY", key='chat')
        with st.form(key='chat_data_form', clear_on_submit=False):
            query = st.text_area("Insert your query")
            submit_btn = st.form_submit_button(label='Query')

    with response_container:
        if submit_btn and query and api_key:
            df = format_data(data)
            agent = create_agent(df, api_key)
            response = query_agent(agent=agent, query=query)
            st.write(response)
        elif submit_btn and query and not api_key:
            st.write('Enter Openai API Key')

with tab3:
    st.header("👨‍💻 Chat With Any Data")

    container = st.container()
    response_container = st.container()

    with container:
        api_key = st.text_input("Openai API KEY", key='any')
        with st.form(key='chat_any_data_form', clear_on_submit=False):
            query = st.text_area("Insert your query")
            submit_btn = st.form_submit_button(label='Query')

    with response_container:
        if submit_btn and query and api_key:
            df = pd.read_excel(data)
            agent = create_agent(df, api_key)
            response = query_agent(agent=agent, query=query)
            st.write(response)
        elif submit_btn and query and not api_key:
            st.write('Enter Openai API Key')
