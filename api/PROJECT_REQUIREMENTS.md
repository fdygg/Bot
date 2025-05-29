# Project Requirements & Specifications
Current Date: 2025-05-29 07:10:37
Author: fdygg

## 1. Multi-Platform Integration
### Bot Discord + Web API
- Bot Discord untuk game Growtopia
- API untuk berbagai layanan (PPOB, dll)
- Satu database untuk semua platform
- Konsistensi data antar platform

## 2. Sistem Balance Dual Currency
### Discord Users (Growtopia Players)
- Balance WL (World Lock)
- Balance DL (Diamond Lock)
- Balance BGL (Blue Gem Lock)
- Balance Rupiah
- **Fitur Khusus**: Bisa convert WL/DL/BGL ke Rupiah

### Web/App Users (Non-Discord)
- Balance Rupiah saja
- Tidak ada akses ke currency Growtopia
- Tidak ada fitur convert

## 3. Sistem Konversi (Discord Users Only)
### Rate Konversi (Configurable di Dashboard)
```sql
CREATE TABLE conversion_rates (
    id INTEGER PRIMARY KEY,
    currency TEXT,
    amount INTEGER,
    rate_rupiah INTEGER,
    updated_at TIMESTAMP,
    updated_by TEXT
)