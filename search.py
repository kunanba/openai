import os
import re
import openai
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
env_path = Path('.', '.env')
load_dotenv(dotenv_path=env_path)

OPENAI_ENDPOINT=os.environ.get('OPENAI_ENDPOINT')

openai.api_type = "azure"
openai.api_base = OPENAI_ENDPOINT 
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_KEY")


def normalize_text(s, sep_token = " \n "):
    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,","",s)
    # remove all instances of multiple spaces
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.replace("\n", "")
    s = s.strip()
    
    return s
index_name = "azureblob-index"
# Get the service endpoint and API key from the environment
endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
key = os.environ["AZ_SEARCH_APIKEY"]

# Create a client
credential = AzureKeyCredential(key)
client = SearchClient(endpoint=endpoint,
                      index_name=index_name,
                      credential=credential)

### SEARCH APP

st.set_page_config(
    page_title="Streamlit Search - Demo",
    page_icon=":robot:"
)

st.title('Travel Search')
st.subheader("Search for travel questions you have")

prompt = st.text_input("Enter your search here","", key="input")

if st.button('Submit', key='generationSubmit'):
    
    results = client.search(search_text=prompt)
    results_list = []
    for result in results:
        results_list.append(result)
    res = normalize_text(results_list[0]['content'])

    # Build a prompt to provide the original query, the result and ask to summarise for the user
    summary_prompt = '''Summarise this result in a bulleted list to answer the search query a customer has sent.
    Search query: SEARCH_QUERY_HERE
    Search result: SEARCH_RESULT_HERE
    Summary:
    '''
    summary_prepped = summary_prompt.replace('SEARCH_QUERY_HERE',prompt).replace('SEARCH_RESULT_HERE', res)
    summary = openai.Completion.create(engine="gpt-35-turbo", prompt=summary_prepped,max_tokens=500)
    
    # Response provided by GPT-3
    st.write(summary['choices'][0]['text'])

    # Option to display raw table instead of summary from GPT-3
    #st.table(result_df)