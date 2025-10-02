function randomConf() { return Math.round((0.55 + Math.random() * 0.4) * 100) / 100 }
export async function mockAsk(query, top_k=5) {
  const confidence = randomConf()
  const citations = Array.from({length: Math.min(top_k,3)}, (_,i)=> ({
    title: i===0 ? 'Metformin Side Effects — PubMed' : i===1 ? 'AHA/ASA Guidelines for Stroke Imaging' : 'WHO Clinical Guidance Example',
    url: i===0 ? 'https://pubmed.ncbi.nlm.nih.gov/0000001/' : i===1 ? 'https://www.ahajournals.org/doi/10.1161/STROKEAHA.115.011585' : 'https://www.who.int/',
    snippet: i===0 ? 'Common adverse effects include GI upset (nausea, diarrhea); rare risk in renal impairment.' :
             i===1 ? 'CT quickly rules out hemorrhage; MRI (DWI) more sensitive for acute ischemia.' :
                     'Guideline snippet placeholder relevant to the query.'
  }))
  const bullets = [
    'Summary: concise evidence‑based points aligned to retrieved sources.',
    'All claims reference citations [1]‑[3].',
    'Caution if renal/hepatic impairment or imaging contraindications.'
  ]
  return { answer: `• ${bullets.join('\n• ')}`, citations, confidence }
}
export async function mockIngest(file) {
  await new Promise(r=>setTimeout(r, 300))
  return { ok: true, added: 12, skipped: 0, filename: file?.name || 'mock.pdf' }
}
