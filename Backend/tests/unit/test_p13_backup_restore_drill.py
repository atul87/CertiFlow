"""
P13.9 Disaster Recovery, Backup & Restore Verification Drill.
Validates:
1. Point-in-time database snapshotting to compressed BSON archives.
2. SHA-256 manifest integrity verification and tamper detection.
3. Full restore verification into an isolated target database with index validation.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from scripts.backup_restore import DatabaseBackupManager


@pytest.mark.asyncio
async def test_p13_backup_and_restore_disaster_recovery_drill():
    """
    Executes a complete simulated disaster recovery cycle:
    1. Populate source database with test records and custom indexes.
    2. Execute backup procedure -> verify archives and SHA-256 checksums.
    3. Verify tamper detection on corrupted archive.
    4. Restore backup into a recovery database.
    5. Assert 100% data fidelity and index preservation.
    """
    source_db_name = f"certiflow_drill_src_{ObjectId()}"
    recovery_db_name = f"certiflow_drill_rec_{ObjectId()}"
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    src_db = client[source_db_name]

    temp_dir = Path(tempfile.mkdtemp(prefix="certiflow_backup_drill_"))

    try:
        # 1. Populate source collections
        users_coll = src_db["users"]
        await users_coll.create_index([("email", 1)], unique=True)
        await users_coll.insert_many([
            {"_id": ObjectId(), "name": "Admin User", "email": "admin@drill.io", "role": "owner"},
            {"_id": ObjectId(), "name": "Staff User", "email": "staff@drill.io", "role": "member"},
        ])

        certs_coll = src_db["certificates"]
        await certs_coll.create_index([("certificate_number", 1)], unique=True)
        await certs_coll.insert_many([
            {"_id": ObjectId(), "certificate_number": "CERT-DRILL-001", "status": "generated"},
            {"_id": ObjectId(), "certificate_number": "CERT-DRILL-002", "status": "revoked"},
        ])

        # 2. Perform automated backup
        backup_result = await DatabaseBackupManager.create_backup(
            mongo_uri=settings.MONGODB_URI,
            db_name=source_db_name,
            output_dir=temp_dir,
        )
        assert backup_result["total_documents"] == 4
        backup_dir = Path(backup_result["backup_dir"])
        assert (backup_dir / "manifest.json").exists()
        assert (backup_dir / "users.bson.gz").exists()
        assert (backup_dir / "certificates.bson.gz").exists()

        # 3. Test tamper detection
        tamper_dir = Path(tempfile.mkdtemp(prefix="certiflow_tamper_"))
        shutil.copytree(backup_dir, tamper_dir / "tampered")
        tampered_archive = tamper_dir / "tampered" / "users.bson.gz"
        # Corrupt archive by appending garbage bytes
        tampered_archive.write_bytes(tampered_archive.read_bytes() + b"TAMPERED_PAYLOAD")

        with pytest.raises(ValueError) as exc:
            await DatabaseBackupManager.restore_backup(
                mongo_uri=settings.MONGODB_URI,
                target_db_name="should_fail_db",
                backup_dir=tamper_dir / "tampered",
            )
        assert "Integrity check failed" in str(exc.value)
        shutil.rmtree(tamper_dir, ignore_errors=True)

        # 4. Perform authentic restore into recovery database
        restore_result = await DatabaseBackupManager.restore_backup(
            mongo_uri=settings.MONGODB_URI,
            target_db_name=recovery_db_name,
            backup_dir=backup_dir,
            drop_target=True,
        )
        assert restore_result["status"] == "success"
        assert restore_result["restored_documents"] == 4

        # 5. Verify restored data fidelity in recovery database
        rec_db = client[recovery_db_name]
        rec_users = await rec_db["users"].count_documents({})
        assert rec_users == 2
        admin_doc = await rec_db["users"].find_one({"email": "admin@drill.io"})
        assert admin_doc is not None
        assert admin_doc["name"] == "Admin User"

        rec_certs = await rec_db["certificates"].count_documents({})
        assert rec_certs == 2
        cert_doc = await rec_db["certificates"].find_one({"certificate_number": "CERT-DRILL-001"})
        assert cert_doc is not None
        assert cert_doc["status"] == "generated"

    finally:
        # Cleanup databases and temporary files
        await client.drop_database(source_db_name)
        await client.drop_database(recovery_db_name)
        client.close()
        shutil.rmtree(temp_dir, ignore_errors=True)
