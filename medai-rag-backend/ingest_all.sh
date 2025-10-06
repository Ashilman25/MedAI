#!/bin/bash
# Run all PubMed ingestion commands to populate the RAG index

python -m app.ingest --pubmed "atrial fibrillation anticoagulation" --types "Review,Systematic Review" --retmax 120 --mindate 2019 --lang English
python -m app.ingest --pubmed "heart failure guideline"             --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2018 --lang English
python -m app.ingest --pubmed "chest pain evaluation guideline"     --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2018 --lang English
python -m app.ingest --pubmed "coronary artery disease secondary prevention" --types "Review,Systematic Review" --retmax 120 --mindate 2018 --lang English

python -m app.ingest --pubmed "type 2 diabetes guideline adults"    --types "Guideline,Practice Guideline,Systematic Review,Review" --retmax 150 --mindate 2018 --lang English
python -m app.ingest --pubmed "thyroid nodule management guideline" --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2017 --lang English
python -m app.ingest --pubmed "osteoporosis treatment guideline"    --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2017 --lang English

python -m app.ingest --pubmed "antibiotic stewardship guideline"    --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
python -m app.ingest --pubmed "community acquired pneumonia guideline adults" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2018 --lang English
python -m app.ingest --pubmed "UTI treatment guideline adults"      --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2017 --lang English
python -m app.ingest --pubmed "Clostridioides difficile guideline"  --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2017 --lang English

python -m app.ingest --pubmed "acute ischemic stroke imaging guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2017 --lang English
python -m app.ingest --pubmed "status epilepticus management guideline" --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2016 --lang English
python -m app.ingest --pubmed "migraine prophylaxis guideline"         --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2016 --lang English

python -m app.ingest --pubmed "COPD guideline adults"                --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2017 --lang English
python -m app.ingest --pubmed "asthma guideline adults"              --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2017 --lang English
python -m app.ingest --pubmed "pulmonary embolism diagnosis guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English

python -m app.ingest --pubmed "cancer screening guideline adults"   --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
python -m app.ingest --pubmed "palliative care cancer guideline"    --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2016 --lang English

python -m app.ingest --pubmed "prenatal care guideline"             --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English
python -m app.ingest --pubmed "gestational diabetes guideline"      --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
python -m app.ingest --pubmed "postpartum hemorrhage guideline"     --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English

python -m app.ingest --pubmed "fever in infants guideline"          --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2016 --lang English
python -m app.ingest --pubmed "ADHD treatment guideline children"   --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English
python -m app.ingest --pubmed "asthma guideline children"           --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2016 --lang English

python -m app.ingest --pubmed "chronic kidney disease guideline"    --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
python -m app.ingest --pubmed "hemodialysis access guideline"       --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2016 --lang English
python -m app.ingest --pubmed "IBD ulcerative colitis guideline"    --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
python -m app.ingest --pubmed "hepatitis B management guideline"    --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2016 --lang English
python -m app.ingest --pubmed "upper GI bleed guideline"            --types "Guideline,Practice Guideline,Review" --retmax 80 --mindate 2016 --lang English

python -m app.ingest --pubmed "sepsis management guideline adults"  --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
python -m app.ingest --pubmed "traumatic brain injury guideline"    --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English
python -m app.ingest --pubmed "DVT prophylaxis trauma guideline"    --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English

python -m app.ingest --pubmed "pulmonary embolism imaging guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
python -m app.ingest --pubmed "low back pain imaging guideline"      --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English
python -m app.ingest --pubmed "stroke CT vs MRI review"              --types "Review,Systematic Review" --retmax 120 --mindate 2015 --lang English

python -m app.ingest --pubmed "major depressive disorder guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 120 --mindate 2016 --lang English
python -m app.ingest --pubmed "generalized anxiety disorder guideline" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English

python -m app.ingest --pubmed "drug drug interaction review"        --types "Review,Systematic Review" --retmax 150 --mindate 2015 --lang English
python -m app.ingest --pubmed "medication reconciliation guideline" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2015 --lang English
python -m app.ingest --pubmed "metformin lactic acidosis review"    --types "Review,Systematic Review" --retmax 120 --mindate 2010 --lang English

python -m app.ingest --pubmed "preventive care guideline adults"    --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 150 --mindate 2016 --lang English
python -m app.ingest --pubmed "multimorbidity management guideline" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2016 --lang English

python -m app.ingest --pubmed "drug safety review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "drug interactions guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "polypharmacy elderly review" --retmax 200 --mindate 2015

python -m app.ingest --pubmed "antibiotics guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "antiviral therapy review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "chemotherapy guideline cancer" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "antidepressant efficacy review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "antipsychotic guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "opioid prescribing guideline" --retmax 200 --mindate 2015

python -m app.ingest --pubmed "type 2 diabetes pharmacologic management guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "hypertension drug therapy guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "asthma pharmacologic management guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "heart failure drug therapy guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "lipid lowering therapy guideline" --retmax 200 --mindate 2015

python -m app.ingest --pubmed "alcohol use disorder treatment guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "nicotine replacement therapy review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "cannabis health effects review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "cocaine abuse treatment guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "methamphetamine abuse review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "psychedelic therapy review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "LSD psilocybin clinical review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "opioid overdose treatment guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "naloxone distribution guideline" --retmax 200 --mindate 2015

python -m app.ingest --pubmed "anabolic steroid abuse health effects review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "testosterone therapy guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "corticosteroid treatment guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "glucocorticoid adverse effects review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "creatine supplementation safety review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "protein supplements health effects review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "caffeine performance review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "pre workout supplement review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "dietary supplement safety guideline" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "herbal supplements efficacy review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "ginseng health effects review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "turmeric curcumin review" --retmax 200 --mindate 2015
python -m app.ingest --pubmed "omega 3 fatty acids supplementation review" --retmax 200 --mindate 2015


python -m app.ingest --pubmed "autism spectrum disorder guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 150 --mindate 2015 --lang English
python -m app.ingest --pubmed "ADHD adult guideline" --types "Guideline,Review,Systematic Review" --retmax 150 --mindate 2015 --lang English
python -m app.ingest --pubmed "intellectual disability guideline" --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2015 --lang English
python -m app.ingest --pubmed "learning disabilities educational interventions review" --types "Review,Systematic Review" --retmax 100 --mindate 2015 --lang English
python -m app.ingest --pubmed "dyslexia intervention guideline" --types "Guideline,Review" --retmax 80 --mindate 2015 --lang English
python -m app.ingest --pubmed "developmental disabilities guideline" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2015 --lang English

python -m app.ingest --pubmed "spinal cord injury rehabilitation guideline" --types "Guideline,Practice Guideline,Review,Systematic Review" --retmax 150 --mindate 2015 --lang English
python -m app.ingest --pubmed "cerebral palsy management guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English
python -m app.ingest --pubmed "amputation prosthetics rehabilitation guideline" --types "Guideline,Review" --retmax 120 --mindate 2015 --lang English
python -m app.ingest --pubmed "muscular dystrophy treatment guideline" --types "Guideline,Practice Guideline,Review" --retmax 100 --mindate 2015 --lang English

python -m app.ingest --pubmed "chronic fatigue syndrome guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English
python -m app.ingest --pubmed "fibromyalgia guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English
python -m app.ingest --pubmed "epilepsy management guideline" --types "Guideline,Practice Guideline,Review" --retmax 120 --mindate 2015 --lang English
python -m app.ingest --pubmed "multiple sclerosis guideline" --types "Guideline,Review,Systematic Review" --retmax 150 --mindate 2015 --lang English

python -m app.ingest --pubmed "hearing loss rehabilitation guideline" --types "Guideline,Review,Systematic Review" --retmax 100 --mindate 2015 --lang English
python -m app.ingest --pubmed "visual impairment management guideline" --types "Guideline,Review,Systematic Review" --retmax 120 --mindate 2015 --lang English
python -m app.ingest --pubmed "assistive technology disability review" --types "Review,Systematic Review" --retmax 100 --mindate 2015 --lang English

python -m app.ingest --pubmed "disability inclusion healthcare review" --types "Review,Systematic Review" --retmax 100 --mindate 2015 --lang English
python -m app.ingest --pubmed "accessibility guideline disability" --types "Guideline,Review" --retmax 80 --mindate 2015 --lang English
python -m app.ingest --pubmed "employment disability interventions review" --types "Review,Systematic Review" --retmax 80 --mindate 2015 --lang English

