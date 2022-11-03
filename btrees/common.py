import os
project_name = 'random_walk'
root = os.path.dirname(os.path.abspath(__file__))
root = root[0:root.find(project_name)] + project_name
CSV_FILENAME = 'sampling_tests.csv'
SAMPLING_TESTS_CSV = root + "/" + CSV_FILENAME
