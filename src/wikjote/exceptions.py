class WrongHTTPResponseCode(Exception):
    def __init__(self, response_code, expected, url):
        self.response_code = response_code
        self.expected = expected
        self.url = url
        super().__init__(
            f"Wrong HTTP response code, expected {self.expected} but {self.response_code} obtained from {self.url}."
        )


class XMLNotFound(Exception):
    def __init__(self, query):
        self.query = query
        super().__init__(f"The query {self.query} found nothing.")
