#!/usr/bin/env python
import pytest
import os
from src.services.assets.futures import upload_assets
from src.services import mdb
from src.util import settings


class TestUploadAssetsIntegration:
    """
    Integration test for the upload_assets function in futures.py.
    This test does not mock any calls and tests the real integration.
    """
    
    def test_upload_assets_no_mocks(self):
        """
        Test upload_assets function without any mocks.
        Requires actual database and API connectivity.
        """
        # Skip if not in development environment or missing API key
        if not settings.constants.development:
            pytest.skip("Integration test requires development environment")
        
        if not os.environ.get('EODHISTORICALDATA_API_KEY'):
            pytest.skip("EODHISTORICALDATA_API_KEY required for integration test")
        
        # Execute the function
        upload_assets()
        
        # Verify the results by checking the database
        mdbe = mdb.engine()
        collection = mdbe.get_collection(settings.constants.FUTURE_ASSETS_COLLECTION)
        
        # Check that documents were inserted
        document_count = collection.count_documents({})
        assert document_count > 0, f"Expected documents to be inserted, but found {document_count}"
        
        # Verify document structure
        sample_document = collection.find_one({})
        
        # Check required fields exist
        required_fields = ['SravzId', 'APICode', 'Code', 'Country', 'Ticker']
        for field in required_fields:
            assert field in sample_document, f"Missing required field: {field}"
        
        # Verify SravzId format
        assert sample_document['SravzId'].startswith('fut_'), \
            f"SravzId should start with 'fut_', got: {sample_document['SravzId']}"
        
        # Verify Ticker equals Code
        assert sample_document['Ticker'] == sample_document['Code'], \
            f"Ticker should equal Code: {sample_document['Ticker']} != {sample_document['Code']}"
        
        # Verify APICode format
        assert '.' in sample_document['APICode'], \
            f"APICode should contain '.', got: {sample_document['APICode']}"
        
        print(f"✅ Integration test passed!")
        print(f"📊 Inserted {document_count} futures assets")
        print(f"📋 Sample document structure verified")
        print(f"🔍 Sample SravzId: {sample_document['SravzId']}")
        print(f"🔗 Sample APICode: {sample_document['APICode']}")

