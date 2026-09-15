# PharmaLens AI — FastAPI Backend (Phase 1)

هذا الباك إند الجديد بديل كامل لـ `server/` القديم (Express + tRPC + Drizzle/MySQL)، ومبني على
الـ stack المطلوب في مستند الـ architecture: **FastAPI + Supabase Postgres + Supabase Auth +
Cloudflare R2**. كل الـ business logic (شير الملفات في `shared/*.ts`) اتترجم لبايثون في
`app/engines/`، وكل الـ API endpoints بديل مطابق للي كان في `server/routers.ts`.

## إيه اللي اتعمل (Phase 1 — Backend فقط)

- **API**: FastAPI بديل كامل لـ `routers.ts` — نفس العمليات بالظبط (auth, workspaces, files,
  filters, products, product-runs, copilot, reports) لكن REST بدل tRPC.
- **DB**: `app/models.py` + `supabase_schema.sql` — نفس جداول `drizzle/schema.ts` لكن Postgres
  بدل MySQL (لأن Supabase Postgres مش MySQL).
- **Auth**: Supabase Auth بدل Manus OAuth. الباك إند بيتحقق من الـ JWT اللي الفرونت بياخده من
  Supabase (`Authorization: Bearer <token>`)، وبيعمل sync تلقائي لسطر المستخدم في جدول `users`
  أول ما يوصل.
- **Storage**: Cloudflare R2 بدل الـ Manus Forge presign flow، عبر `boto3` (R2 متوافق مع S3 API).
- **Engines**: كل الـ 14 product engine (`analytics/strategy/operations`) + `canonical.ts` +
  `market-insights.ts` + `engine-registry.ts` اتترجموا حرفيًا لبايثون.
- **Reports**: PDF عبر `reportlab`، PPTX عبر `python-pptx` (بديل `pdfkit`/`pptxgenjs`).
- **Copilot**: OpenAI عبر `openai` SDK الرسمي.

## اللي لسه ما اتعملش (خطوات جاية)

- الفرونت إند (تحويل Vite → Next.js) — الصفحات والمكونات في `client/src` قابلة لإعادة الاستخدام
  بنسبة كبيرة (نفس Tailwind/shadcn)، لكن استدعاءات tRPC محتاجة تتحول لـ REST + Supabase Auth
  client.
- Background jobs / queue للملفات الكبيرة (حاليًا المعالجة synchronous داخل الـ request).
- Cloudflare Workers/AI Gateway الاختياري.

## التشغيل محليًا (Free tier)

### 1) Supabase (مجاني)

1. اعمل مشروع جديد على [supabase.com](https://supabase.com) (الخطة المجانية: 500MB DB، 50K MAU).
2. من `Settings > Database`، انسخ الـ **Connection string (URI)** — استخدم وضع
   **Session pooler** لو بتشتغل من جهازك المحلي.
3. من `Settings > API`، انسخ `Project URL` و `JWT Secret` و `service_role key`.
4. شغّل `supabase_schema.sql` من `SQL Editor` في لوحة تحكم Supabase (أو `python create_tables.py`
   بعد ما تظبط `.env`).

> ملحوظة: مشروع Supabase المجاني بيتوقف بعد أسبوع من عدم الاستخدام — طبيعي في مرحلة التطوير،
> بس لازم تعرفها قبل الـ production.

### 2) Cloudflare R2 (مجاني حتى 10GB-month)

1. من لوحة تحكم Cloudflare > R2 > أنشئ Bucket اسمه مثلاً `pharmalens-data`.
2. من `Manage R2 API Tokens` اعمل token جديد (Object Read & Write) وانسخ
   `Access Key ID` و `Secret Access Key` و `Account ID`.

### 3) إعداد الباك إند

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # واملأ القيم اللي جمعتها فوق
python create_tables.py
uvicorn app.main:app --reload --port 8000
```

افتح `http://localhost:8000/docs` — هتلاقي Swagger UI فيه كل الـ endpoints جاهزة للتجربة.
لو `OPENAI_API_KEY` مش متظبط، كل حاجة هتشتغل عدا الـ Copilot.

### 4) اختبار سريع بدون فرونت إند

الـ endpoints المحمية محتاجة `Authorization: Bearer <supabase-jwt>`. أسهل طريقة تجيب token
تجربة هي تعمل مستخدم في Supabase Auth (Dashboard > Authentication > Users > Add user)، وبعدين
تستخدم Supabase JS/Python client لتسجيل الدخول وتاخد الـ access_token، أو تستخدم
`supabase.auth.sign_in_with_password` من REPL بايثون بسيط.

## هيكل المشروع

```
backend/
  app/
    main.py            # FastAPI app + CORS + include_router
    config.py           # قراءة متغيرات البيئة
    database.py          # SQLAlchemy engine/session
    models.py             # جداول Postgres (بديل drizzle/schema.ts)
    deps.py                # التحقق من Supabase JWT
    storage.py              # Cloudflare R2 (بديل server/storage.ts)
    crud.py                  # وصول قاعدة البيانات (بديل server/db.ts)
    canonical.py              # تنظيف/تحقق البيانات (بديل shared/canonical.ts)
    canonical_service.py       # قراءة CSV/XLSX/Parquet (بديل server/canonical-service.ts)
    llm.py                      # استدعاء OpenAI للـ Copilot
    engines/                     # الـ 14 محرك تحليلي (بديل shared/*-engines.ts)
    reports/                      # مولدات PDF/PPTX (بديل server/pdf-report.ts, pptx-report.ts)
    routers/                       # كل الـ API endpoints
  supabase_schema.sql
  create_tables.py
  requirements.txt
  .env.example
```

## Phase 1.5 — Organizations/RBAC + Dataset Registry (إضافة فوق اللي فات)

بنيت على نفس الباك إند من غير ما أكسر حاجة شغالة (زي ما المستندات الثلاثة بتشترط "backward
compatible", "do NOT break working functionality"). "Workspace" في الكود = "Organization" في
المستندات (نفس الحدود الأمنية/الـ tenant isolation)، خليتها بنفس الاسم عشان الـ API اللي
سلمتهولك قبل كده يفضل شغال زي ما هو.

### اللي جديد

- **RBAC**: أدوار جديدة على `workspace_members` (`admin`, `manager`, `analyst`, `sales_user`
  بالإضافة لـ `owner/editor/viewer` القديمة). Endpoints:
  - `GET/POST /api/workspaces/{id}/members` — عرض/دعوة عضو (لازم يكون عنده حساب already).
  - `PATCH /api/workspaces/{id}/members/{user_id}` — تغيير الدور (Admin/Owner بس).
- **Dataset Registry** (`app/models.py`: `Dataset`, `DatasetVersion`, `DatasetMapping`,
  `DataQualityReport`) — كل ملف بياخد identity ثابتة وversions (v1, v2, ...)، مش overwrite.
- **Auto-Mapping Engine** (`app/mapping_engine.py`) — بياخد أسماء الأعمدة اللي المستخدم رفعها
  ويقترح mapping لموديل بيانات موحّد (product/brand/molecule/hcp/territory/disease/population...)
  مع confidence score لكل حقل، مطابق تمامًا لمثال "Product_Name → product_name" في المستند.
- **Data Quality Engine** (`app/data_quality.py`) — quality score (0-100) شفّاف ومبني على قواعد
  واضحة (completeness, duplicates, invalid numerics/dates, mapping confidence)، + critical_errors
  + warnings + recommendations بالعربي\الإنجليزي مفهومة للمستخدم مش رسائل تقنية.
- **Onboarding workflow**: `POST /api/v1/datasets` (تسجيل الملف بعد رفعه لـ R2 عبر
  `/api/v1/datasets/presign`) → `POST .../versions/{id}/profile` (schema detection + اقتراح
  mapping) → `POST .../versions/{id}/mapping` (تأكيد الـ mapping، تشغيل الـ quality engine،
  كتابة نسخة curated بصيغة Parquet في R2) → `GET .../versions/{id}/quality-report`.

### اللي لسه مش موجود (اتقال بوضوح في الـ Audit)

- Background jobs حقيقية (المعالجة حاليًا synchronous جوه الـ request — كافي للملفات المتوسطة،
  لكن للملفات الضخمة (500MB) محتاجين worker/queue فعلي، ده الخطوة الجاية المقترحة).
- External Data connectors (WHO/CAPMAS/IQVIA/Statista...)، Subscriptions/Billing، Google/Microsoft
  OAuth، Business Review/Plan/Decision engines، AI tool-calling الحقيقي (الـ Copilot لسه LLM call
  واحد، مش agent بـ tools).

## الخطوة الجاية

جرّب الجزء ده كمان محليًا (استخدم `/docs` لترفع ملف تجريبي وتتابع الـ flow: presign → create →
profile → mapping → quality-report)، وبعدين نكمل حسب الأولوية اللي هتحددها: Background Jobs
للملفات الكبيرة، ولا External Data connectors، ولا الفرونت إند Next.js.
