const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Geunsik Lim and Hyun Jo';
pptx.subject = 'HEAR-WORK AI AJA study (Korean)';
pptx.title = 'HEAR-WORK AI (한글판)';
pptx.company = 'Sungkyunkwan University / Ajou University';
pptx.lang = 'ko-KR';
pptx.theme = {
  headFontFace: 'Malgun Gothic',
  bodyFontFace: 'Malgun Gothic',
  lang: 'ko-KR'
};
pptx.defineLayout({ name:'LAYOUT_WIDE', width:13.333, height:7.5 });

// Default every text box to a Korean-capable font (맑은 고딕).
const KF = 'Malgun Gothic';
const _origAddSlide = pptx.addSlide.bind(pptx);
pptx.addSlide = function(...a){
  const s = _origAddSlide(...a);
  const _add = s.addText.bind(s);
  s.addText = (t, o = {}) => _add(t, ('fontFace' in o) ? o : Object.assign({ fontFace: KF }, o));
  return s;
};

const C = {
  navy:'1F3A5F', blue:'4E79A7', teal:'59A14F', orange:'F28E2B', gray:'6B7280', light:'F4F7FB', dark:'111827', white:'FFFFFF', red:'E15759', purple:'7B61FF'
};

function title(slide, t, st){ slide.addText(t,{x:0.65,y:0.35,w:12,h:0.5,fontSize:28,bold:true,color:C.dark,margin:0}); if(st) slide.addText(st,{x:0.68,y:0.87,w:11.8,h:0.3,fontSize:12,color:C.gray,margin:0}); }
function footer(slide){ slide.addText('HEAR-WORK AI | AJA 목표 공개 데이터 논문', {x:0.65,y:7.12,w:7,h:0.18,fontSize:8,color:C.gray,margin:0}); }
function pill(slide, text, x,y,w,color){ slide.addShape(pptx.ShapeType.roundRect,{x,y,w,h:0.34,rectRadius:0.06,fill:{color},line:{color}}); slide.addText(text,{x:x+0.08,y:y+0.08,w:w-0.16,h:0.15,fontSize:8.5,color:C.white,bold:true,align:'center',margin:0}); }
function check(slide){ /* layout self-check hook (no-op in standalone build) */ }

// 1
{
let s=pptx.addSlide();
s.background = { color: C.light };
s.addText('HEAR-WORK AI', {x:0.7,y:0.75,w:7,h:0.7,fontSize:44,bold:true,color:C.navy,margin:0});
s.addText('직장인 스트레스·이명·난청의 연관성을 위한 공개 데이터 기반 개발 및 외부검증 프레임워크', {x:0.75,y:1.62,w:7.2,h:0.95,fontSize:19,color:C.dark,bold:false,breakLine:false,margin:0.02});
pill(s,'American Journal of Audiology 목표',0.75,2.9,2.35,C.blue);
pill(s,'KNHANES + NHANES',3.25,2.9,1.85,C.teal);
pill(s,'공개 의료 AI',5.25,2.9,1.5,C.orange);
s.addShape(pptx.ShapeType.ellipse,{x:8.25,y:0.95,w:1.55,h:1.55,fill:{color:C.blue,transparency:12},line:{color:C.blue}});
s.addShape(pptx.ShapeType.ellipse,{x:10.2,y:2.55,w:1.55,h:1.55,fill:{color:C.teal,transparency:12},line:{color:C.teal}});
s.addShape(pptx.ShapeType.ellipse,{x:8.25,y:4.15,w:1.55,h:1.55,fill:{color:C.orange,transparency:12},line:{color:C.orange}});
s.addText('청각학', {x:8.47,y:1.52,w:1.12,h:0.2,fontSize:12,bold:true,color:C.white,align:'center',margin:0});
s.addText('오픈\n사이언스', {x:10.47,y:3.0,w:1.0,h:0.4,fontSize:11,bold:true,color:C.white,align:'center',margin:0});
s.addText('임상\n안전성', {x:8.47,y:4.6,w:1.1,h:0.4,fontSize:11,bold:true,color:C.white,align:'center',margin:0});
s.addText('Geunsik Lim · Hyun Jo\n초안 v0.7 · 2026년 7월 31일', {x:0.75,y:6.55,w:6,h:0.5,fontSize:12,color:C.gray,margin:0});
check(s);
}

// 2
{
let s=pptx.addSlide(); title(s,'핵심 연구 질문','인과관계가 아닌 연관성 규명'); footer(s);
s.addText('공개 인구집단 데이터와 공개 의료 AI를 활용해 스트레스·이명·난청 사이의 강건하고 임상적으로 유용한 연관성을 규명할 수 있는가?', {x:0.8,y:1.25,w:11.6,h:0.8,fontSize:23,bold:true,color:C.navy,margin:0.03,fit:'shrink'});
const xs=[1.0,4.6,8.2]; const labels=['스트레스 관련 노출','이명 / 청력 결과','임상적 실행가능성']; const desc=['인지된 스트레스, 근로 변수, 수면, 소음','순음청력검사, 이명, 청력 곤란, 비대칭','안전한 의뢰, 재활, 추적관찰']; const colors=[C.orange,C.blue,C.teal];
for(let i=0;i<3;i++){ s.addShape(pptx.ShapeType.roundRect,{x:xs[i],y:2.65,w:3.0,h:1.45,rectRadius:0.08,fill:{color:colors[i],transparency:5},line:{color:colors[i]}}); s.addText(labels[i],{x:xs[i]+0.2,y:2.95,w:2.6,h:0.32,fontSize:17,bold:true,color:C.white,align:'center',margin:0}); s.addText(desc[i],{x:xs[i]+0.25,y:3.33,w:2.5,h:0.55,fontSize:10.5,color:C.white,align:'center',margin:0.02}); }
s.addShape(pptx.ShapeType.line,{x:4.0,y:3.35,w:0.55,h:0,line:{color:C.gray,pt:2,beginArrowType:'none',endArrowType:'triangle'}});
s.addShape(pptx.ShapeType.line,{x:7.6,y:3.35,w:0.55,h:0,line:{color:C.gray,pt:2,endArrowType:'triangle'}});
s.addText('원칙: 공개 데이터는 연관성과 재현 가능한 벤치마크에, 치료 시기·회복·중재 문제는 전향적 임상 코호트로 규명한다.', {x:1.2,y:5.25,w:10.8,h:0.55,fontSize:18,color:C.dark,align:'center',margin:0.02});
check(s);
}

//3
{
let s=pptx.addSlide(); title(s,'데이터셋 선정','개발용 KNHANES, 외부검증용 NHANES'); footer(s);
const data=[['KNHANES','주 개발 데이터','한국인 대상, 이명/청력 선행연구, 순음청력 및 건강 공변량'],['NHANES','외부 검증','공개 CDC 자료, 순음청력, 소음 노출, 국가 간 강건성'],['OHHR / OpenNeuro','보조 방법 검증','청각학·신경생리 하위연구에 유용, 주 스트레스-결과 분석에는 부적합']];
for(let i=0;i<data.length;i++){
 const y=1.25+i*1.25;
 s.addShape(pptx.ShapeType.roundRect,{x:0.8,y,w:11.7,h:0.95,rectRadius:0.04,fill:{color:i===0?'EEF6FF':i===1?'F0FBF3':'FFF7ED'},line:{color:'D1D5DB'}});
 s.addText(data[i][0],{x:1.05,y:y+0.2,w:2.1,h:0.23,fontSize:16,bold:true,color:C.navy,margin:0});
 s.addText(data[i][1],{x:3.35,y:y+0.22,w:2.25,h:0.22,fontSize:14,bold:true,color:i===0?C.blue:i===1?C.teal:C.orange,margin:0});
 s.addText(data[i][2],{x:5.85,y:y+0.18,w:6.15,h:0.5,fontSize:13,color:C.dark,margin:0.02,fit:'shrink'});
}
s.addText('근거: 직장 스트레스 + 이명 + 순음청력 + 치료 경과를 모두 담은 단일 공개 데이터셋은 없다. KNHANES/NHANES가 가장 강력한 공개 기준선을 제공하며, 치료 시기와 회복은 병원 코호트로 다룬다.', {x:0.95,y:5.4,w:11.2,h:0.8,fontSize:16,color:C.navy,bold:true,align:'center',margin:0.02});
check(s);
}

//4
{
let s=pptx.addSlide(); title(s,'분석 파이프라인','공개 데이터에서 임상 확장까지'); footer(s);
const steps=[['1','다운로드','KDCA로 KNHANES, CDC로 NHANES'],['2','조화','스트레스·소음·이명·순음청력 매핑'],['3','추정','복합표본 가중 연관성 모형'],['4','검증','KNHANES 학습, NHANES 검정'],['5','확장','아주대 임상데이터 + 임상의 검증 LLM 추출']];
for(let i=0;i<steps.length;i++){
 const y=1.25+i*0.95;
 s.addShape(pptx.ShapeType.ellipse,{x:0.9,y:y,w:0.55,h:0.55,fill:{color:C.blue},line:{color:C.blue}});
 s.addText(steps[i][0],{x:1.08,y:y+0.13,w:0.18,h:0.18,fontSize:13,bold:true,color:C.white,margin:0});
 s.addText(steps[i][1],{x:1.65,y:y+0.02,w:2.0,h:0.28,fontSize:18,bold:true,color:C.navy,margin:0});
 s.addText(steps[i][2],{x:3.95,y:y+0.06,w:7.95,h:0.3,fontSize:14,color:C.dark,margin:0});
 if(i<steps.length-1) s.addShape(pptx.ShapeType.line,{x:1.18,y:y+0.57,w:0,h:0.38,line:{color:C.gray,pt:1.5,endArrowType:'triangle'}});
}
check(s);
}

//5
{
let s=pptx.addSlide(); title(s,'공개 의료 AI의 역할','MedGemma 등 공개 모델은 임상의 대체가 아닌 연구 가속 도구'); footer(s);
const left=[['허용','스키마 추출'],['허용','근거 연계 설명'],['허용','결측 데이터 탐지'],['금지','진단·스테로이드 권고'],['금지','응급징후 억제']];
for(let i=0;i<left.length;i++){
 const y=1.2+i*0.82; const ok=left[i][0]==='허용';
 s.addShape(pptx.ShapeType.roundRect,{x:0.85,y,w:1.6,h:0.45,rectRadius:0.05,fill:{color:ok?C.teal:C.red},line:{color:ok?C.teal:C.red}});
 s.addText(left[i][0],{x:1.05,y:y+0.11,w:1.2,h:0.2,fontSize:12,bold:true,color:C.white,align:'center',margin:0});
 s.addText(left[i][1],{x:2.65,y:y+0.08,w:4.6,h:0.23,fontSize:16,color:C.dark,margin:0});
}
s.addShape(pptx.ShapeType.roundRect,{x:8.2,y:1.3,w:3.45,h:3.6,rectRadius:0.08,fill:{color:C.light},line:{color:'D1D5DB'}});
s.addText('신뢰 계층', {x:8.55,y:1.65,w:2.8,h:0.32,fontSize:22,bold:true,color:C.navy,align:'center',margin:0});
s.addText('임상의 검증\n고정 스키마\n버전 관리 프롬프트\n외부 검증\n공정성·오류 검토', {x:8.55,y:2.3,w:2.8,h:2.3,fontSize:16,color:C.dark,align:'center',breakLine:false,fit:'shrink',margin:0.02});
check(s);
}

//6
{
let s=pptx.addSlide(); title(s,'기대 기여','청각학계를 위한 신뢰성·강건성·유용성 향상'); footer(s);
const cards=[['재현 가능한 공개 기준선','KNHANES + NHANES 매핑 및 코드'],['임상 청각학 초점','PTA, 비대칭, 이명 부담, 청력 곤란'],['안전한 AI 설계','진단 없음; 응급징후 규칙이 확률 추정을 우선 대체'],['공개 협업','논문·코드·슬라이드를 담은 GitHub 패키지']];
for(let i=0;i<cards.length;i++){
 const x=i%2===0?0.9:6.8; const y=i<2?1.35:4.0;
 s.addShape(pptx.ShapeType.roundRect,{x,y,w:5.1,h:1.65,rectRadius:0.07,fill:{color:'FFFFFF'},line:{color:'D1D5DB',pt:1}});
 s.addShape(pptx.ShapeType.rect,{x,y,w:0.16,h:1.65,fill:{color:i%2===0?C.blue:C.orange},line:{color:i%2===0?C.blue:C.orange}});
 s.addText(cards[i][0],{x:x+0.35,y:y+0.32,w:4.4,h:0.28,fontSize:18,bold:true,color:C.navy,margin:0});
 s.addText(cards[i][1],{x:x+0.35,y:y+0.8,w:4.35,h:0.5,fontSize:13.5,color:C.dark,margin:0.02});
}
check(s);
}

//7
{
let s=pptx.addSlide(); title(s,'협업 계획','지금은 공개 데이터 논문, 다음은 임상 검증'); footer(s);
s.addShape(pptx.ShapeType.chevron,{x:0.85,y:2.1,w:2.35,h:1.1,fill:{color:C.blue},line:{color:C.blue}}); s.addText('공개\n분석', {x:1.25,y:2.34,w:1.4,h:0.5,fontSize:18,bold:true,color:C.white,align:'center',margin:0});
s.addShape(pptx.ShapeType.chevron,{x:3.3,y:2.1,w:2.35,h:1.1,fill:{color:C.teal},line:{color:C.teal}}); s.addText('임상\n코호트', {x:3.72,y:2.34,w:1.4,h:0.5,fontSize:18,bold:true,color:C.white,align:'center',margin:0});
s.addShape(pptx.ShapeType.chevron,{x:5.75,y:2.1,w:2.35,h:1.1,fill:{color:C.orange},line:{color:C.orange}}); s.addText('모형\n검증', {x:6.15,y:2.34,w:1.4,h:0.5,fontSize:18,bold:true,color:C.white,align:'center',margin:0});
s.addShape(pptx.ShapeType.chevron,{x:8.2,y:2.1,w:2.35,h:1.1,fill:{color:C.purple},line:{color:C.purple}}); s.addText('AJA\n투고', {x:8.62,y:2.34,w:1.3,h:0.5,fontSize:18,bold:true,color:C.white,align:'center',margin:0});
s.addText('협력 요청: 변수 검증, 청각학 결과지표 정교화, 실현 가능한 임상 데이터 항목 발굴, IRB 제출 전 안전 제약 검토.', {x:1.1,y:4.5,w:11.1,h:0.7,fontSize:19,bold:true,color:C.navy,align:'center',margin:0.02});
check(s);
}

//7b 연구 목표 및 가설
{
let s=pptx.addSlide(); title(s,'연구 목표 및 사전 가설','분석 전 고정한 반증 가능한 주장'); footer(s);
const aims=[
 ['H1','연관성','보정 후에도 인지된 스트레스는 이명과 연관; 연령·소음 보정 시 스트레스-역치 연관성은 약화된다.'],
 ['H2','이식성','KNHANES 모형은 NHANES에서 변별력을 유지; 재보정으로 보정도가 회복된다(이명 > 난청 모형).'],
 ['H3','안전·설명가능 AI','스키마 제약 추출은 임상의 검증 정확도가 높고, 응급징후 계층은 거의 완전한 재현율을 달성한다.'],
 ['A4','홍익 기여','공개 코드·데이터 사전·모델 카드·프롬프트·합성데이터 경로로 전 세계 재사용 장벽을 낮춘다.']
];
for(let i=0;i<aims.length;i++){
 const y=1.3+i*1.25; const col=[C.blue,C.teal,C.red,C.orange][i];
 s.addShape(pptx.ShapeType.roundRect,{x:0.85,y,w:1.35,h:0.95,rectRadius:0.06,fill:{color:col},line:{color:col}});
 s.addText(aims[i][0],{x:0.85,y:y+0.32,w:1.35,h:0.3,fontSize:20,bold:true,color:C.white,align:'center',margin:0});
 s.addText(aims[i][1],{x:2.45,y:y+0.1,w:3.0,h:0.35,fontSize:16,bold:true,color:C.navy,margin:0});
 s.addText(aims[i][2],{x:2.45,y:y+0.5,w:9.6,h:0.5,fontSize:12.5,color:C.dark,margin:0.02,fit:'shrink'});
}
check(s);
}

//7c 엄밀성·보고·안전
{
let s=pptx.addSlide(); title(s,'엄밀성, 보고, 그리고 치료 골든타임','프레임워크를 신뢰할 수 있고 안전하게 만드는 요소'); footer(s);
const cards=[
 ['보고 표준','STROBE(관찰연구) + TRIPOD+AI(예측); 목표·예측변수·지표를 사전 고정.'],
 ['AUROC를 넘어','보정 기울기/절편, Brier, 결정곡선 유용성, SHAP 해석가능성.'],
 ['공정성','성별·연령·고용·소음·비대칭 하위집단별 변별력과 보정도.'],
 ['골든타임 안전장치','결정론적 응급징후 계층이 돌발성 난청/신경징후에 대해 모형을 우선 대체 — 선별 사례에서 재현율 1.0 검증.']
];
for(let i=0;i<cards.length;i++){
 const x=i%2===0?0.9:6.8; const y=i<2?1.35:4.0; const col=i===3?C.red:(i%2===0?C.blue:C.teal);
 s.addShape(pptx.ShapeType.roundRect,{x,y,w:5.1,h:1.7,rectRadius:0.07,fill:{color:'FFFFFF'},line:{color:'D1D5DB',pt:1}});
 s.addShape(pptx.ShapeType.rect,{x,y,w:0.16,h:1.7,fill:{color:col},line:{color:col}});
 s.addText(cards[i][0],{x:x+0.35,y:y+0.26,w:4.5,h:0.3,fontSize:18,bold:true,color:C.navy,margin:0});
 s.addText(cards[i][1],{x:x+0.35,y:y+0.74,w:4.5,h:0.85,fontSize:13,color:C.dark,margin:0.02,fit:'shrink'});
}
check(s);
}

//8
{
let s=pptx.addSlide(); s.background={color:C.navy};
s.addText('HEAR-WORK AI', {x:0.85,y:0.9,w:6.5,h:0.55,fontSize:38,bold:true,color:C.white,margin:0});
s.addText('이명·난청·스트레스 관련 노출과 안전한 AI 보조 임상 학습을 위한 공개·재현 가능한 청각학 연구.', {x:0.9,y:1.75,w:10.8,h:0.9,fontSize:24,color:C.white,bold:false,margin:0.02});
s.addText('다음 단계: 변수 매핑을 확정하고 KNHANES/NHANES 기준선 분석을 실행.', {x:0.9,y:4.95,w:10.5,h:0.4,fontSize:19,bold:true,color:'DDEEFF',margin:0});
s.addText('Geunsik Lim · leemgs@g.skku.edu\nHyun Jo · joehyun@ajou.ac.kr', {x:0.9,y:6.15,w:6,h:0.45,fontSize:13,color:'DDEEFF',margin:0});
check(s);
}

pptx.writeFile({ fileName: 'HEAR-WORK_AI_AJA_public_dataset_presentation_ko_v0.7.pptx' });
