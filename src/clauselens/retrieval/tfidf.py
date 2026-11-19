
from collections.abc import Mapping, Sequence  
# mapping gives key value pair , sequence provide sequential input .. 
# as we used it for input as parameter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from clauselens.schemas.clause import Clause_format


class TfidfRetriever:
    def __init__(
        self,
        leases: Mapping[str, Sequence[Clause_format]],
    ) -> None:

        self._texts = []
        self._rows = {}

        # Build one searchable text for every clause.
        for lease_id, clauses in leases.items():

            lease_rows = []

            for clause in clauses:
                text = f"{clause.title or ''} {clause.text}"

                row_index = len(self._texts)

                self._texts.append(text)
                lease_rows.append(row_index)

            self._rows[lease_id] = lease_rows

        # Fit one TF-IDF vectorizer across all leases.
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform(self._texts)

    def search(
        self,
        lease_id: str,
        query: str,
        k: int,
    ) -> list[int]:

        if lease_id not in self._rows:
            raise ValueError(f"Unknown lease_id: {lease_id}")

        if k < 1:
            raise ValueError(f"k must be at least 1, got {k}")

        # Convert the query into the same TF-IDF vocabulary.
        query_vector = self._vectorizer.transform([query])

        # Get only the rows belonging to the requested lease.
        lease_rows = self._rows[lease_id]
        lease_matrix = self._matrix[lease_rows]

        # Calculate similarity scores.
        scores = linear_kernel(query_vector, lease_matrix).flatten()

        # Rank clauses from highest score to lowest.
        ranked_positions = scores.argsort()[::-1][:k]

        # Return positions within this lease, not global matrix rows.
        return [int(position) for position in ranked_positions]
