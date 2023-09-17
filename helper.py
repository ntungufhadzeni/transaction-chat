import pandas as pd
from langchain import OpenAI
from langchain.agents import create_pandas_dataframe_agent
import uuid

import numpy as np


def string_to_uuid(input_string):
    try:
        # Remove any hyphens and convert the string to lowercase
        cleaned_string = input_string.replace('-', '').lower()

        # Check if the cleaned string is a valid UUID
        if len(cleaned_string) == 32:
            return uuid.UUID(cleaned_string)
        else:
            return np.NaN
    except ValueError:
        return np.NaN
    except AttributeError:
        return np.NaN


def create_slug(x, y, z):
    return f"{x}-{y}-{z}"


def format_data(filename: str):
    # Read the CSV file into a Pandas DataFrame.
    df = pd.read_excel(filename)

    df['Card No.'] = df['Card No.'].astype(str)
    df['TRANS Date'] = df['TRANS Date'].astype(str)
    df['TRANS Time'] = df['TRANS Time'].astype(str)
    df['TRANS DT'] = df['TRANS Date'] + df['TRANS Time']
    df['TRANS DT'] = pd.to_datetime(df['TRANS DT'], format='%Y%m%d%H%M%S')
    df['TRANS DT Str'] = df['TRANS DT'].dt.strftime('%Y-%m-%d-%H-%M-%S')
    df['slug'] = np.vectorize(create_slug)(df['TRANS DT Str'], df['Card No.'], df['Autual Amount'])

    df = df[
        ['Merchant',
         'Route Name',
         'Plate No.',
         'Card No.',
         'Autual Amount',
         'Receiving Time',
         'Station Name',
         'Liquidation status',
         'Reason for refusal',
         'TRANS DT',
         'slug'
         ]
    ]
    df.rename(columns={'Plate No.': 'Bus Number',
                       'Card No.': 'Card Number',
                       'Autual Amount': 'Transaction Amount',
                       'Liquidation status': 'Transaction Status',
                       'Reason for refusal': 'Comment',
                       'TRANS DT': 'Transaction Time',
                       'slug': 'Unique Id'
                       },
              inplace=True)

    return df


def create_agent(df: pd.DataFrame, api_key: str):
    # Create an OpenAI object.
    llm = OpenAI(openai_api_key=api_key)

    # Create a Pandas DataFrame agent.
    return create_pandas_dataframe_agent(llm, df, verbose=True)


def query_agent(agent, query):
    prompt = (
            """
                Use 'Comment' column to determine duplicates. The value for duplicate is 'DUPLICATE TX'.
                Query: 
                """
            + query
    )
    # Run the prompt through the agent.
    response = agent.run(prompt)

    # Convert the response to a string.
    return response.__str__()
