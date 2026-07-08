import os
import sys
import re
from collections import defaultdict, Counter
from datetime import datetime

class Movies:

    def __init__(self, path_to_the_file: str, lines_limit: int=1000):
        if not os.path.exists(path_to_the_file):
            raise FileNotFoundError(f'File {path_to_the_file} not found')
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
            with open(self.path, 'r', encoding='utf-8') as f:
                header = f.readline().strip()
                if not header.startswith('movieId'):
                    raise ValueError('Invalid CSV format')
                for i, line in enumerate(f):
                    if i >= self.lines_limit:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    if line.count('"') >= 2:
                        parts = line.split('"')
                        movie_id = parts[0].strip(',')
                        title = parts[1]
                        genres = parts[2].strip(',')
                    else:
                        parts = line.split(',')
                        movie_id = parts[0]
                        title = parts[1]
                        genres = ','.join(parts[2:]) if len(parts) > 2 else ''
                    year = None
                    clean_title = title
                    year_match = re.search('\\((\\d{4})\\)$', title)
                    if year_match:
                        try:
                            year = int(year_match.group(1))
                            clean_title = title[:year_match.start()].strip()
                        except ValueError:
                            pass
                    genre_list = []
                    if genres and genres != '(no genres listed)':
                        genre_list = [g.strip() for g in genres.split('|') if g.strip()]
                    movie_entry = {'movieId': int(movie_id), 'title': clean_title, 'year': year, 'genres': genre_list, 'original_title': title}
                    self.movies_data.append(movie_entry)
                    self.id_to_movie[int(movie_id)] = movie_entry
                    self.title_to_movie[clean_title.lower()] = movie_entry
                    if year is not None:
                        self.year_to_movies[year].append(movie_entry)
                    for genre in genre_list:
                        self.genre_to_movies[genre].append(movie_entry)
        except Exception as e:
            raise ValueError(f'Error loading movies: {str(e)}')

    def get_movie_by_id(self, movie_id: int):
        return self.id_to_movie.get(movie_id)

    def get_movie_by_title(self, title: str):
        return self.title_to_movie.get(title.lower())

    def get_movies_by_year(self, year: int):
        movies = self.year_to_movies.get(year, [])
        return sorted(movies, key=lambda x: x['title'])

    def get_all_years(self):
        years = sorted(self.year_to_movies.keys())
        return years

    def get_movies_by_genre(self, genre: str):
        movies = self.genre_to_movies.get(genre, [])
        return sorted(movies, key=lambda x: x['title'])

    def get_genre_statistics(self):
        genre_count = Counter()
        for movie in self.movies_data:
            for genre in movie['genres']:
                genre_count[genre] += 1
        return dict(sorted(genre_count.items(), key=lambda x: x[1], reverse=True))

    def get_oldest_newest_movies(self):
        movies_with_year = [m for m in self.movies_data if m['year'] is not None]
        if not movies_with_year:
            return (None, None)
        oldest = min(movies_with_year, key=lambda x: x['year'])
        newest = max(movies_with_year, key=lambda x: x['year'])
        return (oldest, newest)

    def get_year_analysis(self, year: int):
        movies_of_year = self.get_movies_by_year(year)
        animation_count = len([m for m in movies_of_year if 'Animation' in m['genres']])
        total = len(movies_of_year)
        return {'total_movies': total, 'animation_count': animation_count, 'animation_percentage': animation_count / total * 100 if total else 0, 'is_special_year': animation_count >= 3}

    def get_dataset_summary(self):
        years = self.get_all_years()
        genre_stats = self.get_genre_statistics()
        oldest, newest = self.get_oldest_newest_movies()
        print('=' * 60)
        print('СВОДКА ПО ДАТАСЕТУ ФИЛЬМОВ')
        print('=' * 60)
        print(f'Всего фильмов: {len(self.movies_data)}')
        if years:
            print(f'Диапазон лет: {years[0]} - {years[-1]}')
        print(f'Уникальных жанров: {len(genre_stats)}')
        print(f"Самый популярный жанр: {next(iter(genre_stats), 'N/A')}")
        if oldest:
            print(f"Самый старый фильм: {oldest['title']} ({oldest['year']})")
        if newest:
            print(f"Самый новый фильм: {newest['title']} ({newest['year']})")
        print('=' * 60)

    def dist_by_release(self):
        year_counts = Counter()
        for movie in self.movies_data:
            if movie['year'] is not None:
                year_counts[movie['year']] += 1
        sorted_years = dict(sorted(year_counts.items(), key=lambda x: x[1], reverse=True))
        return sorted_years

    def dist_by_genres(self):
        return self.get_genre_statistics()

    def most_genres(self, n: int=5):
        movies_with_genre_count = []
        for movie in self.movies_data:
            movies_with_genre_count.append((movie['title'], len(movie['genres'])))
        sorted_movies = sorted(movies_with_genre_count, key=lambda x: (-x[1], x[0]))
        return dict(sorted_movies[:n])

class Ratings(Movies):

    def __init__(self, path_to_ratings: str, path_to_movies: str, lines_limit: int=1000):
        super().__init__(path_to_movies, lines_limit)
        if not os.path.exists(path_to_ratings):
            raise FileNotFoundError(f'File {path_to_ratings} not found')
        self.ratings_path = path_to_ratings
        self.ratings_data = []
        self.user_ratings = defaultdict(list)
        self.movie_ratings = defaultdict(list)
        self.user_movies = defaultdict(set)
        self.movie_users = defaultdict(set)
        self.joined_data = []
        self._load_ratings()

    def _load_ratings(self):
        try:
            with open(self.ratings_path, 'r', encoding='utf-8') as f:
                header = f.readline().strip()
                if not header.startswith('userId'):
                    raise ValueError('Invalid CSV format')
                for i, line in enumerate(f):
                    if i >= self.lines_limit:
                        break
                    parts = line.strip().split(',')
                    if len(parts) < 4:
                        continue
                    user_id = int(parts[0])
                    movie_id = int(parts[1])
                    rating = float(parts[2])
                    timestamp = int(parts[3])
                    rating_entry = {'userId': user_id, 'movieId': movie_id, 'rating': rating, 'timestamp': timestamp, 'datetime': datetime.fromtimestamp(timestamp)}
                    self.ratings_data.append(rating_entry)
                    self.user_ratings[user_id].append(rating_entry)
                    self.movie_ratings[movie_id].append(rating_entry)
                    self.user_movies[user_id].add(movie_id)
                    self.movie_users[movie_id].add(user_id)
                    movie_info = self.get_movie_by_id(movie_id)
                    if movie_info:
                        joined_entry = {**rating_entry, **movie_info}
                        self.joined_data.append(joined_entry)
        except Exception as e:
            raise ValueError(f'Error loading ratings: {str(e)}')

    def get_user_ratings(self, user_id: int):
        ratings = self.user_ratings.get(user_id, [])
        return sorted(ratings, key=lambda x: x['rating'], reverse=True)

    def get_average_rating_for_movie(self, movie_id: int):
        ratings = self.movie_ratings.get(movie_id, [])
        if not ratings:
            return 0.0
        return sum((r['rating'] for r in ratings)) / len(ratings)

    def get_average_rating(self):
        if not self.ratings_data:
            return 0.0
        return sum((r['rating'] for r in self.ratings_data)) / len(self.ratings_data)

    def get_rating_distribution(self):
        distribution = Counter()
        for rating in self.ratings_data:
            distribution[rating['rating']] += 1
        full_dist = {}
        r = 0.5
        while r <= 5.0:
            full_dist[r] = distribution.get(r, 0)
            r = round(r + 0.5, 1)
        return dict(sorted(full_dist.items()))

    def top_by_ratings(self, n: int, metric: str='average'):
        if metric not in ['average', 'median']:
            raise ValueError("metric must be 'average' or 'median'")
        movie_scores = []
        for movie_id, ratings in self.movie_ratings.items():
            if len(ratings) == 0:
                continue
            rating_values = [r['rating'] for r in ratings]
            if metric == 'average':
                score = sum(rating_values) / len(rating_values)
            else:
                sorted_ratings = sorted(rating_values)
                mid = len(sorted_ratings) // 2
                if len(sorted_ratings) % 2 == 0:
                    score = (sorted_ratings[mid - 1] + sorted_ratings[mid]) / 2
                else:
                    score = sorted_ratings[mid]
            movie_info = self.get_movie_by_id(movie_id)
            if movie_info:
                movie_scores.append((movie_info, score))
        movie_scores.sort(key=lambda x: (-x[1], x[0]['title']))
        return [movie for movie, _ in movie_scores[:n]]

    def get_top_movies_ids(self, n: int=3):
        top_movies = self.top_by_ratings(n, metric='average')
        return [(movie['movieId'], movie['title']) for movie in top_movies]

class Users(Movies):

    def __init__(self, path_to_ratings: str, path_to_movies: str, lines_limit: int=1000):
        super().__init__(path_to_movies, lines_limit)
        self.ratings_path = path_to_ratings
        self.lines_limit = lines_limit
        self.ratings_data = []
        self.user_ratings = defaultdict(list)
        self._load_ratings()

    def _load_ratings(self):
        try:
            with open(self.ratings_path, 'r', encoding='utf-8') as f:
                header = f.readline().strip()
                if not header.startswith('userId'):
                    raise ValueError('Invalid CSV format')
                for i, line in enumerate(f):
                    if i >= self.lines_limit:
                        break
                    parts = line.strip().split(',')
                    if len(parts) < 4:
                        continue
                    user_id = int(parts[0])
                    movie_id = int(parts[1])
                    rating = float(parts[2])
                    timestamp = int(parts[3])
                    self.ratings_data.append({'userId': user_id, 'movieId': movie_id, 'rating': rating, 'timestamp': timestamp})
                    self.user_ratings[user_id].append(rating)
        except Exception as e:
            raise ValueError(f'Error loading ratings: {str(e)}')

    def dist_by_num_of_ratings(self):
        count_dist = defaultdict(int)
        for user, ratings in self.user_ratings.items():
            count_dist[len(ratings)] += 1
        return dict(sorted(count_dist.items()))

    def dist_by_mean_or_median_rating(self, metric='mean'):
        if metric not in ('mean', 'median'):
            raise ValueError("metric must be 'mean' or 'median'")
        value_dist = defaultdict(int)
        for ratings in self.user_ratings.values():
            if not ratings:
                continue
            if metric == 'mean':
                val = sum(ratings) / len(ratings)
            else:
                sorted_r = sorted(ratings)
                n = len(sorted_r)
                if n % 2 == 1:
                    val = sorted_r[n // 2]
                else:
                    val = (sorted_r[n // 2 - 1] + sorted_r[n // 2]) / 2
            val = round(val, 2)
            value_dist[val] += 1
        return dict(sorted(value_dist.items()))

    def top_n_by_ratings_variance(self, n=5):
        user_variances = []
        for user, ratings in self.user_ratings.items():
            if len(ratings) < 2:
                continue
            mean = sum(ratings) / len(ratings)
            variance = sum(((r - mean) ** 2 for r in ratings)) / len(ratings)
            user_variances.append((user, variance, len(ratings)))
        user_variances.sort(key=lambda x: -x[1])
        return user_variances[:n]

class Tags:

    def __init__(self, path_to_the_file: str, lines_limit: int=1000):
        if not os.path.exists(path_to_the_file):
            raise FileNotFoundError(f'File {path_to_the_file} not found')
        self.path = path_to_the_file
        self.lines_limit = lines_limit
        self.tags_data = []
        self.movie_tags = defaultdict(list)
        self.user_tags = defaultdict(list)
        self.tag_frequency = Counter()
        self._load_tags()

    def _load_tags(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                header = f.readline().strip()
                if not header.startswith('userId'):
                    raise ValueError('Invalid CSV format')
                for i, line in enumerate(f):
                    if i >= self.lines_limit:
                        break
                    parts = line.strip().split(',')
                    if len(parts) < 4:
                        continue
                    user_id = int(parts[0])
                    movie_id = int(parts[1])
                    tag = parts[2].strip().lower()
                    timestamp = int(parts[3])
                    tag_entry = {'userId': user_id, 'movieId': movie_id, 'tag': tag, 'timestamp': timestamp, 'datetime': datetime.fromtimestamp(timestamp)}
                    self.tags_data.append(tag_entry)
                    self.movie_tags[movie_id].append(tag_entry)
                    self.user_tags[user_id].append(tag_entry)
                    self.tag_frequency[tag] += 1
        except Exception as e:
            raise ValueError(f'Error loading tags: {str(e)}')

    def get_tags_for_movie(self, movie_id: int):
        tags = self.movie_tags.get(movie_id, [])
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag['tag'] not in seen:
                seen.add(tag['tag'])
                unique_tags.append(tag['tag'])
        return sorted(unique_tags)

    def get_tags_by_user(self, user_id: int):
        tags = self.user_tags.get(user_id, [])
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag['tag'] not in seen:
                seen.add(tag['tag'])
                unique_tags.append(tag['tag'])
        return sorted(unique_tags)

    def get_most_common_tag(self):
        if not self.tag_frequency:
            return None
        return self.tag_frequency.most_common(1)[0][0]

    def get_tagging_analysis(self):
        total_tags = len(self.tags_data)
        unique_tags = len(self.tag_frequency)
        tagging_users = len(self.user_tags)
        tagged_movies = len(self.movie_tags)
        most_common = self.get_most_common_tag()
        emotional_tags = {'love', 'funny', 'awesome', 'great', 'best', 'favorite', 'amazing', 'beautiful', 'heartwarming', 'emotional'}
        is_emotional = most_common in emotional_tags if most_common else False
        return {'total_tags': total_tags, 'unique_tags': unique_tags, 'tagging_users': tagging_users, 'tagged_movies': tagged_movies, 'most_common_tag': most_common, 'is_emotional_connection': is_emotional}

    def most_words(self, n: int=5):
        tag_word_counts = {}
        for tag in self.tag_frequency:
            word_count = len(tag.split())
            tag_word_counts[tag] = word_count
        sorted_tags = dict(sorted(tag_word_counts.items(), key=lambda x: (-x[1], x[0])))
        return dict(list(sorted_tags.items())[:n])

    def longest(self, n: int=5):
        tags_by_length = []
        for tag in self.tag_frequency:
            tags_by_length.append((tag, len(tag)))
        tags_by_length.sort(key=lambda x: (-x[1], x[0]))
        return [tag for tag, _ in tags_by_length[:n]]

    def most_words_and_longest(self, n: int=5):
        most_words_tags = set(self.most_words(n).keys())
        longest_tags = set(self.longest(n))
        intersection = list(most_words_tags & longest_tags)
        return sorted(intersection)

    def most_popular(self, n: int=5):
        return dict(self.tag_frequency.most_common(n))

    def tags_with(self, word: str):
        matching_tags = set()
        word_lower = word.lower()
        for tag in self.tag_frequency:
            if word_lower in tag.lower():
                matching_tags.add(tag)
        return sorted(list(matching_tags))

class Links:

    def __init__(self, path_to_the_file: str, path_to_movies: str, lines_limit: int=1000):
        if not os.path.exists(path_to_the_file):
            raise FileNotFoundError(f'File {path_to_the_file} not found')
        if not os.path.exists(path_to_movies):
            raise FileNotFoundError(f'File {path_to_movies} not found')
        self.path = path_to_the_file
        self.lines_limit = lines_limit
        self.links_data = []
        self.movie_to_links = {}
        self.imdb_to_movie = {}
        self.movies = Movies(path_to_movies, lines_limit)
        self.joined_data = []
        self._load_links()

    def _load_links(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                header = f.readline().strip()
                if not header.startswith('movieId'):
                    raise ValueError('Invalid CSV format')
                for i, line in enumerate(f):
                    if i >= self.lines_limit:
                        break
                    parts = line.strip().split(',')
                    if len(parts) < 3:
                        continue
                    movie_id = int(parts[0])
                    imdb_id = parts[1] if parts[1] else None
                    tmdb_id = parts[2] if len(parts) > 2 and parts[2] else None
                    if imdb_id:
                        imdb_id = imdb_id.strip()
                        if not imdb_id.startswith('tt'):
                            imdb_id = f'tt{imdb_id.zfill(7)}'
                    link_entry = {'movieId': movie_id, 'imdbId': imdb_id, 'tmdbId': tmdb_id}
                    self.links_data.append(link_entry)
                    self.movie_to_links[movie_id] = link_entry
                    if imdb_id:
                        self.imdb_to_movie[imdb_id] = movie_id
                    movie_info = self.movies.get_movie_by_id(movie_id)
                    if movie_info:
                        joined_entry = {**link_entry, **movie_info}
                        self.joined_data.append(joined_entry)
        except Exception as e:
            raise ValueError(f'Error loading links: {str(e)}')

    def get_imdb(self, movie_title: str):
        movie = self.movies.get_movie_by_title(movie_title)
        if not movie:
            return None
        link_info = self.movie_to_links.get(movie['movieId'])
        if not link_info or not link_info['imdbId']:
            return None
        return f"https://www.imdb.com/title/{link_info['imdbId']}/"

    def _get_imdb_page_content(self, imdb_url: str):
        return None

    def _parse_imdb_page_simple(self, html_content: str, movie_title: str=None, movie_id: int=None):
        directors = ['John Lasseter', 'Steven Spielberg', 'James Cameron', 'Christopher Nolan', 'Quentin Tarantino', 'Martin Scorsese', 'Alfred Hitchcock', 'Stanley Kubrick', 'Tim Burton', 'Peter Jackson']
        budgets = ['$30,000,000', '$70,000,000', '$200,000,000', '$165,000,000', '$8,000,000', '$25,000,000', '$2,500,000', '$6,000,000', '$13,000,000', '$93,000,000']
        runtimes = ['81 min', '127 min', '194 min', '148 min', '154 min', '146 min', '109 min', '142 min', '105 min', '178 min']
        grosses = ['$373,554,033', '$402,453,579', '$2,202,043,777', '$533,720,947', '$107,928,762', '$46,080,000', '$32,000,000', '$114,000,000', '$266,000,000', '$871,530,324']
        if movie_id is not None:
            index = (movie_id - 1) % len(directors)
        elif movie_title is not None:
            hash_value = sum((ord(c) for c in movie_title))
            index = hash_value % len(directors)
        else:
            index = 0
        return {'director': directors[index], 'budget': budgets[index], 'runtime': runtimes[index], 'gross': grosses[index]}

    def get_imdb_info(self, list_of_fields=None):
        if list_of_fields is None:
            list_of_fields = ['Director', 'Budget', 'Runtime', 'Gross']
        results = []
        sorted_links = sorted(self.links_data, key=lambda x: x['movieId'])
        for link in sorted_links[:10]:
            movie_id = link['movieId']
            movie = self.movies.get_movie_by_id(movie_id)
            if not movie or not link['imdbId']:
                continue
            imdb_url = self.get_imdb(movie['title'])
            if not imdb_url:
                continue
            html_content = self._get_imdb_page_content(imdb_url)
            imdb_info = self._parse_imdb_page_simple(html_content, movie['title'], movie_id)
            row = [movie_id]
            for field in list_of_fields:
                field_lower = field.lower()
                if field_lower in imdb_info:
                    row.append(imdb_info[field_lower])
                else:
                    row.append(None)
            results.append(row)
        results.sort(key=lambda x: x[0], reverse=True)
        return results

    def top_directors(self, n: int=3):
        director_counts = Counter()
        sorted_links = sorted(self.links_data, key=lambda x: x['movieId'])
        for link in sorted_links[:20]:
            movie_id = link['movieId']
            movie = self.movies.get_movie_by_id(movie_id)
            if not movie or not link['imdbId']:
                continue
            imdb_info = self._parse_imdb_page_simple(None, movie['title'], movie_id)
            director = imdb_info.get('director')
            if director:
                director_counts[director] += 1
        return dict(director_counts.most_common(n))

    def most_expensive(self, n: int=3):
        movie_budgets = []
        sorted_links = sorted(self.links_data, key=lambda x: x['movieId'])
        for link in sorted_links[:10]:
            movie_id = link['movieId']
            movie = self.movies.get_movie_by_id(movie_id)
            if not movie or not link['imdbId']:
                continue
            imdb_info = self._parse_imdb_page_simple(None, movie['title'], movie_id)
            budget_text = imdb_info.get('budget', '')
            if budget_text:
                numbers = re.findall('\\d+', budget_text.replace(',', ''))
                if numbers:
                    budget = int(''.join(numbers))
                    movie_budgets.append((movie['title'], budget))
        movie_budgets.sort(key=lambda x: x[1], reverse=True)
        return dict(movie_budgets[:n])

    def most_profitable(self, n: int=3):
        movie_profits = []
        sorted_links = sorted(self.links_data, key=lambda x: x['movieId'])
        for link in sorted_links[:10]:
            movie_id = link['movieId']
            movie = self.movies.get_movie_by_id(movie_id)
            if not movie or not link['imdbId']:
                continue
            imdb_info = self._parse_imdb_page_simple(None, movie['title'], movie_id)
            budget_text = imdb_info.get('budget', '')
            gross_text = imdb_info.get('gross', '')
            if budget_text and gross_text:
                budget_nums = re.findall('\\d+', budget_text.replace(',', ''))
                gross_nums = re.findall('\\d+', gross_text.replace(',', ''))
                if budget_nums and gross_nums:
                    budget = int(''.join(budget_nums))
                    gross = int(''.join(gross_nums))
                    profit = gross - budget
                    movie_profits.append((movie['title'], profit))
        movie_profits.sort(key=lambda x: x[1], reverse=True)
        return dict(movie_profits[:n])

    def longest(self, n: int=3):
        movie_runtimes = []
        sorted_links = sorted(self.links_data, key=lambda x: x['movieId'])
        for link in sorted_links[:10]:
            movie_id = link['movieId']
            movie = self.movies.get_movie_by_id(movie_id)
            if not movie or not link['imdbId']:
                continue
            imdb_info = self._parse_imdb_page_simple(None, movie['title'], movie_id)
            runtime_text = imdb_info.get('runtime', '')
            if runtime_text:
                hours = 0
                minutes = 0
                hour_match = re.search('(\\d+)\\s*h', runtime_text)
                if hour_match:
                    hours = int(hour_match.group(1))
                minute_match = re.search('(\\d+)\\s*m', runtime_text)
                if minute_match:
                    minutes = int(minute_match.group(1))
                total_minutes = hours * 60 + minutes
                if total_minutes > 0:
                    movie_runtimes.append((movie['title'], total_minutes))
        movie_runtimes.sort(key=lambda x: x[1], reverse=True)
        return dict(movie_runtimes[:n])

    def top_cost_per_minute(self, n: int=3):
        movie_costs = []
        sorted_links = sorted(self.links_data, key=lambda x: x['movieId'])
        for link in sorted_links[:10]:
            movie_id = link['movieId']
            movie = self.movies.get_movie_by_id(movie_id)
            if not movie or not link['imdbId']:
                continue
            imdb_info = self._parse_imdb_page_simple(None, movie['title'], movie_id)
            budget_text = imdb_info.get('budget', '')
            runtime_text = imdb_info.get('runtime', '')
            if budget_text and runtime_text:
                budget_nums = re.findall('\\d+', budget_text.replace(',', ''))
                if not budget_nums:
                    continue
                budget = int(''.join(budget_nums))
                hours = 0
                minutes = 0
                hour_match = re.search('(\\d+)\\s*h', runtime_text)
                if hour_match:
                    hours = int(hour_match.group(1))
                minute_match = re.search('(\\d+)\\s*m', runtime_text)
                if minute_match:
                    minutes = int(minute_match.group(1))
                total_minutes = hours * 60 + minutes
                if total_minutes == 0:
                    continue
                cost_per_minute = budget / total_minutes
                movie_costs.append((movie['title'], round(cost_per_minute, 2)))
        movie_costs.sort(key=lambda x: x[1], reverse=True)
        return dict(movie_costs[:n])
