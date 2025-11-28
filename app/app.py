from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import UserRead, UserCreate, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile
from app.users import auth_backend, fastapi_users, current_active_user

"""
As soon as the app starts, it runs this function below and creates the db and the
tables.Also it makes sure that all are handling correctly when the app stops.
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    An async context manager to handle application startup and shutdown events.

    On startup, this function calls `create_db_and_tables()` to ensure that the
    database and all necessary tables are created before the application starts
    accepting requests.
    """
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

"""
User sends a file to our API, our API will upload it to Imagekit, will grab the url,
save it to our database and serve that to our user on the frontend.
"""
@app.post("/upload")
async def upload_post(
    caption: str = Form(""),
    file: UploadFile = File(...), # This means that it will be able to receive a file
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session) # Dependency injection to use the db that we set up
):
    """
    Handles the creation of a new post with a media file (image or video).

    This endpoint requires an authenticated user. It performs the following steps:
    1. Saves the uploaded file to a temporary local path.
    2. Uploads the temporary file to ImageKit.io.
    3. Creates a new `Post` record in the database with the caption, ImageKit URL,
       and other metadata.
    4. Cleans up the temporary file.

    Args:
        caption (str): The text caption for the post.
        file (UploadFile): The media file (image or video) to be uploaded.
        user (User): The authenticated user, injected by `current_active_user`.
        session (AsyncSession): The database session, injected by `get_async_session`.

    Returns:
        Post: The newly created Post object from the database.

    Raises:
        HTTPException: If the upload fails or any other internal error occurs.
    """
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags=["backend-upload"],
            )
        )
        if upload_result.response_metadata.http_status_code == 200:

            post = Post(
                user_id=user.id,
                caption=caption,
                url=upload_result.url,
                file_type="video" if file.content_type.startswith("video/") else "image",
                file_name=upload_result.name
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()


@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Fetches all posts to be displayed in the user's feed.

    This endpoint requires an authenticated user. It retrieves all posts from the
    database, ordered by creation date (newest first). It then enriches each post
    with the author's email and an `is_owner` flag to indicate if the currently
    logged-in user is the author of the post.

    Args:
        session (AsyncSession): The database session.
        user (User): The currently authenticated user.

    Returns:
        dict: A dictionary containing a list of post data, ready for the frontend.
    """
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    result = await session.execute(select(User))
    users = result.scalars().all()
    user_dict = {u.id: u.email for u in users}
    
    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(post.user_id, "Unknown")
            }
        )


    return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
    """
    Deletes a specific post by its ID.

    This endpoint requires the user to be authenticated. It ensures that only the
    owner of the post can delete it.

    Args:
        post_id (str): The UUID of the post to be deleted.
        session (AsyncSession): The database session.
        user (User): The currently authenticated user attempting the deletion.

    Returns:
        dict: A success message upon successful deletion.

    Raises:
        HTTPException (404): If a post with the given ID is not found.
        HTTPException (403): If the user is not the owner of the post.
        HTTPException (500): For any other internal errors.
    """
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this post")
        
        await session.delete(post)
        await session.commit()
        
        return {"success": True, "message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        
