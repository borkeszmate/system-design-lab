"""Unit tests for Product Service"""
import pytest
from unittest.mock import Mock
from app.core.services import ProductService
from app.core.exceptions import ProductNotFoundException
from app.domain.schemas import ProductCreate, ProductResponse


@pytest.fixture
def mock_repository():
    """Mock product repository"""
    return Mock()


@pytest.fixture
def product_service(mock_repository):
    """Product service with mocked repository"""
    return ProductService(mock_repository)


def test_get_all_products(product_service, mock_repository):
    """Test getting all products"""
    # Arrange
    mock_products = [Mock(id=1, name="Test Product", price=10.0, stock=5)]
    mock_repository.get_all.return_value = mock_products

    # Act
    result = product_service.get_all_products()

    # Assert
    assert len(result) == 1
    mock_repository.get_all.assert_called_once_with(0, 100)


def test_get_product_by_id_not_found(product_service, mock_repository):
    """Test getting product that doesn't exist"""
    # Arrange
    mock_repository.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ProductNotFoundException):
        product_service.get_product_by_id(999)
