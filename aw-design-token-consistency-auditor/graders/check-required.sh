#!/bin/sh
node <<'NODE'
const fs=require('fs'),s=JSON.parse(fs.readFileSync('grader-spec.json','utf8')),c=[],a=(n,p,m)=>c.push({name:n,passed:p,message:m});
if(!fs.existsSync(s.file))a('output-file',false,`Missing ${s.file}`);else{const t=fs.readFileSync(s.file,'utf8');a('output-file',true,`Found ${s.file}`);if(s.json)try{const d=JSON.parse(t);a('valid-json',true,'Output is valid JSON');for(const k of s.required_keys||[])a(`key:${k}`,Object.prototype.hasOwnProperty.call(d,k),`Required key: ${k}`)}catch(e){a('valid-json',false,e.message)}for(const v of s.required||[])a(`contains:${v}`,t.toLowerCase().includes(v.toLowerCase()),`Required text: ${v}`);for(const v of s.forbidden||[])a(`excludes:${v}`,!t.toLowerCase().includes(v.toLowerCase()),`Forbidden text: ${v}`)}
const p=c.filter(x=>x.passed).length;console.log(JSON.stringify({score:c.length?p/c.length:0,details:`${p}/${c.length} checks passed`,checks:c}));
NODE
