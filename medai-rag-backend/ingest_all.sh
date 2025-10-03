#!/bin/bash
# Run all PubMed ingestion commands to populate the RAG index

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

