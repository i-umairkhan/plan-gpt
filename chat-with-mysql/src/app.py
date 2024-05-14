# from dotenv import load_dotenv
# from langchain_core.messages import AIMessage, HumanMessage
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# from langchain_community.utilities import SQLDatabase
# from langchain_core.output_parsers import StrOutputParser
# from langchain_openai import ChatOpenAI
# from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI
# import streamlit as st

# def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
#   db_uri = f"mysql+mysqlconnector://{user}:plan-gpt-db@{host}:{port}/mydb"
#   return SQLDatabase.from_uri(db_uri)


# def get_sql_chain(db):
#   template = """
#     You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
#     Based on the table schema below, write a MySql query that would answer the user's question. Take the conversation history into account.
    
#     <SCHEMA>{schema}</SCHEMA>
    
#     Conversation History: {chat_history}
    
#     Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
    
#     For example:
#     Question: which 3 artists have the most tracks?
#     SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
#     Question: Name 10 artists
#     SQL Query: SELECT Name FROM Artist LIMIT 10;
    
#     Your turn:
    
#     Question: {question}
#     SQL Query:
#     """

    
#   prompt = ChatPromptTemplate.from_template(template)
  
#  # llm = ChatOpenAI(model="gpt-3.5-turbo")
#  # llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
#   llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="AIzaSyALF-zsnXlTaBBHiKjLXzTSecrQup7hWtU")

  
#   def get_schema(_):
#     return db.get_table_info()
  
#   return (
#     RunnablePassthrough.assign(schema=get_schema)
#     | prompt
#     | llm
#     | StrOutputParser()
#   )
    
# def get_response(user_query: str, db: SQLDatabase, chat_history: list):
#   sql_chain = get_sql_chain(db)
  
#   template = """
#     You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
#     Based on the table schema below, question, sql query, and sql response, write a natural language response donot give SQL query in response.
#     <SCHEMA>{schema}</SCHEMA>

#     Conversation History: {chat_history}
#     SQL Query: <SQL>{query}</SQL>
#     User question: {question}
#     SQL Response: {response}"""
  
#   prompt = ChatPromptTemplate.from_template(template)
  
# #  llm = ChatOpenAI(model="gpt-3.5-turbo")
# # llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
#   llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="AIzaSyALF-zsnXlTaBBHiKjLXzTSecrQup7hWtU")

  
#   chain = (
#     RunnablePassthrough.assign(query=sql_chain).assign(
#       schema=lambda _: db.get_table_info(),
#       response=lambda vars: db.run(vars["query"]),
#     )
#     | prompt
#     | llm
#     | StrOutputParser()
#   )
  
#   return chain.invoke({
#     "question": user_query,
#     "chat_history": chat_history,
# })
    
  
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = [
#       AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),
#     ]

# load_dotenv()

# st.set_page_config(page_title="Chat with MySQL", page_icon=":speech_balloon:")

# st.title("Chat with MySQL")

# with st.sidebar:
#     st.subheader("Settings")
#     st.write("This is a simple chat application using MySQL. Connect to the database and start chatting.")
    
#     st.text_input("Host", value="localhost", key="Host")
#     st.text_input("Port", value="3306", key="Port")
#     st.text_input("User", value="root", key="User")
#     st.text_input("Password", type="password", value="admin", key="Password")
#     st.text_input("Database", value="Chinook", key="Database")
    
#     if st.button("Connect"):
#         with st.spinner("Connecting to database..."):
#             db = init_database(
#                 st.session_state["User"],
#                 st.session_state["Password"],
#                 st.session_state["Host"],
#                 st.session_state["Port"],
#                 st.session_state["Database"]
#             )
#             st.session_state.db = db
#             st.success("Connected to database!")
    
# for message in st.session_state.chat_history:
#     if isinstance(message, AIMessage):
#         with st.chat_message("AI"):
#             st.markdown(message.content)
#     elif isinstance(message, HumanMessage):
#         with st.chat_message("Human"):
#             st.markdown(message.content)

# user_query = st.chat_input("Type a message...")
# if user_query is not None and user_query.strip() != "":
#     st.session_state.chat_history.append(HumanMessage(content=user_query))
    
#     with st.chat_message("Human"):
#         st.markdown(user_query)
        
#     with st.chat_message("AI"):
#         response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
#         st.markdown(response)
        
#     st.session_state.chat_history.append(AIMessage(content=response))


from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:plan-gpt-db@{host}:{port}/mydb"
  return SQLDatabase.from_uri(db_uri)


def get_sql_chain(db):
  template = """
    You are data analyst and your job is create write SQL quires.Based on table schema below, write a MySql query that would answer the user's question{question}. Take the conversation history into account.

    <SCHEMA>{schema}</SCHEMA>
    Only Write SQL quires and nothing else. Do not wrap the SQL query in any other text, not even backticks.
    if there is "sql" or "mysql" in front of generated query remove it.
    """

    
  prompt = ChatPromptTemplate.from_template(template)
  
  # llm = ChatOpenAI(model="gpt-3.5-turbo-16k",max_tokens="1000")
  # llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
  llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="AIzaSyBRMWyWv20Jch7kiU1118rCQmRkmXXhfNs")

  
  def get_schema(_):
    return db.get_table_info()
  
  return (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm
    | StrOutputParser()
  )
    
def get_response(user_query: str, db: SQLDatabase, chat_history: list):
  sql_chain = get_sql_chain(db)
  
  template = """
     You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, question, sql query, and sql response, write a natural language response donot give SQL query in response. Natural language response should be in such a way that it should be easy to understand for a non technical person it should be in simple english.
      <SCHEMA>{schema}</SCHEMA>

       Conversation History: {chat_history}
       SQL Query: <SQL>{query}</SQL>
       User question: {question}
       SQL Response: {response}"""
  
  prompt = ChatPromptTemplate.from_template(template)
  
  # llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
  # llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
  llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="AIzaSyBRMWyWv20Jch7kiU1118rCQmRkmXXhfNs")

  
  chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
      schema=lambda _: db.get_table_info(),
      response=lambda vars: db.run(vars["query"]),
    )
    | prompt
    | llm
    | StrOutputParser()
  )
  
  return chain.invoke({
    "question": user_query,
    "chat_history": chat_history,
})
    
  
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
      AIMessage(content="Hello! I'm a PlanGPT assistant. Ask me anything about your Project."),
    ]

load_dotenv()

st.set_page_config(page_title="Chat with PlanGPT", page_icon=":speech_balloon:")

st.title("Plan GPT QA Chatbot")

with st.sidebar:
    st.subheader("Settings")
    st.write("")
    
    st.text_input("Host", value="localhost", key="Host")
    st.text_input("Port", value="3306", key="Port")
    st.text_input("User", value="root", key="User")
    st.text_input("Password", type="password", value="plangptdb", key="Password")
    st.text_input("Database", value="mydb", key="Database")
    
    if st.button("Connect"):
        with st.spinner("Connecting to database..."):
            db = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"]
            )
            st.session_state.db = db
            st.success("Connected to database!")
    
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Type a message...")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))
