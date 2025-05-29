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

# Struktur Folder Inti API
Last Updated: 2025-05-29 07:37:07 UTC
Author: fdygg

## Urutan Prioritas Folder (Dari Terpenting)

### 1. models/ - HIGHEST PRIORITY
Folder ini adalah INTI dari struktur data aplikasi.
```
models/
├── __init__.py
├── balance.py        # WL, DL, BGL, Rupiah management
├── conversion.py     # Rate conversion handling
├── user.py          # Discord & non-Discord users
├── transaction.py   # Conversion & balance transactions
├── product.py       # PPOB products
└── auth.py          # Authentication models
```
**Alasan**: Semua folder lain bergantung pada definisi model.

### 2. service/ - HIGH PRIORITY
Berisi logika bisnis dan operasi data.
```
service/
├── __init__.py
├── balance_service.py     # Balance management
├── conversion_service.py  # Conversion logic
├── auth_service.py       # Authentication
├── user_service.py       # User management
└── transaction_service.py # Transaction processing
```
**Alasan**: Menghubungkan models dengan routes.

### 3. routes/ - MEDIUM PRIORITY
Mendefinisikan endpoint API.
```
routes/
├── __init__.py
├── balance.py      # Balance endpoints
├── conversion.py   # Conversion endpoints
├── auth.py        # Auth endpoints
├── user.py        # User endpoints
└── transaction.py # Transaction endpoints
```
**Alasan**: Menggunakan service untuk handle requests.

### 4. middleware/ - NORMAL PRIORITY
Menangani proses request/response.
```
middleware/
├── __init__.py         # Middleware initialization
├── auth.py            # Token validation
├── rate_limiting.py   # Request limitations
├── error_handling.py  # Error handlers
└── logging.py         # System logging
```
**Alasan**: Menambah layer keamanan dan monitoring.

## File Pendukung (Menyesuaikan dengan Folder Inti)

```
api/
├── server.py       # Server configuration
├── config.py       # Global configurations
├── dependencies.py # Dependency injection
└── utils/         # Helper functions
```

## Aturan Pengembangan

1. **Selalu mulai dari models/**
   - Buat/update model terlebih dahulu
   - Test relasi antar model
   - Validasi struktur data

2. **Lanjut ke service/**
   - Implementasi logika bisnis
   - Gunakan models yang sudah dibuat
   - Pastikan error handling proper

3. **Kemudian routes/**
   - Buat endpoint yang menggunakan service
   - Dokumentasikan API dengan baik
   - Test endpoint secara menyeluruh

4. **Terakhir middleware/**
   - Implementasi security features
   - Setup logging dan monitoring
   - Atur rate limiting

## Catatan Penting

- Setiap perubahan di models/ harus diikuti update di service/
- Service baru memerlukan route baru
- Middleware bisa dikembangkan paralel setelah 3 folder utama siap
- Dokumentasi harus diupdate setiap ada perubahan struktur
- Testing harus dilakukan di setiap level (model, service, route)

## Version Control

- Development Date: 2025-05-29
- Last Updated: 07:37:07 UTC
- Author: fdygg
- Version: 1.0.0