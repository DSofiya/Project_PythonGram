import enum
from datetime import date
from typing import List, Optional

from sqlalchemy import String, ForeignKey, DateTime, func, Enum, Integer, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in the FastAPI application."""
    pass


class TimeStampMixin:
    """Mixin class providing timestamp information (created_at, updated_at) for SQLAlchemy models."""
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[date] = mapped_column(
        'created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column(
        'updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)


picture_tag_association = Table(
    'picture_tag_association',
    Base.metadata,
    Column('picture_id', Integer, ForeignKey('pictures.id', ondelete="CASCADE")),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Picture(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'pictures' table in the database."""
    __tablename__ = 'pictures'
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    cloudinary_public_id: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    transformed_pictures: Mapped["TransformedPicture"] = relationship(
        "TransformedPicture", back_populates="original_picture", lazy='joined')
    user: Mapped["User"] = relationship("User", back_populates="pictures", lazy='joined')
    comment: Mapped[List["Comment"]] = relationship(back_populates="picture", cascade='all, delete', lazy='joined')
    tags: Mapped[List["Tag"]] = relationship(
        secondary=picture_tag_association, back_populates='pictures', lazy='joined')


class Tag(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'tags' table in the database."""
    __tablename__ = 'tags'
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    pictures: Mapped[List["Picture"]] = relationship(
        secondary=picture_tag_association, back_populates='tags', lazy='joined')


class TransformedPicture(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'transformed_pictures' table in the database."""
    __tablename__ = 'transformed_pictures'
    original_picture_id: Mapped[int] = mapped_column(ForeignKey('pictures.id'), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    public_id: Mapped[str] = mapped_column(String, nullable=False)  # cloudinary public id
    qr_url: Mapped[str] = mapped_column(String(255), nullable=True)
    qr_public_id: Mapped[str] = mapped_column(String, nullable=True)  # cloudinary public id
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    original_picture = relationship("Picture", back_populates="transformed_pictures")


class Role(enum.Enum):
    """Enumeration class representing user roles in the FastAPI application."""
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'users' table in the database."""
    __tablename__ = "users"
    full_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[Enum] = mapped_column("role", Enum(Role), default=Role.user, nullable=True)
    ban: Mapped[bool] = mapped_column(default=False, nullable=True)
    picture_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True)

    pictures: Mapped["Picture"] = relationship(
        "Picture", back_populates="user", uselist=True, lazy='joined', cascade='all, delete')
    blacklisted_tokens: Mapped["Blacklisted"] = relationship("Blacklisted", back_populates="user", lazy='joined')
    comment: Mapped["Comment"] = relationship("Comment", back_populates="user", lazy='joined', cascade='all, delete')


class Blacklisted(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'blacklisted' table in the database."""
    __tablename__ = "blacklisted"
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    token: Mapped[str] = mapped_column(String(255), nullable=True)

    user = relationship("User", back_populates="blacklisted_tokens")


class Comment(TimeStampMixin, Base):
    """SQLAlchemy model representing the 'comments' table in the database."""
    __tablename__ = "comments"
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    picture_id: Mapped[int] = mapped_column(Integer, ForeignKey(Picture.id), nullable=False)
    text: Mapped[str] = mapped_column(String(255), nullable=False)

    user = relationship("User", back_populates="comment")
    picture: Mapped[List["Picture"]] = relationship(back_populates='comment')
