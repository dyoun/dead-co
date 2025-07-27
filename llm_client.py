from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def get_response(user_input):
    llm = OpenAI(temperature=0.7) # Setting temperature for creativity
    prompt_template = PromptTemplate(
        input_variables=["user_input"],
        template="Create a poem based on lyrics from the Grateful Dead from the following: {user_input}",
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)

    response = chain.run(user_input)

    return response

if __name__ == "__main__":
    user_input = 'going to san francisco'
    response = get_response(user_input)
    print(f"A Grateful Dead Poem based on '{user_input}'", response)