import test from 'node:test';
import assert from 'node:assert/strict';
import {summarizeReport} from '../scripts/summarize-lighthouse.mjs';
const report={lighthouseVersion:'12.0.0',finalDisplayedUrl:'http://localhost/index.html',categories:{performance:{score:.81},accessibility:{score:.95},'best-practices':{score:1},seo:{score:0}},audits:{'largest-contentful-paint':{numericValue:2550},'cumulative-layout-shift':{numericValue:.02},'total-blocking-time':{numericValue:88},'first-contentful-paint':{numericValue:1200}}};
test('report scores and raw metrics not confused',()=>{const s=summarizeReport(report);assert.equal(s.scores.performance,81);assert.equal(s.metrics.lcp,2550);assert.equal(s.metrics.cls,.02);assert.equal(s.budgetEnforced,false)});
test('zero scores preserved',()=>assert.equal(summarizeReport(report).scores.seo,0));
test('missing audit is null, never a PASS',()=>{const clone=structuredClone(report);delete clone.audits['largest-contentful-paint'];assert.equal(summarizeReport(clone).metrics.lcp,null)});
test('invalid report rejected',()=>assert.throws(()=>summarizeReport({categories:{}})));
