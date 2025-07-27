import argparse
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


def get_response(user_input):
    llm = OpenAI(temperature=0.7)  # Setting temperature for creativity
    prompt_template = PromptTemplate(
        input_variables=["user_input"],
        template="Create a poem based on lyrics from the Grateful Dead from the following: {user_input}",
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)

    response = chain.run(user_input)

    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Grateful Dead poem from lyrics.")
    parser.add_argument("--lyrics", type=str, help="Lyrics to base the poem on")
    parser.add_argument("--load", type=str, help="Path to JSONL file to load")

    args = parser.parse_args()
    lyrics = args.lyrics
    jsonl_file = args.load

    if lyrics:
        # user_input = 'going to san francisco'
        response = get_response(lyrics)
        print(f"A Grateful Dead Poem based on '{lyrics}'", response)

    if jsonl_file:
        from langchain_community.document_loaders import JSONLoader
        from pprint import pprint

        loader = JSONLoader(
            file_path=jsonl_file,
            jq_schema='{title, venue, date, views_all_time, views_last_30day, views_last_7day}',
            text_content=False,
            json_lines=True)

        data = loader.load()
        pprint(data)
