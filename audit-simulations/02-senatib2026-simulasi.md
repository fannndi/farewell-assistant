# Simulasi Audit — senatib2026-sim

> **Footer:** `Farewell: ON | Project: senatib2026-sim | BUILD | Turn: 1 | Chain: 3 | 70% | Eco`
> **User:** fix bug image worker crash
> **Role:** AI model auditing distributed image processing pipeline

---

## Pipeline Route (Real)

```
Input:          "fix bug image worker crash"
Intent:         fix
Domain:         general
Complexity:     medium
Confidence:     70%
Source:         quick
Stack:          [python, nodejs]
Model:          Free=Free / Emergency=Free
Skill Chain (3 steps):
  1. search-first        — Check known issues
  2. orch-fix-defect     — Reproduce → fix → verify
  3. verification-loop   — Verify fix doesn't break others
```

---

## Skenario 1: Fix Worker Crash — Image Processing

**Input AI:** `"fix bug image worker crash"`

### Architecture Snapshot
```
api-producer (Node/Express)
  ↓ HTTP upload (multipart)
RabbitMQ (message broker)
  ↓ queue
worker-a1 (Python/Pillow)  ← CRASH HERE
worker-a2 (Python/Pillow)
  ↓ output
Samba (shared storage)
```

### AI Model Perspective
Sebagai AI model, saya harus:

1. **Cek log worker** — `logs/` directory, CSV per worker
2. **Cek crash pattern** — reproducible? Image tertentu?
3. **Cek memory** — Pillow resize OOM untuk image besar?
4. **Cek RabbitMQ** — DLQ? Unacked messages?
5. **Cek error handling** — try/except di `worker.py`?
6. **Cek reconnection** — worker reconnect ke RabbitMQ setelah crash?

### Checklist Item Spesifik

| # | Item | Cek | Severity |
|---|------|-----|----------|
| ST-1 | Worker error handling | `worker.py` ada try/except di loop? | CRITICAL |
| ST-2 | Image validation | Cek format, size sebelum process? | HIGH |
| ST-3 | OOM protection | Max image size limit di upload? | HIGH |
| ST-4 | RabbitMQ prefetch | `prefetch_count=1` agar worker ga overload? | MEDIUM |
| ST-5 | DLQ routing | Message masuk DLQ setelah N retry? | MEDIUM |
| ST-6 | Worker healthcheck | Docker compose healthcheck untuk worker? | HIGH |
| ST-7 | Worker restart policy | `restart: unless-stopped` di compose? | HIGH |
| ST-8 | Logging | Apakah tiap worker log exception? | MEDIUM |
| ST-9 | Graceful shutdown | Worker handle SIGTERM? | LOW |

### Simulasi Execution: orch-fix-defect

```
Step 1/3: search-first
  → Check: `logs/` untuk trace terakhir
  → Search: `worker.py` untuk crash pattern
  → Find: resize() tanpa try/except untuk image corrupted

Step 2/3: orch-fix-defect
  → Reproduce: kirim image rusak via API
  → Fix: tambah try/except + retry logic
  → Fix: validasi image sebelum resize
  → Fix: MAX_IMAGE_SIZE = 50MB di upload endpoint

Step 3/3: verification-loop
  → Test: kirim 100 image (50 valid, 50 corrupted)
  → Verify: 0 crash, corrupted masuk DLQ
  → Lint: `ruff check worker.py`
```

### Code Fix Simulation

```python
# Before
def process_image(path):
    img = Image.open(path)
    img = img.resize((800, 600))  # Crash di sini!
    img.save(output_path)

# After
def process_image(path):
    try:
        img = Image.open(path)
        img.verify()  # validate before open
        img = Image.open(path)
        img = img.resize((800, 600))
        img.save(output_path)
        return True
    except (IOError, OSError, MemoryError) as e:
        log.error(f"Crash on {path}: {e}")
        return False  # DLQ akan handle
```

---

## Skenario 2: Deploy Pipeline — Docker Compose

**Input AI:** `"deploy rabbitmq worker scaling"`

### Pipeline Prediction
| Intent | Domain | Chain |
|--------|--------|-------|
| deploy | infra | deploy (4 steps) |

### Docker Compose Audit
```yaml
# docker-compose.yml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]  # 🔴 management exposed

  api-producer:
    build: ./api-producer
    ports: ["3000:3000"]
    depends_on: [rabbitmq]

  worker-a1:
    build: ./worker
    depends_on: [rabbitmq]
    restart: unless-stopped  # ✅

  worker-a2:
    build: ./worker
    depends_on: [rabbitmq]
    restart: unless-stopped  # ✅

  samba:
    image: dperson/samba
    volumes: ["./data:/mount"]
```

### Checklist
| # | Item | Status | Severity |
|---|------|--------|----------|
| ST-10 | RabbitMQ management port public? | ❌ Exposed di compose | CRITICAL |
| ST-11 | Healthcheck di tiap service? | ❌ Missing | HIGH |
| ST-12 | Resource limits (mem/cpu)? | ❌ Missing | HIGH |
| ST-13 | Network isolation? | ❌ Semua di default bridge | MEDIUM |
| ST-14 | Volume permission? | ❌ Default | LOW |

---

## Skenario 3: Database — Dataset Management

**Input AI:** `"optimize image storage in dataset"`

### Pipeline Prediction
| Intent | Domain | Chain |
|--------|--------|-------|
| fix | data | fix (3 steps) |

### Temuan
~40 synthetic images di `dataset/raw_photos/`. Auto-rename via `cv_rename.py` tapi:
- No deduplication (hash check)
- No compression before write
- No metadata tracking

---

## Ringkasan Temuan

| # | Temuan | Severity | File |
|---|--------|----------|------|
| 1 | Worker no try/except → crash on corrupt image | CRITICAL | `worker/worker.py` |
| 2 | RabbitMQ management port exposed | CRITICAL | `docker-compose.yml` |
| 3 | No healthcheck di compose | HIGH | `docker-compose.yml` |
| 4 | No image size limit di upload | HIGH | `api-producer/server.js` |
| 5 | No DLQ monitoring | MEDIUM | `docker-compose.yml` |
| 6 | No OOM protection di worker | HIGH | `worker/worker.py` |
| 7 | Dataset no dedup | LOW | `dataset/` |

---

*Simulasi: 2026-06-22 | farewell-assistant v1.5.0 | Route: fix → general*
