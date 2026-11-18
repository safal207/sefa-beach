import {readdir,readFile,mkdir,writeFile} from 'node:fs/promises';
import {join} from 'node:path';

export function summarizeReport(lhr){
  if(lhr?.lighthouseVersion == null || !lhr.categories?.performance || !lhr.audits) throw Error('Invalid Lighthouse result');
  const scores=Object.fromEntries(['performance','accessibility','best-practices','seo'].map(k=>[k,Number.isFinite(lhr.categories[k]?.score)?Math.round(lhr.categories[k].score*100):null]));
  const metrics=Object.fromEntries([['lcp','largest-contentful-paint'],['cls','cumulative-layout-shift'],['tbt','total-blocking-time'],['fcp','first-contentful-paint']].map(([short,k])=>[short,Number.isFinite(lhr.audits[k]?.numericValue)?lhr.audits[k].numericValue:null]));
  return {profile:process.env.SEFA_LH_PROFILE||'mobile',url:lhr.finalDisplayedUrl||lhr.finalUrl||null,lighthouseVersion:lhr.lighthouseVersion,scores,metrics,kind:'observed-lab-metrics',budgetEnforced:false};
}
const input=process.argv[2];
if(input){
 const files=(await readdir(input)).filter(f=>/^lhr.*\.json$/.test(f)).sort();
 if(!files.length)throw Error('No Lighthouse JSON report found');
 const reports=[];
 for(const file of files)reports.push(summarizeReport(JSON.parse(await readFile(join(input,file),'utf8'))));
 await mkdir('.artifacts/performance',{recursive:true});
 const out={head:process.env.GITHUB_SHA||null,runId:process.env.GITHUB_RUN_ID||null,results:reports};
 await writeFile('.artifacts/performance/summary.json',JSON.stringify(out,null,2)+'\n');
 const lines=reports.map(r=>[r.profile,JSON.stringify(r.scores),'LCP='+r.metrics.lcp,'CLS='+r.metrics.cls,'TBT='+r.metrics.tbt].join(' | '));
 await writeFile('.artifacts/performance/summary.md',['# Sefa Lighthouse advisory report','',...lines,'','Lab measurements, not user traffic. Thresholds are not yet approved.',''].join('\n'));
 console.log(lines.join('\n'));
}
