# MovieLens Analytics

Учебный аналитический проект на Python по датасету MovieLens. Проект исследует фильмы, оценки пользователей, теги и связь идентификаторов MovieLens с IMDb и TMDb.

## Возможности

- распределение фильмов по годам и жанрам;
- поиск фильмов по ID, названию, году и жанру;
- распределение пользовательских оценок;
- поиск фильмов с наибольшей средней или медианной оценкой;
- анализ активности пользователей и дисперсии их оценок;
- поиск популярных, длинных и многословных тегов;
- получение IMDb- и TMDb-идентификаторов фильма;
- формирование ссылки на страницу фильма в IMDb.

Проект использует только данные из локальных CSV-файлов. Бюджеты, сборы, режиссёры и длительность фильмов в датасет MovieLens не входят, поэтому такая статистика здесь не вычисляется.

## Структура проекта

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

## Установка

```bash
git clone https://github.com/skylar999/MovieLens-Analytics.git
cd MovieLens-Analytics
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

В Windows окружение активируется командой:

```bash
.venv\Scripts\activate
```

## Запуск ноутбука

```bash
jupyter notebook src/movielens_report_ready.ipynb
```

## Запуск тестов

```bash
python -m pytest tests
```

## Пример использования

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

По умолчанию загружается весь датасет. Для быстрого эксперимента можно передать `lines_limit`, например `Ratings(..., lines_limit=1000)`.
