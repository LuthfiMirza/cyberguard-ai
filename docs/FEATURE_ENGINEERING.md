# Feature Engineering

CyberGuard AI menggunakan dua kelompok fitur: URL structural features dan email NLP features.

## URL Structural Features

- `url_length`
- `domain_length`
- `path_length`
- `count_dots`
- `count_hyphens`
- `count_at`
- `count_question`
- `count_equal`
- `count_percent`
- `count_digits`
- `has_https`
- `has_ip_address`
- `subdomain_count`
- `suspicious_keyword_count`
- `suspicious_tld_flag`

Keyword mencurigakan contoh: `login`, `verify`, `secure`, `account`, `update`, `banking`, `password`, `confirm`, `wallet`, `payment`.

TLD mencurigakan contoh: `xyz`, `top`, `click`, `work`, `country`, `stream`, `gq`, `tk`, `ml`, `cf`.

## Email NLP Features

Jika dataset memiliki `subject` dan `body`, keduanya digabung menjadi `email_text`, lalu diproses dengan `TfidfVectorizer`.

Jika kolom email tidak tersedia, pipeline tetap berjalan dengan fitur URL saja dan `email_text` kosong.

## Safety

Semua fitur diekstrak dari string input lokal. Sistem tidak membuka URL, tidak crawling, dan tidak melakukan request ke domain target.
