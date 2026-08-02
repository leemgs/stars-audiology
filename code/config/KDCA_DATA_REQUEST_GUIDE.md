# KDCA / KNHANES raw-data request — copy-paste guide

**Purpose:** reduce your only remaining manual step to *log in → paste → submit*.
Everything that can be pre-written is pre-written here. What you paste is ready;
you only supply the identity-gated actions a person legally must do themselves.

> **Why this part can't be automated.** The KNHANES raw-data portal
> (`https://knhanes.kdca.go.kr`) requires **본인인증** (Korean real-name identity
> verification via 공동/금융인증서 or 휴대폰) and a **legally binding data-use
> agreement** signed in your name. That is an act of legal identity, not
> clerical busywork — no tool can (or should) perform it on your behalf. Once
> the files exist on disk, though, **every downstream step is automated** (place,
> verify, run) and I do it.

---

## Step 1 — Log in (only you can do this)

1. Go to **https://knhanes.kdca.go.kr** → 원시자료 (raw data) → 자료 요청/다운로드.
2. Complete 본인인증 with your certificate or phone.

## Step 2 — Select the datasets

Request the **otologic-examination + health-interview** files for the cycles
STARS uses. Decide 2009–2012 vs 2010–2012 first (see the open question in
`REVIEW_NOTES.md §3.2`); the SAS release files are:

- `HN09_ALL.sas7bdat` (2009) — *include only if you keep 2009 in scope*
- `HN10_ALL.sas7bdat` (2010)
- `HN11_ALL.sas7bdat` (2011)
- `HN12_ALL.sas7bdat` (2012)

Also download the matching **코드북 (codebook) PDF** for each cycle — it carries
the exact variable names to confirm the two prefilled best-guess items
(`HtE_1`, `HtE_5`) and the audiometry thresholds (see
`KNHANES_MAPPING_VERIFICATION.md`).

## Step 3 — Research-purpose text (paste this)

Most application forms ask for 이용목적 / 연구계획. Draft you can paste and edit:

> **연구제목:** 지각된 스트레스·직업 관련 요인과 이명 및 청력 결과의 연관성에 관한
> 공개조사자료 기반 분석 (STARS)
>
> **이용목적:** 국민건강영양조사(KNHANES) 이과검진·건강설문 자료를 이용하여 성인의
> 지각된 스트레스(스트레스 인지도, BP1)와 이명 유무 및 순음청력 기반 청력손실 간의
> 설문가중 연관성을 추정한다. 연령·성별·교육·직업·소음노출을 보정한 설계기반
> 로지스틱 회귀를 사용하며, 결과는 인과가 아닌 연관으로 보고한다. 미국 NHANES를
> 이용한 교차국가 외적타당도 평가를 병행한다.
>
> **분석변수:** 스트레스 인지(BP1), 2주 이상 우울감(BP5), 이명 문항, 직업성 소음노출
> 문항, 순음청력 역치(0.5–6 kHz, 좌/우), 연령·성별·교육(edu)·소득(ho_incm)·직업(occp)·
> 경제활동상태, 통합가중치(wt_itvex)·분산층(kstrata)·집락(psu).
>
> **산출물:** 학술논문(American Journal of Audiology 투고 예정). 원자료는 재배포하지
> 않으며, 코드·매핑·합성데이터만 공개 저장소에 공개함.

(English mirror, if a form needs it:)

> **Title:** Public-data analysis of associations among perceived stress /
> work-related factors, tinnitus, and hearing outcomes (STARS).
> **Purpose:** Estimate survey-weighted associations between perceived stress
> (BP1) and tinnitus/audiometric hearing loss in KNHANES adults, adjusting for
> age, sex, education, occupation, and noise; associations, not causal effects.
> Cross-national external validation in U.S. NHANES. **Outputs:** a journal
> article (target: *American Journal of Audiology*); raw microdata are not
> redistributed — only code, mappings, and synthetic data are made public.

## Step 4 — After approval & download → hand it to me

Place each file exactly here (the loader's expected layout):

```
code/data/raw/knhanes/2010/HN10_ALL.sas7bdat
code/data/raw/knhanes/2011/HN11_ALL.sas7bdat
code/data/raw/knhanes/2012/HN12_ALL.sas7bdat
# (+ 2009/HN09_ALL.sas7bdat if in scope)
```

Then tell me it's placed (and share the codebook so I can confirm the two
best-guess variable names). From there **I do the rest without you touching
anything else:**

1. Read the codebook and confirm/fix `tinnitus_item` (`HtE_1`?),
   `occupational_noise` (`HtE_5`?), verify the 12 audiometry variable names, the
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
   `tab:results_knhanes` + the Results prose), and refresh the abstract.

`code/data/` is already git-ignored, so the restricted raw files never get
committed — see `.gitignore`.
