import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from movielens_analysis import Movies


movies = Movies(PROJECT_ROOT / "src" / "tables" / "movies.csv")
print(list(movies.get_genre_statistics().items())[:5])
