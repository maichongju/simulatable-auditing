import argparse
import sympy
import abc


class PrivacyLeakException(Exception):
    pass


class Auditor(abc.ABC):
    def __init__(self, data: list) -> None:
        if not self._validate(data):
            raise ValueError("Invalid data")
        self._data = data
        self._variable_size = len(data)

    def _validate(self, data: list) -> bool:
        if not isinstance(data, list):
            return False
        if len(data) < 2:
            return False
        return True

    @abc.abstractmethod
    def execute_query(self, query: str) -> int:
        """
        Executes the given query and returns the result.

        Args:
            query (str): The query to be executed.

        Returns:
            int: The result of the query.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError("Method not implemented")

    @property
    def data(self) -> list:
        """
        Returns the dataset.

        Returns:
            list: The dataset.
        """
        return self._data


class SumAuditing(Auditor):
    def __init__(self, data: list) -> None:
        super().__init__(data)
        self._queries = []

    def execute_query(self, query: str) -> int:
        """
        Executes the given query and returns the result.

        Args:
            query (str): The query to be executed.

        Returns:
            int: The result of the query.

        Raises:
            PrivacyLeakException: If a privacy leak is detected.

        """
        query_list = self._convert_input_query(query)
        if self._check_privacy_leak(query_list):
            raise PrivacyLeakException("Privacy leak detected")
        self._queries.append(query_list)
        return sum([self._data[i] for i in range(self._variable_size) if query_list[i] == 1])
    
    def _convert_input_query(self, query: str) -> list:
        """
        Converts the input query string into a binary list representation.

        Args:
            query (str): The input query string containing comma-separated indices.

        Returns:
            list: A binary list representation of the query, where 1 indicates the presence of an index and 0 indicates its absence.
        """
        query_list = [0] * self._variable_size
        query = query.split(",")
        for i in query:
            i = int(i)
            if i < 1 or i > self._variable_size:
                raise ValueError("Invalid query")
            query_list[i-1] = 1
        return query_list

    def _check_privacy_leak(self, query: list) -> bool:
        """
        Checks if there is a privacy leak in the given query.

        Parameters:
        query (list): The query to be checked.

        Returns:
        bool: True if there is a privacy leak, False otherwise.
        """
        matrix = sympy.Matrix.vstack(sympy.Matrix(
            self._queries), sympy.Matrix([query]))
        reduced_matrix = matrix.rref()[0].tolist()
        for row in reduced_matrix:
            if sum(row) == 1:
                return True
        return False

    @property
    def queries(self) -> list:
        """
        Returns the list of queries executed so far.

        Returns:
            list: A list of queries executed so far. Represented as binary lists.
        """
        return list(self._queries)

    def __str__(self) -> str:
        return f'Dataset: {self._data}, Number of Query: {len(self._queries)}'


class MaxAuditing(Auditor):
    def __init__(self, data: list) -> None:
        super().__init__(data)
        # check if there is duplicate value
        if len(set(data)) != len(data):
            raise ValueError("Duplicate value detected")
        self._queries = []
        self._answers = []

    def _convert_input_query(self, query: str) -> list:
        query_list = []
        query = query.split(",")
        for i in query:
            i = int(i)
            if i < 1 or i > self._variable_size:
                raise ValueError("Invalid query")
            query_list.append(i)
        return query_list

    def execute_query(self, query: str) -> int:
        query_list = self._convert_input_query(query)
        
        if self._check_privacy_leak(query_list):
            raise PrivacyLeakException("Privacy leak detected")
        
        self._queries.append(query_list)
        answer = max([self._data[i-1] for i in query_list])
        self._answers.append(answer)
        return answer

    def _get_intersect_query(self, query: list) -> list:
        intersect_query = []
        for index, q in enumerate(self._queries):
            for x in query:
                if x in q:
                    intersect_query.append([q.copy(), self._answers[index]])
                    break
        return intersect_query

    def _check_privacy_leak(self, query: list) -> bool:
        
        # If there is no query so far
        if len(self._queries) == 0:
            # single element query will lead to privacy leak
            if len(query) == 1:
                return True
            else:
                return False
        
        # get intersect query and answers 
        intersect_query = self._get_intersect_query(query)
        intersect_query = sorted(intersect_query, key=lambda x: x[1])
        
        a_list = [intersect_query[0][1] - 1, intersect_query[0][1]]  # lower bound+
        for index, (_, answer) in enumerate(intersect_query[1:]):
            a_list.append((intersect_query[index][1] + answer) / 2) # (a_s + a_(s+1)) / 2
            a_list.append(answer) # a_(s+1)
        a_list.append(intersect_query[-1][1] + 1) # upper bound
        
        for at in a_list:
            extreme_elements = self._calculate_extreme_element(
                self._queries+[query], self._answers+[at])
            if self._check_is_consistent(extreme_elements) and self._check_value_identified(extreme_elements):
                return True
        return False

    def _check_is_consistent(self, extreme_elements) -> bool:
        """
        The query set is consistent if and only of every query set has at least one extreme element.
        """
        for q in extreme_elements:
            if len(q) == 0:
                return False
        return True

    def _check_value_identified(self, extreme_elements: list) -> bool:
        """
        A value is uniquely determined if and only if there exists a query set qk for which j is the only extreme element.
        """
        for q in extreme_elements:
            if len(q) == 1:
                return True
        return False

    def _calculate_extreme_element(self, queries: list, answers: list) -> list:
        if len(queries) != len(answers):
            raise ValueError("Queries and answers must be of the same length")
        upper_bound = [float('inf')] * self._variable_size
        # Store the index of the extreme element of the query
        extreme_element = [[] for _ in range(self._variable_size)]

        for index, (qi, ai) in enumerate(zip(queries, answers)):
            for xi in qi:
                # ak < uj, update uj
                if ai < upper_bound[xi-1]:  # xi-1 because xi starts from 1
                    upper_bound[xi-1] = ai
                    # index + 1 because index starts from 0
                    extreme_element[xi-1] = [index + 1]
                # ak = uj, append index
                elif ai == upper_bound[xi-1]:
                    extreme_element[xi-1].append(index + 1)

        # construct extreme element for each query
        extreme_element_query = [[] for _ in range(len(queries))]
        for index, xi in enumerate(extreme_element):
            for j in xi:
                extreme_element_query[j-1].append(index + 1)
        return extreme_element_query


def process_dataset(file) -> list:
    """
    Processes the dataset file and returns a list of the data.

    Args:
        filename (str): The name of the dataset file.

    Returns:
        list: A list of the data.
    """
    data = file.read().splitlines()
    data = [float(i) for i in data]
    return data


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Simulatable Auditing for sum and max queries')
    
    
    parser.add_argument('-s', '--sum', action='store_true', help='Use sum auditing')
    parser.add_argument('-m', '--max', action='store_true', help='Use max auditing')
    parser.add_argument('-d', '--data', type=float, nargs='*', help='Dataset')
    parser.add_argument('-f', '--file', type=argparse.FileType('r'), help='Dataset file')
    

    args = parser.parse_args()
    
    if (args.sum and args.max) or (not args.sum and not args.max):
        parser.error('Must use either sum or max auditing')
        
    if (args.data is None and args.file is None) or (args.data is not None and args.file is not None):
        parser.error('Must provide either dataset or dataset file')

    data = args.data
    
    if data is None:
        data = process_dataset(args.file)

    if args.sum:
        auditor = SumAuditing(data)
        print('SUM AUDITING')
    else:
        auditor = MaxAuditing(data)
        print('MAX AUDITING')
    
    print('Enter quit or q to quit')
    while True:
        query = input("Enter query (use a command separator): ")
        if query.lower() == 'q' or query.lower() == 'quit':
            break
        try:
            print(auditor.execute_query(query))
        except PrivacyLeakException:
            print("Denied")
        except ValueError:
            print("Invalid query")
        
