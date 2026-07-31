const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Geunsik Lim and Hyun Jo';
pptx.subject = 'HEAR-WORK AI AJA study';
pptx.title = 'HEAR-WORK AI';
pptx.company = 'Sungkyunkwan University / Ajou University';
pptx.lang = 'en-US';
pptx.theme = {
  headFontFace: 'Aptos Display',
  bodyFontFace: 'Aptos',
  lang: 'en-US'
};
pptx.defineLayout({ name:'LAYOUT_WIDE', width:13.333, height:7.5 });

const C = {
  navy:'1F3A5F', blue:'4E79A7', teal:'59A14F', orange:'F28E2B', gray:'6B7280', light:'F4F7FB', dark:'111827', white:'FFFFFF', red:'E15759', purple:'7B61FF'
};

function title(slide, t, st){ slide.addText(t,{x:0.65,y:0.35,w:12,h:0.5,fontSize:28,bold:true,color:C.dark,margin:0}); if(st) slide.addText(st,{x:0.68,y:0.87,w:11.8,h:0.3,fontSize:12,color:C.gray,margin:0}); }
function footer(slide){ slide.addText('HEAR-WORK AI | AJA-targeted public-data manuscript', {x:0.65,y:7.12,w:7,h:0.18,fontSize:8,color:C.gray,margin:0}); }
function pill(slide, text, x,y,w,color){ slide.addShape(pptx.ShapeType.roundRect,{x,y,w,h:0.34,rectRadius:0.06,fill:{color},line:{color}}); slide.addText(text,{x:x+0.08,y:y+0.08,w:w-0.16,h:0.15,fontSize:8.5,color:C.white,bold:true,align:'center',margin:0}); }
function check(slide){ /* layout self-check hook (no-op in standalone build) */ }

// 1
{
let s=pptx.addSlide();
s.background = { color: C.light };
s.addText('HEAR-WORK AI', {x:0.7,y:0.75,w:7,h:0.7,fontSize:44,bold:true,color:C.navy,margin:0});
s.addText('Public-data development and external validation framework for occupational stress, tinnitus, and hearing outcomes', {x:0.75,y:1.62,w:7.2,h:0.95,fontSize:19,color:C.dark,bold:false,breakLine:false,margin:0.02});
pill(s,'American Journal of Audiology target',0.75,2.9,2.25,C.blue);
pill(s,'KNHANES + NHANES',3.15,2.9,1.85,C.teal);
pill(s,'Open medical AI',5.15,2.9,1.72,C.orange);
s.addShape(pptx.ShapeType.ellipse,{x:8.25,y:0.95,w:1.55,h:1.55,fill:{color:C.blue,transparency:12},line:{color:C.blue}});
s.addShape(pptx.ShapeType.ellipse,{x:10.2,y:2.55,w:1.55,h:1.55,fill:{color:C.teal,transparency:12},line:{color:C.teal}});
s.addShape(pptx.ShapeType.ellipse,{x:8.25,y:4.15,w:1.55,h:1.55,fill:{color:C.orange,transparency:12},line:{color:C.orange}});
s.addText('Audiology', {x:8.47,y:1.52,w:1.12,h:0.2,fontSize:12,bold:true,color:C.white,align:'center',margin:0});
s.addText('Open\nScience', {x:10.47,y:3.05,w:1.0,h:0.3,fontSize:11,bold:true,color:C.white,align:'center',margin:0});
s.addText('Clinical\nSafety', {x:8.47,y:4.65,w:1.1,h:0.3,fontSize:11,bold:true,color:C.white,align:'center',margin:0});
s.addText('Geunsik Lim · Hyun Jo\nDraft v0.7 · July 31, 2026', {x:0.75,y:6.55,w:6,h:0.5,fontSize:12,color:C.gray,margin:0});
check(s);
}

// 2
{
let s=pptx.addSlide(); title(s,'Core research question','Association, not unsupported causation'); footer(s);
s.addText('Can public population datasets and open medical AI help researchers identify robust, clinically useful associations among stress, tinnitus, and hearing outcomes?', {x:0.8,y:1.25,w:11.6,h:0.8,fontSize:23,bold:true,color:C.navy,margin:0.03,fit:'shrink'});
const xs=[1.0,4.6,8.2]; const labels=['Stress-related exposure','Tinnitus / hearing outcomes','Clinical actionability']; const desc=['perceived stress, work variables, sleep, noise','audiometry, tinnitus, hearing difficulty, asymmetry','referral safety, rehabilitation, follow-up']; const colors=[C.orange,C.blue,C.teal];
for(let i=0;i<3;i++){ s.addShape(pptx.ShapeType.roundRect,{x:xs[i],y:2.65,w:3.0,h:1.45,rectRadius:0.08,fill:{color:colors[i],transparency:5},line:{color:colors[i]}}); s.addText(labels[i],{x:xs[i]+0.2,y:2.95,w:2.6,h:0.32,fontSize:17,bold:true,color:C.white,align:'center',margin:0}); s.addText(desc[i],{x:xs[i]+0.25,y:3.33,w:2.5,h:0.45,fontSize:10.5,color:C.white,align:'center',margin:0.02}); }
s.addShape(pptx.ShapeType.line,{x:4.0,y:3.35,w:0.55,h:0,line:{color:C.gray,pt:2,beginArrowType:'none',endArrowType:'triangle'}});
s.addShape(pptx.ShapeType.line,{x:7.6,y:3.35,w:0.55,h:0,line:{color:C.gray,pt:2,endArrowType:'triangle'}});
s.addText('Principle: use public data for associations and reproducible benchmarks; use prospective clinical cohorts for timing, recovery, and intervention questions.', {x:1.2,y:5.25,w:10.8,h:0.55,fontSize:18,color:C.dark,align:'center',margin:0.02});
check(s);
}

//3
{
let s=pptx.addSlide(); title(s,'Dataset decision','KNHANES selected as development dataset; NHANES selected as external validation'); footer(s);
const data=[['KNHANES','Primary development','Korean population, prior tinnitus/hearing research, audiometry and health covariates'],['NHANES','External validation','Public CDC files, audiometry, noise exposure, cross-national robustness'],['OHHR / OpenNeuro','Secondary methods','Useful for audiology or neurophysiology substudy, not main stress-outcome analysis']];
for(let i=0;i<data.length;i++){
 const y=1.25+i*1.25;
 s.addShape(pptx.ShapeType.roundRect,{x:0.8,y,w:11.7,h:0.95,rectRadius:0.04,fill:{color:i===0?'EEF6FF':i===1?'F0FBF3':'FFF7ED'},line:{color:'D1D5DB'}});
 s.addText(data[i][0],{x:1.05,y:y+0.2,w:2.0,h:0.23,fontSize:17,bold:true,color:C.navy,margin:0});
 s.addText(data[i][1],{x:3.3,y:y+0.22,w:2.25,h:0.22,fontSize:14,bold:true,color:i===0?C.blue:i===1?C.teal:C.orange,margin:0});
 s.addText(data[i][2],{x:5.8,y:y+0.18,w:6.2,h:0.28,fontSize:13.2,color:C.dark,margin:0.02,fit:'shrink'});
}
s.addText('Reasoning: no single public dataset fully captures workplace stress + tinnitus + audiometry + treatment course. KNHANES/NHANES give the strongest public baseline; hospital cohorts handle treatment timing and recovery.', {x:0.95,y:5.45,w:11.2,h:0.72,fontSize:17,color:C.navy,bold:true,align:'center',margin:0.02});
check(s);
}

//4
{
let s=pptx.addSlide(); title(s,'Analysis pipeline','From public data to clinical extension'); footer(s);
const steps=[['1','Download','KNHANES via KDCA; NHANES via CDC'],['2','Harmonize','Map stress, noise, tinnitus, audiometry'],['3','Estimate','Survey-weighted association models'],['4','Validate','Train on KNHANES, test on NHANES'],['5','Extend','Ajou clinical data + clinician-verified LLM extraction']];
for(let i=0;i<steps.length;i++){
 const y=1.25+i*0.95;
 s.addShape(pptx.ShapeType.ellipse,{x:0.9,y:y,w:0.55,h:0.55,fill:{color:C.blue},line:{color:C.blue}});
 s.addText(steps[i][0],{x:1.08,y:y+0.13,w:0.18,h:0.18,fontSize:13,bold:true,color:C.white,margin:0});
 s.addText(steps[i][1],{x:1.65,y:y+0.02,w:1.8,h:0.28,fontSize:18,bold:true,color:C.navy,margin:0});
 s.addText(steps[i][2],{x:3.75,y:y+0.06,w:8.15,h:0.3,fontSize:14,color:C.dark,margin:0});
 if(i<steps.length-1) s.addShape(pptx.ShapeType.line,{x:1.18,y:y+0.57,w:0,h:0.38,line:{color:C.gray,pt:1.5,endArrowType:'triangle'}});
}
check(s);
}

//5
{
let s=pptx.addSlide(); title(s,'Open medical AI role','MedGemma or similar model as a research accelerator, not a clinician replacement'); footer(s);
const left=[['Allowed','Schema extraction'],['Allowed','Evidence-linked explanations'],['Allowed','Missing data detection'],['Blocked','Diagnosis or steroid advice'],['Blocked','Suppressing red flags']];
for(let i=0;i<left.length;i++){
 const y=1.2+i*0.82; const ok=left[i][0]==='Allowed';
 s.addShape(pptx.ShapeType.roundRect,{x:0.85,y,w:2.0,h:0.45,rectRadius:0.05,fill:{color:ok?C.teal:C.red},line:{color:ok?C.teal:C.red}});
 s.addText(left[i][0],{x:1.15,y:y+0.13,w:1.4,h:0.12,fontSize:10,bold:true,color:C.white,align:'center',margin:0});
 s.addText(left[i][1],{x:3.05,y:y+0.08,w:4.2,h:0.23,fontSize:16,color:C.dark,margin:0});
}
s.addShape(pptx.ShapeType.roundRect,{x:8.2,y:1.3,w:3.45,h:3.6,rectRadius:0.08,fill:{color:C.light},line:{color:'D1D5DB'}});
s.addText('Trust layer', {x:8.55,y:1.65,w:2.8,h:0.32,fontSize:22,bold:true,color:C.navy,align:'center',margin:0});
s.addText('clinician verification\nfixed schema\nversioned prompts\nexternal validation\nfairness and error review', {x:8.55,y:2.25,w:2.8,h:1.6,fontSize:16,color:C.dark,align:'center',breakLine:false,fit:'shrink',margin:0.02});
check(s);
}

//6
{
let s=pptx.addSlide(); title(s,'Expected contributions','Higher credibility, robustness, and usefulness for the audiology community'); footer(s);
const cards=[['Reproducible public baseline','KNHANES + NHANES mapping and code'],['Clinical audiology focus','PTA, asymmetry, tinnitus burden, hearing difficulty'],['Safe AI design','No diagnosis; red-flag rules override probabilistic estimates'],['Open collaboration','GitHub-ready package with paper, code, and slides']];
for(let i=0;i<cards.length;i++){
 const x=i%2===0?0.9:6.8; const y=i<2?1.35:4.0;
 s.addShape(pptx.ShapeType.roundRect,{x,y,w:5.1,h:1.65,rectRadius:0.07,fill:{color:'FFFFFF'},line:{color:'D1D5DB',pt:1}});
 s.addShape(pptx.ShapeType.rect,{x,y,w:0.16,h:1.65,fill:{color:i%2===0?C.blue:C.orange},line:{color:i%2===0?C.blue:C.orange}});
 s.addText(cards[i][0],{x:x+0.35,y:y+0.32,w:4.4,h:0.28,fontSize:18,bold:true,color:C.navy,margin:0});
 s.addText(cards[i][1],{x:x+0.35,y:y+0.8,w:4.35,h:0.35,fontSize:13.5,color:C.dark,margin:0.02});
}
check(s);
}

//7
{
let s=pptx.addSlide(); title(s,'Collaboration plan','Public-data manuscript now; clinical validation next'); footer(s);
s.addShape(pptx.ShapeType.chevron,{x:0.85,y:2.1,w:2.35,h:1.1,fill:{color:C.blue},line:{color:C.blue}}); s.addText('Public\nanalysis', {x:1.25,y:2.38,w:1.3,h:0.42,fontSize:18,bold:true,color:C.white,align:'center',margin:0});
s.addShape(pptx.ShapeType.chevron,{x:3.3,y:2.1,w:2.35,h:1.1,fill:{color:C.teal},line:{color:C.teal}}); s.addText('Clinical\ncohort', {x:3.72,y:2.38,w:1.3,h:0.42,fontSize:18,bold:true,color:C.white,align:'center',margin:0});
s.addShape(pptx.ShapeType.chevron,{x:5.75,y:2.1,w:2.35,h:1.1,fill:{color:C.orange},line:{color:C.orange}}); s.addText('Model\nvalidation', {x:6.15,y:2.38,w:1.4,h:0.42,fontSize:18,bold:true,color:C.white,align:'center',margin:0});
s.addShape(pptx.ShapeType.chevron,{x:8.2,y:2.1,w:2.35,h:1.1,fill:{color:C.purple},line:{color:C.purple}}); s.addText('AJA\nsubmission', {x:8.62,y:2.38,w:1.3,h:0.42,fontSize:18,bold:true,color:C.white,align:'center',margin:0});
s.addText('Ask from collaborators: validate variables, refine audiology outcomes, identify feasible clinical data fields, and review safety constraints before IRB submission.', {x:1.1,y:4.5,w:11.1,h:0.7,fontSize:20,bold:true,color:C.navy,align:'center',margin:0.02});
check(s);
}

//7b Aims and hypotheses
{
let s=pptx.addSlide(); title(s,'Aims and prespecified hypotheses','Falsifiable claims frozen before analysis'); footer(s);
const aims=[
 ['H1','Association','Perceived stress is associated with tinnitus after adjustment; the stress–threshold association attenuates once age and noise are controlled.'],
 ['H2','Transportability','KNHANES models retain discrimination in NHANES; calibration is restored by recalibration (tinnitus > hearing-loss model).'],
 ['H3','Safe, explainable AI','Schema-constrained extraction reaches high clinician-verified accuracy; the red-flag layer achieves near-complete recall.'],
 ['A4','Shared benefit','Open code, data dictionary, model cards, prompts, and a synthetic-data path lower the barrier for global reuse.']
];
for(let i=0;i<aims.length;i++){
 const y=1.3+i*1.25; const col=[C.blue,C.teal,C.red,C.orange][i];
 s.addShape(pptx.ShapeType.roundRect,{x:0.85,y,w:1.35,h:0.95,rectRadius:0.06,fill:{color:col},line:{color:col}});
 s.addText(aims[i][0],{x:0.85,y:y+0.32,w:1.35,h:0.3,fontSize:20,bold:true,color:C.white,align:'center',margin:0});
 s.addText(aims[i][1],{x:2.45,y:y+0.12,w:3.0,h:0.3,fontSize:16,bold:true,color:C.navy,margin:0});
 s.addText(aims[i][2],{x:2.45,y:y+0.5,w:9.6,h:0.42,fontSize:12.5,color:C.dark,margin:0.02,fit:'shrink'});
}
check(s);
}

//7c Rigor, reporting, and clinical safety
{
let s=pptx.addSlide(); title(s,'Rigor, reporting, and the treatment window','What makes the framework credible and safe'); footer(s);
const cards=[
 ['Reporting standards','STROBE (observational) + TRIPOD+AI (prediction); frozen targets, predictors, and metrics.'],
 ['Beyond AUROC','Calibration slope/intercept, Brier, decision-curve utility, SHAP interpretability.'],
 ['Fairness','Subgroup discrimination and calibration by sex, age, employment, noise, asymmetry.'],
 ['Golden-window safety','Deterministic red-flag layer overrides the model for SSNHL / neuro signs — validated at recall = 1.0 on curated vignettes.']
];
for(let i=0;i<cards.length;i++){
 const x=i%2===0?0.9:6.8; const y=i<2?1.35:4.0; const col=i===3?C.red:(i%2===0?C.blue:C.teal);
 s.addShape(pptx.ShapeType.roundRect,{x,y,w:5.1,h:1.7,rectRadius:0.07,fill:{color:'FFFFFF'},line:{color:'D1D5DB',pt:1}});
 s.addShape(pptx.ShapeType.rect,{x,y,w:0.16,h:1.7,fill:{color:col},line:{color:col}});
 s.addText(cards[i][0],{x:x+0.35,y:y+0.28,w:4.5,h:0.3,fontSize:18,bold:true,color:C.navy,margin:0});
 s.addText(cards[i][1],{x:x+0.35,y:y+0.76,w:4.5,h:0.8,fontSize:13,color:C.dark,margin:0.02,fit:'shrink'});
}
check(s);
}

//8
{
let s=pptx.addSlide(); s.background={color:C.navy};
s.addText('HEAR-WORK AI', {x:0.85,y:0.9,w:6.5,h:0.55,fontSize:38,bold:true,color:C.white,margin:0});
s.addText('Open, reproducible audiology research for tinnitus, hearing loss, stress-related exposures, and safe AI-assisted clinical learning.', {x:0.9,y:1.75,w:10.8,h:0.9,fontSize:24,color:C.white,bold:false,margin:0.02});
s.addText('Next step: finalize variable mapping and run KNHANES/NHANES baseline analysis.', {x:0.9,y:4.95,w:9.5,h:0.4,fontSize:19,bold:true,color:'DDEEFF',margin:0});
s.addText('Geunsik Lim · leemgs@g.skku.edu\nHyun Jo · joehyun@ajou.ac.kr', {x:0.9,y:6.15,w:6,h:0.45,fontSize:13,color:'DDEEFF',margin:0});
check(s);
}

pptx.writeFile({ fileName: 'HEAR-WORK_AI_AJA_public_dataset_presentation_v0.7.pptx' });
