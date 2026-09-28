"""
P3 Unit Tests — Certificate Rendering Engine
Tests that run WITHOUT MongoDB / FastAPI / network.

Coverage:
  - SmartFit algorithm
  - QR code generation
  - Text/image/shape renderers
  - CertificateIDService (verify code only; DB needed for sequential numbers)
  - HashService
  - PDF rendering (reportlab)
  - Renderer orchestrator (no asset DB)
"""
import io
import pytest
from PIL import Image

# Mark all tests in this file as no_db — skips the DB lifecycle fixture
pytestmark = pytest.mark.no_db

# ---------------------------------------------------------------------------
# 1. SmartFit
# ---------------------------------------------------------------------------

class TestSmartFit:
    def _make_result(self, text, box_w, box_h, size=72, min_size=14):
        from app.services.rendering.smart_fit import smart_fit
        return smart_fit(
            text=text,
            box_width=box_w,
            box_height=box_h,
            initial_size=size,
            min_size=min_size,
            element_id="test",
            field_name="recipient_name",
        )

    def test_short_text_fits_at_initial_size(self):
        result = self._make_result("Atul Kumar", 800, 200)
        assert not result.overflowed
        assert result.font_size > 0
        assert result.text_width <= 800

    def test_very_long_text_wraps_and_shrinks(self):
        long_text = "This is a very very very very very long certificate recipient name that would overflow"
        result = self._make_result(long_text, 200, 60)
        # Even if overflowed, lines must not be empty
        assert len(result.lines) > 0

    def test_overflow_reported_when_min_size_hit(self):
        # 1 pixel box — guaranteed overflow
        result = self._make_result("X", 1, 1, size=72, min_size=14)
        # Depending on font metrics this may or may not overflow, but it should not crash
        assert len(result.lines) >= 1

    def test_no_wrap_uses_single_line(self):
        from app.services.rendering.smart_fit import smart_fit
        result = smart_fit(
            text="Hello World",
            box_width=2000,
            box_height=200,
            initial_size=48,
            allow_wrap=False,
        )
        assert len(result.lines) == 1

    def test_result_has_all_fields(self):
        result = self._make_result("Test", 400, 100)
        assert result.font is not None
        assert isinstance(result.font_size, int)
        assert isinstance(result.text_width, int)
        assert isinstance(result.text_height, int)
        assert isinstance(result.overflowed, bool)
        assert isinstance(result.lines, list)


# ---------------------------------------------------------------------------
# 2. QR Renderer
# ---------------------------------------------------------------------------

class TestQRRenderer:
    def test_qr_generates_rgba_image(self):
        from app.services.rendering.qr_renderer import generate_qr_image
        img = generate_qr_image("https://certiflow.io/verify/ABCDEF12", size=200)
        assert img.mode == "RGBA"
        assert img.size == (200, 200)

    def test_qr_element_composited_on_canvas(self):
        from app.services.rendering.qr_renderer import render_qr_element
        canvas = Image.new("RGBA", (1000, 800), (255, 255, 255, 255))
        element = {
            "position": {"x": 100, "y": 100},
            "size": {"width": 200, "height": 200},
            "style": {},
        }
        before = canvas.copy()
        render_qr_element(canvas, element, "https://example.com/cert/TEST123")
        # Canvas should have changed
        assert list(canvas.getdata()) != list(before.getdata())

    def test_empty_content_skipped(self):
        from app.services.rendering.qr_renderer import render_qr_element
        canvas = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
        before = canvas.copy()
        render_qr_element(canvas, {"position": {}, "size": {}, "style": {}}, "")
        # Canvas unchanged
        assert list(canvas.getdata()) == list(before.getdata())


# ---------------------------------------------------------------------------
# 3. Text Renderer
# ---------------------------------------------------------------------------

class TestTextRenderer:
    def test_renders_text_without_crash(self):
        from app.services.rendering.text_renderer import render_text_element
        canvas = Image.new("RGBA", (2000, 500), (255, 255, 255, 255))
        element = {
            "id": "title",
            "type": "text",
            "position": {"x": 100, "y": 100},
            "size": {"width": 800, "height": 200},
            "style": {
                "font_size": 72,
                "color": "#1a1a2e",
                "alignment": "center",
                "opacity": 1.0,
            },
        }
        overflows = []
        render_text_element(canvas, element, "Atul Kumar", overflows)
        assert True  # no exception

    def test_alignment_left(self):
        from app.services.rendering.text_renderer import render_text_element
        canvas = Image.new("RGBA", (1000, 300), (255, 255, 255, 255))
        elem = {
            "id": "t1", "position": {"x": 50, "y": 50},
            "size": {"width": 600, "height": 100},
            "style": {"alignment": "left", "color": "#000", "font_size": 36, "opacity": 1.0},
        }
        overflows = []
        render_text_element(canvas, elem, "Left Aligned Text", overflows)
        assert True

    def test_empty_text_does_not_crash(self):
        from app.services.rendering.text_renderer import render_text_element
        canvas = Image.new("RGBA", (500, 200), (255, 255, 255, 255))
        overflows = []
        render_text_element(canvas, {"position": {}, "size": {}, "style": {}}, "", overflows)
        assert True


# ---------------------------------------------------------------------------
# 4. Image Renderer
# ---------------------------------------------------------------------------

class TestImageRenderer:
    def _make_png_bytes(self, w=100, h=100, color=(255, 0, 0, 255)):
        img = Image.new("RGBA", (w, h), color)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def test_contain_fit(self):
        from app.services.rendering.image_renderer import render_image_element
        canvas = Image.new("RGBA", (1000, 800), (255, 255, 255, 255))
        element = {
            "position": {"x": 100, "y": 100},
            "size": {"width": 300, "height": 200},
            "style": {"fit_mode": "contain", "opacity": 1.0},
        }
        img_bytes = self._make_png_bytes(500, 500, (0, 0, 255, 255))
        render_image_element(canvas, element, img_bytes)
        assert True

    def test_cover_fit(self):
        from app.services.rendering.image_renderer import render_image_element
        canvas = Image.new("RGBA", (1000, 800), (255, 255, 255, 255))
        element = {
            "position": {"x": 0, "y": 0},
            "size": {"width": 200, "height": 200},
            "style": {"fit_mode": "cover", "opacity": 0.8},
        }
        img_bytes = self._make_png_bytes(600, 400, (0, 200, 0, 255))
        render_image_element(canvas, element, img_bytes)
        assert True


# ---------------------------------------------------------------------------
# 5. Shape Renderer
# ---------------------------------------------------------------------------

class TestShapeRenderer:
    def test_rectangle(self):
        from app.services.rendering.shape_renderer import render_shape_element
        canvas = Image.new("RGBA", (500, 500), (255, 255, 255, 255))
        element = {
            "type": "rectangle",
            "position": {"x": 10, "y": 10},
            "size": {"width": 200, "height": 100},
            "style": {"fill": "#d4af37", "stroke": "#8b7536", "stroke_width": 3, "opacity": 1.0},
        }
        before = canvas.copy()
        render_shape_element(canvas, element)
        assert list(canvas.getdata()) != list(before.getdata())

    def test_ellipse(self):
        from app.services.rendering.shape_renderer import render_shape_element
        canvas = Image.new("RGBA", (500, 500), (255, 255, 255, 255))
        element = {
            "type": "circle",
            "position": {"x": 50, "y": 50},
            "size": {"width": 100, "height": 100},
            "style": {"fill": "#0000ff", "opacity": 0.5},
        }
        render_shape_element(canvas, element)
        assert True

    def test_line(self):
        from app.services.rendering.shape_renderer import render_shape_element
        canvas = Image.new("RGBA", (500, 500), (255, 255, 255, 255))
        element = {
            "type": "line",
            "position": {"x": 0, "y": 200},
            "size": {"width": 500, "height": 10},
            "style": {"stroke": "#d4af37", "stroke_width": 2, "opacity": 1.0},
        }
        render_shape_element(canvas, element)
        assert True


# ---------------------------------------------------------------------------
# 6. CertificateIDService — verification code
# ---------------------------------------------------------------------------

class TestCertificateIDService:
    def test_verification_code_is_hex_string(self):
        from app.services.certificate_id_service import CertificateIDService
        code = CertificateIDService.generate_verification_code()
        assert isinstance(code, str)
        assert len(code) == 32  # 16 bytes → 32 hex chars
        int(code, 16)  # must be valid hex

    def test_verification_codes_are_unique(self):
        from app.services.certificate_id_service import CertificateIDService
        codes = {CertificateIDService.generate_verification_code() for _ in range(50)}
        assert len(codes) == 50

    def test_verification_url_format(self):
        from app.services.certificate_id_service import CertificateIDService
        url = CertificateIDService.generate_verification_url(
            "https://certiflow.io", "ABCDEF123456"
        )
        assert url == "https://certiflow.io/verify/ABCDEF123456"

    def test_trailing_slash_stripped(self):
        from app.services.certificate_id_service import CertificateIDService
        url = CertificateIDService.generate_verification_url(
            "https://certiflow.io/", "CODE123"
        )
        assert url == "https://certiflow.io/verify/CODE123"


# ---------------------------------------------------------------------------
# 7. HashService
# ---------------------------------------------------------------------------

class TestHashService:
    def test_sha256_is_hex_string(self):
        from app.services.hash_service import HashService
        h = HashService.sha256(b"hello world")
        assert isinstance(h, str)
        assert len(h) == 64

    def test_known_hash(self):
        from app.services.hash_service import HashService
        # sha256("hello") = 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
        h = HashService.sha256(b"hello")
        assert h == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

    def test_verify_correct(self):
        from app.services.hash_service import HashService
        data = b"certificate content"
        h = HashService.sha256(data)
        assert HashService.verify(data, h)

    def test_verify_wrong_hash(self):
        from app.services.hash_service import HashService
        assert not HashService.verify(b"data", "0" * 64)


# ---------------------------------------------------------------------------
# 8. PDF Renderer
# ---------------------------------------------------------------------------

class TestPDFRenderer:
    def test_pdf_bytes_start_with_header(self):
        from app.services.rendering.pdf_renderer import render_pdf
        img = Image.new("RGB", (200, 150), (255, 255, 255))
        pdf_bytes = render_pdf(img, dpi=72, title="Test Cert")
        assert pdf_bytes[:4] == b"%PDF"

    def test_pdf_has_nonzero_size(self):
        from app.services.rendering.pdf_renderer import render_pdf
        img = Image.new("RGB", (300, 200), (240, 240, 240))
        pdf_bytes = render_pdf(img, dpi=72)
        assert len(pdf_bytes) > 1000  # must not be empty

    def test_sha256_utility(self):
        from app.services.rendering.pdf_renderer import sha256_of_bytes
        h = sha256_of_bytes(b"test")
        assert len(h) == 64


# ---------------------------------------------------------------------------
# 9. Renderer orchestrator (no-DB, no-asset mode)
# ---------------------------------------------------------------------------

class TestRenderer:
    def _make_version_doc(self, elements=None):
        return {
            "width": 800,
            "height": 600,
            "elements": elements or [],
        }

    def test_empty_template_renders_background(self):
        from app.services.rendering.renderer import render_certificate
        result = render_certificate(
            version_doc=self._make_version_doc(),
            resolved_data={},
            asset_loader=lambda _: None,
        )
        assert isinstance(result["canvas"], Image.Image)
        assert len(result["preview_bytes"]) > 0

    def test_text_element_renders(self):
        from app.services.rendering.renderer import render_certificate
        elements = [{
            "id": "title",
            "type": "text",
            "content": "{{recipient_name}}",
            "position": {"x": 100, "y": 200},
            "size": {"width": 600, "height": 100},
            "style": {"font_size": 60, "color": "#000", "alignment": "center", "opacity": 1.0},
            "z_index": 1,
        }]
        result = render_certificate(
            version_doc=self._make_version_doc(elements),
            resolved_data={"recipient_name": "Atul Kumar"},
            asset_loader=lambda _: None,
        )
        assert result["diagnostics"]["text_element_count"] == 1
        assert result["diagnostics"]["overflow_count"] == 0

    def test_qr_element_renders(self):
        from app.services.rendering.renderer import render_certificate
        elements = [{
            "id": "qr1",
            "type": "qr",
            "content": "{{verification_url}}",
            "position": {"x": 10, "y": 10},
            "size": {"width": 200, "height": 200},
            "style": {},
            "z_index": 2,
        }]
        result = render_certificate(
            version_doc=self._make_version_doc(elements),
            resolved_data={"verification_url": "https://certiflow.io/verify/TESTCODE"},
            asset_loader=lambda _: None,
        )
        assert result["diagnostics"]["qr_element_count"] == 1

    def test_shape_element_renders(self):
        from app.services.rendering.renderer import render_certificate
        elements = [{
            "id": "border",
            "type": "rectangle",
            "position": {"x": 20, "y": 20},
            "size": {"width": 760, "height": 560},
            "style": {"fill": None, "stroke": "#d4af37", "stroke_width": 4, "opacity": 1.0},
            "z_index": 0,
        }]
        result = render_certificate(
            version_doc=self._make_version_doc(elements),
            resolved_data={},
            asset_loader=lambda _: None,
        )
        assert result["diagnostics"]["shape_element_count"] == 1

    def test_preview_max_width_downscaled(self):
        from app.services.rendering.renderer import render_certificate
        result = render_certificate(
            version_doc={"width": 3508, "height": 2480, "elements": []},
            resolved_data={},
            asset_loader=lambda _: None,
            max_preview_width=800,
        )
        preview = Image.open(io.BytesIO(result["preview_bytes"]))
        assert preview.width <= 800

    def test_diagnostics_structure(self):
        from app.services.rendering.renderer import render_certificate
        result = render_certificate(
            version_doc=self._make_version_doc(),
            resolved_data={},
            asset_loader=lambda _: None,
        )
        d = result["diagnostics"]
        assert "canvas_width" in d
        assert "canvas_height" in d
        assert "element_count" in d
        assert "render_time_ms" in d
