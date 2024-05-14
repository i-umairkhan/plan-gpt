from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

user_query = "Cybersecurity Audit for a bank" 

db = SQLDatabase.from_uri("mysql+mysqlconnector://root:plan-gpt-db@localhost:3306/mydb")


# Define SQL chain
def get_sql_chain():
    template = """
        You are Project planner and a data analyst. User will give you a project idea you have to generate a detailed project plan that will be utilized in kabban board for that idea. Structure of plan should be like below.
        Plan should include domain spacific details it should not be general project plan it shpould include minor and major details of project.

        Board: Board conatins project name.
        List: Lists contains the milestones that need to be completed for the project.
        Card: Cards will contain the tasks. 
        Descriptio: Detailed description of each task.

        Number of Lists msut be 5 or greater and number of Cards must be 20 or more.Eeach list can have minimum of 3 Cards.
        Generate a detailed project plan for that must includes several milestones tasks and subtasks use your knowledge to design extensive,professional and detailed project plan for {question} for user.Do not plan a project that is too simple or general. The project plan should be detailed and professional.

        Using above project plan and below schema, write a MySQL query that will take the project plan and insert it MySQL database.Use this as orgid "org_2fSqiA61oEGNeWoEpMYnNXkYlab"
        Use imageid = "img_2fSqiA61oEGNeWoEpMYnNXkYlab" for the image.
        use imagethumbnailUrl and imagefullUrl = "https://images.unsplash.com/photo-1629221892514-7abb71a803f7?q=80&w=1374&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
        use imageusername and imageLinkhtml = "umair"
        Use all coloumns and give sample values if you dont have any values. Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.Check for MySQL syntax errors before submitting the query.Use transactions in query.Write SQL quries in such a way Quiers run one by one.

        <SCHEMA>{schema}</SCHEMA>

        if there is "sql" or "mysql" in front of generated query remove it.
        """


    prompt = ChatPromptTemplate.from_template(template)

    # llm = ChatOpenAI(model="gpt-3.5-turbo-16k",max_tokens="1000")
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="AIzaSyBRMWyWv20Jch7kiU1118rCQmRkmXXhfNs")


    def get_schema(_):
        return db.get_table_info()

    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )

# Define response generator
def get_response():
    sql_chain = get_sql_chain()

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
    llm = ChatGoogleGenerativeAI(model="gemini-pro",google_api_key="AIzaSyBRMWyWv20Jch7kiU1118rCQmRkmXXhfNs")

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
    })

# Get response
response = get_response()