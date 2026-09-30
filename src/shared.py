
from dotenv import load_dotenv
from langsmith import Client
load_dotenv()

from langsmith import Client

print(Client().share_dataset(dataset_name="mba-ia-pull-evaluation-prompt-eval-eval")["url"])