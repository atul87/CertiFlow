import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import IndexModel, ASCENDING
from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls) -> None:
        """Connect to local or remote MongoDB instance."""
        if cls.client is None:
            logger.info("Connecting to MongoDB at %s...", settings.MONGODB_URI)
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            cls.db = cls.client[settings.MONGODB_DATABASE]
            # Test ping
            await cls.client.admin.command("ping")
            logger.info("Successfully connected to MongoDB database '%s'", settings.MONGODB_DATABASE)
            # Initialize required collections & indexes
            await cls.init_indexes()

    @classmethod
    async def close(cls) -> None:
        """Close MongoDB connection pool."""
        if cls.client is not None:
            logger.info("Closing MongoDB connection pool...")
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("MongoDB connection closed.")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        if cls.db is None:
            raise RuntimeError("Database is not connected. Call DatabaseManager.connect() first.")
        return cls.db

    @classmethod
    def get_collection(cls, name: str) -> AsyncIOMotorCollection:
        return cls.get_db()[name]

    @classmethod
    async def init_indexes(cls) -> None:
        """Create indexes defined in P0 specification."""
        db = cls.get_db()
        logger.info("Verifying and creating MongoDB indexes...")

        # 1. Users collection
        users_col = db["users"]
        await users_col.create_indexes([
            IndexModel([("email", ASCENDING)], unique=True, name="uniq_users_email"),
            IndexModel([("created_at", ASCENDING)], name="idx_users_created_at")
        ])

        # 2. Organizations collection
        orgs_col = db["organizations"]
        await orgs_col.create_indexes([
            IndexModel([("slug", ASCENDING)], unique=True, name="uniq_organizations_slug"),
            IndexModel([("owner_id", ASCENDING)], name="idx_organizations_owner_id")
        ])

        # 3. Organization members collection
        members_col = db["organization_members"]
        await members_col.create_indexes([
            IndexModel(
                [("organization_id", ASCENDING), ("user_id", ASCENDING)],
                unique=True,
                name="uniq_org_members_org_user"
            ),
            IndexModel([("user_id", ASCENDING)], name="idx_org_members_user_id"),
            IndexModel([("organization_id", ASCENDING)], name="idx_org_members_org_id")
        ])

        # 4. Refresh tokens collection
        refresh_col = db["refresh_tokens"]
        await refresh_col.create_indexes([
            IndexModel([("token_hash", ASCENDING)], unique=True, name="uniq_refresh_tokens_hash"),
            IndexModel([("user_id", ASCENDING)], name="idx_refresh_tokens_user_id"),
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0, name="idx_refresh_tokens_ttl")
        ])

        # 5. Audit logs collection
        audit_col = db["audit_logs"]
        await audit_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_audit_org_created"),
            IndexModel([("user_id", ASCENDING)], name="idx_audit_user_id"),
            IndexModel([("action", ASCENDING)], name="idx_audit_action")
        ])

        logger.info("MongoDB indexes verified successfully.")


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency provider for FastAPI route handlers."""
    return DatabaseManager.get_db()
