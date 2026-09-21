import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from movielens_analysis import Links


tables = PROJECT_ROOT / "src" / "tables"
links = Links(tables / "links.csv", tables / "movies.csv")
print(links.get_external_ids("Toy Story"))
print(links.get_imdb("Toy Story"))
