import pickle
from typing import List, Union, Dict, Any, Union

def save_data(data:Any, path:str) -> None:
    """
    Saves data as a byte stream.
    :param data: Data to save
    :param path: Path to save
    """
    with open(path, 'wb') as fp: # Pickling
        pickle.dump(data, fp)


def load_data(path:str) -> Any:
    """
    Loads data saved as a byte stream.
    :param path: Path to the data
    """
    with open(path, 'rb') as fp: # Unpickling
        b = pickle.load(fp)
        return b
