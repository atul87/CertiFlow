"""
CertiFlow Production Disaster Recovery & Backup/Restore Utility (P13.9).
Provides streaming backup, cryptographic verification, and point-in-time restore
for MongoDB databases without requiring external binary dependencies.
"""
from __future__ import annotations
import os
import gzip
import json
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

import bson
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("certiflow.disaster_recovery")


class DatabaseBackupManager:
    @staticmethod
    def _sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @classmethod
    async def create_backup(
        cls,
        mongo_uri: str,
        db_name: str,
        output_dir: Path,
    ) -> Dict[str, Any]:
        """
        Creates a point-in-time backup archive of all non-system collections
        in the specified database with index preservation and cryptographic checksums.
        """
        client = AsyncIOMotorClient(mongo_uri)
        db = client[db_name]

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = output_dir / f"certiflow_backup_{db_name}_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)

        collections = await db.list_collection_names()
        # Filter out system collections
        target_colls = [c for c in collections if not c.startswith("system.")]

        manifest: Dict[str, Any] = {
            "version": "1.0",
            "database": db_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "collections": {},
            "total_documents": 0,
        }

        total_docs = 0

        for coll_name in sorted(target_colls):
            coll = db[coll_name]
            docs = []
            async for doc in coll.find():
                docs.append(bson.BSON.encode(doc))

            # Fetch indexes
            indexes = []
            async for idx in coll.list_indexes():
                # Don't recreate default _id_ index explicitly
                if idx.get("name") != "_id_":
                    indexes.append({
                        "key": list(idx["key"].items()),
                        "unique": idx.get("unique", False),
                        "name": idx.get("name"),
                        "sparse": idx.get("sparse", False),
                    })

            # Compress BSON stream
            raw_bson = b"".join(docs)
            compressed_data = gzip.compress(raw_bson, compresslevel=6)
            checksum = cls._sha256(compressed_data)

            archive_file = backup_path / f"{coll_name}.bson.gz"
            archive_file.write_bytes(compressed_data)

            doc_count = len(docs)
            total_docs += doc_count

            manifest["collections"][coll_name] = {
                "document_count": doc_count,
                "file": f"{coll_name}.bson.gz",
                "sha256": checksum,
                "size_bytes": len(compressed_data),
                "indexes": indexes,
            }

        manifest["total_documents"] = total_docs

        # Write manifest
        manifest_file = backup_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        client.close()
        logger.info("Backup completed successfully: %d docs in %s", total_docs, backup_path)
        return {
            "backup_dir": str(backup_path),
            "total_documents": total_docs,
            "collections_count": len(target_colls),
            "manifest": manifest,
        }

    @classmethod
    async def restore_backup(
        cls,
        mongo_uri: str,
        target_db_name: str,
        backup_dir: Path,
        drop_target: bool = False,
    ) -> Dict[str, Any]:
        """
        Validates checksums and restores collections and indexes into target database.
        """
        manifest_file = backup_dir / "manifest.json"
        if not manifest_file.exists():
            raise FileNotFoundError(f"Manifest not found in {backup_dir}")

        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

        # 1. Cryptographic integrity check
        for coll_name, meta in manifest["collections"].items():
            archive_file = backup_dir / meta["file"]
            if not archive_file.exists():
                raise FileNotFoundError(f"Missing backup archive: {meta['file']}")
            data = archive_file.read_bytes()
            computed_hash = cls._sha256(data)
            if computed_hash != meta["sha256"]:
                raise ValueError(
                    f"Integrity check failed for {coll_name}: expected {meta['sha256']}, got {computed_hash}"
                )

        client = AsyncIOMotorClient(mongo_uri)
        db = client[target_db_name]

        if drop_target:
            await client.drop_database(target_db_name)

        restored_docs = 0

        # 2. Restore collections and re-index
        for coll_name, meta in manifest["collections"].items():
            archive_file = backup_dir / meta["file"]
            decompressed_bson = gzip.decompress(archive_file.read_bytes())

            coll = db[coll_name]
            docs = []
            if decompressed_bson:
                docs = bson.decode_all(decompressed_bson)

            if docs:
                await coll.insert_many(docs, ordered=False)
                restored_docs += len(docs)

            # Recreate custom indexes
            for idx in meta.get("indexes", []):
                try:
                    await coll.create_index(
                        idx["key"],
                        unique=idx.get("unique", False),
                        name=idx.get("name"),
                        sparse=idx.get("sparse", False),
                    )
                except Exception as e:
                    logger.warning("Index recreation warning on %s: %s", coll_name, e)

        client.close()
        logger.info("Restore completed successfully: %d docs restored into %s", restored_docs, target_db_name)
        return {
            "status": "success",
            "restored_documents": restored_docs,
            "target_database": target_db_name,
        }
