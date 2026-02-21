"""Unit tests for ProductService — mocked DAO ports, no DB."""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from products.domain.exceptions import InvalidFilterError, ProductNotFoundError
from products.domain.models import Brand, Category, PriceTier, Product
from products.domain.ports import BrandDAO, CategoryDAO, ProductDAO
from products.domain.services import ProductService


@pytest.fixture()
def mock_daos() -> dict[str, MagicMock]:
    """Return mocked DAO implementations."""
    return {
        "product_dao": MagicMock(spec=ProductDAO),
        "brand_dao": MagicMock(spec=BrandDAO),
        "category_dao": MagicMock(spec=CategoryDAO),
    }


@pytest.fixture()
def service(mock_daos: dict[str, MagicMock]) -> ProductService:
    """Return a ProductService wired to mocks."""
    return ProductService(**mock_daos)


class TestGetAllProducts:
    """Tests for ProductService.get_all_products."""

    def test_delegates_to_product_dao(
        self, service: ProductService, mock_daos: dict[str, MagicMock]
    ) -> None:
        mock_daos["product_dao"].get_all.return_value = ([], 0)
        products, total = service.get_all_products(page=0, page_size=20)
        mock_daos["product_dao"].get_all.assert_called_once_with(0, 20)
        assert products == []
        assert total == 0


class TestGetFiltered:
    """Tests for ProductService.get_filtered."""

    def test_raises_when_no_filters(self, service: ProductService) -> None:
        with pytest.raises(InvalidFilterError):
            service.get_filtered(tier=None, category_ids=None, page=0, page_size=20)

    def test_raises_when_empty_category_list(self, service: ProductService) -> None:
        with pytest.raises(InvalidFilterError):
            service.get_filtered(tier=None, category_ids=[], page=0, page_size=20)

    def test_filters_by_tier(
        self, service: ProductService, mock_daos: dict[str, MagicMock]
    ) -> None:
        mock_daos["product_dao"].get_filtered.return_value = ([], 0)
        service.get_filtered(tier=PriceTier.BUDGET, category_ids=None, page=0, page_size=10)
        mock_daos["product_dao"].get_filtered.assert_called_once_with(
            PriceTier.BUDGET, None, 0, 10
        )

    def test_filters_by_categories(
        self, service: ProductService, mock_daos: dict[str, MagicMock]
    ) -> None:
        mock_daos["product_dao"].get_filtered.return_value = ([], 0)
        service.get_filtered(tier=None, category_ids=[1, 2], page=0, page_size=10)
        mock_daos["product_dao"].get_filtered.assert_called_once_with(None, [1, 2], 0, 10)


class TestCreate:
    """Tests for ProductService.create."""

    def test_creates_with_existing_brand_and_category(
        self, service: ProductService, mock_daos: dict[str, MagicMock]
    ) -> None:
        brand = Brand(id=1, name="Nike")
        category = Category(id=10, name="Sneakers")
        mock_daos["brand_dao"].find_by_name_icase.return_value = brand
        mock_daos["category_dao"].find_by_name_icase.return_value = category

        expected_product = Product(
            id=1,
            public_id=uuid4(),
            title="Nike Air",
            brand=brand,
            categories=[category],
            price=Decimal("150"),
            tier=PriceTier.BUDGET,
        )
        mock_daos["product_dao"].save.return_value = expected_product

        result = service.create(
            title="Nike Air",
            brand_name="Nike",
            category_names=["Sneakers"],
            price=Decimal("150"),
            gender="U",
            color="White",
            product_url="",
            image_url="",
        )

        assert result == expected_product
        mock_daos["brand_dao"].find_by_name_icase.assert_called_once_with("Nike")
        mock_daos["brand_dao"].create.assert_not_called()
        mock_daos["product_dao"].save.assert_called_once()

    def test_creates_brand_when_not_found(
        self, service: ProductService, mock_daos: dict[str, MagicMock]
    ) -> None:
        mock_daos["brand_dao"].find_by_name_icase.return_value = None
        mock_daos["brand_dao"].create.return_value = Brand(id=99, name="NewBrand")
        mock_daos["category_dao"].find_by_name_icase.return_value = Category(id=1, name="T-Shirt")
        mock_daos["product_dao"].save.return_value = MagicMock(spec=Product)

        service.create(
            title="Test",
            brand_name="NewBrand",
            category_names=["T-Shirt"],
            price=Decimal("50"),
            gender="M",
            color="Black",
            product_url="",
            image_url="",
        )

        mock_daos["brand_dao"].create.assert_called_once_with("NewBrand")

    def test_auto_calculates_tier(
        self, service: ProductService, mock_daos: dict[str, MagicMock]
    ) -> None:
        mock_daos["brand_dao"].find_by_name_icase.return_value = Brand(id=1, name="Gucci")
        mock_daos["category_dao"].find_by_name_icase.return_value = Category(id=1, name="Coat")
        mock_daos["product_dao"].save.return_value = MagicMock(spec=Product)

        service.create(
            title="Gucci Coat",
            brand_name="Gucci",
            category_names=["Coat"],
            price=Decimal("5000"),
            gender="F",
            color="Red",
            product_url="",
            image_url="",
        )

        # Verify the tier passed to save is PREMIUM
        call_kwargs = mock_daos["product_dao"].save.call_args.kwargs
        assert call_kwargs["tier"] == PriceTier.PREMIUM


class TestDelete:
    """Tests for ProductService.delete."""

    def test_deletes_existing_product(
        self, service: ProductService, mock_daos: dict[str, MagicMock]
    ) -> None:
        pid = uuid4()
        mock_daos["product_dao"].find_by_public_id.return_value = MagicMock(spec=Product)
        service.delete(pid)
        mock_daos["product_dao"].delete_by_public_id.assert_called_once_with(pid)

    def test_raises_when_not_found(
        self, service: ProductService, mock_daos: dict[str, MagicMock]
    ) -> None:
        pid = uuid4()
        mock_daos["product_dao"].find_by_public_id.return_value = None
        with pytest.raises(ProductNotFoundError):
            service.delete(pid)
