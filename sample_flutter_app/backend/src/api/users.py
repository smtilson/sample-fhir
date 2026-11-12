"""User accounts API router (SMP-EP1-TK01).

WHY THIS FILE EXISTS:
    Provides HTTP endpoints for creating and querying user accounts.
    - POST /api/v1/users: creates a new user, hashes their password, prevents duplicate emails.
    - GET /api/v1/users: lists existing users (used by the Flutter app for the user switcher).
    - GET /api/v1/users/{user_id}: fetches a single user by ID.

Devin re-Cognito:
    In AWS Cognito, user sign-up is handled via the Cognito Identity Provider
    API (`SignUp` or `AdminCreateUser`). Your FastAPI backend does not need
    endpoints for user registration or user password handling. Instead, Flutter
    calls Cognito directly (via Amplify or the Cognito SDK), and FastAPI only
    receives the verified JWT bearer token containing the user's `sub` claim.
"""

from fastapi import APIRouter, HTTPException, status

from src.core.security import hash_password
from src.models.user import User
from src.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
)
async def create_user(user_in: UserCreate) -> UserOut:
    """Create a user account with a bcrypt-hashed password.

    Rejects duplicate emails with HTTP 400 Bad Request.
    """
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_pw = hash_password(user_in.password)
    user = User(
        name=user_in.name,
        email=user_in.email,
        password=hashed_pw,
    )
    await user.insert()

    return UserOut(
        id=str(user.id),
        name=user.name,
        email=user.email,
    )


@router.get(
    "",
    response_model=list[UserOut],
    summary="List all users",
)
async def list_users() -> list[UserOut]:
    """Return all user accounts (for Flutter active-user switcher)."""
    users = await User.find_all().to_list()
    return [
        UserOut(id=str(u.id), name=u.name, email=u.email)
        for u in users
    ]


@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Get user profile by ID",
)
async def get_user(user_id: str) -> UserOut:
    """Retrieve a specific user account by its database identifier."""
    try:
        user = await User.get(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserOut(
        id=str(user.id),
        name=user.name,
        email=user.email,
    )


@router.patch(
    "/{user_id}",
    response_model=UserOut,
    summary="Update user profile fields",
)
async def update_user(user_id: str, user_in: UserUpdate) -> UserOut:
    """Update specific fields of an existing user account."""
    try:
        user = await User.get(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # If email is being changed, check for conflict with another user
    if user_in.email is not None and user_in.email != user.email:
        existing = await User.find_one(User.email == user_in.email)
        if existing is not None and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        user.email = user_in.email

    if user_in.name is not None:
        user.name = user_in.name

    if user_in.password is not None:
        user.password = hash_password(user_in.password)

    await user.save()

    return UserOut(
        id=str(user.id),
        name=user.name,
        email=user.email,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user account",
)
async def delete_user(user_id: str) -> None:
    """Delete a user account by its database identifier."""
    try:
        user = await User.get(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await user.delete()

