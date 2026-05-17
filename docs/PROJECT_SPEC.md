# CyberGuard AI Project Spec

CyberGuard AI adalah sistem machine learning defensif untuk membantu mengklasifikasikan URL dan email yang berisiko phishing.

## Scope MVP

- Input URL-only: `url,label`.
- Input hybrid: `url,subject,body,label`.
- Ekstraksi fitur struktural URL tanpa membuka URL.
- NLP email menggunakan gabungan `subject` dan `body` dengan TF-IDF.
- Model baseline menggunakan scikit-learn.
- Output berupa predicted label, risk score, dan risk level.
- Evaluasi menghasilkan classification report dan confusion matrix.

## Out of Scope

- Crawling, scraping, atau request ke URL target.
- Exploit, active scanning, credential harvesting, atau automation ofensif.
- WHOIS/domain age/reputation API pada MVP.

## Goal

Menyediakan pipeline offline yang aman untuk pembelajaran defensive security dan portofolio machine learning.
