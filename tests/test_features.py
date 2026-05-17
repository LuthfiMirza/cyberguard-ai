from src.features import extract_url_features


def test_https_url():
    features = extract_url_features("https://www.example.com/path")
    assert features["has_https"] == 1
    assert features["url_length"] > 0


def test_ip_address_url():
    features = extract_url_features("http://192.168.1.1/login")
    assert features["has_ip_address"] == 1


def test_empty_url():
    features = extract_url_features("")
    assert features["url_length"] == 0
    assert features["digit_ratio"] == 0.0


def test_suspicious_words():
    features = extract_url_features("http://secure-login-verify.example.com")
    assert features["has_suspicious_words"] == 1

def test_hybrid_url_features():
    features = extract_url_features("http://secure-payment-example.xyz/login?token=123")
    assert features["suspicious_keyword_count"] >= 2
    assert features["suspicious_tld_flag"] == 1
    assert features["count_percent"] == 0
