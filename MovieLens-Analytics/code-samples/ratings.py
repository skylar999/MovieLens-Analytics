import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from movielens_analysis import Ratings


tables = PROJECT_ROOT / "src" / "tables"
ratings = Ratings(tables / "ratings.csv", tables / "movies.csv")
print(f"Средняя оценка: {ratings.get_average_rating():.2f}")
print(ratings.top_by_num_of_ratings(5))
