# Feature Engineering

CyberGuard AI versi awal menggunakan fitur lexical, yaitu fitur yang bisa dihitung dari teks URL tanpa mengakses website.

## Fitur Dasar

- `url_length`: panjang URL.
- `hostname_length`: panjang hostname/domain.
- `path_length`: panjang path.
- `count_dots`: jumlah titik.
- `count_hyphens`: jumlah tanda hubung.
- `count_at`: jumlah karakter `@`.
- `count_question`: jumlah `?`.
- `count_equal`: jumlah `=`.
- `count_slash`: jumlah `/`.
- `count_digits`: jumlah angka.
- `count_letters`: jumlah huruf.
- `digit_ratio`: rasio angka terhadap panjang URL.
- `has_https`: apakah URL menggunakan HTTPS.
- `has_ip_address`: apakah hostname berupa IP address.
- `has_suspicious_words`: apakah URL mengandung kata seperti login, verify, update, secure, account, bank, paypal.

## Fitur Tambahan

- `num_subdomains`: jumlah subdomain.
- `tld_length`: panjang top-level domain.
- `is_shortened_url`: indikasi URL shortener.
- `entropy`: ukuran keacakan karakter URL.

## Kenapa Fitur Ini Berguna?

URL phishing sering memiliki pola seperti:

- URL terlalu panjang.
- Banyak angka atau simbol.
- Banyak subdomain.
- Mengandung kata pemancing seperti `login`, `verify`, `secure`, atau `update`.
- Menggunakan domain yang terlihat mirip brand resmi.
- Memakai IP address langsung.

## Catatan

Fitur lexical cepat dan aman karena tidak perlu membuka URL. Namun fitur ini tidak sempurna. Untuk sistem produksi, perlu dikombinasikan dengan reputasi domain, threat intelligence, dan analisis konten halaman.
