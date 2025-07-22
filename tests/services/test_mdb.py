import unittest
from unittest.mock import Mock, patch
from src.services import mdb
from src.services.cache import Cache

class TestGetCollectionItems(unittest.TestCase):
    def setUp(self):
        # Initialize YourClass instance
        self.engine = mdb.engine()

    def test_get_collection_items(self):
        # Create mock collection
        mock_collection = Mock()
        mock_find_result = ['item1', 'item2']  # Mocked find result
        mock_collection.find.return_value = mock_find_result

        # Mock get_collection method to return the mock collection
        self.engine.get_collection = Mock(return_value=mock_collection)

        # Call the method with different parameters
        result = self.engine.get_collection_items('collection_name')

        # Assert that the method returns the correct result
        self.assertEqual(result, mock_find_result)
        mock_collection.find.assert_called_once()

    # # Add more test methods to cover other scenarios
    # def test_get_from_cache(self):
    #     # Create an instance of YourClass
    #     engine = mdb.engine()
    #     cache_instance = Cache.Instance()
    #     # Mock Cache.Instance().get method
    #     with patch.object(engine, 'get_env', return_value='test'):
    #         with patch.object(engine, 'database_name', 'your_database_name'):
    #             with patch.object(engine, 'db_type', 'your_db_type'):
    #                 with patch(cache_instance) as mock_cache_instance:
    #                     mock_cache_instance.return_value.get.return_value = 'cached_value'

    #                     # Call the method
    #                     result = engine.get_from_cache('collection_name')

    #                     # Check that Cache.Instance().get method is called with the correct arguments
    #                     mock_cache_instance.return_value.get.assert_called_once_with(
    #                         'collection_name_your_database_name_your_db_type_test'
    #                     )

    #     # Assert that the result is correct
    #     assert result == 'cached_value'

if __name__ == '__main__':
    unittest.main()
