"""Tests for confidence bands"""

import pytest

from vif.confidence_bands import (
    ConfidenceBand,
    BandDefinition,
    determine_band,
    get_band_definition,
    format_confidence_for_user,
    format_band_badge,
    get_confidence_color,
    get_recommended_action,
    should_show_warning,
    get_all_band_info,
    BandRouter,
    STANDARD_BANDS,
)


def test_standard_bands_defined():
    """Test standard bands are properly defined"""
    assert ConfidenceBand.A in STANDARD_BANDS
    assert ConfidenceBand.B in STANDARD_BANDS
    assert ConfidenceBand.C in STANDARD_BANDS
    
    band_a = STANDARD_BANDS[ConfidenceBand.A]
    assert band_a.min_confidence == 0.90
    assert band_a.color == "green"


def test_determine_band_high():
    """Test band determination for high confidence"""
    assert determine_band(0.95) == ConfidenceBand.A
    assert determine_band(0.90) == ConfidenceBand.A


def test_determine_band_medium():
    """Test band determination for medium confidence"""
    assert determine_band(0.80) == ConfidenceBand.B
    assert determine_band(0.70) == ConfidenceBand.B


def test_determine_band_low():
    """Test band determination for low confidence"""
    assert determine_band(0.65) == ConfidenceBand.C
    assert determine_band(0.50) == ConfidenceBand.C


def test_determine_band_edge_cases():
    """Test band determination at boundaries"""
    assert determine_band(0.899) == ConfidenceBand.B
    assert determine_band(0.900) == ConfidenceBand.A
    assert determine_band(0.699) == ConfidenceBand.C
    assert determine_band(0.700) == ConfidenceBand.B


def test_get_band_definition():
    """Test getting band definition"""
    defn = get_band_definition(ConfidenceBand.A)
    
    assert defn.band == ConfidenceBand.A
    assert defn.name == "High Confidence"
    assert defn.emoji == "🟢"


def test_format_confidence_full():
    """Test full confidence formatting"""
    formatted = format_confidence_for_user(0.95)
    
    assert "🟢" in formatted
    assert "95%" in formatted
    assert "highly reliable" in formatted.lower()


def test_format_confidence_no_emoji():
    """Test formatting without emoji"""
    formatted = format_confidence_for_user(0.95, include_emoji=False)
    
    assert "🟢" not in formatted
    assert "95%" in formatted


def test_format_confidence_no_percentage():
    """Test formatting without percentage"""
    formatted = format_confidence_for_user(0.95, include_percentage=False)
    
    assert "%" not in formatted
    assert "🟢" in formatted


def test_format_confidence_no_message():
    """Test formatting without message"""
    formatted = format_confidence_for_user(0.95, include_message=False)
    
    assert "🟢" in formatted
    assert "95%" in formatted
    assert "reliable" not in formatted.lower()


def test_format_band_badge():
    """Test band badge formatting"""
    badge = format_band_badge(ConfidenceBand.A)
    assert "🟢" in badge
    assert "Band A" in badge


def test_get_confidence_color():
    """Test color extraction"""
    assert get_confidence_color(0.95) == "green"
    assert get_confidence_color(0.75) == "yellow"
    assert get_confidence_color(0.50) == "red"


def test_get_recommended_action():
    """Test recommended action extraction"""
    action_a = get_recommended_action(0.95)
    assert "trust" in action_a.lower()
    
    action_b = get_recommended_action(0.75)
    assert "review" in action_b.lower()
    
    action_c = get_recommended_action(0.50)
    assert "verify" in action_c.lower()


def test_should_show_warning():
    """Test warning indicator"""
    assert should_show_warning(0.95) is False  # Band A
    assert should_show_warning(0.75) is False  # Band B
    assert should_show_warning(0.50) is True   # Band C


def test_get_all_band_info():
    """Test getting all band info"""
    info = get_all_band_info()
    
    assert len(info) == 3
    assert all("band" in item for item in info)
    assert all("color" in item for item in info)
    assert all("emoji" in item for item in info)


def test_band_router_initialization():
    """Test BandRouter initialization"""
    router = BandRouter()
    
    assert ConfidenceBand.A in router.auto_proceed_bands
    assert ConfidenceBand.C in router.review_required_bands


def test_band_router_auto_proceed():
    """Test routing high confidence to auto-proceed"""
    router = BandRouter()
    
    routing = router.route(0.95)
    assert routing == "auto_proceed"
    assert router.can_auto_proceed(0.95) is True


def test_band_router_review_required():
    """Test routing low confidence to review"""
    router = BandRouter()
    
    routing = router.route(0.50)
    assert routing == "review_required"
    assert router.can_auto_proceed(0.50) is False


def test_band_router_notify():
    """Test routing medium confidence to notify"""
    router = BandRouter()
    
    routing = router.route(0.75)
    assert routing == "notify"


def test_band_router_custom_config():
    """Test custom router configuration"""
    # Strict: Only Band A auto-proceeds
    router = BandRouter(
        auto_proceed_bands=[ConfidenceBand.A],
        review_required_bands=[ConfidenceBand.B, ConfidenceBand.C]
    )
    
    assert router.route(0.95) == "auto_proceed"
    assert router.route(0.75) == "review_required"
    assert router.route(0.50) == "review_required"


def test_all_bands_have_definitions():
    """Test all enum bands have definitions"""
    for band in ConfidenceBand:
        defn = get_band_definition(band)
        assert defn.band == band
        assert defn.color in ["green", "yellow", "red"]
        assert len(defn.emoji) > 0


def test_band_ranges_non_overlapping():
    """Test band ranges don't overlap"""
    bands = list(STANDARD_BANDS.values())
    
    # Sort by min confidence
    bands_sorted = sorted(bands, key=lambda b: b.min_confidence)
    
    for i in range(len(bands_sorted) - 1):
        current = bands_sorted[i]
        next_band = bands_sorted[i + 1]
        
        # Current max should be less than next min
        assert current.max_confidence <= next_band.min_confidence


def test_band_ranges_cover_full_spectrum():
    """Test bands cover entire 0-1 range"""
    assert STANDARD_BANDS[ConfidenceBand.C].min_confidence == 0.0
    assert STANDARD_BANDS[ConfidenceBand.A].max_confidence == 1.0


def test_realistic_ui_display():
    """Test realistic UI display formatting"""
    confidences = [0.95, 0.75, 0.50]
    
    for conf in confidences:
        display = format_confidence_for_user(conf)
        band = determine_band(conf)
        color = get_confidence_color(conf)
        action = get_recommended_action(conf)
        
        assert len(display) > 0
        assert isinstance(band, ConfidenceBand)
        assert color in ["green", "yellow", "red"]
        assert len(action) > 0

