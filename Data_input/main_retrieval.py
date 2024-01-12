from Data_retrieval import data_retrieval

data_retr = data_retrieval()


unique_types = data_retr.return_unique()

batterij = data_retr.batterij()
print(batterij)