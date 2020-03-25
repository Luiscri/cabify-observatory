# Sustainable Mobility Observatory Tests

To run the tests, it is necessary to install the **pytest** packages and upgrade to the latest PyYAML version. 

```bash
pip install -U PyYAML
pip install pytest
```

*test_scrapper* requires a [Google News API Key](https://newsapi.org/s/google-news-api) defined as an environment variable which should be named "*NEWS_API_KEY*".

To run all tests:

```bash
pytest
```

To run a specific test:

```bash
pytest test_ANYTEST.py
```

where ANYTEST is the name of any available test in this folder.
