# MovieLens Analytics

An educational data analytics project in Python based on the MovieLens dataset. The project explores movies, user ratings, tags, and the relationship between MovieLens IDs and IMDb/TMDb identifiers.

## Features

- distribution of movies by year and genre;
- search for movies by ID, title, year, and genre;
- distribution of user ratings;
- finding movies with the highest average or median ratings;
- analysis of user activity and rating variance;
- finding popular, long, and multi-word tags;
- retrieving IMDb and TMDb movie identifiers;
- generating a link to a movie's IMDb page.

The project uses only data from local CSV files. Movie budgets, box office revenue, directors, and movie runtimes are not included in the MovieLens dataset, so this type of statistics is not calculated.

## Project Structure

```text
MovieLens-Analytics/
├── README.md
├── requirements.txt
├── code-samples/
├── src/
│   ├── movielens_analysis.py
│   ├── movielens_report_ready.ipynb
│   └── tables/
│       ├── links.csv
│       ├── movies.csv
│       ├── ratings.csv
│       └── tags.csv
└── tests/
    └── test_movielens_analysis.py
```

## Installation

```bash
git clone https://github.com/skylar999/MovieLens-Analytics.git
cd MovieLens-Analytics
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the virtual environment with:

```bash
.venv\Scripts\activate
```

## Running the Notebook

```bash
jupyter notebook src/movielens_report_ready.ipynb
```

## Running Tests

```bash
python -m pytest tests
```

## Example Usage

```python
from pathlib import Path
import sys

SRC_DIR = Path("src")
DATA_DIR = SRC_DIR / "tables"
sys.path.insert(0, str(SRC_DIR))

from movielens_analysis import Links, Movies, Ratings, Tags, Users

movies = Movies(DATA_DIR / "movies.csv")
ratings = Ratings(DATA_DIR / "ratings.csv", DATA_DIR / "movies.csv")
tags = Tags(DATA_DIR / "tags.csv")
links = Links(DATA_DIR / "links.csv", DATA_DIR / "movies.csv")
users = Users(DATA_DIR / "ratings.csv", DATA_DIR / "movies.csv")

print(movies.get_genre_statistics())
print(ratings.get_rating_distribution())
print(tags.most_popular(10))
print(users.top_n_by_ratings_variance(5))
print(links.get_external_ids("Toy Story"))
```

By default, the entire dataset is loaded. For quick experiments, you can pass a `lines_limit` parameter, for example:

```python
Ratings(..., lines_limit=1000)
```
