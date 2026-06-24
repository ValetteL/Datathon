from dotenv import load_dotenv

load_dotenv()

from prompts.prompts import get_llm

llm = get_llm()
response = llm.invoke("Réponds juste OK.")
print(response.content)
