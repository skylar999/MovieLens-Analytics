# MovieLens Analytics

Analytical Python project based on the MovieLens dataset. The project explores movies, ratings, users, tags, and external movie identifiers through a reusable Python module, a Jupyter Notebook report, and PyTest tests.

## Project Overview

The project answers practical analytical questions:

- Which movie genres are the most frequent?
- How are movies distributed by release year?
- What is the distribution of user ratings?
- Which movies have the highest average or median rating?
- Which users are the most inconsistent in their ratings?
- Which tags are the most popular or descriptive?
- How can MovieLens IDs be connected with IMDb and TMDb identifiers?

The main logic is implemented in `src/movielens_analysis.py`. The notebook is used as a readable analytical report. Tests are placed separately in `tests/`.

## Repository Structure

```text
MovieLens_Analytics/
├── README.md
├── requirements.txt
├── code-samples/
│   ├── links.py
│   ├── movies.py
│   ├── ratings.py
│   └── tags.py
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

## Main Functionality

### Movies

- loading and parsing movie metadata;
- extracting titles, release years, and genres;
- searching by ID, title, year, and genre;
- calculating release-year and genre distributions;
- finding the oldest, newest, and most genre-diverse movies.

### Ratings

- loading and parsing user ratings;
- calculating average and median ratings;
- building rating distributions;
- finding top movies by rating statistics;
- analyzing user rating activity.

### Users

- calculating the number of ratings per user;
- analyzing users by mean and median rating;
- finding users with the highest rating variance.

### Tags

- loading user-generated tags;
- finding popular tags;
- extracting longest and most descriptive tags;
- searching tags by keyword.

### Links

- loading IMDb and TMDb identifiers;
- matching MovieLens movies with external IDs;
- generating IMDb links;
- running exploratory methods based on linked movie metadata.

The IMDb-related methods are kept as an exploratory extension. The core analytical value of the project is based on local MovieLens CSV files.

## Technologies

- Python 3
- Jupyter Notebook
- PyTest
- CSV data processing
- Object-oriented programming
- Exploratory data analysis

## Installation

```bash
git clone <repository-url>
cd MovieLens_Analytics
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Notebook

```bash
jupyter notebook src/movielens_report_ready.ipynb
```

## Run Tests

```bash
python -m pytest tests
```

## Example Usage

```python
from pathlib import Path
import sys

PROJECT_ROOT = Path.cwd()
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from movielens_analysis import Movies, Ratings, Tags, Links, Users

DATA_DIR = SRC_DIR / "tables"

movies = Movies(str(DATA_DIR / "movies.csv"))
ratings = Ratings(str(DATA_DIR / "ratings.csv"), str(DATA_DIR / "movies.csv"))
tags = Tags(str(DATA_DIR / "tags.csv"))
links = Links(str(DATA_DIR / "links.csv"), str(DATA_DIR / "movies.csv"))
users = Users(str(DATA_DIR / "ratings.csv"), str(DATA_DIR / "movies.csv"))

print(movies.get_genre_statistics())
print(ratings.get_rating_distribution())
print(tags.most_popular(10))
print(users.top_n_by_ratings_variance(5))
```

## What This Project Demonstrates

- structuring analytical Python code into reusable classes;
- reading and processing CSV datasets;
- performing exploratory data analysis;
- calculating descriptive statistics;
- preparing a Jupyter Notebook report;
- writing PyTest checks for analytical methods;
- working with real-world dataset relationships.

## Possible Improvements

- Add visualizations for rating distribution, genre frequency, and movies by year.
- Add a Streamlit or Dash dashboard.
- Replace exploratory IMDb metadata logic with a real cached dataset or an official API-based pipeline.
- Add more robust CSV parsing through pandas.
