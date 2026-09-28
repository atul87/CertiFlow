import io
import pytest
from PIL import Image
from httpx import AsyncClient


def create_dummy_png(width: int = 800, height: int = 600, color: str = "blue") -> bytes:
    img = Image.new("RGBA", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_asset_upload_valid_image(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Create a template
    t_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Asset Test Template"})
    template_id = t_resp.json()["data"]["id"]

    # 2. Upload PNG background
    png_bytes = create_dummy_png(1200, 800)
    files = {"file": ("cert_bg.png", png_bytes, "image/png")}
    data = {"asset_type": "background"}

    upload_resp = await client.post(
        f"/api/v1/templates/{template_id}/assets",
        headers=headers,
        files=files,
        data=data
    )
    assert upload_resp.status_code == 201
    asset_data = upload_resp.json()["data"]
    asset_id = asset_data["id"]

    assert asset_data["filename"] == "cert_bg.png"
    assert asset_data["mime_type"] == "image/png"
    assert asset_data["width"] == 1200
    assert asset_data["height"] == 800
    assert asset_data["asset_type"] == "background"

    # 3. List assets
    list_resp = await client.get(f"/api/v1/templates/{template_id}/assets", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) >= 1

    # 4. Delete asset
    del_resp = await client.delete(f"/api/v1/templates/{template_id}/assets/{asset_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True


@pytest.mark.asyncio
async def test_asset_upload_invalid_file(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    t_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Invalid File Test"})
    template_id = t_resp.json()["data"]["id"]

    # Upload non-image garbage file
    files = {"file": ("corrupt.png", b"this is definitely not a real png image file", "image/png")}
    resp = await client.post(
        f"/api/v1/templates/{template_id}/assets",
        headers=headers,
        files=files,
        data={"asset_type": "background"}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "INVALID_IMAGE_FILE"


@pytest.mark.asyncio
async def test_template_preview_generation(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # Create template
    t_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Preview Test Template"})
    template_id = t_resp.json()["data"]["id"]

    # Request preview with custom sample data
    preview_payload = {
        "sample_data": {
            "recipient_name": "Dr. Sarah Connor",
            "program_name": "Robotics & Cybernetic Systems"
        }
    }
    prev_resp = await client.post(
        f"/api/v1/templates/{template_id}/preview",
        headers=headers,
        json=preview_payload
    )
    assert prev_resp.status_code == 200
    body = prev_resp.json()
    assert body["success"] is True
    pdata = body["data"]

    assert pdata["format"] == "png"
    assert pdata["preview_url"].startswith("data:image/png;base64,")
    assert len(pdata["preview_url"]) > 1000


@pytest.mark.asyncio
async def test_list_fonts(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    resp = await client.get("/api/v1/fonts", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    fonts = body["data"]

    font_families = [f["family"] for f in fonts]
    assert "Inter" in font_families
    assert "Poppins" in font_families
    assert "Playfair Display" in font_families
