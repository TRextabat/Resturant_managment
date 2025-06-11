from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from fastapi import HTTPException, BackgroundTasks
from src.user.repositories import UserRepository
from src.auth.utils import (
    generate_passwd_hash, 
    create_access_token, 
    decode_token,
    verify_password
)
from src.auth.utils import VerificationCodeManager
from src.mail.mail import send_email, EmailSchema
from src.core.settings import settings
from src.auth.schemas import (
    RegisterRequest, 
    VerifyEmailRequest, 
    VerifyEmailResponse, 
    RegisterResponse,
    TokenRefreshRequest,
    UserProfileResponse,
    TokenResponse
)
from src.errors import (
    UserAlreadyExists, 
    UserNotFound, 
    InvalidToken,
    AccountNotVerified,
    InvalidCredentials,
    TooManyRequests
)
from src.core.redis_manager import TokenBlocklist
from loguru import logger

class AuthService:
    """Handles authentication operations (registration, verification, login)."""

    @staticmethod
    async def register_user(request: RegisterRequest, background_tasks: BackgroundTasks, db: AsyncSession) -> RegisterResponse:
        """Register a new user and send a verification code."""
        user_repo = UserRepository(db)

        # Check if email exists
        existing_user = await user_repo.get_by_email(request.email)
        if existing_user:
            raise UserAlreadyExists()
        logger.info(f"user {existing_user}")
        # Hash password
        hashed_password = await generate_passwd_hash(request.password)

        # Generate & Store Code
        verification_code = await VerificationCodeManager.set_code(request.email)
        logger.info(f"Verification code for {request.email}: {verification_code}")
        logger.info(f"Verification code for {request.email}: {verification_code}")
        # Create unverified user
        user_data = {
            "username" : request.email.split('@')[0],  # Default to email prefix
            "primary_email": request.email,
            "hashed_password": hashed_password,
            "primary_email_verified": False
        }
        user = await user_repo.create_user_with_customer(user_data)

        user_data_for_token = {"id": str(user.id), "email": user.primary_email, "resend_only": True}
        verification_token = await create_access_token(user_data_for_token)

        # Send email
        email_content = EmailSchema(
            email=user .primary_email,
            subject="Verify Your Email",
            body=f"Your verification code is: {verification_code}"
        )
        background_tasks.add_task(send_email, email_content)

        return RegisterResponse(
            id= user.id,
            message="Verification email sent",
            verifection_token=verification_token,
            token_type="bearer")

    @staticmethod
    async def verify_email(request: VerifyEmailRequest, db: AsyncSession) -> VerifyEmailResponse:
        """Verify email with the 6-digit code and issue tokens."""
        user_repo = UserRepository(db)

        # Find user
        user = await user_repo.get_by_email(request.email)
        if not user:
            raise UserNotFound()

        # Retrieve stored verification code
        stored_code = await VerificationCodeManager.get_code(request.email)
        if not stored_code or stored_code != request.code:
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")

        # Mark user as verified
        await user_repo.update(user.id, {"primary_email_verified": True})
        await VerificationCodeManager.delete_code(request.email)

        # Generate JWT tokens
        user_data = {"id": str(user.id), "email": user.primary_email}
        access_token = await create_access_token(user_data, expiry=timedelta())
        refresh_token = await create_access_token(user_data, expiry=timedelta(), refresh=True)

        return VerifyEmailResponse(
            message="Email verified successfully",
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    @staticmethod
    async def login_user(email: str, password: str, db: AsyncSession) -> TokenResponse:
        """Authenticate user and return access & refresh tokens."""
        user_repo = UserRepository(db)

        # Find user by email
        user = await user_repo.get_by_email(email)
        if not user:
            logger.error(f"User not found: {email}")
            raise UserNotFound()

        # Ensure email is verified
        if not user.primary_email_verified:
            logger.error("User email not verified")
            raise AccountNotVerified()

        # Verify password
        is_valid = await verify_password(password, user.hashed_password)
        if not is_valid:
            raise InvalidCredentials()

        # Generate JWT tokens
        user_data = {"id": str(user.id), "email": user.primary_email}
        access_token = await create_access_token(user_data, expiry=timedelta(hours=1))
        refresh_token = await create_access_token(user_data, expiry=timedelta(days=7), refresh=True)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    @staticmethod
    async def refresh_token(request: TokenRefreshRequest) -> TokenResponse:
        """Issue a new access token using a valid refresh token."""
        token_data = await decode_token(request.refresh_token)

        if not token_data or not token_data.get("refresh"):
            raise InvalidToken()

        # Generate new access token
        user_data = {"id": token_data["user"]["id"], "email": token_data["user"]["email"]}
        access_token = await create_access_token(user_data)

        return TokenResponse(access_token=access_token, refresh_token=request.refresh_token)

    @staticmethod
    async def get_current_user(token: dict, db: AsyncSession) -> UserProfileResponse:
        """Fetch user profile from token."""
        user_repo = UserRepository(db)
        user_id = token["user"]["id"]

        user = await user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound()

        return UserProfileResponse.model_validate(user)
    
    @staticmethod
    async def resend_verification_email(
        current_user, background_tasks: BackgroundTasks, db: AsyncSession
    ) -> RegisterResponse:
        """Resends a verification email if the user's email is not verified."""
        user_repo = UserRepository(db)

        # Fetch the authenticated user
        user = await user_repo.get_by_id(current_user.id)
        if not user:
            raise UserNotFound()

        # Ensure the user is NOT already verified
        if user.primary_email_verified:
            raise AccountNotVerified("Email is already verified.")

        # Generate a new verification code
        verification_code = await VerificationCodeManager.set_code(user.primary_email)

        if verification_code is None:
            raise TooManyRequests()
        # Send the email asynchronously
        email_content = EmailSchema(
            email=user.primary_email,
            subject="Resend Email Verification",
            body=f"Your new verification code is: {verification_code}"
        )
        background_tasks.add_task(send_email, email_content)

        return RegisterResponse(message="Verification email resent successfully.")
    
    @staticmethod
    async def logout_user(token_data: dict, db: AsyncSession):
        """Revokes the refresh token by blacklisting it in Redis."""
        token_id = token_data.get("jti")
        if not token_id:
            raise InvalidToken()

        # Blacklist the refresh token in Redis
        await TokenBlocklist.add_token_to_blocklist(token_id, expiry_seconds=900)

        return {"message": "Successfully logged out"}