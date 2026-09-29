import logging
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection, AsyncIOMotorClientSession
from pymongo import IndexModel, ASCENDING
from pymongo.errors import OperationFailure
from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    @asynccontextmanager
    async def transaction_scope(cls) -> AsyncGenerator[Optional[AsyncIOMotorClientSession], None]:
        """
        Async context manager providing a MongoDB multi-document transaction boundary — P12.08.
        Automatically commits on successful exit, aborts on unhandled exception.
        Gracefully falls back to non-transactional session if connected to standalone MongoDB.
        """
        if cls.client is None:
            raise RuntimeError("Database is not connected. Call DatabaseManager.connect() first.")

        async with await cls.client.start_session() as session:
            try:
                async with session.start_transaction():
                    yield session
            except (OperationFailure, Exception) as exc:
                err_msg = str(exc)
                if (
                    "Transaction numbers are only allowed on a replica set member" in err_msg
                    or "standalone" in err_msg.lower()
                ):
                    logger.debug("Standalone MongoDB detected; running operations without replica-set transaction")
                    yield None
                else:
                    raise

    @classmethod
    def get_collection(cls, name: str) -> AsyncIOMotorCollection:
        return cls.get_db()[name]

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
        try:
            await certs_col.drop_index("uniq_certs_org_idempotency_key")
        except Exception:
            pass
        try:
            await certs_col.drop_index("uniq_certs_org_import_row")
        except Exception:
            pass
        await certs_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_certs_org_created"),
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_certs_org_status"),
            IndexModel([("organization_id", ASCENDING), ("template_id", ASCENDING)], name="idx_certs_org_template"),
            IndexModel([("organization_id", ASCENDING), ("certificate_number", ASCENDING)], unique=True, name="uniq_certs_org_cert_number"),
            IndexModel([("verification_code", ASCENDING)], unique=True, name="uniq_certs_verification_code"),
            IndexModel(
                [("organization_id", ASCENDING), ("idempotency_key", ASCENDING)],
                unique=True,
                partialFilterExpression={"idempotency_key": {"$type": "string"}},
                name="uniq_certs_org_idempotency_key",
            ),
            IndexModel(
                [("organization_id", ASCENDING), ("import_id", ASCENDING), ("import_row_id", ASCENDING)],
                unique=True,
                partialFilterExpression={"import_row_id": {"$type": "string"}},
                name="uniq_certs_org_import_row",
            ),
            IndexModel([("organization_id", ASCENDING), ("recipient.email", ASCENDING)], name="idx_certs_recipient_email"),
            IndexModel([("file.sha256", ASCENDING)], name="idx_certs_file_sha256", sparse=True),
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

        # 16. Issuance Jobs collection (P4)
        jobs_col = db["issuance_jobs"]
        await jobs_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_issuance_jobs_org_created"),
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_issuance_jobs_org_status"),
            IndexModel([("import_id", ASCENDING)], name="idx_issuance_jobs_import_id"),
            IndexModel([("template_id", ASCENDING)], name="idx_issuance_jobs_template_id"),
        ])

        # 17. Issuance Job Items collection (P4)
        items_col = db["issuance_job_items"]
        await items_col.create_indexes([
            IndexModel([("job_id", ASCENDING), ("status", ASCENDING)], name="idx_issuance_items_job_status"),
            IndexModel([("job_id", ASCENDING), ("row_number", ASCENDING)], name="idx_issuance_items_job_row"),
            IndexModel([("job_id", ASCENDING), ("certificate_id", ASCENDING)], name="idx_issuance_items_job_cert"),
            IndexModel([("job_id", ASCENDING), ("import_row_id", ASCENDING)], unique=True, name="uniq_issuance_items_job_row_id"),
            IndexModel([("organization_id", ASCENDING)], name="idx_issuance_items_org_id"),
        ])

        # 18. Verification Events collection (P5)
        events_col = db["verification_events"]
        await events_col.create_indexes([
            IndexModel([("certificate_id", ASCENDING), ("timestamp", ASCENDING)], name="idx_verif_events_cert_ts"),
            IndexModel([("verification_code", ASCENDING), ("timestamp", ASCENDING)], name="idx_verif_events_code_ts"),
            IndexModel([("organization_id", ASCENDING), ("timestamp", ASCENDING)], name="idx_verif_events_org_ts"),
        ])

        # 19. Email Templates collection (P6)
        email_tmpl_col = db["email_templates"]
        await email_tmpl_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("name", ASCENDING)], name="idx_email_tmpl_org_name"),
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_email_tmpl_org_status"),
        ])

        # 20. Email Settings collection (P6)
        email_settings_col = db["email_settings"]
        await email_settings_col.create_indexes([
            IndexModel([("organization_id", ASCENDING)], unique=True, name="uniq_email_settings_org"),
        ])

        # 21. Email Deliveries collection (P6)
        email_deliv_col = db["email_deliveries"]
        await email_deliv_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_email_deliv_org_created"),
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_email_deliv_org_status"),
            IndexModel([("certificate_id", ASCENDING)], name="idx_email_deliv_cert_id"),
            IndexModel([("recipient_email", ASCENDING)], name="idx_email_deliv_recipient"),
            IndexModel([("provider_message_id", ASCENDING)], name="idx_email_deliv_msg_id", sparse=True),
            IndexModel([("email_job_id", ASCENDING)], name="idx_email_deliv_job_id", sparse=True),
        ])

        # 22. Email Jobs collection (P6)
        email_jobs_col = db["email_jobs"]
        await email_jobs_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_email_jobs_org_created"),
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_email_jobs_org_status"),
        ])

        # 23. Email Events collection (P6)
        email_events_col = db["email_events"]
        await email_events_col.create_indexes([
            IndexModel([("delivery_id", ASCENDING), ("timestamp", ASCENDING)], name="idx_email_events_deliv_ts"),
            IndexModel([("provider_event_id", ASCENDING)], unique=True, sparse=True, name="uniq_email_events_provider_event_id"),
        ])

        # 24. Email Suppressions collection (P6)
        email_supp_col = db["email_suppressions"]
        await email_supp_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("email", ASCENDING)], unique=True, name="uniq_email_supp_org_email"),
        ])

        # 25. Report Jobs collection (P7)
        report_jobs_col = db["report_jobs"]
        await report_jobs_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_report_jobs_org_created"),
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_report_jobs_org_status"),
        ])

        # 26. Daily Analytics collection (P7 — pre-aggregated metrics)
        analytics_daily_col = db["analytics_daily"]
        await analytics_daily_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("date", ASCENDING)], unique=True, name="uniq_analytics_daily_org_date"),
            IndexModel([("organization_id", ASCENDING), ("date", ASCENDING)], name="idx_analytics_daily_org_date"),
        ])

        # 27. Organization Invitations collection (P8)
        invitations_col = db["organization_invitations"]
        await invitations_col.create_indexes([
            IndexModel([("token_hash", ASCENDING)], unique=True, name="uniq_invitations_token_hash"),
            IndexModel([("organization_id", ASCENDING), ("email", ASCENDING)], name="idx_invitations_org_email"),
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_invitations_org_status"),
            IndexModel([("expires_at", ASCENDING)], name="idx_invitations_expires_at"),
        ])

        # 28. Custom & System Roles collection (P8)
        roles_col = db["roles"]
        await roles_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("name", ASCENDING)], unique=True, name="uniq_roles_org_name"),
            IndexModel([("organization_id", ASCENDING)], name="idx_roles_org_id"),
        ])

        # 29. Teams collection (P8)
        teams_col = db["teams"]
        await teams_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("name", ASCENDING)], unique=True, name="uniq_teams_org_name"),
            IndexModel([("organization_id", ASCENDING)], name="idx_teams_org_id"),
        ])

        # 30. Team Members collection (P8)
        team_members_col = db["team_members"]
        await team_members_col.create_indexes([
            IndexModel([("team_id", ASCENDING), ("user_id", ASCENDING)], unique=True, name="uniq_team_members_team_user"),
            IndexModel([("organization_id", ASCENDING)], name="idx_team_members_org_id"),
            IndexModel([("user_id", ASCENDING)], name="idx_team_members_user_id"),
        ])

        # 31. API Keys collection (P8)
        api_keys_col = db["api_keys"]
        await api_keys_col.create_indexes([
            IndexModel([("key_hash", ASCENDING)], unique=True, name="uniq_api_keys_hash"),
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_api_keys_org_status"),
            IndexModel([("prefix", ASCENDING)], name="idx_api_keys_prefix"),
        ])

        # 32. Service Accounts collection (P8)
        service_accounts_col = db["service_accounts"]
        await service_accounts_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("name", ASCENDING)], unique=True, name="uniq_service_accounts_org_name"),
            IndexModel([("organization_id", ASCENDING)], name="idx_service_accounts_org_id"),
        ])

        # 33. Idempotency Keys collection (P8)
        idempotency_col = db["idempotency_keys"]
        await idempotency_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("endpoint", ASCENDING), ("key", ASCENDING)], unique=True, name="uniq_idempotency_org_ep_key"),
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0, name="idx_idempotency_ttl"),
        ])

        # 34. Webhook Endpoints collection (P8)
        webhook_ep_col = db["webhook_endpoints"]
        await webhook_ep_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("status", ASCENDING)], name="idx_webhook_ep_org_status"),
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_webhook_ep_org_created"),
        ])

        # 35. Webhook Events collection (P8)
        webhook_events_col = db["webhook_events"]
        await webhook_events_col.create_indexes([
            IndexModel([("event_id", ASCENDING)], unique=True, name="uniq_webhook_events_id"),
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_webhook_events_org_created"),
        ])

        # 36. Webhook Deliveries collection (P8)
        webhook_deliv_col = db["webhook_deliveries"]
        await webhook_deliv_col.create_indexes([
            IndexModel([("webhook_endpoint_id", ASCENDING), ("created_at", ASCENDING)], name="idx_webhook_deliv_ep_created"),
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_webhook_deliv_org_created"),
            IndexModel([("event_id", ASCENDING)], name="idx_webhook_deliv_event_id"),
            IndexModel([("status", ASCENDING)], name="idx_webhook_deliv_status"),
        ])

        # 37. API Usage Events collection (P8)
        api_usage_col = db["api_usage_events"]
        await api_usage_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_api_usage_org_created"),
            IndexModel([("api_key_id", ASCENDING), ("created_at", ASCENDING)], name="idx_api_usage_key_created"),
        ])

        # 38. Password Reset Tokens collection (P9)
        reset_tokens_col = db["password_reset_tokens"]
        await reset_tokens_col.create_indexes([
            IndexModel([("token_hash", ASCENDING)], unique=True, name="uniq_reset_token_hash"),
            IndexModel([("user_id", ASCENDING)], name="idx_reset_token_user"),
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0, name="idx_reset_token_ttl"),
        ])

        # 39. Worker Heartbeats collection (P9)
        heartbeats_col = db["worker_heartbeats"]
        await heartbeats_col.create_indexes([
            IndexModel([("worker_id", ASCENDING)], unique=True, name="uniq_worker_heartbeats_id"),
            IndexModel([("last_seen", ASCENDING)], name="idx_worker_heartbeats_last_seen"),
        ])

        # 40. Plans collection (P10)
        plans_col = db["plans"]
        await plans_col.create_indexes([
            IndexModel([("plan_id", ASCENDING)], unique=True, name="uniq_plans_plan_id"),
            IndexModel([("status", ASCENDING)], name="idx_plans_status"),
        ])

        # 41. Subscriptions collection (P10)
        subs_col = db["subscriptions"]
        await subs_col.create_indexes([
            IndexModel([("organization_id", ASCENDING)], unique=True, name="uniq_subscriptions_org"),
            IndexModel([("status", ASCENDING)], name="idx_subscriptions_status"),
            IndexModel([("provider_subscription_id", ASCENDING)], name="idx_subscriptions_provider_id"),
        ])

        # 42. Billing Customers collection (P10)
        billing_cust_col = db["billing_customers"]
        await billing_cust_col.create_indexes([
            IndexModel([("organization_id", ASCENDING)], unique=True, name="uniq_billing_cust_org"),
            IndexModel([("provider", ASCENDING), ("provider_customer_id", ASCENDING)], name="idx_billing_cust_provider_id"),
        ])

        # 43. Billing Events collection (P10) - Idempotency
        billing_events_col = db["billing_events"]
        await billing_events_col.create_indexes([
            IndexModel([("provider", ASCENDING), ("event_id", ASCENDING)], unique=True, name="uniq_billing_events_prov_id"),
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_billing_events_org_created"),
        ])

        # 44. Invoices collection (P10)
        invoices_col = db["invoices"]
        await invoices_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_invoices_org_created"),
            IndexModel([("provider_invoice_id", ASCENDING)], name="idx_invoices_provider_id"),
            IndexModel([("status", ASCENDING)], name="idx_invoices_status"),
        ])

        # 45. Usage Events collection (P10)
        usage_events_col = db["usage_events"]
        await usage_events_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("metric", ASCENDING), ("period", ASCENDING)], name="idx_usage_events_org_metric_period"),
            IndexModel([("created_at", ASCENDING)], name="idx_usage_events_created"),
        ])

        # 46. Usage Counters collection (P10)
        usage_counters_col = db["usage_counters"]
        await usage_counters_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("metric", ASCENDING), ("period", ASCENDING)], unique=True, name="uniq_usage_counters_key"),
        ])

        # 47. Entitlement Overrides collection (P10)
        entitlement_overrides_col = db["entitlement_overrides"]
        await entitlement_overrides_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("feature", ASCENDING)], name="idx_entitlement_overrides_org_feat"),
        ])

        # 48. Issuer Profiles collection (P11)
        issuer_profiles_col = db["issuer_profiles"]
        await issuer_profiles_col.create_indexes([
            IndexModel([("organization_id", ASCENDING)], unique=True, name="uniq_issuer_profiles_org"),
            IndexModel([("issuer_id", ASCENDING)], unique=True, name="uniq_issuer_profiles_issuer_id"),
            IndexModel([("status", ASCENDING)], name="idx_issuer_profiles_status"),
        ])

        # 49. Achievements collection (P11)
        achievements_col = db["achievements"]
        await achievements_col.create_indexes([
            IndexModel([("organization_id", ASCENDING), ("name", ASCENDING)], name="idx_achievements_org_name"),
            IndexModel([("achievement_id", ASCENDING)], unique=True, name="uniq_achievements_id"),
        ])

        # 50. Credentials collection (P11)
        credentials_col = db["credentials"]
        await credentials_col.create_indexes([
            IndexModel([("credential_id", ASCENDING)], unique=True, name="uniq_credentials_cred_id"),
            IndexModel([("organization_id", ASCENDING), ("created_at", ASCENDING)], name="idx_credentials_org_created"),
            IndexModel([("certificate_id", ASCENDING)], name="idx_credentials_cert_id"),
            IndexModel([("issuer_id", ASCENDING)], name="idx_credentials_issuer_id"),
            IndexModel([("achievement_id", ASCENDING)], name="idx_credentials_achievement_id"),
            IndexModel([("status", ASCENDING)], name="idx_credentials_status"),
            IndexModel([("verification_code", ASCENDING)], name="idx_credentials_verification_code"),
        ])

        # 51. Credential Status collection (P11)
        credential_status_col = db["credential_status"]
        await credential_status_col.create_indexes([
            IndexModel([("credential_id", ASCENDING)], unique=True, name="uniq_credential_status_id"),
            IndexModel([("status", ASCENDING)], name="idx_credential_status_status"),
        ])

        # 52. Credential Keys collection (P11)
        credential_keys_col = db["credential_keys"]
        await credential_keys_col.create_indexes([
            IndexModel([("issuer_id", ASCENDING), ("key_id", ASCENDING)], unique=True, name="uniq_credential_keys_issuer_key"),
            IndexModel([("organization_id", ASCENDING)], name="idx_credential_keys_org"),
            IndexModel([("status", ASCENDING)], name="idx_credential_keys_status"),
        ])

        # 53. Credential Evidence collection (P11)
        credential_evidence_col = db["credential_evidence"]
        await credential_evidence_col.create_indexes([
            IndexModel([("credential_id", ASCENDING)], name="idx_credential_evidence_cred_id"),
        ])

        # 54. Credential Events collection (P11)
        credential_events_col = db["credential_events"]
        await credential_events_col.create_indexes([
            IndexModel([("credential_id", ASCENDING), ("created_at", ASCENDING)], name="idx_credential_events_cred_created"),
        ])

        logger.info("MongoDB indexes verified successfully.")


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency provider for FastAPI route handlers."""
    return DatabaseManager.get_db()
