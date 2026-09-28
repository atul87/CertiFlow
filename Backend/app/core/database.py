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

        # 6. Templates collection (P1)
        templates_col = db["templates"]
        await templates_col.create_indexes([
            IndexModel([("organization_id", ASCENDING)], name="idx_templates_org_id"),
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_templates_org_status"),
            IndexModel([("organization_id", ASCENDING), ("name", ASCENDING)], name="idx_templates_org_name"),
            IndexModel([("created_at", ASCENDING)], name="idx_templates_created_at")
        ])

        # 7. Template versions collection (P1)
        versions_col = db["template_versions"]
        await versions_col.create_indexes([
            IndexModel(
                [("template_id", ASCENDING), ("version", ASCENDING)],
                unique=True,
                name="uniq_template_version_number"
            ),
            IndexModel([("template_id", ASCENDING), ("status", ASCENDING)], name="idx_template_versions_status"),
            IndexModel([("organization_id", ASCENDING)], name="idx_template_versions_org_id")
        ])

        # 8. Assets collection (P1)
        assets_col = db["assets"]
        await assets_col.create_indexes([
            IndexModel([("organization_id", ASCENDING)], name="idx_assets_org_id"),
            IndexModel([("template_id", ASCENDING)], name="idx_assets_template_id")
        ])

        # 9. Fonts collection (P1)
        fonts_col = db["fonts"]
        await fonts_col.create_indexes([
            IndexModel([("organization_id", ASCENDING)], name="idx_fonts_org_id"),
            IndexModel([("family", ASCENDING)], name="idx_fonts_family")
        ])

        # Seed system fonts if not already seeded
        existing_fonts_count = await fonts_col.count_documents({"source": "system"})
        if existing_fonts_count == 0:
            system_fonts = [
                {"name": "Inter", "family": "Inter", "source": "system", "organization_id": None},
                {"name": "Poppins", "family": "Poppins", "source": "system", "organization_id": None},
                {"name": "Montserrat", "family": "Montserrat", "source": "system", "organization_id": None},
                {"name": "Roboto", "family": "Roboto", "source": "system", "organization_id": None},
                {"name": "Open Sans", "family": "Open Sans", "source": "system", "organization_id": None},
                {"name": "Playfair Display", "family": "Playfair Display", "source": "system", "organization_id": None},
                {"name": "Lora", "family": "Lora", "source": "system", "organization_id": None},
            ]
            await fonts_col.insert_many(system_fonts)
            logger.info("Seeded %d system fonts.", len(system_fonts))

        # 10. Imports collection (P2)
        imports_col = db["imports"]
        await imports_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_imports_org_created"),
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_imports_org_status"),
            IndexModel([("organization_id", ASCENDING), ("template_id", ASCENDING)], name="idx_imports_org_template")
        ])

        # 11. Import Mappings collection (P2)
        import_mappings_col = db["import_mappings"]
        await import_mappings_col.create_indexes([
            IndexModel([("import_id", ASCENDING)], unique=True, name="uniq_import_mappings_import_id"),
            IndexModel([("template_version_id", ASCENDING)], name="idx_import_mappings_version_id"),
            IndexModel([("organization_id", ASCENDING)], name="idx_import_mappings_org_id")
        ])

        # 12. Import Rows collection (P2)
        import_rows_col = db["import_rows"]
        await import_rows_col.create_indexes([
            IndexModel([("import_id", ASCENDING), ("row_number", ASCENDING)], unique=True, name="uniq_import_rows_import_row"),
            IndexModel([("import_id", ASCENDING), ("status", ASCENDING)], name="idx_import_rows_import_status"),
            IndexModel([("organization_id", ASCENDING)], name="idx_import_rows_org_id")
        ])

        # 13. Mapping Profiles collection (P2)
        mapping_profiles_col = db["mapping_profiles"]
        await mapping_profiles_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("template_id", ASCENDING)], name="idx_mapping_profiles_org_template"),
            IndexModel([("organization_id", ASCENDING), ("name", ASCENDING)], name="idx_mapping_profiles_org_name")
        ])

        # 14. Certificates collection (P3)
        certs_col = db["certificates"]
        await certs_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_certs_org_created"),
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_certs_org_status"),
            IndexModel([("organization_id", ASCENDING), ("template_id", ASCENDING)], name="idx_certs_org_template"),
            IndexModel([("certificate_number", ASCENDING)], name="idx_certs_cert_number"),
            IndexModel([("verification_code", ASCENDING)], unique=True, name="uniq_certs_verification_code"),
            IndexModel([("idempotency_key", ASCENDING)], name="idx_certs_idempotency_key", sparse=True),
            IndexModel([("organization_id", ASCENDING), ("recipient.email", ASCENDING)], name="idx_certs_recipient_email"),
        ])

        # 15. Sequences collection (P3 — atomic counters)
        seq_col = db["sequences"]
        await seq_col.create_indexes([
            IndexModel(
                [("organization_id", ASCENDING), ("key", ASCENDING), ("year", ASCENDING)],
                unique=True,
                name="uniq_sequences_org_key_year"
            ),
        ])

        logger.info("MongoDB indexes verified successfully.")


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency provider for FastAPI route handlers."""
    return DatabaseManager.get_db()
