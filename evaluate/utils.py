import pickle

def save_data(data, path):
    """
    Saves data as a byte stream.
    :param data: Data to save
    :param path: Path to save
    """
    with open(path, 'wb') as fp: # Pickling
        pickle.dump(data, fp)


def load_data(path:str):
    """
    Loads data saved as a byte stream.
    :param path: Path to the data
    """
    with open(path, 'rb') as fp: # Unpickling
        b = pickle.load(fp)
        return b
