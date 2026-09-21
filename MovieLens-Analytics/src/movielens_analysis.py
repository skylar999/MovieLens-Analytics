import csv
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone


def read_csv(path, required_columns, lines_limit=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} not found")

    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        columns = set(reader.fieldnames or [])
        if not set(required_columns).issubset(columns):
            raise ValueError(f"Invalid CSV format: {path}")

        for index, row in enumerate(reader):
            if lines_limit is not None and index >= lines_limit:
                break
            yield row


class Movies:
    def __init__(self, path_to_the_file, lines_limit=None):
        self.path = path_to_the_file
        self.lines_limit = lines_limit
        self.movies_data = []
        self.id_to_movie = {}
        self.title_to_movie = {}
        self.year_to_movies = defaultdict(list)
        self.genre_to_movies = defaultdict(list)
        self._load_movies()

    def _load_movies(self):
        try:
            rows = read_csv(
                self.path,
                ["movieId", "title", "genres"],
                self.lines_limit,
            )
            for row in rows:
                movie_id = int(row["movieId"])
                original_title = row["title"].strip()
                match = re.search(r"\((\d{4})\)$", original_title)
                year = int(match.group(1)) if match else None
                title = original_title[:match.start()].strip() if match else original_title

                genres = []
                if row["genres"] and row["genres"] != "(no genres listed)":
                    genres = row["genres"].split("|")

                movie = {
                    "movieId": movie_id,
                    "title": title,
                    "year": year,
                    "genres": genres,
                    "original_title": original_title,
                }
                self.movies_data.append(movie)
                self.id_to_movie[movie_id] = movie
                self.title_to_movie.setdefault(title.casefold(), movie)

                if year is not None:
                    self.year_to_movies[year].append(movie)
                for genre in genres:
                    self.genre_to_movies[genre].append(movie)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Error loading movies: {error}") from error

    def get_movie_by_id(self, movie_id):
        return self.id_to_movie.get(movie_id)

    def get_movie_by_title(self, title):
        return self.title_to_movie.get(title.casefold())

    def get_movies_by_year(self, year):
        return sorted(self.year_to_movies.get(year, []), key=lambda movie: movie["title"])

    def get_all_years(self):
        return sorted(self.year_to_movies)

    def get_movies_by_genre(self, genre):
        return sorted(self.genre_to_movies.get(genre, []), key=lambda movie: movie["title"])

    def get_genre_statistics(self):
        counts = Counter()
        for movie in self.movies_data:
            counts.update(movie["genres"])
        return dict(counts.most_common())

    def get_oldest_newest_movies(self):
        movies = [movie for movie in self.movies_data if movie["year"] is not None]
        if not movies:
            return None, None
        return (
            min(movies, key=lambda movie: movie["year"]),
            max(movies, key=lambda movie: movie["year"]),
        )

    def get_year_analysis(self, year):
        movies = self.get_movies_by_year(year)
        animation_count = sum("Animation" in movie["genres"] for movie in movies)
        total = len(movies)
        return {
            "total_movies": total,
            "animation_count": animation_count,
            "animation_percentage": animation_count / total * 100 if total else 0,
            "is_special_year": animation_count >= 3,
        }

    def get_dataset_summary(self):
        years = self.get_all_years()
        genres = self.get_genre_statistics()
        oldest, newest = self.get_oldest_newest_movies()

        print("=" * 60)
        print("СВОДКА ПО ДАТАСЕТУ ФИЛЬМОВ")
        print("=" * 60)
        print(f"Всего фильмов: {len(self.movies_data)}")
        if years:
            print(f"Диапазон лет: {years[0]} - {years[-1]}")
        print(f"Уникальных жанров: {len(genres)}")
        print(f"Самый популярный жанр: {next(iter(genres), 'N/A')}")
        if oldest:
            print(f"Самый старый фильм: {oldest['title']} ({oldest['year']})")
        if newest:
            print(f"Самый новый фильм: {newest['title']} ({newest['year']})")
        print("=" * 60)

    def dist_by_release(self):
        counts = Counter(
            movie["year"] for movie in self.movies_data if movie["year"] is not None
        )
        return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    def dist_by_genres(self):
        return self.get_genre_statistics()

    def most_genres(self, n=5):
        movies = [(movie["title"], len(movie["genres"])) for movie in self.movies_data]
        movies.sort(key=lambda item: (-item[1], item[0]))
        return dict(movies[:n])


class Ratings(Movies):
    def __init__(self, path_to_ratings, path_to_movies, lines_limit=None):
        super().__init__(path_to_movies)
        self.ratings_path = path_to_ratings
        self.lines_limit = lines_limit
        self.ratings_data = []
        self.user_ratings = defaultdict(list)
        self.movie_ratings = defaultdict(list)
        self.user_movies = defaultdict(set)
        self.movie_users = defaultdict(set)
        self.joined_data = []
        self._load_ratings()

    def _load_ratings(self):
        try:
            rows = read_csv(
                self.ratings_path,
                ["userId", "movieId", "rating", "timestamp"],
                self.lines_limit,
            )
            for row in rows:
                rating = {
                    "userId": int(row["userId"]),
                    "movieId": int(row["movieId"]),
                    "rating": float(row["rating"]),
                    "timestamp": int(row["timestamp"]),
                }
                rating["datetime"] = datetime.fromtimestamp(
                    rating["timestamp"], timezone.utc
                )

                self.ratings_data.append(rating)
                self.user_ratings[rating["userId"]].append(rating)
                self.movie_ratings[rating["movieId"]].append(rating)
                self.user_movies[rating["userId"]].add(rating["movieId"])
                self.movie_users[rating["movieId"]].add(rating["userId"])

                movie = self.get_movie_by_id(rating["movieId"])
                if movie:
                    self.joined_data.append({**rating, **movie})
        except (TypeError, ValueError) as error:
            raise ValueError(f"Error loading ratings: {error}") from error

    def get_user_ratings(self, user_id):
        return sorted(
            self.user_ratings.get(user_id, []),
            key=lambda rating: rating["rating"],
            reverse=True,
        )

    def get_average_rating_for_movie(self, movie_id):
        ratings = self.movie_ratings.get(movie_id, [])
        if not ratings:
            return 0.0
        return sum(item["rating"] for item in ratings) / len(ratings)

    def get_average_rating(self):
        if not self.ratings_data:
            return 0.0
        return sum(item["rating"] for item in self.ratings_data) / len(self.ratings_data)

    def get_rating_distribution(self):
        counts = Counter(item["rating"] for item in self.ratings_data)
        return {rating / 2: counts.get(rating / 2, 0) for rating in range(1, 11)}

    def dist_by_year(self):
        counts = Counter(item["datetime"].year for item in self.ratings_data)
        return dict(sorted(counts.items()))

    def top_by_num_of_ratings(self, n=5):
        movies = []
        for movie_id, ratings in self.movie_ratings.items():
            movie = self.get_movie_by_id(movie_id)
            if movie:
                movies.append((movie["title"], len(ratings)))
        movies.sort(key=lambda item: (-item[1], item[0]))
        return dict(movies[:n])

    def top_by_ratings(self, n, metric="average", min_ratings=1):
        if metric not in {"average", "median"}:
            raise ValueError("metric must be 'average' or 'median'")

        scores = []
        for movie_id, rows in self.movie_ratings.items():
            if len(rows) < min_ratings:
                continue
            values = sorted(row["rating"] for row in rows)
            if metric == "average":
                score = sum(values) / len(values)
            else:
                middle = len(values) // 2
                score = values[middle]
                if len(values) % 2 == 0:
                    score = (values[middle - 1] + values[middle]) / 2

            movie = self.get_movie_by_id(movie_id)
            if movie:
                scores.append((movie, score))

        scores.sort(key=lambda item: (-item[1], item[0]["title"]))
        return [movie for movie, _ in scores[:n]]

    def get_top_movies_ids(self, n=3, min_ratings=1):
        return [
            (movie["movieId"], movie["title"])
            for movie in self.top_by_ratings(
                n, metric="average", min_ratings=min_ratings
            )
        ]

    def top_controversial(self, n=5, min_ratings=2):
        movies = []
        for movie_id, ratings in self.movie_ratings.items():
            if len(ratings) < min_ratings:
                continue
            values = [item["rating"] for item in ratings]
            mean = sum(values) / len(values)
            variance = sum((value - mean) ** 2 for value in values) / len(values)
            movie = self.get_movie_by_id(movie_id)
            if movie:
                movies.append((movie["title"], variance))
        movies.sort(key=lambda item: (-item[1], item[0]))
        return dict(movies[:n])


class Users(Movies):
    def __init__(self, path_to_ratings, path_to_movies, lines_limit=None):
        super().__init__(path_to_movies)
        self.ratings_path = path_to_ratings
        self.lines_limit = lines_limit
        self.ratings_data = []
        self.user_ratings = defaultdict(list)
        self._load_ratings()

    def _load_ratings(self):
        try:
            rows = read_csv(
                self.ratings_path,
                ["userId", "movieId", "rating", "timestamp"],
                self.lines_limit,
            )
            for row in rows:
                rating = {
                    "userId": int(row["userId"]),
                    "movieId": int(row["movieId"]),
                    "rating": float(row["rating"]),
                    "timestamp": int(row["timestamp"]),
                }
                self.ratings_data.append(rating)
                self.user_ratings[rating["userId"]].append(rating["rating"])
        except (TypeError, ValueError) as error:
            raise ValueError(f"Error loading ratings: {error}") from error

    def dist_by_num_of_ratings(self):
        counts = Counter(len(ratings) for ratings in self.user_ratings.values())
        return dict(sorted(counts.items()))

    def dist_by_mean_or_median_rating(self, metric="mean"):
        if metric not in {"mean", "median"}:
            raise ValueError("metric must be 'mean' or 'median'")

        distribution = Counter()
        for ratings in self.user_ratings.values():
            values = sorted(ratings)
            if metric == "mean":
                result = sum(values) / len(values)
            else:
                middle = len(values) // 2
                result = values[middle]
                if len(values) % 2 == 0:
                    result = (values[middle - 1] + values[middle]) / 2
            distribution[round(result, 2)] += 1
        return dict(sorted(distribution.items()))

    def top_n_by_ratings_variance(self, n=5):
        variances = []
        for user_id, ratings in self.user_ratings.items():
            if len(ratings) < 2:
                continue
            mean = sum(ratings) / len(ratings)
            variance = sum((rating - mean) ** 2 for rating in ratings) / len(ratings)
            variances.append((user_id, variance, len(ratings)))
        variances.sort(key=lambda item: (-item[1], item[0]))
        return variances[:n]


class Tags:
    def __init__(self, path_to_the_file, lines_limit=None):
        self.path = path_to_the_file
        self.lines_limit = lines_limit
        self.tags_data = []
        self.movie_tags = defaultdict(list)
        self.user_tags = defaultdict(list)
        self.tag_frequency = Counter()
        self._load_tags()

    def _load_tags(self):
        try:
            rows = read_csv(
                self.path,
                ["userId", "movieId", "tag", "timestamp"],
                self.lines_limit,
            )
            for row in rows:
                tag = {
                    "userId": int(row["userId"]),
                    "movieId": int(row["movieId"]),
                    "tag": row["tag"].strip().lower(),
                    "timestamp": int(row["timestamp"]),
                }
                tag["datetime"] = datetime.fromtimestamp(tag["timestamp"], timezone.utc)
                self.tags_data.append(tag)
                self.movie_tags[tag["movieId"]].append(tag)
                self.user_tags[tag["userId"]].append(tag)
                self.tag_frequency[tag["tag"]] += 1
        except (TypeError, ValueError) as error:
            raise ValueError(f"Error loading tags: {error}") from error

    def get_tags_for_movie(self, movie_id):
        return sorted({tag["tag"] for tag in self.movie_tags.get(movie_id, [])})

    def get_tags_by_user(self, user_id):
        return sorted({tag["tag"] for tag in self.user_tags.get(user_id, [])})

    def get_most_common_tag(self):
        return self.tag_frequency.most_common(1)[0][0] if self.tag_frequency else None

    def get_tagging_analysis(self):
        most_common = self.get_most_common_tag()
        emotional_tags = {
            "love",
            "funny",
            "awesome",
            "great",
            "best",
            "favorite",
            "amazing",
            "beautiful",
            "heartwarming",
            "emotional",
        }
        return {
            "total_tags": len(self.tags_data),
            "unique_tags": len(self.tag_frequency),
            "tagging_users": len(self.user_tags),
            "tagged_movies": len(self.movie_tags),
            "most_common_tag": most_common,
            "is_emotional_connection": most_common in emotional_tags if most_common else False,
        }

    def most_words(self, n=5):
        tags = [(tag, len(tag.split())) for tag in self.tag_frequency]
        tags.sort(key=lambda item: (-item[1], item[0]))
        return dict(tags[:n])

    def longest(self, n=5):
        tags = sorted(self.tag_frequency, key=lambda tag: (-len(tag), tag))
        return tags[:n]

    def most_words_and_longest(self, n=5):
        return sorted(set(self.most_words(n)) & set(self.longest(n)))

    def most_popular(self, n=5):
        return dict(self.tag_frequency.most_common(n))

    def tags_with(self, word):
        word = word.casefold()
        return sorted(tag for tag in self.tag_frequency if word in tag.casefold())


class Links:
    def __init__(self, path_to_the_file, path_to_movies, lines_limit=None):
        self.path = path_to_the_file
        self.lines_limit = lines_limit
        self.links_data = []
        self.movie_to_links = {}
        self.imdb_to_movie = {}
        self.movies = Movies(path_to_movies)
        self.joined_data = []
        self._load_links()

    def _load_links(self):
        try:
            rows = read_csv(
                self.path,
                ["movieId", "imdbId", "tmdbId"],
                self.lines_limit,
            )
            for row in rows:
                movie_id = int(row["movieId"])
                imdb_id = row["imdbId"].strip() or None
                tmdb_id = row["tmdbId"].strip() or None
                if imdb_id and not imdb_id.startswith("tt"):
                    imdb_id = f"tt{imdb_id.zfill(7)}"

                link = {
                    "movieId": movie_id,
                    "imdbId": imdb_id,
                    "tmdbId": tmdb_id,
                }
                self.links_data.append(link)
                self.movie_to_links[movie_id] = link
                if imdb_id:
                    self.imdb_to_movie[imdb_id] = movie_id

                movie = self.movies.get_movie_by_id(movie_id)
                if movie:
                    self.joined_data.append({**link, **movie})
        except (TypeError, ValueError) as error:
            raise ValueError(f"Error loading links: {error}") from error

    def get_external_ids(self, movie_title):
        movie = self.movies.get_movie_by_title(movie_title)
        if not movie:
            return None
        link = self.movie_to_links.get(movie["movieId"])
        if not link:
            return None
        return {"imdbId": link["imdbId"], "tmdbId": link["tmdbId"]}

    def get_imdb(self, movie_title):
        ids = self.get_external_ids(movie_title)
        if not ids or not ids["imdbId"]:
            return None
        return f"https://www.imdb.com/title/{ids['imdbId']}/"
