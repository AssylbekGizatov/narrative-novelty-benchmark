/* Execute real Ink programs; preserve selected save states for audit/replay. */
const fs=require('fs'), crypto=require('crypto');
const {Compiler,Story}=require('inkjs/full');
const hash=x=>crypto.createHash('sha256').update(typeof x==='string'?x:JSON.stringify(x)).digest('hex');
function loadStory(code){const s=new Story(code);s.auditErrors=[];s.onError=(message,type)=>{s.auditErrors.push({message,type});};return s;}
function rng(seed){let a=seed>>>0;return()=>{a+=0x6D2B79F5;let t=a;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296}}
function drain(s){let text='',n=0;while(s.canContinue){text+=s.Continue();if(++n>10000)throw Error('continuation bound');}return text.trim();}
function vars(s){return JSON.parse(s.state.ToJson()).variablesState;}
function observable(s,text,before){const after=vars(s);let delta={};for(const k of Object.keys(after).sort())if(JSON.stringify(after[k])!==JSON.stringify(before[k]))delta[k]=after[k];return {text,delta,next_actions:s.currentChoices.map(c=>c.sourcePath),terminal:!s.currentChoices.length};}
const meta=[];
for(const game of ['the_intercept','emoji']){
 const source=fs.readFileSync(`data/raw/${game}.ink`,'utf8');let compiler=new Compiler(source);let compiled=compiler.Compile();if(compiler.errors.length)throw Error(compiler.errors);
 const bytecode=compiled.ToJson();fs.writeFileSync(`data/processed/${game}.compiled.json`,bytecode);
 const reservoir=[],seen=new Set(),rand=rng(731);let eligible=0,truncated=0,terminations=0,stepsTotal=0,errorRuns=0;const traces=[],exclusions=[];
 for(let run=0;run<200;run++){
  const s=loadStory(bytecode),random=rng(1000+run);s.state.storySeed=1000+run;
  let context=drain(s),steps=0;const trace=[];
  while(s.currentChoices.length&&steps<120&&!s.auditErrors.length){
   const state=s.state.ToJson();const st=JSON.parse(state);delete st.storySeed;delete st.previousRandom;const key=hash(st);
   if(s.currentChoices.length>=2&&!seen.has(key)){
    seen.add(key);eligible++;const item={game,context_id:key,run,step:steps,context,state};
    if(reservoir.length<120)reservoir.push(item);else{const j=Math.floor(rand()*eligible);if(j<120)reservoir[j]=item;}
   }
   let j=Math.floor(random()*s.currentChoices.length);trace.push(s.currentChoices[j].sourcePath);s.ChooseChoiceIndex(j);context=drain(s);steps++;
  }
  if(s.auditErrors.length)errorRuns++;else if(s.currentChoices.length)truncated++;else terminations++;stepsTotal+=steps;traces.push({run,steps,terminated:!s.currentChoices.length&&!s.auditErrors.length,errors:s.auditErrors,actions:trace});
 }
 const output=[];
 for(const item of reservoir){
  const s=loadStory(bytecode);s.state.LoadJson(item.state);const before=vars(s),choices=s.currentChoices.map(c=>({index:c.index,id:c.sourcePath,text:c.text}));let edges=[];
  for(const c of choices){s.state.LoadJson(item.state);s.ChooseChoiceIndex(c.index);const obs=observable(s,drain(s),before);edges.push({...c,outcome:hash(obs),...obs,action_text:c.text});edges.at(-1).text=obs.text;}
  if(s.auditErrors.length)exclusions.push({context_id:item.context_id,errors:s.auditErrors});else output.push({...item,edges});
 }
 fs.writeFileSync(`data/processed/${game}.contexts.json`,JSON.stringify(output,null,2));
 fs.writeFileSync(`data/processed/${game}.walks.json`,JSON.stringify(traces,null,2));
 fs.writeFileSync(`data/processed/${game}.exclusions.json`,JSON.stringify(exclusions,null,2));
 const row={game,source_sha256:hash(source),runs:200,horizon:120,eligible_states:eligible,sampled_states:reservoir.length,retained_states:output.length,excluded_states:exclusions.length,total_choices:stepsTotal,truncated,terminations,error_runs:errorRuns,extracted_edges:output.reduce((a,c)=>a+c.edges.length,0),compiler_warnings:compiler.warnings};meta.push(row);console.log(row);
}
fs.writeFileSync('data/processed/extraction_summary.json',JSON.stringify(meta,null,2));
