from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository.transform import TransformRepository
from src.schemas.transform import TransformSchema, TransformResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/transform', tags=['transform'])


def access_checking(picture, current_user: User):
    """
    Helper function for checking access to the picture.

    :param picture: Picture object to check access for.
    :type picture: Union[None, Picture]
    :param current_user: Current authenticated user.
    :type current_user: User
    :raises HTTPException: If access is denied.
    """
    if not picture:
        raise HTTPException(status_code=404, detail="Зображення не знайдено")
    if picture.user_id != current_user.id and current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Недостатньо прав для цієї операції")
    return


@router.post(
    '/create_transform/{original_picture_id}',
    response_model=TransformResponse,
    status_code=status.HTTP_201_CREATED)
async def create_transform(
        request: TransformSchema,
        original_picture_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
    Endpoint to create a transformed picture.

    :param request: TransformCreate instance containing transformation parameters.
    :type request: TransformSchema
    :param original_picture_id: ID of the original picture.
    :type original_picture_id: int
    :param current_user: Current authenticated user (dependency injection).
    :type current_user: User
    :param session: Asynchronous SQLAlchemy session (dependency injection).
    :type session: AsyncSession
    :return: The created transformed picture.
    :rtype: TransformResponse
    :raises HTTPException: If transformation parameters are missing or the transformation fails.

    Available transformation params:
    - `width`: The width of the transformed image. 100-2000.
    - `height`: The height of the transformed image. 100-2000.
    - `crop`: The crop mode. `fill`, `limit`, `scale`, `thumb`, `fit`, `lfill`
    - `effect`: `grayscale`, `sepia`, `vignette`, `cartoonify`,`pixelate`, `blur`, `brightness`,
    `contrast`, `saturation`, `sharpen`
    - `border`: `5px_solid_lightblue`, `5px_dotted_lightblue`, `5px_dashed_lightblue`
    - `angle`: 0-360
    """
    transform_repo = TransformRepository(session)
    transformation_params = request.transformation_params
    picture = await transform_repo.get_picture_by_id(original_picture_id)
    access_checking(picture, current_user)
    if not transformation_params:
        raise HTTPException(status_code=400, detail="Необхідно вказати хоча б один параметр трансформації")
    transformed_picture = await transform_repo.create_transformed_picture(
        user_id=picture.user_id,
        original_picture_id=original_picture_id,
        transformation_params=transformation_params
    )
    if transformed_picture is None:
        raise HTTPException(
            status_code=500, detail='Трансформація не виконана')
    return transformed_picture


@router.get("/user_transforms", response_model=List[TransformResponse], status_code=status.HTTP_200_OK)
async def list_user_transforms(
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
    Endpoint to list transformed pictures for the current user.

    :param current_user: Current authenticated user (dependency injection).
    :type current_user: User
    :param session: Asynchronous SQLAlchemy session (dependency injection).
    :type session: AsyncSession
    :return: List of transformed pictures for the user.
    :rtype: List[TransformResponse]
    :raises HTTPException: If no transformed pictures are found.
    """
    transform_repo = TransformRepository(session)
    user_transforms = await transform_repo.get_user_transforms(current_user.id)
    if user_transforms is None:
        raise HTTPException(status_code=404, detail="Зображення не знайдено")
    return user_transforms


@router.get("/{transform_id}", response_model=TransformResponse, status_code=status.HTTP_200_OK)
async def get_transform(
        transform_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
    Endpoint to retrieve a specific transformed picture by its ID.

    :param transform_id: ID of the transformed picture to be retrieved.
    :type transform_id: int
    :param current_user: Current authenticated user (dependency injection).
    :type current_user: User
    :param session: Asynchronous SQLAlchemy session (dependency injection).
    :type session: AsyncSession
    :return: The retrieved transformed picture.
    :rtype: TransformResponse
    :raises HTTPException: If the transformed picture is not found.
    """
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    access_checking(transformed_picture, current_user)
    return transformed_picture


@router.get("/{transform_id}/qr", status_code=status.HTTP_200_OK)
async def get_transform_qr(
        transform_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
    Endpoint to retrieve the QR code URL for a specific transformed picture by its ID.

    :param transform_id: ID of the transformed picture.
    :type transform_id: int
    :param current_user: Current authenticated user (dependency injection).
    :type current_user: User
    :param session: Asynchronous SQLAlchemy session (dependency injection).
    :type session: AsyncSession
    :return: Dictionary containing the QR code URL.
    :rtype: dict
    :raises HTTPException: If the transformed picture is not found.
    """
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    access_checking(transformed_picture, current_user)
    return {"qr_url": transformed_picture.qr_url}


@router.patch("/{transform_id}", response_model=TransformResponse, status_code=status.HTTP_200_OK)
async def update_transform(
        request: TransformSchema,
        transform_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
    Endpoint to update a specific transformed picture by its ID.

    :param request: TransformSchema instance containing updated transformation parameters.
    :type request: TransformSchema
    :param transform_id: ID of the transformed picture to be updated.
    :type transform_id: int
    :param current_user: Current authenticated user (dependency injection).
    :type current_user: User
    :param session: Asynchronous SQLAlchemy session (dependency injection).
    :type session: AsyncSession
    :return: The updated transformed picture.
    :rtype: TransformResponse
    :raises HTTPException: If the transformed picture is not found.

    Available transformation params:
    - `width`: The width of the transformed image. 100-2000.
    - `height`: The height of the transformed image. 100-2000.
    - `crop`: The crop mode. `fill`, `limit`, `scale`, `thumb`, `fit`, `lfill`
    - `effect`: `grayscale`, `sepia`, `vignette`, `cartoonify`,`pixelate`, `blur`, `brightness`,
    `contrast`, `saturation`, `sharpen`
    - `border`: `5px_solid_lightblue`, `5px_dotted_lightblue`, `5px_dashed_lightblue`
    - `angle`: 0-360
    """
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    access_checking(transformed_picture, current_user)
    new_transformed_picture = await transform_repo.update_transformed_picture(
        transformed_picture_id=transform_id,
        transformation_params=request.transformation_params)
    if not new_transformed_picture:
        raise HTTPException(status_code=404, detail="Трансформація не виконана")
    return new_transformed_picture


@router.delete("/{transform_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transform(
        transform_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
    Endpoint to delete a specific transformed picture by its ID.

    :param transform_id: ID of the transformed picture to be deleted.
    :type transform_id: int
    :param current_user: Current authenticated user (dependency injection).
    :type current_user: User
    :param session: Asynchronous SQLAlchemy session (dependency injection).
    :type session: AsyncSession
    :raises HTTPException: If the transformed picture is not found or deletion fails.
    """
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    access_checking(transformed_picture, current_user)
    success = await transform_repo.delete_transformed_picture(transform_id)
    if not success:
        raise HTTPException(status_code=404, detail="Видалення не виконано")
