const fs=require('fs'),crypto=require('crypto');const {Story}=require('inkjs/full');
const hash=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');let checked=0;
for(const game of ['the_intercept','emoji']){
 const code=fs.readFileSync(`data/processed/${game}.compiled.json`,'utf8');
 const contexts=JSON.parse(fs.readFileSync(`data/processed/${game}.contexts.json`));
 for(const c of contexts)for(const expected of c.edges){
  const s=new Story(code);s.state.LoadJson(c.state);let before=JSON.parse(s.state.ToJson()).variablesState;
  s.ChooseChoiceIndex(expected.index);let text='';while(s.canContinue)text+=s.Continue();text=text.trim();
  const after=JSON.parse(s.state.ToJson()).variablesState;let delta={};for(const k of Object.keys(after).sort())if(JSON.stringify(after[k])!==JSON.stringify(before[k]))delta[k]=after[k];
  const obs={text,delta,next_actions:s.currentChoices.map(c=>c.sourcePath),terminal:!s.currentChoices.length};
  if(hash(obs)!==expected.outcome)throw Error(`Replay mismatch: ${game}/${c.context_id}/${expected.id}`);checked++;
 }
}
fs.writeFileSync('results/replay_verification.json',JSON.stringify({checked,failures:0},null,2));console.log(`${checked} transitions replayed exactly.`);
