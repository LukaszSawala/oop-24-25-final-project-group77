
import json
from typing import Tuple, List, Union
import os

from autoop.core.storage import Storage


class Database():
    """ The database class """
    def __init__(self, storage: Storage) -> None:
        """ Initialize the database """
        self._storage = storage
        self._data = {}
        self._load()

    def set(self, collection: str, id: str, entry: dict) -> dict:
        """Set a key in the database
        Args:
            collection (str): The collection to store the data in
            id (str): The id of the data
            entry (dict): The data to store
        Returns:
            dict: The data that was stored
        """
        assert isinstance(entry, dict), "Data must be a dictionary"
        assert isinstance(collection, str), "Collection must be a string"
        assert isinstance(id, str), "ID must be a string"
        if not self._data.get(collection, None):
            self._data[collection] = {}
        self._data[collection][id] = entry
        # the following _persist method also contains temporary fixes
        self._persist()
        return entry

    def get(self, collection: str, id: str) -> Union[dict, None]:
        """Get a key from the database
        Args:
            collection (str): The collection to get the data from
            id (str): The id of the data
        Returns:
            Union[dict, None]: The data that was stored, or None if
            it doesn't exist
        """
        if not self._data.get(collection, None):
            return None
        return self._data[collection].get(id, None)

    def delete(self, collection: str, id: str) -> None:
        """Delete a key from the database
        Args:
            collection (str): The collection to delete the data from
            id (str): The id of the data
        Returns:
            None
        """

        if not self._data.get(collection, None):
            print("Collection does not exist")
            return
        if self._data[collection].get(id, None):
            print("Deleted", id, "from", collection)
            del self._data[collection][id]
        self._persist(skip=True)  # works until here

    def list(self, collection: str) -> List[Tuple[str, dict]]:
        """Lists all data in a collection
        Args:
            collection (str): The collection to list the data from
        Returns:
            List[Tuple[str, dict]]: A list of tuples containing the id
            and data for each item in the collection
        """
        if not self._data.get(collection, None):
            return []
        return [(id, data) for id, data in self._data[collection].items()]

    def refresh(self) -> None:
        """Refresh the database by loading the data from storage"""
        self._load()

    def _persist(self, skip: bool = False) -> None:
        """
        Persist the data to storage
        Added the skip boolean to avoid removal errors.
        Again, a TA should note that this is a temporary fix, and
        we are the group to develop the solution to the Windows problem,
        hence it is a bit spaghetti.
        """
        for collection, data in self._data.items():
            if not data or skip:   # fix nr 1 here
                continue
            for id, item in data.items():
                # remove the equal signs from the id
                id = id.replace("=", "")
                self._storage.save(json.dumps(item).encode(),
                                   f"{collection}{os.sep}{id}")

        # for things that were deleted, we need to remove them from the storage
        keys = self._storage.list("")
        for key in keys:
            collection, id = key.split(os.sep)[-2:]
            # Check if `collection` exists in `_data` and if `id` is in that
            # collection's dictionary
            if collection in self._data and id in self._data[collection]:
                continue
            else:
                # If not found, delete it from storage
                self._storage.delete(f"{collection}{os.sep}{id}")
                print(f"Succesfuly removed {collection}{os.sep}{id}")

    def _load(self) -> None:
        """Load the data from storage"""
        self._data = {}
        for key in self._storage.list(""):
            collection, id = key.split(os.sep)[-2:]
            data = self._storage.load(f"{collection}{os.sep}{id}")
            # Ensure the collection exists in the dictionary
            if collection not in self._data:
                self._data[collection] = {}
            self._data[collection][id] = json.loads(data.decode())
