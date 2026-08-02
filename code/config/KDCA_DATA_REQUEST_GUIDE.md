# KNHANES raw-data download — follow-along guide

**Purpose:** get the KNHANES files STARS needs, matching the *actual* KDCA
download page. This guide was corrected after seeing the real portal.

> **Honest note on scope.** KNHANES **원시자료 다운로드** (raw-data download —
> the page at `knhanes.kdca.go.kr/.../rawDataDwnld.do`) is **self-service**: log
> in, agree to the data-use pledge, and download the SAS files directly with the
> `SAS ⬇` buttons. There is **no committee approval or waiting period** for the
> standard raw data. (The heavier "학술연구 자료신청" in the right sidebar is a
> *separate* path for linked/special data such as death-record linkage — **STARS
> does not need it**.) The only step no tool can do for you is the **login +
> 본인인증**.

---

## Step 1 — Log in (only you can do this)

1. Go to **https://knhanes.kdca.go.kr** → **원시자료** → **원시자료 다운로드**.
2. Complete **본인인증** (certificate or phone) and agree to the 원시자료 이용
   **서약** if prompted. (First-time users register once.)

## Step 2 — Set the query (on the 다운로드 screen you're looking at)

1. **조사영역:** keep **공통** and **건강설문조사** checked (검진조사 too).
   - **건강설문조사** = the health interview — carries the **스트레스 인지 (`BP1`)**
     item → the STARS *primary exposure*. ✅ This IS in the 기본DB.
   - **영양조사** (nutrition) is not needed; leaving it checked is harmless.
2. **조사연도:** set to **2010 ~ 2012** (the STARS development window).
3. Click **자료조회**.

## Step 3 — Download TWO kinds of file per year

> ⚠️ **Correction (verified against the real files):** the 공통 "기본DB"
> (`HN{yy}_ALL`) does **NOT** contain the hearing exam. It has the stress
> exposure + covariates but **no audiometry, tinnitus, or noise variables**. In
> KNHANES 2010–2012 the **이비인후검사 (ENT exam: 순음청력 + 이명), fielded on
> adults ≥40, is a SEPARATE examination file.** You need **both** files per year.

**(a) The 기본DB (exposure) — you already downloaded these ✅**
For each year, the **공통 / 기본DB** row (제목: "검진조사, 건강설문조사, 영양조사")
→ **SAS ⬇**. These are `hn10_all` / `hn11_all` / `hn12_all` and are confirmed to
carry `BP1` (stress) + all covariates.

**(b) The ENT / audiometry (outcomes) — still needed ⬅️**
Isolate the examination-survey files so the hearing file stands out:
1. **조사영역: uncheck 공통, 건강설문조사, 영양조사 — check ONLY 검진조사.**
2. **조사연도: 2010 ~ 2012.**
3. **자료조회.**
4. In the results, find the row whose **제목 mentions 이비인후 / 청력 / 순음**
   (it may sit next to other special exams like 안검사 / 폐기능). For each of
   2010, 2011, 2012 → **SAS ⬇**.
- **If no such row appears, or you're unsure which it is:** screenshot the whole
  2010–2012 결과 목록 and send it — I'll point to the exact row (or confirm the
  access path). Last resort: KDCA 건강영양조사분석과 ☎ 043-719-7508.
- This ENT file carries the pure-tone thresholds, the tinnitus item, the
  occupational-noise item, and the otology-exam subsample weight.

Also grab the **codebook**: top of the page → **이용지침서 바로가기** → download
the 이용지침서 / 코드북 (변수설명서), **especially the 이비인후검사 section**, so the
ENT variable names can be confirmed.

## Step 4 — (Only if a form asks 이용목적) paste this

Standard raw-data download usually needs only the pledge checkbox. If a
registration/pledge form asks for a research purpose (이용목적), you can paste:

> **연구제목:** 지각된 스트레스·직업 관련 요인과 이명 및 청력 결과의 연관성 분석 (STARS)
> **이용목적:** 국민건강영양조사 이과검진·건강설문 자료로 성인의 스트레스 인지(BP1)와
> 이명 유무 및 순음청력 기반 청력손실 간의 설문가중 연관성을 추정(연령·성별·교육·직업·
> 소음 보정, 인과 아님). 미국 NHANES로 교차국가 외적타당도 평가 병행. 원자료는
> 재배포하지 않고 코드·매핑·합성데이터만 공개.

## Step 5 — Place the files where the loader expects them

```
code/data/raw/knhanes/2010/   ← hn10_all.sas7bdat (done) + the 2010 ENT file
code/data/raw/knhanes/2011/   ← hn11_all.sas7bdat (done) + the 2011 ENT file
code/data/raw/knhanes/2012/   ← hn12_all.sas7bdat (done) + the 2012 ENT file
```

Just drop the ENT `.sas7bdat` files next to the `hn{yy}_all` ones (any name is
fine — tell me the names and I'll point `config/knhanes_mapping.yaml → files:
ent:` at them). `code/data/` is git-ignored, so these restricted files are never
committed (`.gitignore`).

## Step 6 — Hand it to me → I finish the rest

Tell me the ENT files are placed (and share the codebook's 이비인후검사 section).
From there **I do the rest without you touching anything else:**

1. Wire the loader to merge each year's ENT file into the `hn{yy}_all` file on
   `id`, and fill the ENT variable names in `knhanes_mapping.yaml`
   (`tinnitus_item`, `occupational_noise`, the audiometry thresholds, the
   otology-exam weight) from the codebook.
2. Apply the pooling weight divisor in the loader.
3. Run:
   ```bash
   cd code
   python src/knhanes_analysis.py --mapping config/knhanes_mapping.yaml \
       --data-dir data/raw/knhanes --cycles 2010 2011 2012 \
       --out outputs/knhanes_results.json \
       --latex ../paper/tables/table_results_knhanes.tex
   ```
4. Insert the primary perceived-stress results into the manuscript (Table
   `tab:results_knhanes` + the Results prose) and refresh the abstract.
