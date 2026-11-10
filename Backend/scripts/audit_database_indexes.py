import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import DatabaseManager

async def check():
    await DatabaseManager.connect()
    db = DatabaseManager.get_db()
    collections = await db.list_collection_names()
    print("=" * 70)
    print("MONGODB ENTERPRISE DATABASE & INDEX ARCHITECTURE AUDIT")
    print("=" * 70)
    print(f"Total Collections: {len(collections)}")
    
    total_indexes = 0
    ttl_indexes = []
    unique_indexes = []
    collection_stats = []

    for coll_name in sorted(collections):
        indexes = await db[coll_name].index_information()
        count = await db[coll_name].count_documents({})
        total_indexes += len(indexes)
        idx_names = []
        for idx_name, idx_info in indexes.items():
            if "expireAfterSeconds" in idx_info:
                ttl_sec = idx_info["expireAfterSeconds"]
                ttl_indexes.append(f"{coll_name}.{idx_name} (TTL: {ttl_sec}s / {ttl_sec//86400 if ttl_sec>=86400 else ttl_sec//3600}d)")
            if idx_info.get("unique"):
                unique_indexes.append(f"{coll_name}.{idx_name}")
            idx_names.append(idx_name)
        collection_stats.append((coll_name, count, len(indexes), idx_names))

    print(f"Total Active Indexes: {total_indexes}")
    print(f"Total Unique Constraints: {len(unique_indexes)}")
    print(f"Total TTL Auto-Purge Indexes: {len(ttl_indexes)}")
    
    print("\n[TTL Automatic Purge Policies]")
    for ttl in sorted(ttl_indexes):
        print(f"  ✓ {ttl}")

    print("\n[Sample High-Value Unique & Compound Constraints (First 15)]")
    for u in sorted(unique_indexes)[:15]:
        print(f"  ✓ {u}")
    if len(unique_indexes) > 15:
        print(f"  ... and {len(unique_indexes) - 15} more unique constraints enforced across collections")

    print("\n[Collection Breakdown & Document Inventory]")
    for name, cnt, idx_cnt, _ in sorted(collection_stats, key=lambda x: x[1], reverse=True)[:20]:
        print(f"  - {name:<35} documents: {cnt:<6} indexes: {idx_cnt}")

    print("=" * 70)
    await DatabaseManager.close()

if __name__ == "__main__":
    asyncio.run(check())
