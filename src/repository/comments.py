from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Comment, User, Picture
from src.schemas.comment import CommentSchema


async def create_comment(body: CommentSchema, picture_id: int, db: AsyncSession, user: User):
    """
    Create a new comment in the database.

    :param body: The schema representing the comment data.
    :type body: CommentSchema
    :param picture_id: The ID of the picture associated with the comment.
    :type picture_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user creating the comment.
    :type user: User
    :return: The created comment.
    :rtype: Comment
    """
    comment = Comment(**body.model_dump(exclude_unset=True), user_id=user.id, picture_id=picture_id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments(picture_id: int, offset: int, limit: int, db: AsyncSession):
    """
    Retrieve a list of comments for a specific picture from the database.

    :param picture_id: The ID of the picture for which comments are retrieved.
    :type picture_id: int
    :param offset: The offset for pagination.
    :type offset: int
    :param limit: The limit for the number of comments to retrieve.
    :type limit: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: A list of comments.
    :rtype: List[Comment]
    """
    stmt = select(Picture).where(Picture.id == picture_id)
    picture = await db.execute(stmt)
    picture = picture.unique().scalar_one_or_none()
    if picture:
        smtp = select(Comment).filter_by(picture_id=picture_id).offset(offset).limit(limit)
        comments = await db.execute(smtp)
        return comments.scalars().all()


async def get_comment(comment_id: int, db: AsyncSession):
    """
    Retrieve a specific comment by its ID from the database.

    :param comment_id: The ID of the comment to retrieve.
    :type comment_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The retrieved comment or None if not found.
    :rtype: Optional[Comment]
    """
    smtp = select(Comment).filter_by(id=comment_id)
    comment = await db.execute(smtp)
    return comment.scalar_one_or_none()


async def update_comment(comment_id: int, body: CommentSchema, db: AsyncSession, user: User):
    """
    Update a specific comment's text content in the database.

    :param comment_id: The ID of the comment to update.
    :type comment_id: int
    :param body: The schema representing the updated comment data.
    :type body: CommentSchema
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user updating the comment.
    :type user: User
    :return: The updated comment or None if not found.
    :rtype: Optional[Comment]
    """
    stmt = select(Comment).filter_by(id=comment_id, user_id=user.id)
    comment = await db.execute(stmt)
    comment = comment.scalar_one_or_none()
    if comment:
        comment.text = body.text
        await db.commit()
        await db.refresh(comment)
    return comment


async def delete_comment(comment_id: int, db: AsyncSession):
    """
    Delete a specific comment from the database.

    :param comment_id: The ID of the comment to delete.
    :type comment_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The deleted comment or None if not found.
    :rtype: Optional[Comment]
    """
    stmt = select(Comment).filter_by(id=comment_id)
    comment = await db.execute(stmt)
    comment = comment.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment
