# PythonGram

<p align="center">
  <img src="https://res.cloudinary.com/plain-team/image/upload/v1705616920/PythonGram/logo/jmzohn7ypdnpgg8der8x.png"
  alt="PythonGram" width="256" height="256">
</p>

---

PythonGram is a REST API application implemented using the FastAPI framework.
It allows users to upload, manage, and share photos, as well as interact through comments and ratings.

---

[![Documentation Status](https://readthedocs.org/projects/pythongram/badge/?version=latest)](
https://pythongram.readthedocs.io/en/latest/?badge=latest
)
[![Deploy Status](https://img.shields.io/badge/deploy-active-green?style=flat&link=https://python-gram-secure-organization.koyeb.app/docs/)](https://python-gram-secure-organization.koyeb.app/docs/)

## Table of Contents

- [Technologies](#technologies)
- [Basic functionality](#basic-functionality)
  - [Authentication](#authentication)
  - [Working with photos](#working-with-photos)
  - [Comments](#comments)
  - [Profile](#profile)
  - [Ratings](#ratings)
  - [Search](#search)
- [Usage](#usage)
  - [Installation](#installation)
  - [Additional information](#additional-information)
- [License](#license)
- [Authors](#authors)

## Technologies

| **Module**                                                     | **Description**    |
|----------------------------------------------------------------|--------------------|
| [FastAPI](https://fastapi.tiangolo.com/)                       | Framework          |
| [Pydantic](https://pydantic-docs.helpmanual.io/)               | Validation library |
| [SQLAlchemy](https://docs.sqlalchemy.org/)                     | ORM                |
| [Alembic](https://alembic.sqlalchemy.org/en/latest/)           | Migration tool     |
| [PostgreSQL](https://www.postgresql.org/)                      | Database           |
| [Cloudinary](https://cloudinary.com/)                          | Image hosting      |
| [FastAPI-limiter](https://github.com/long2ice/fastapi-limiter) | Rate limiting      |
| [Passlib](https://passlib.readthedocs.io/en/stable/)           | Password hashing   |
| [Qrcode](https://pypi.org/project/qrcode/)                     | QR code generator  |
| [Pillow](https://pypi.org/project/Pillow/)                     | Image processing   |

## Basic functionality

### Authentication

**Endpoints:**

```
POST /api/auth/signup
```
```
POST /api/auth/login
```
```
POST /api/auth/logout
```
```
POST /api/auth/refresh_token
```

*The names speak for themselves*

The application uses JWT tokens for authentication. Users have three roles: regular user, moderator, and administrator.

To implement different access levels (regular user, moderator, and administrator),
FastAPI decorators are used to check the token and user role.

### Working with photos

**Users can perform various operations related to photos:**

- Upload photos with descriptions.
    ```
    POST /api/images/upload_picture
    ```
- Delete photos.
    ```
    DELETE /api/images/{picture_id}
    ```
- Edit photo descriptions.
    ```
    PATCH /api/images/{picture_id}
    ```
- Retrieve a photo by a unique link.
    ```
    GET /api/images/{picture_id}
    ```
- Add up to 5 tags per photo.


- Apply basic photo transformations using 
[Cloudinary services](https://cloudinary.com/documentation/image_transformations).
    ```
    POST /api/transform/create_transform/{original_picture_id}
    ```
- Generate links to transformed images for viewing as URL and QR-code. Links are stored on the server.

With the help of [FastAPI decorators, described above](#authentication), 
administrators can perform all CRUD operations with user photos.

### Comments

**Under each photo, there is a comment section. Users can:**

- Add and read comments to each other's photos.
  ```
  POST /api/comments/{picture_id}
  ```
  ```
  GET /api/comments/all/{picture_id}
  ```
- Open and edit comment.
  ```
  GET /api/comments/{comment_id}
  ```
  ```
  PATCH /api/comments/{comment_id}
  ```
- Administrators and moderators [if you have the role](#authentication) can delete comments.
  ```
  DELETE /api/comments/{comment_id}
  ```

### Profile

**Endpoints for user profile:**

- See your profile.
    ```
    GET /api/users/me
    ```
- Edit your profile, or change your avatar.
    ```
    PATCH /api/users/me
    ```
    ```
    PATCH /api/users/avatar
    ```
- See another user's profile.
    ```
    GET /api/users/{username}
    ```
- Ban users, if you have the [administrator role](#authentication).
    ```
    PATCH /api/users/{username}
    ```

- Create a route for a user profile based on their unique username.
It returns all user information, including name, registration date, and the number of uploaded photos.

- Users can edit their own information and view it.

- Administrators can deactivate users (ban them). Inactive users cannot log in.

### Ratings

**soon...**

### Search

**soon...**

## Usage

### Installation

- Clone the repository.
```Shell
  git clone https://github.com/GodVov4/PythonGram.git
```

- Install dependencies.
```Shell
  pip install -r requirements.txt
```
*or with poetry*
```Shell
  poetry install
```

- Setup the ".env" file.
```Shell
  cp .env.example .env
```
*and fill in the information you need*

- Run the application.
```Shell
  uvicorn main:app --reload
```

- Enjoy!

### Additional information

- [Documentation](https://pythongram.readthedocs.io/en/latest/)
- [Swagger documentation(soon)](https://python-gram-secure-organization.koyeb.app/docs)
- [GitHub](https://github.com/GodVov4/PythonGram)

## License

This project is licensed under the [MIT License](https://github.com/GodVov4/PythonGram/blob/main/LICENSE).

## Authors

- [GodVov4](https://github.com/GodVov4)
- [DSofiya](https://github.com/DSofiya)
- [fls0](https://github.com/fls0)
- [GennadiiBukh](https://github.com/GennadiiBukh)

Feel free to provide feedback, report issues, or contribute to the project!
