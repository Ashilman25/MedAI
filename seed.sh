#!/usr/bin/env bash
set -euo pipefail

# ==== CONFIG ====
# Your deployed backend URL:
BACKEND_URL="https://medai-backend-997702033779.us-central1.run.app"

# Optional: if you want ingested items to show as "mine" in the Docs tab
# set this to your Firebase Auth UID (or leave empty for global docs).
OWNER_UID=""   # e.g., OWNER_UID="LG3FVco6GghTlagIPWTK39341Y93"

# Language and defaults for scanning:
LANG="en"
TOP_K=5
TARGET_CONF=0.62
MAX_PASSES=2
RETMAX=60
MINDATE_DEFAULT=2017
DONE_FILE="seed_done.txt"


retry_curl () {
  local body="$1"
  local url="$2"
  local tries=4
  local delay=5
  local code
  for ((i=1;i<=tries;i++)); do
    code=$(curl -s -o /tmp/seed_resp.json -w "%{http_code}" \
      -H "Content-Type: application/json" \
      --connect-timeout 10 --max-time 180 \
      -d "$body" "$url" || true)
    if [[ "$code" == "200" ]]; then
      echo "$code"                 # <-- stdout: ONLY the code
      return 0
    fi
    echo "… attempt $i failed (HTTP $code). Retrying in ${delay}s" >&2  # <-- stderr: logs only
    sleep "$delay"
    delay=$((delay*2))
  done
  echo "$code"
  return 1
}


# Helper to post one topic
post_topic () {
  local q="$1"
  local types_csv="$2"
  local mindate="${3:-$MINDATE_DEFAULT}"

  echo "➡️  Seeding: ${q}   (types: [${types_csv}]  mindate: ${mindate})"

  # skip if done already
  if grep -Fqx "$q|$types_csv|$mindate" "$DONE_FILE" 2>/dev/null; then
    echo "↩︎  Skipping already-done: $q"
    return 0
  fi

  # Build body
  local body
  body=$(
    jq -n \
      --arg query "$q" \
      --argjson top_k $TOP_K \
      --argjson target_confidence $TARGET_CONF \
      --argjson max_passes $MAX_PASSES \
      --argjson per_pass_retmax $RETMAX \
      --argjson mindate $mindate \
      --arg lang "$LANG" \
      --arg owner_uid "${OWNER_UID}" \
      --arg types_csv "$types_csv" '
        {
          query: $query,
          top_k: $top_k,
          wide: true,
          target_confidence: $target_confidence,
          max_passes: $max_passes,
          per_pass_retmax: $per_pass_retmax,
          mindate: $mindate,
          lang: $lang,
          types: ( "[" + $types_csv + "]" | fromjson )
        }
        | if ($owner_uid | length) > 0
          then . + { owner_uid: $owner_uid }
          else .
          end
      '
  )

  # Call backend ONCE
  code=$(retry_curl "$body" "$BACKEND_URL/expand-sources")
  if [[ "$code" != "200" ]]; then
    echo "❌  HTTP $code for: $q"
    cat /tmp/seed_resp.json || true
    echo "$q|$types_csv|$mindate" >> seed_failures.txt
    return 1
  fi

  # Success → mark done NOW
  echo "$q|$types_csv|$mindate" >> "$DONE_FILE"

  # Print brief summary
  found=$(jq -r '.found // 0' /tmp/seed_resp.json 2>/dev/null || echo 0)
  added=$(jq -r '.added // 0' /tmp/seed_resp.json 2>/dev/null || echo 0)
  conf=$(jq -r '.confidence // 0' /tmp/seed_resp.json 2>/dev/null || echo 0)
  echo "   ✓ found=$found  added=$added  confidence=$conf"
  sleep 1
}

# ==== TOPICS TO SEED ====
# ---- CARDIO / GENERAL IM ----
# post_topic "atrial fibrillation anticoagulation" "\"Review\",\"Systematic Review\"" 2019
# post_topic "heart failure guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2018
# post_topic "chest pain evaluation guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2018
# post_topic "coronary artery disease secondary prevention" "\"Review\",\"Systematic Review\"" 2018

# # ---- ENDO / METABOLIC ----
# post_topic "type 2 diabetes guideline adults" "\"Guideline\",\"Practice Guideline\",\"Systematic Review\",\"Review\"" 2018
# post_topic "thyroid nodule management guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2017
# post_topic "osteoporosis treatment guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2017

# # ---- ID / ANTIMICROBIALS ----
# post_topic "antibiotic stewardship guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "community acquired pneumonia guideline adults" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2018
# post_topic "UTI treatment guideline adults" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2017
# post_topic "Clostridioides difficile guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2017

# # ---- NEURO ----
# post_topic "acute ischemic stroke imaging guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2017
# post_topic "status epilepticus management guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "migraine prophylaxis guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016

# # ---- PULM (some duplicates noted) ----
# post_topic "COPD guideline adults" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2017    # (dup of one you already have)
# post_topic "asthma guideline adults" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2017
# post_topic "pulmonary embolism diagnosis guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2016    # (dup of same topic above but ok)

# # ---- ONC / PALLIATIVE ----
# post_topic "cancer screening guideline adults" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "palliative care cancer guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016

# # ---- OB / GYN ----
# post_topic "prenatal care guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "gestational diabetes guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "postpartum hemorrhage guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016

# # ---- PEDS ----
# post_topic "fever in infants guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "ADHD treatment guideline children" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "asthma guideline children" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016

# # ---- RENAL / HEPATIC / GI ----
# post_topic "chronic kidney disease guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "hemodialysis access guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "IBD ulcerative colitis guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "hepatitis B management guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "upper GI bleed guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016

# # ---- EMERGENCY / CRITICAL CARE / TRAUMA ----
# post_topic "sepsis management guideline adults" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "traumatic brain injury guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "DVT prophylaxis trauma guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016

# # ---- IMAGING ----
# post_topic "pulmonary embolism imaging guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "low back pain imaging guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "stroke CT vs MRI review" "\"Review\",\"Systematic Review\"" 2015

# # ---- PSYCH ----
# post_topic "major depressive disorder guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "generalized anxiety disorder guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016

# # ---- MED SAFETY / MED RECON ----
# post_topic "drug drug interaction review" "\"Review\",\"Systematic Review\"" 2015
# post_topic "medication reconciliation guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2015
# post_topic "metformin lactic acidosis review" "\"Review\",\"Systematic Review\"" 2010     # (dup of one you already have)

# ---- PREVENTIVE / MULTIMORBIDITY ----
# post_topic "preventive care guideline adults" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "multimorbidity management guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016

# # ---- PHARM / LARGE SCANS (no explicit types → pass empty to use backend defaults) ----
# post_topic "drug safety review" "" 2015
# post_topic "drug interactions guideline" "" 2015
# post_topic "polypharmacy elderly review" "" 2015

# post_topic "antibiotics guideline" "" 2015
# post_topic "antiviral therapy review" "" 2015
# post_topic "chemotherapy guideline cancer" "" 2015
# post_topic "antidepressant efficacy review" "" 2015
# post_topic "antipsychotic guideline" "" 2015
# post_topic "opioid prescribing guideline" "" 2015

# post_topic "type 2 diabetes pharmacologic management guideline" "" 2015
# post_topic "hypertension drug therapy guideline" "" 2015
# post_topic "asthma pharmacologic management guideline" "" 2015
# post_topic "heart failure drug therapy guideline" "" 2015
# post_topic "lipid lowering therapy guideline" "" 2015

# ---- SUBSTANCE USE / HARM REDUCTION ----
# post_topic "alcohol use disorder treatment guideline" "" 2015
# post_topic "nicotine replacement therapy review" "" 2015
# post_topic "cannabis health effects review" "" 2015
# post_topic "cocaine abuse treatment guideline" "" 2015
# post_topic "methamphetamine abuse review" "" 2015
# post_topic "psychedelic therapy review" "" 2015
# post_topic "LSD psilocybin clinical review" "" 2015
# post_topic "opioid overdose treatment guideline" "" 2015
# post_topic "naloxone distribution guideline" "" 2015

# # ---- SPORTS / SUPPLEMENTS ----
# post_topic "anabolic steroid abuse health effects review" "" 2015
# post_topic "testosterone therapy guideline" "" 2015
# post_topic "corticosteroid treatment guideline" "" 2015
# post_topic "glucocorticoid adverse effects review" "" 2015
# post_topic "creatine supplementation safety review" "" 2015
# post_topic "protein supplements health effects review" "" 2015
# post_topic "caffeine performance review" "" 2015
# post_topic "pre workout supplement review" "" 2015
# post_topic "dietary supplement safety guideline" "" 2015
# post_topic "herbal supplements efficacy review" "" 2015
# post_topic "ginseng health effects review" "" 2015
# post_topic "turmeric curcumin review" "" 2015
# post_topic "omega 3 fatty acids supplementation review" "" 2015

# # ---- NEURODEVELOPMENT / EDUCATION ----
# post_topic "autism spectrum disorder guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2015
# post_topic "ADHD adult guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
# post_topic "intellectual disability guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2015
# post_topic "learning disabilities educational interventions review" "\"Review\",\"Systematic Review\"" 2015
# post_topic "dyslexia intervention guideline" "\"Guideline\",\"Review\"" 2015
# post_topic "developmental disabilities guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2015

# # ---- REHAB / NEUROMUSCULAR ----
# post_topic "spinal cord injury rehabilitation guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2015
# post_topic "cerebral palsy management guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
# post_topic "amputation prosthetics rehabilitation guideline" "\"Guideline\",\"Review\"" 2015
# post_topic "muscular dystrophy treatment guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2015

# # ---- NEURO / CHRONIC PAIN ----
# post_topic "chronic fatigue syndrome guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
# post_topic "fibromyalgia guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
# post_topic "epilepsy management guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2015
# post_topic "multiple sclerosis guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015

# # ---- HEARING / VISION / ASSISTIVE TECH ----
# post_topic "hearing loss rehabilitation guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
# post_topic "visual impairment management guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
# post_topic "assistive technology disability review" "\"Review\",\"Systematic Review\"" 2015

# # ---- DISABILITY / ACCESS / EMPLOYMENT ----
# post_topic "disability inclusion healthcare review" "\"Review\",\"Systematic Review\"" 2015
# post_topic "accessibility guideline disability" "\"Guideline\",\"Review\"" 2015
# post_topic "employment disability interventions review" "\"Review\",\"Systematic Review\"" 2015

# # ---- HEME / ONC (SCREENING & TREATMENT) ----
# post_topic "anemia diagnosis guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "venous thromboembolism guideline adults" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "hematologic malignancies guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "leukemia treatment guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "lymphoma management guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "breast cancer screening guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "prostate cancer screening guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "colorectal cancer screening guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "lung cancer screening guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016

# # ---- INFECTIOUS DISEASES ----
# post_topic "HIV treatment guideline adults" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "tuberculosis management guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "malaria treatment guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "COVID-19 management guideline" "\"Guideline\",\"Practice Guideline\",\"Review\",\"Systematic Review\"" 2020
# post_topic "Ebola outbreak management review" "\"Review\",\"Systematic Review\"" 2015
# post_topic "vaccination schedule guideline adults children" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2015

# # ---- PSYCH (ADULT) ----
# post_topic "bipolar disorder treatment guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "schizophrenia management guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "post traumatic stress disorder guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
# post_topic "eating disorder treatment guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
# post_topic "sleep disorders insomnia guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
# post_topic "autism adult management review" "\"Review\",\"Systematic Review\"" 2015

# # ---- OB/GYN ----
# post_topic "contraception guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
# post_topic "menopause hormone therapy guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "infertility evaluation guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "polycystic ovary syndrome guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "endometriosis management guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "gynecologic oncology guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016

# ---- NEONATAL / PEDIATRICS ----
post_topic "neonatal sepsis guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
post_topic "pediatric vaccination schedule guideline" "\"Guideline\",\"Review\"" 2016
post_topic "pediatric obesity management guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "pediatric pain management guideline" "\"Guideline\",\"Review\"" 2015

# ---- DENTAL / ORAL HEALTH ----
post_topic "dental caries prevention guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
post_topic "periodontal disease management guideline" "\"Guideline\",\"Review\"" 2015
post_topic "oral cancer screening guideline" "\"Guideline\",\"Review\"" 2015

# ---- RHEUM / MSK / ORTHO / SARCOMA ----
post_topic "osteoarthritis management guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "rheumatoid arthritis guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
post_topic "gout management guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "osteosarcoma treatment review" "\"Review\",\"Systematic Review\"" 2016

# ---- ALLERGY / IMMUNOLOGY ----
post_topic "anaphylaxis management guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "food allergy guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "immunodeficiency management guideline" "\"Guideline\",\"Review\"" 2016

# ---- GERI / NEURO / HOSPITAL MEDICINE ----
post_topic "falls prevention guideline elderly" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "dementia management guideline" "\"Guideline\",\"Practice Guideline\",\"Review\"" 2016
post_topic "delirium management guideline hospital" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016

# ---- EMERGENCY / PERIOP ----
post_topic "mass casualty triage guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "acute pain management emergency department guideline" "\"Guideline\",\"Review\"" 2016
post_topic "perioperative antibiotic prophylaxis guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "perioperative cardiovascular evaluation guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016

# ---- LAB / DIAGNOSTICS ----
post_topic "laboratory test interpretation guideline" "\"Guideline\",\"Review\"" 2015
post_topic "biomarker validation review" "\"Review\",\"Systematic Review\"" 2016
post_topic "point of care testing accuracy review" "\"Review\",\"Systematic Review\"" 2015

# ---- UROLOGY ----
post_topic "benign prostatic hyperplasia guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "erectile dysfunction guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "urinary incontinence guideline adults" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016

# ---- DERM / ENT / OPHTHO ----
post_topic "acne treatment guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "psoriasis management guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "atopic dermatitis guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2016
post_topic "skin cancer prevention guideline" "\"Guideline\",\"Review\"" 2016
post_topic "otitis media guideline" "\"Guideline\",\"Review\"" 2015
post_topic "sinusitis management guideline" "\"Guideline\",\"Review\"" 2015
post_topic "glaucoma treatment guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
post_topic "diabetic retinopathy screening guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015

# ---- NEURO (PARKINSON / DEMENTIA / PAIN) ----
post_topic "Parkinson disease management guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
post_topic "dementia Alzheimer disease guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015
post_topic "neuropathic pain treatment guideline" "\"Guideline\",\"Review\",\"Systematic Review\"" 2015

# ---- ENVIRONMENT / PUBLIC HEALTH ----
post_topic "obesity prevention policy review" "\"Review\",\"Systematic Review\"" 2015
post_topic "climate change health effects review" "\"Review\",\"Systematic Review\"" 2016
post_topic "air pollution cardiovascular effects review" "\"Review\",\"Systematic Review\"" 2016
post_topic "health disparities guideline" "\"Guideline\",\"Review\"" 2016
post_topic "social determinants of health interventions review" "\"Review\",\"Systematic Review\"" 2016
