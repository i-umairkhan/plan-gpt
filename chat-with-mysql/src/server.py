from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
import mysql.connector


app = Flask(__name__)
CORS(app)

# Load environment variables from .env file
load_dotenv()

# Initialize SQLDatabase
db = SQLDatabase.from_uri("mysql+mysqlconnector://root:plan-gpt-db@localhost:3306/mydb")

conn = mysql.connector.connect(
    database="mydb",
    user="root",
    password="plan-gpt-db",
    host="localhost",
)


# Define route for handling user queries
@app.route('/query', methods=['POST'])
def query():
    data = request.json
    user_query = data['user_query']
    chat_history = data['chat_history']

    # Define SQL chain
    def get_sql_chain():
        template = """
            You are an expert project planner. User will give you a project idea you have to generate a detailed project plan that will be utilized in kabban board for that idea. Structure of plan should be like below.
            Plan should include domain spacific details it should not be general project plan it should include minor and major details of project.

            Board: Board conatins project name.
            List: Lists contains the milestones that need to be completed for the project.
            Card: Cards will contain the tasks. 
            Descriptio: Detailed description of each task.

            
            Generate a detailed project plan for that must includes several milestones tasks and subtasks use your knowledge to design extensive,professional and detailed project plan for {question} for user.Do not plan a project that is too simple or general. The project plan should be detailed and professional.

            Each board should have altlest 4 lists and  atleast 20 cards. Each card should have a detailed description. Do not include any duplicate id's. Use the following schema to generate the project plan

            Using above generated project plan ,schema give below and prisma schema given below to write a MySQL query that will take the project plan and intract with MySQL database.

            <SCHEMA>{schema}</SCHEMA>
            <PRISMASCHEMA>{prismaschema}</PRISMASCHEMA>

            Use this as orgid "org_2fSqiA61oEGNeWoEpMYnNXkYlab"
            Use imageid = "img_2fSqiA61oEGNeWoEpMYnNXkYlab" for the image.
            ids of all boards, lists and cards should be like boad-"name of board"-x, list-"name of board"-y, card-"name of board"-z where x is number of that board,y is number of that list, and z is number of card. x,y,z should be unique for each board,list and card and increment by 1 for each new board,list and card.
            Donot include any duplicate id's.
            use separate Insert statements for each row entry in table. Do not use single insert statement for all rows.
=            All ids should be unique all over the database.
            use imagethumbnailUrl and imagefullUrl = "https://images.unsplash.com/photo-1629221892514-7abb71a803f7?q=80&w=1374&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
            use imageusername and imageLinkhtml = "umair"
            Use today's date as createdat and updatedat.
            For duedate use current date for first card and than soo on for other
            Query should first create board than list and than cards and than description.
            Use all coloumns and give sample values if you dont have any values. Write only the SQL query and nothing else. Return only one query for whole plan donot multiple queries. Write SQL quries in such a way Quiers run one by one. Query should be directly run on MySQL database it should not give any error like "Commands out of sync; you can't run this command now". To solve commands out of sync error i found a solution on stackoverflow hear is it "
            To fix this I decided to run db.commit() only if the sql command will update the database state (by checking if the sql command contain the statements CREATE TABLE,INSERT INTO, etc.) instead of catching the exception."
            Do not wrap the SQL query in any other text, not even backticks.Check for MySQL syntax errors before submitting the query.Write query without any trasactions. Write SQL quries in such a way Quiers run one by one. Query should be directly run on MySQL database it should not give any error like "Commands out of sync; you can't run this command now". Respone should only include SQL query do not include any other text in response.
    Only Write SQL quires and nothing else. Do not wrap the SQL query in any other text, not even backticks. Donot give half reponse give full reponse in SQL.

            if there is "sql" or "mysql" in front of generated query remove it.
            Response should only include SQL query do not include any other text or backticks in response.
            """

        prompt = ChatPromptTemplate.from_template(template)

        # llm = ChatOpenAI(model="gpt-3.5-turbo-16k",max_tokens="1000")
        llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="AIzaSyDaEbG21tai7McVBc68Q9AadJvhktu0pCU",)


        def get_schema(_):
            return db.get_table_info()

        chain_main =  (
            RunnablePassthrough.assign(schema=get_schema)
            | prompt
            | llm
            | StrOutputParser()
        )
        

        sql_quer =   chain_main.invoke({
            "question": user_query,
            "chat_history": chat_history,
            "prismaschema": """            model Board {
            id            String @id @default(uuid())
            orgId         String
            title         String
            imageId       String
            imageThumbUrl String @db.Text
            imageFullUrl  String @db.Text
            imageUserName String @db.Text
            imageLinkHTML String @db.Text

            lists List[]

            createdAt DateTime @default(now())
            updatedAt DateTime @updatedAt
            }

            model List {
            id    String @id @default(uuid())
            title String
            order Int

            boardId String
            board   Board  @relation(fields: [boardId], references: [id], onDelete: Cascade)

            cards Card[]

            createdAt DateTime @default(now())
            updatedAt DateTime @updatedAt

            @@index([boardId])
            }

            model Card {
            id          String   @id @default(uuid())
            title       String
            order       Int
            description String?  @db.Text
            duedate     DateTime @default(now())

            listId String
            list   List   @relation(fields: [listId], references: [id], onDelete: Cascade)

            createdAt DateTime @default(now())
            updatedAt DateTime @updatedAt

            @@index([listId])
            }
            """
        })
        

        # db.run(command=sql_quer,fetch="cursor")
        f = open("newplan.sql", "w")
        f.write(sql_quer)
        f.close()
        # with open('newplan.sql', 'r') as sql_file:
        #     sql_script = sql_file.read()            
        cur = conn.cursor() 
        # cur.execute(sql_script)
        # conn.commit()
        with open('newplan.sql', 'r') as sql_file:
            sql_statements = sql_file.read().split(';')

        # Execute each SQL statement
        for sql_statement in sql_statements:
            if sql_statement.strip():
                try:
                    cur.execute(sql_statement)
                    conn.commit()
                    print("SQL statement executed successfully!")
                except Exception as e:
                    conn.rollback()
                    print("Error executing SQL statement:", e)
        cur.close()
        conn.close()

    
        return sql_quer
    
    # Define response generator
    # def get_response():
    #     sql_chain = get_sql_chain()

    #     template = """
    #     Based on the table schema below, question, sql query, and sql response, write a natural language response donot give SQL query in response. Natural language response should be in such a way that it should be easy to understand for a non technical person it should be in simple english.
    #   <SCHEMA>{schema}</SCHEMA>

    #    Conversation History: {chat_history}
    #    SQL Query: <SQL>{query}</SQL>
    #    User question: {question}
    #    SQL Response: {response}"""

    #     prompt = ChatPromptTemplate.from_template(template)


    #     # llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
    #     llm = ChatGoogleGenerativeAI(model="gemini-pro",google_api_key="AIzaSyBRMWyWv20Jch7kiU1118rCQmRkmXXhfNs")

    #     chain = (
    #         RunnablePassthrough.assign(query=sql_chain).assign(
    #             schema=lambda _: db.get_table_info(),
    #             response=lambda vars: db.run(vars["query"]),
    #         )
    #         | prompt
    #         | llm
    #         | StrOutputParser()
    #     )

        # return chain.invoke({
        #     "question": user_query,
        #     "chat_history": chat_history,
        #     "prismaschema": """            model Board {
        #     id            String @id @default(uuid())
        #     orgId         String
        #     title         String
        #     imageId       String
        #     imageThumbUrl String @db.Text
        #     imageFullUrl  String @db.Text
        #     imageUserName String @db.Text
        #     imageLinkHTML String @db.Text

        #     lists List[]

        #     createdAt DateTime @default(now())
        #     updatedAt DateTime @updatedAt
        #     }

        #     model List {
        #     id    String @id @default(uuid())
        #     title String
        #     order Int

        #     boardId String
        #     board   Board  @relation(fields: [boardId], references: [id], onDelete: Cascade)

        #     cards Card[]

        #     createdAt DateTime @default(now())
        #     updatedAt DateTime @updatedAt

        #     @@index([boardId])
        #     }

        #     model Card {
        #     id          String   @id @default(uuid())
        #     title       String
        #     order       Int
        #     description String?  @db.Text
        #     duedate     DateTime @default(now())

        #     listId String
        #     list   List   @relation(fields: [listId], references: [id], onDelete: Cascade)

        #     createdAt DateTime @default(now())
        #     updatedAt DateTime @updatedAt

        #     @@index([listId])
        #     }
        #     """
        # })

    # Get response
    print(get_sql_chain())
    return '', 204

    # Return response
    # return jsonify({"response": response})

# # Define route for handling user queries
@app.route('/report', methods=['GET'])
def report():

    # Define SQL chain
    def get_sql_chain():
        template = """
            You are Project Manager. You have to generate a professional project report of diffrent projects. Your Main focus area of report should be Risk and Cost Management.  

            You can read the deails of projects from schema below and write a detailed report for the projects. The report should include the following sections:

            <SCHEMA>{schema}</SCHEMA>


            Project Overview: A brief description of the project.
            Risk Management: A detailed analysis of the risks associated with the project and the strategies to mitigate them.
            Cost Optimization: A detailed analysis of the costs associated with the project and the strategies to optimize them.


            """


        prompt = ChatPromptTemplate.from_template(template)

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
        # sql_chain = get_sql_chain()

        template = """
            You are Project Manager. You have to generate a professional project report of diffrent projects. Your Main focus area of report should be Risk and Cost Management.  

            You can read the deails of projects from schema below and write a detailed report for the projects.Iclude all projects do not skip any project. The report should include the following sections:

            <SCHEMA>{schema}</SCHEMA>


            Project Overview: A brief description of the project.
            Risk Management: A detailed analysis of the risks associated with the project and the strategies to mitigate them.
            Cost Optimization: A detailed analysis of the costs associated with the project and the strategies to optimize them.

            Now return report for the project in markdown.
        Properly format the Markdown using heading, italic and blods so it looks like a professional report.
        """
        prompt = ChatPromptTemplate.from_template(template)


        # llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
        llm = ChatGoogleGenerativeAI(model="gemini-pro",google_api_key="AIzaSyBRMWyWv20Jch7kiU1118rCQmRkmXXhfNs")

        # chain = (
        #     RunnablePassthrough.assign(query=sql_chain).assign(
        #         schema=lambda _: db.get_table_info(),
        #         response=lambda vars: db.run(vars["query"]),
        #     )
        #     | prompt
        #     | llm
        #     | StrOutputParser()
        # )

        def get_schema(_):
            return db.get_table_info()
        
        chain = (
            RunnablePassthrough.assign(schema=get_schema)
            | prompt
            | llm
            | StrOutputParser()
        )


        return chain.invoke({})

    # Get response
    response = get_response()

    # Return response
    return jsonify({"response": response})



if __name__ == '__main__':  
    app.run(debug=True)
