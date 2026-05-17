# Project Specification: CyberGuard AI

## Nama Proyek

CyberGuard AI: Prediksi URL Phishing dan Ancaman Siber Menggunakan Machine Learning

## Latar Belakang

Serangan phishing sering menggunakan URL yang menyerupai layanan resmi. Pengguna awam sulit membedakan URL sah dan URL berbahaya. Machine learning dapat digunakan untuk mengenali pola-pola mencurigakan dari struktur URL.

## Tujuan

Membangun model klasifikasi yang memprediksi apakah URL termasuk phishing/malicious atau benign berdasarkan fitur yang diekstrak dari string URL.

## Input

Sebuah URL dalam bentuk teks.

Contoh:

```text
https://secure-login-bank-example.com/verify/account
```

## Output

Prediksi:

```text
Phishing / Malicious
```

Skor risiko:

```text
Risk probability: 87.4%
```

Penjelasan sederhana:

```text
URL memiliki banyak tanda hubung, panjang tidak normal, dan mengandung kata sensitif seperti login atau verify.
```

## Scope Versi 1

- Prediksi berdasarkan lexical features dari URL.
- Tidak menggunakan crawling halaman web.
- Tidak melakukan scanning aktif ke domain target.
- Tidak mengirim request ke URL input.

## Scope Versi Lanjutan

- WHOIS/domain age features.
- DNS reputation features.
- Threat intelligence enrichment.
- Email phishing classification.
- Browser extension prototype.

## Batasan Etis dan Keamanan

Proyek ini hanya untuk deteksi, edukasi, dan pencegahan. Jangan menambahkan fitur yang membantu pembuatan phishing page, credential harvesting, bypass security, atau eksploitasi sistem.
