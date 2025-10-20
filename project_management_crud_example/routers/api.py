"""API endpoints for item management."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from project_management_crud_example.dal.sqlite.repository import ItemRepository
from project_management_crud_example.dependencies import get_item_repo
from project_management_crud_example.domain_models import Item, ItemCreateCommand, ItemData

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemData,
    repo: ItemRepository = Depends(get_item_repo),  # noqa: B008
) -> Item:
    """Create a new item."""
    item_create_command = ItemCreateCommand(item_data=item_data)
    return repo.create_item(item_create_command)


@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: str,
    repo: ItemRepository = Depends(get_item_repo),  # noqa: B008
) -> Item:
    """Get an item by ID."""
    item = repo.get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.get("", response_model=List[Item])
async def get_all_items(
    repo: ItemRepository = Depends(get_item_repo),  # noqa: B008
) -> List[Item]:
    """Get all items."""
    return repo.get_all_items()


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    repo: ItemRepository = Depends(get_item_repo),  # noqa: B008
) -> None:
    """Delete an item by ID."""
    success = repo.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
