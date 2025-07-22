from src.analytics import charts


def test_create_returns_tear_sheet():
    e = charts.engine()
    x = e.get_combined_chart(['stk_us_cvna', 'stk_us_twlo'], upload_to_aws = True)
    assert x['signed_url'] is not None        
    assert x['data'] is not None        

