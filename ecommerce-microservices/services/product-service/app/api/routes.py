"""API routes for Product Service"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from ..domain.schemas import ProductResponse, ProductCreate, ProductUpdate
from ..core import ProductService, ProductNotFoundException, InsufficientStockException
from .dependencies import get_product_service

router = APIRouter()


@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends(get_product_service)
):
    """Get all products with pagination"""
    return service.get_all_products(skip, limit)


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """Get a specific product by ID"""
    try:
        return service.get_product_by_id(product_id)
    except ProductNotFoundException:
        raise HTTPException(status_code=404, detail="Product not found")


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    """Create a new product"""
    return service.create_product(product)


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    service: ProductService = Depends(get_product_service)
):
    """Update an existing product"""
    try:
        return service.update_product(product_id, product_update)
    except ProductNotFoundException:
        raise HTTPException(status_code=404, detail="Product not found")


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """Delete a product"""
    try:
        service.delete_product(product_id)
        return None
    except ProductNotFoundException:
        raise HTTPException(status_code=404, detail="Product not found")


@router.patch("/products/{product_id}/stock", response_model=ProductResponse)
async def update_stock(
    product_id: int,
    stock_change: int,
    service: ProductService = Depends(get_product_service)
):
    """Update product stock (add or subtract)"""
    try:
        return service.update_stock(product_id, stock_change)
    except ProductNotFoundException:
        raise HTTPException(status_code=404, detail="Product not found")
    except InsufficientStockException as e:
        raise HTTPException(status_code=400, detail=str(e))
