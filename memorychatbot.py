import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI

# Session State
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []

# Define Function
def custom_css(css):
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    <style>
        .stTextInput>div>div>input {
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            outline: none;
        }
        .stButton>button {
            padding: 10px 20px;
            background-color: #2e67ff;
            border: none;
            color: #fff;
            font-size: 1rem;
            cursor: pointer;
            border-radius: 5px;
            outline: none;
        }
        .stButton>button:hover {
            background-color: #1a47b7;
        }
    </style>
    """, unsafe_allow_html=True)

def get_text():
    """
    Get the user input text.
    Returns:
        (str): The text entered by the user
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input",
                            placeholder="Your AI assistant here! Ask me anything ...",
                            label_visibility='hidden')
    return input_text

# Start a new chat
def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.memory = {}
    st.session_state.entity_memory.buffer.clear()

# Set up the App Layout and widget to accept secret API key
st.title("J.A.R.V.I.S")
st.markdown(
    '''
    > :black[**JARVIS by Alchemic Technology,**  *powered by -  [LangChain]('https://langchain.readthedocs.io/en/latest/modules/memory.html#memory') +
    [OpenAI]('https://platform.openai.com/docs/models/gpt-3-5') +
    [Streamlit]('https://streamlit.io')]
    ''')
with st.sidebar.expander(" 🛠️ Settings ", expanded=False):
    if st.checkbox("Preview memory store"):
        st.write(st.session_state.entity_memory.store)
    if st.checkbox("Preview memory buffer"):
        st.write(st.session_state.entity_memory.buffer)
    MODEL = st.selectbox(label='Model', options=['gpt-3.5-turbo', 'text-davinci-003', 'text-davinci-002', 'code-davinci-002'])
    K = st.number_input(' (#)Summary of prompts to consider', min_value=3, max_value=1000)

API= st.sidebar.text_input(":blue[Enter Your OPENAI API-KEY :]",
                              placeholder="Paste your OpenAI API key here (sk-...)",
                              type="password")

if API:
    llm = OpenAI(temperature=0.25,
                 openai_api_key=API,
                 model_name=MODEL,
                 verbose=False,
                 max_tokens=3000)

    if 'entity_memory' not in st.session_state:
        st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K)

    # Create the ConversationChain object with the specified configuration
    Conversation = ConversationChain(
        llm=llm,
        prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        memory=st.session_state.entity_memory
    )
else:
    st.markdown('''
        ```
        - 1. Enter API Key + Hit enter 🔐

        - 2. Ask anything via the text input widget

        Your API-key is not stored in any form by this app. However, for transparency ensure to delete your API once used.
        ```

        ''')
    st.sidebar.warning('API key required to try this app. The API key is not stored in any form.')

# Button to Clear the memory
st.sidebar.button("New Chat", on_click=new_chat, type='primary')

# Get the user INPUT and RUN the chain. Also, store them
user_input = st.text_input("Type your message:", value=st.session_state["input"], key="input")
if st.button("Send"):
    if user_input:
        output = Conversation.run(input=user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)

# Display the conversation history using an expander, and allow the user to download it.
download_str = []
with st.expander("Conversation", expanded=True):
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        st.info(f"User: {st.session_state['past'][i]}", icon="🧐")
        st.success(f"JARVIS: {st.session_state['generated'][i]}", icon="🤖")
        download_str.append(st.session_state['past'][i])
        download_str.append(st.session_state['generated'][i])

    download_str = '\n'.join(download_str)
    if download_str:
        st.download_button('Download', download_str)

# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
    with st.sidebar.expander(label=f"Conversation-Session:{i}"):
        st.write(sublist)

# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session
 
