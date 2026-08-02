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

1. **조사영역:** keep **공통**, **검진조사**, **건강설문조사** checked.
   - **검진조사** = the examination module — carries **순음청력검사 (audiometry)**
     and the **이명 (tinnitus)** items → the STARS *outcomes*.
   - **건강설문조사** = the health interview — carries the **스트레스 인지 (`BP1`)**
     item → the STARS *primary exposure*.
   - **영양조사** (nutrition) is not needed; leaving it checked is harmless.
2. **조사연도:** set to **2010 ~ 2012**.
   - KNHANES ran the ENT/hearing exam only in **2008–2012**, so 2010–2012 is the
     window that has both audiometry and the tinnitus item. (This is the STARS
     development window; see `KNHANES_MAPPING_VERIFICATION.md`.)
3. Click **자료조회**.

## Step 3 — Download the files (SAS, per year)

In the results table, for **each** year (2010, 2011, 2012):

1. Find the **공통 / 기본DB** row — its 제목 reads "검진조사, 건강설문조사, 영양조사".
   This one integrated file per year contains audiometry + tinnitus + stress
   together (it is the `HN10_ALL` / `HN11_ALL` / `HN12_ALL` file the pipeline
   expects).
2. Click **SAS ⬇** (not SPSS — the loader reads `.sas7bdat`).

Also grab the **codebook**: top of the page → **이용지침서 바로가기** → download
the 이용지침서 / 코드북 (변수설명서) for these years. That is where the exact
variable names are confirmed (`tinnitus_item`, currently the best-guess `HtE_1`;
the occupational-noise item; the 12 audiometry variables; the weight variable).

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
code/data/raw/knhanes/2010/   ← the 2010 SAS file (e.g., HN10_ALL.sas7bdat)
code/data/raw/knhanes/2011/   ← the 2011 SAS file
code/data/raw/knhanes/2012/   ← the 2012 SAS file
```

If a downloaded file unzips to a different name, either rename it to
`HN<yy>_ALL.sas7bdat` or tell me the actual name and I will point the mapping at
it (`config/knhanes_mapping.yaml` → `files:`). `code/data/` is git-ignored, so
these restricted files are never committed (`.gitignore`).

## Step 6 — Hand it to me → I finish the rest

Tell me the files are placed (and share the codebook so I can confirm the
best-guess variable names). From there **I do the rest without you touching
anything else:**

1. Read the codebook and confirm/fix `tinnitus_item` (`HtE_1`?),
   `occupational_noise` (`HtE_5`?), the 12 audiometry variable names, the
   sentinels, and the weight variable in `knhanes_mapping.yaml`.
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
