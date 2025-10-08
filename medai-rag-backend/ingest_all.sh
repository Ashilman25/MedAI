#!/bin/bash
# Run all PubMed ingestion commands to populate the RAG index

# python -m app.ingest --pubmed "atrial fibrillation anticoagulation" --types "Review,Systematic Review" --retmax 120 --mindate 2019 --lang English
# python -m app.ingest --pubmed "heart failure guideline"             --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2018 --lang English
# python -m app.ingest --pubmed "chest pain evaluation guideline"     --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2018 --lang English
# python -m app.ingest --pubmed "coronary artery disease secondary prevention" --types "Review,Systematic Review" --retmax 120 --mindate 2018 --lang English

# python -m app.ingest --pubmed "type 2 diabetes guideline adults"    --types "Guideline,Practice Guideline,Systematic Review,Review" --retmax 150 --mindate 2018 --lang English
# python -m app.ingest --pubmed "thyroid nodule management guideline" --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2017 --lang English
# python -m app.ingest --pubmed "osteoporosis treatment guideline"    --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2017 --lang English

# python -m app.ingest --pubmed "antibiotic stewardship guideline"    --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "community acquired pneumonia guideline adults" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2018 --lang English
# python -m app.ingest --pubmed "UTI treatment guideline adults"      --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2017 --lang English
# python -m app.ingest --pubmed "Clostridioides difficile guideline"  --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2017 --lang English

# python -m app.ingest --pubmed "acute ischemic stroke imaging guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2017 --lang English
# python -m app.ingest --pubmed "status epilepticus management guideline" --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2016 --lang English
# python -m app.ingest --pubmed "migraine prophylaxis guideline"         --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2016 --lang English

# python -m app.ingest --pubmed "COPD guideline adults"                --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2017 --lang English
# python -m app.ingest --pubmed "asthma guideline adults"              --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2017 --lang English
# python -m app.ingest --pubmed "pulmonary embolism diagnosis guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English

# python -m app.ingest --pubmed "cancer screening guideline adults"   --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "palliative care cancer guideline"    --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2016 --lang English

# python -m app.ingest --pubmed "prenatal care guideline"             --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English
# python -m app.ingest --pubmed "gestational diabetes guideline"      --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "postpartum hemorrhage guideline"     --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English

# python -m app.ingest --pubmed "fever in infants guideline"          --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2016 --lang English
# python -m app.ingest --pubmed "ADHD treatment guideline children"   --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English
# python -m app.ingest --pubmed "asthma guideline children"           --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2016 --lang English

# python -m app.ingest --pubmed "chronic kidney disease guideline"    --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "hemodialysis access guideline"       --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2016 --lang English
# python -m app.ingest --pubmed "IBD ulcerative colitis guideline"    --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "hepatitis B management guideline"    --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "upper GI bleed guideline"            --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2016 --lang English

# python -m app.ingest --pubmed "sepsis management guideline adults"  --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "traumatic brain injury guideline"    --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English
# python -m app.ingest --pubmed "DVT prophylaxis trauma guideline"    --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English

# python -m app.ingest --pubmed "pulmonary embolism imaging guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "low back pain imaging guideline"      --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English
# python -m app.ingest --pubmed "stroke CT vs MRI review"              --types "Review,Systematic Review" --retmax 120 --mindate 2015 --lang English

# python -m app.ingest --pubmed "major depressive disorder guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "generalized anxiety disorder guideline" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English

# python -m app.ingest --pubmed "drug drug interaction review"        --types "Review,Systematic Review" --retmax 150 --mindate 2015 --lang English
# python -m app.ingest --pubmed "medication reconciliation guideline" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "metformin lactic acidosis review"    --types "Review,Systematic Review" --retmax 120 --mindate 2010 --lang English

# python -m app.ingest --pubmed "preventive care guideline adults"    --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "multimorbidity management guideline" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English

# python -m app.ingest --pubmed "drug safety review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "drug interactions guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "polypharmacy elderly review" --retmax 200 --mindate 2015

# python -m app.ingest --pubmed "antibiotics guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "antiviral therapy review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "chemotherapy guideline cancer" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "antidepressant efficacy review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "antipsychotic guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "opioid prescribing guideline" --retmax 200 --mindate 2015

# python -m app.ingest --pubmed "type 2 diabetes pharmacologic management guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "hypertension drug therapy guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "asthma pharmacologic management guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "heart failure drug therapy guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "lipid lowering therapy guideline" --retmax 200 --mindate 2015

# python -m app.ingest --pubmed "alcohol use disorder treatment guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "nicotine replacement therapy review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "cannabis health effects review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "cocaine abuse treatment guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "methamphetamine abuse review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "psychedelic therapy review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "LSD psilocybin clinical review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "opioid overdose treatment guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "naloxone distribution guideline" --retmax 200 --mindate 2015

# python -m app.ingest --pubmed "anabolic steroid abuse health effects review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "testosterone therapy guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "corticosteroid treatment guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "glucocorticoid adverse effects review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "creatine supplementation safety review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "protein supplements health effects review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "caffeine performance review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "pre workout supplement review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "dietary supplement safety guideline" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "herbal supplements efficacy review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "ginseng health effects review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "turmeric curcumin review" --retmax 200 --mindate 2015
# python -m app.ingest --pubmed "omega 3 fatty acids supplementation review" --retmax 200 --mindate 2015


# python -m app.ingest --pubmed "autism spectrum disorder guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 150 --mindate 2015 --lang English
# python -m app.ingest --pubmed "ADHD adult guideline" --types "Guideline,Review,Systematic Review" --retmax 150 --mindate 2015 --lang English
# python -m app.ingest --pubmed "intellectual disability guideline" --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2015 --lang English
# python -m app.ingest --pubmed "learning disabilities educational interventions review" --types "Review,Systematic Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "dyslexia intervention guideline" --types "Guideline,Review" --retmax 80 --mindate 2015 --lang English
# python -m app.ingest --pubmed "developmental disabilities guideline" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2015 --lang English

# python -m app.ingest --pubmed "spinal cord injury rehabilitation guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 150 --mindate 2015 --lang English
# python -m app.ingest --pubmed "cerebral palsy management guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English
# python -m app.ingest --pubmed "amputation prosthetics rehabilitation guideline" --types "Guideline,Review" --retmax 120 --mindate 2015 --lang English
# python -m app.ingest --pubmed "muscular dystrophy treatment guideline" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2015 --lang English

# python -m app.ingest --pubmed "chronic fatigue syndrome guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English
# python -m app.ingest --pubmed "fibromyalgia guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English
# python -m app.ingest --pubmed "epilepsy management guideline" --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2015 --lang English
# python -m app.ingest --pubmed "multiple sclerosis guideline" --types "Guideline,Review,Systematic Review" --retmax 150 --mindate 2015 --lang English

# python -m app.ingest --pubmed "hearing loss rehabilitation guideline" --types "Guideline,Review,Systematic Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "visual impairment management guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English
# python -m app.ingest --pubmed "assistive technology disability review" --types "Review,Systematic Review" --retmax 100 --mindate 2015 --lang English

# python -m app.ingest --pubmed "disability inclusion healthcare review" --types "Review,Systematic Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "accessibility guideline disability" --types "Guideline,Review" --retmax 80 --mindate 2015 --lang English
# python -m app.ingest --pubmed "employment disability interventions review" --types "Review,Systematic Review" --retmax 80 --mindate 2015 --lang English


# python -m app.ingest --pubmed "anemia diagnosis guideline" --types "Guideline,Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "venous thromboembolism guideline adults" --types "Guideline,Practice Guideline,Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "hematologic malignancies guideline" --types "Guideline,Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "leukemia treatment guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "lymphoma management guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "breast cancer screening guideline" --types "Guideline,Practice Guideline,Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "prostate cancer screening guideline" --types "Guideline,Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "colorectal cancer screening guideline" --types "Guideline,Practice Guideline,Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "lung cancer screening guideline" --types "Guideline,Practice Guideline,Review" --retmax 150 --mindate 2016 --lang English

# python -m app.ingest --pubmed "HIV treatment guideline adults" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "tuberculosis management guideline" --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "malaria treatment guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "COVID-19 management guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 200 --mindate 2020 --lang English
# python -m app.ingest --pubmed "Ebola outbreak management review" --types "Review,Systematic Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "vaccination schedule guideline adults children" --types "Guideline,Practice Guideline,Review" --retmax 200 --mindate 2015 --lang English

# python -m app.ingest --pubmed "bipolar disorder treatment guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "schizophrenia management guideline" --types "Guideline,Practice Guideline,Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "post traumatic stress disorder guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "eating disorder treatment guideline" --types "Guideline,Review,Systematic Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "sleep disorders insomnia guideline" --types "Guideline,Review,Systematic Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "autism adult management review" --types "Review,Systematic Review" --retmax 80 --mindate 2015 --lang English

# python -m app.ingest --pubmed "contraception guideline" --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "menopause hormone therapy guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "infertility evaluation guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "polycystic ovary syndrome guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "endometriosis management guideline" --types "Guideline,Review,Systematic Review" --retmax 100 --mindate 2016 --lang English
# python -m app.ingest --pubmed "gynecologic oncology guideline" --types "Guideline,Review,Systematic Review" --retmax 100 --mindate 2016 --lang English

# python -m app.ingest --pubmed "neonatal sepsis guideline" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English
# python -m app.ingest --pubmed "pediatric vaccination schedule guideline" --types "Guideline,Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "pediatric obesity management guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "pediatric pain management guideline" --types "Guideline,Review" --retmax 80 --mindate 2015 --lang English

# python -m app.ingest --pubmed "dental caries prevention guideline" --types "Guideline,Review,Systematic Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "periodontal disease management guideline" --types "Guideline,Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "oral cancer screening guideline" --types "Guideline,Review" --retmax 80 --mindate 2015 --lang English

# python -m app.ingest --pubmed "osteoarthritis management guideline" --types "Guideline,Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "rheumatoid arthritis guideline" --types "Guideline,Practice Guideline,Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "gout management guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "osteosarcoma treatment review" --types "Review,Systematic Review" --retmax 100 --mindate 2016 --lang English

# python -m app.ingest --pubmed "anaphylaxis management guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "food allergy guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "immunodeficiency management guideline" --types "Guideline,Review" --retmax 100 --mindate 2016 --lang English

# python -m app.ingest --pubmed "falls prevention guideline elderly" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "dementia management guideline" --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "delirium management guideline hospital" --types "Guideline,Review,Systematic Review" --retmax 100 --mindate 2016 --lang English

# python -m app.ingest --pubmed "mass casualty triage guideline" --types "Guideline,Review,Systematic Review" --retmax 100 --mindate 2016 --lang English
# python -m app.ingest --pubmed "acute pain management emergency department guideline" --types "Guideline,Review" --retmax 100 --mindate 2016 --lang English
# python -m app.ingest --pubmed "perioperative antibiotic prophylaxis guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "perioperative cardiovascular evaluation guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English

# python -m app.ingest --pubmed "laboratory test interpretation guideline" --types "Guideline,Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "biomarker validation review" --types "Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "point of care testing accuracy review" --types "Review,Systematic Review" --retmax 100 --mindate 2015 --lang English

# python -m app.ingest --pubmed "benign prostatic hyperplasia guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "erectile dysfunction guideline" --types "Guideline,Review,Systematic Review" --retmax 100 --mindate 2016 --lang English
# python -m app.ingest --pubmed "urinary incontinence guideline adults" --types "Guideline,Review,Systematic Review" --retmax 100 --mindate 2016 --lang English

# python -m app.ingest --pubmed "acne treatment guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "psoriasis management guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "atopic dermatitis guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "skin cancer prevention guideline" --types "Guideline,Review" --retmax 120 --mindate 2016 --lang English

# python -m app.ingest --pubmed "otitis media guideline" --types "Guideline,Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "sinusitis management guideline" --types "Guideline,Review" --retmax 100 --mindate 2015 --lang English
# python -m app.ingest --pubmed "glaucoma treatment guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English
# python -m app.ingest --pubmed "diabetic retinopathy screening guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English

# python -m app.ingest --pubmed "Parkinson disease management guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English
# python -m app.ingest --pubmed "dementia Alzheimer disease guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English
# python -m app.ingest --pubmed "neuropathic pain treatment guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English

# python -m app.ingest --pubmed "obesity prevention policy review" --types "Review,Systematic Review" --retmax 150 --mindate 2015 --lang English
# python -m app.ingest --pubmed "climate change health effects review" --types "Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "air pollution cardiovascular effects review" --types "Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
# python -m app.ingest --pubmed "health disparities guideline" --types "Guideline,Review" --retmax 120 --mindate 2016 --lang English
# python -m app.ingest --pubmed "social determinants of health interventions review" --types "Review,Systematic Review" --retmax 150 --mindate 2016 --lang English

