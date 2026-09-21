import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / 'src'
DATA_DIR = SRC_DIR / 'tables'

sys.path.insert(0, str(SRC_DIR))

from movielens_analysis import Movies, Ratings, Tags, Links, Users

class Tests:
    MOVIES_PATH = str(DATA_DIR / 'movies.csv')
    RATINGS_PATH = str(DATA_DIR / 'ratings.csv')
    TAGS_PATH = str(DATA_DIR / 'tags.csv')
    LINKS_PATH = str(DATA_DIR / 'links.csv')

    @classmethod
    def setup_class(cls):
        missing = []
        for path in [cls.MOVIES_PATH, cls.RATINGS_PATH, cls.TAGS_PATH, cls.LINKS_PATH]:
            if not os.path.exists(path):
                missing.append(path)
        if missing:
            pytest.skip(f'Missing files: {missing}')

    def test_movies_initialization(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        assert isinstance(movies.movies_data, list)
        assert len(movies.movies_data) > 0
        assert all((key in movies.movies_data[0] for key in ['movieId', 'title', 'year', 'genres']))

    def test_movies_get_movie_by_id(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        movie = movies.get_movie_by_id(1)
        assert movie is not None
        assert isinstance(movie['movieId'], int)
        assert isinstance(movie['title'], str)

    def test_movies_get_movie_by_title(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        movie = movies.get_movie_by_title('Toy Story')
        assert movie is not None
        assert isinstance(movie['title'], str)

    def test_movies_get_movies_by_year(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        movies_1995 = movies.get_movies_by_year(1995)
        assert isinstance(movies_1995, list)
        if movies_1995:
            assert all((m['year'] == 1995 for m in movies_1995))
            titles = [m['title'] for m in movies_1995]
            assert titles == sorted(titles)

    def test_movies_get_all_years(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        years = movies.get_all_years()
        assert isinstance(years, list)
        assert years == sorted(years)

    def test_movies_get_movies_by_genre(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        drama_movies = movies.get_movies_by_genre('Drama')
        assert isinstance(drama_movies, list)
        if drama_movies:
            assert all(('Drama' in m['genres'] for m in drama_movies))

    def test_movies_get_genre_statistics(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        stats = movies.get_genre_statistics()
        assert isinstance(stats, dict)
        counts = list(stats.values())
        assert counts == sorted(counts, reverse=True)

    def test_movies_get_oldest_newest_movies(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        oldest, newest = movies.get_oldest_newest_movies()
        if oldest:
            assert isinstance(oldest['title'], str)
            assert isinstance(oldest['year'], int)
        if newest:
            assert isinstance(newest['title'], str)
            assert isinstance(newest['year'], int)

    def test_movies_get_year_analysis(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        years = movies.get_all_years()
        if years:
            analysis = movies.get_year_analysis(years[0])
            assert isinstance(analysis, dict)
            assert 'total_movies' in analysis

    def test_movies_dist_by_release(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        dist = movies.dist_by_release()
        assert isinstance(dist, dict)
        counts = list(dist.values())
        assert counts == sorted(counts, reverse=True)

    def test_movies_dist_by_genres(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        dist = movies.dist_by_genres()
        assert isinstance(dist, dict)
        counts = list(dist.values())
        assert counts == sorted(counts, reverse=True)

    def test_movies_most_genres(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        top = movies.most_genres(3)
        assert isinstance(top, dict)
        assert len(top) <= 3

    def test_ratings_initialization(self):
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH, lines_limit=100)
        assert isinstance(ratings.ratings_data, list)
        assert isinstance(ratings.joined_data, list)
        assert len(ratings.ratings_data) == 100
        assert len(ratings.joined_data) == len(ratings.ratings_data)

    def test_ratings_inheritance(self):
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH, lines_limit=100)
        assert isinstance(ratings, Movies)

    def test_ratings_get_user_ratings(self):
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH, lines_limit=100)
        if ratings.user_ratings:
            user_id = list(ratings.user_ratings.keys())[0]
            user_ratings = ratings.get_user_ratings(user_id)
            assert isinstance(user_ratings, list)
            if len(user_ratings) > 1:
                ratings_values = [r['rating'] for r in user_ratings]
                assert ratings_values == sorted(ratings_values, reverse=True)

    def test_ratings_get_average_rating_for_movie(self):
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH, lines_limit=100)
        if ratings.movie_ratings:
            movie_id = list(ratings.movie_ratings.keys())[0]
            avg = ratings.get_average_rating_for_movie(movie_id)
            assert isinstance(avg, float)
            assert 0.0 <= avg <= 5.0

    def test_ratings_get_average_rating(self):
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH, lines_limit=100)
        avg = ratings.get_average_rating()
        assert isinstance(avg, float)

    def test_ratings_get_rating_distribution(self):
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH, lines_limit=100)
        dist = ratings.get_rating_distribution()
        assert isinstance(dist, dict)
        expected_keys = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        assert all((k in dist for k in expected_keys))
        assert list(dist.keys()) == sorted(dist.keys())

    def test_ratings_top_by_ratings_average(self):
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH, lines_limit=100)
        top = ratings.top_by_ratings(3, metric='average')
        assert isinstance(top, list)
        assert len(top) <= 3

    def test_ratings_top_by_ratings_median(self):
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH, lines_limit=100)
        top = ratings.top_by_ratings(3, metric='median')
        assert isinstance(top, list)
        assert len(top) <= 3

    def test_ratings_get_top_movies_ids(self):
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH, lines_limit=100)
        top_ids = ratings.get_top_movies_ids(3)
        assert isinstance(top_ids, list)
        if top_ids:
            assert isinstance(top_ids[0], tuple)
            assert len(top_ids[0]) == 2

    def test_tags_initialization(self):
        tags = Tags(self.TAGS_PATH, lines_limit=100)
        assert isinstance(tags.tags_data, list)
        if tags.tags_data:
            assert 'tag' in tags.tags_data[0]

    def test_tags_get_tags_for_movie(self):
        tags = Tags(self.TAGS_PATH, lines_limit=100)
        if tags.movie_tags:
            movie_id = list(tags.movie_tags.keys())[0]
            movie_tags = tags.get_tags_for_movie(movie_id)
            assert isinstance(movie_tags, list)
            assert all((isinstance(tag, str) for tag in movie_tags))
            if len(movie_tags) > 1:
                assert movie_tags == sorted(movie_tags)

    def test_tags_get_tags_by_user(self):
        tags = Tags(self.TAGS_PATH, lines_limit=100)
        if tags.user_tags:
            user_id = list(tags.user_tags.keys())[0]
            user_tags = tags.get_tags_by_user(user_id)
            assert isinstance(user_tags, list)
            assert all((isinstance(tag, str) for tag in user_tags))
            if len(user_tags) > 1:
                assert user_tags == sorted(user_tags)

    def test_tags_get_most_common_tag(self):
        tags = Tags(self.TAGS_PATH, lines_limit=100)
        most_common = tags.get_most_common_tag()
        assert most_common is None or isinstance(most_common, str)

    def test_tags_get_tagging_analysis(self):
        tags = Tags(self.TAGS_PATH, lines_limit=100)
        analysis = tags.get_tagging_analysis()
        assert isinstance(analysis, dict)
        assert 'total_tags' in analysis

    def test_tags_most_words(self):
        tags = Tags(self.TAGS_PATH, lines_limit=100)
        result = tags.most_words(3)
        assert isinstance(result, dict)

    def test_tags_longest(self):
        tags = Tags(self.TAGS_PATH, lines_limit=100)
        result = tags.longest(3)
        assert isinstance(result, list)
        assert all((isinstance(tag, str) for tag in result))

    def test_tags_most_words_and_longest(self):
        tags = Tags(self.TAGS_PATH, lines_limit=100)
        result = tags.most_words_and_longest(3)
        assert isinstance(result, list)

    def test_tags_most_popular(self):
        tags = Tags(self.TAGS_PATH, lines_limit=100)
        popular = tags.most_popular(3)
        assert isinstance(popular, dict)
        counts = list(popular.values())
        assert counts == sorted(counts, reverse=True)

    def test_tags_tags_with(self):
        tags = Tags(self.TAGS_PATH, lines_limit=100)
        result = tags.tags_with('action')
        assert isinstance(result, list)
        assert all((isinstance(tag, str) for tag in result))

    def test_links_initialization(self):
        links = Links(self.LINKS_PATH, self.MOVIES_PATH, lines_limit=100)
        assert isinstance(links.links_data, list)
        assert isinstance(links.joined_data, list)

    def test_links_get_imdb(self):
        links = Links(self.LINKS_PATH, self.MOVIES_PATH, lines_limit=50)
        imdb_url = links.get_imdb('Toy Story')
        assert imdb_url == 'https://www.imdb.com/title/tt0114709/'

    def test_links_get_external_ids(self):
        links = Links(self.LINKS_PATH, self.MOVIES_PATH, lines_limit=50)
        assert links.get_external_ids('Toy Story') == {
            'imdbId': 'tt0114709',
            'tmdbId': '862',
        }
        assert links.get_external_ids('Unknown movie') is None

    def test_full_dataset_is_loaded_by_default(self):
        movies = Movies(self.MOVIES_PATH)
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH)
        tags = Tags(self.TAGS_PATH)
        links = Links(self.LINKS_PATH, self.MOVIES_PATH)

        assert len(movies.movies_data) == 9742
        assert len(ratings.ratings_data) == 100836
        assert len(ratings.joined_data) == 100836
        assert len(tags.tags_data) == 3683
        assert len(links.links_data) == 9742
        assert len(links.joined_data) == 9742

    def test_known_dataset_values(self):
        movies = Movies(self.MOVIES_PATH)
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH)
        tags = Tags(self.TAGS_PATH)

        assert next(iter(movies.get_genre_statistics().items())) == ('Drama', 4361)
        assert ratings.get_rating_distribution()[4.0] == 26818
        assert ratings.top_by_num_of_ratings(1) == {'Forrest Gump': 329}
        assert tags.get_most_common_tag() == 'in netflix queue'

    def test_manual_calculation_movies(self):
        movies = Movies(self.MOVIES_PATH, lines_limit=100)
        manual_year_count = {}
        for movie in movies.movies_data:
            if movie['year'] is not None:
                manual_year_count[movie['year']] = manual_year_count.get(movie['year'], 0) + 1
        method_dist = movies.dist_by_release()
        if manual_year_count:
            test_year = list(manual_year_count.keys())[0]
            assert manual_year_count[test_year] == method_dist.get(test_year, 0)

    def test_manual_calculation_ratings(self):
        ratings = Ratings(self.RATINGS_PATH, self.MOVIES_PATH, lines_limit=100)
        if ratings.movie_ratings:
            test_movie_id = list(ratings.movie_ratings.keys())[0]
            manual_ratings = [r['rating'] for r in ratings.movie_ratings[test_movie_id]]
            manual_avg = sum(manual_ratings) / len(manual_ratings) if manual_ratings else 0
            method_avg = ratings.get_average_rating_for_movie(test_movie_id)
            assert abs(manual_avg - method_avg) < 0.01
    USERS_PATH = str(DATA_DIR / 'ratings.csv')
    MOVIES_PATH = str(DATA_DIR / 'movies.csv')

    def test_users_initialization(self):
        users = Users(self.USERS_PATH, self.MOVIES_PATH, lines_limit=100)
        assert isinstance(users.user_ratings, dict)
        assert isinstance(users.ratings_data, list)
        assert len(users.user_ratings) > 0

    def test_dist_by_num_of_ratings(self):
        users = Users(self.USERS_PATH, self.MOVIES_PATH, lines_limit=100)
        dist = users.dist_by_num_of_ratings()
        assert isinstance(dist, dict)
        for num, count in dist.items():
            assert isinstance(num, int)
            assert isinstance(count, int)
        assert sum(dist.values()) == len(users.user_ratings)

    def test_dist_by_mean_or_median_rating(self):
        users = Users(self.USERS_PATH, self.MOVIES_PATH, lines_limit=100)
        dist_mean = users.dist_by_mean_or_median_rating('mean')
        dist_median = users.dist_by_mean_or_median_rating('median')
        assert isinstance(dist_mean, dict)
        assert isinstance(dist_median, dict)
        for val, count in dist_mean.items():
            assert isinstance(val, float)
            assert isinstance(count, int)
        for val, count in dist_median.items():
            assert isinstance(val, float)
            assert isinstance(count, int)
        assert sum(dist_mean.values()) == len(users.user_ratings)
        assert sum(dist_median.values()) == len(users.user_ratings)

    def test_top_n_by_ratings_variance(self):
        users = Users(self.USERS_PATH, self.MOVIES_PATH, lines_limit=100)
        top = users.top_n_by_ratings_variance(n=5)
        assert isinstance(top, list)
        for item in top:
            assert isinstance(item, tuple)
            assert len(item) == 3
            user_id, variance, count = item
            assert isinstance(user_id, int)
            assert isinstance(variance, float)
            assert isinstance(count, int)
            assert count >= 2
        for i in range(len(top) - 1):
            assert top[i][1] >= top[i + 1][1]

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        Movies('non_existent.csv')

def test_invalid_csv_format():
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('invalid,header\n')
        f.write('1,2,3\n')
        temp_path = f.name
    try:
        with pytest.raises(ValueError):
            Movies(temp_path)
    finally:
        os.unlink(temp_path)
