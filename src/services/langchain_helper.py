from __future__ import annotations

import json, os

# LLM
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback

# Generic Agent
from langchain.agents import create_json_agent

# JSON Agent
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.tools.json.tool import  JsonSpec

# Loaders
from langchain.document_loaders import JSONLoader

# Text splitters
from langchain_text_splitters import RecursiveJsonSplitter

# Other imports
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool
from langchain_core.callbacks import StdOutCallbackHandler
from langchain.globals import set_debug

# Tool
from langchain.tools import Tool
from typing import List
from langchain.tools import BaseTool
from langchain.tools.json.tool import JsonSpec

# Embeddings
from langchain_core.documents import Document
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

# SQLLite
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# JsonToolkitExtended 
class JsonToolkitExtended(JsonToolkit):
    """Toolkit for interacting with a JSON spec."""

    spec: JsonSpec

    def compare_lists(self, tool_input: str) -> str:
        tool_input_list = tool_input.split(",")
        left_list = self.spec.value(tool_input_list[0].strip())
        right_list = self.spec.value(tool_input_list[1].strip())
        print(f"\n\ntool_input_list: {tool_input_list}\n\nleft_list: {left_list}\n\nright_list: {right_list}" )
        return list(set(left_list) - set(right_list))

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""

        compare_lists_tool=Tool(
            name="compare_lists",
            func=self.compare_lists,
            description="""
                Compare two lists and get the difference
            """
            )
        
        return super().get_tools() + [compare_lists_tool]
        
if __name__ == '__main__':
    # Set global debug for detailed logging
    set_debug(False)

    # Intialize LLM
    llm = ChatOpenAI(temperature=0,model="gpt-3.5-turbo")

    # Tool: Google search tool
    search = GoogleSearchAPIWrapper()
    tool = Tool(
        name="google_search",
        description="Search Google for recent results.",
        func=search.run,
    )

    # Google search each mutual fund summary
    all_files_data = []
    splitter = RecursiveJsonSplitter(max_chunk_size=300)

    for file in ["AAAAX_US.json", "AAACX_US.json"]:
        loader=JSONLoader(file_path=f"/workspace/backend-py/data/mutual_funds/{file}",
                        jq_schema=".",json_lines=False,text_content=False)
        docs=loader.load()
        data = json.loads(docs[0].page_content)
        output = tool.run(f"Mutual fund {os.path.splitext(file)[0]} summary")
        # print(output)
        data['latest_summary'] = output

        # texts = splitter.split_text(json_data=data)
        docs = splitter.create_documents(texts=[data])
        # [print(doc.page_content) for doc in docs]
        # all_files_data[file] = []
        for index, doc in enumerate(docs):
            # print(doc.page_content)
            json_dict = json.loads(doc.page_content)
            json_dict['code'] = file
            all_files_data.append(Document(page_content=json.dumps(json_dict), metadata=doc.metadata))

    # Embedding and chroma
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_documents(all_files_data, embedding_function)
    # query = "Fund summary of AAACX_US.json"
    # query = "Sector_Weights"
    # query = "Prev_Close_Price"
    query = "Top_Holdings"
    docs = db.similarity_search(query)
    all_files_data = {}
    for doc in docs:
        # print(doc.page_content)
        json_dict = json.loads(doc.page_content)
        if json_dict["code"] in all_files_data:
            all_files_data[json_dict["code"]].update(json_dict)
        else:
            all_files_data[json_dict["code"]] = json_dict
    # print(all_files_data)

    # Tool: duckduckgo
    # for file in ["AAAAX_US.json", "AAACX_US.json"]:
    #     tools=load_tools(["ddg-search"],llm=llm)
    #     agent=initialize_agent(tools,llm,agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,verbose=True)
    #     agent.run(f"Mutual fund {os.path.splitext(file)[0]} summary")

    # Loaders: S3Loaders
    # loader = S3FileLoader("sravz-data", "fundamental/AAAAX_US.json",
    #         endpoint_url=helper.settings.constants.CONTABO_BASE_URL,
    #         aws_access_key_id=helper.settings.constants.CONTABO_KEY,
    #         aws_secret_access_key=helper.settings.constants.CONTABO_SECRET)
    # print(loader.load())

    # loader=DirectoryLoader(path="/workspace/backend-py/data/mutual_funds/",glob="**/*.json",use_multithreading=True)
    # docs=loader.load()
    # print(len(docs)
        
    # # Agent: JSON Agent
    spec=JsonSpec(dict_=all_files_data,max_value_length=4000)
    toolkit=JsonToolkitExtended(spec=spec)
    handler = StdOutCallbackHandler() #verbose=True will automaticall invoke StdOutCallbackHandler
    agent=create_json_agent(llm=llm,
                            toolkit=toolkit,
                            max_iterations=1000, 
                            verbose=True, 
                            agent_executor_kwargs={'handle_parsing_errors':True},
                            return_intermediate_steps=True,
                            callbacks=[handler])



    # JSON Agent: Run agent and query
    with get_openai_callback() as cost:
        # Session 1
        # print(agent.run("What is AAACX_US Top_Holdings Pennant Park Investment Corp weight"))
        # print(agent.run("What are AAAAX_US Sector_Weights Names"))
        # print(agent.run("What are common Sector_Weights between AAAAX_US and AAACX_US"))
        # response=agent({"input":"What are AAACX_US Top_Holdings and also get the latest summary and price"})
        # response=agent({"input":"List difference in Top_Holdings for AAACX_US and AAAAX_US"})  

        # Session 2
       #  print(agent.run("For AAACX_US what is the value of  Prev_Close_Price"))
        # print(agent.run("For AAACX_US in General2 what is the value of  Prev_Close_Price"))
        # print(agent.run("What is AAACX_US Top_Holdings Pennant Park Investment Corp weight"))
        print(agent.run("Get difference between the Top_Holdings of AAACX_US and AAAAX_US"))  

        # Print cost
        print(f"total tokens: {cost.total_tokens}")
        print(f"prompt tokens: {cost.prompt_tokens}") # Tokens in the question
        print(f"completion tokens: {cost.completion_tokens}") # Tokens used to generated response
        print(f"cost is: {cost.total_cost}")