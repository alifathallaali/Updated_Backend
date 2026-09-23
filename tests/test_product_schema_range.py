from app.schemas import ProductRunFromDatasetVersionRequest
def test_product_17_is_valid_request():
 x=ProductRunFromDatasetVersionRequest(product_id="product-17",workspace_id=1,dataset_version_id=1)
 assert x.product_id=="product-17"
