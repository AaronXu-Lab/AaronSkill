#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('grader', ROOT/'graders/check_required.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
GOOD='''---
name: 'Quiet Tools'
colors:
  primary: '#224466'
  surface: '#F7F8FA'
  on-surface: '#17202A'
  on-primary: '#FFFFFF'
typography:
  body-md:
    fontFamily: Inter
    fontSize: 16px
rounded:
  md: 8px
spacing:
  md: 16px
components:
  button-primary:
    backgroundColor: '{colors.primary}'
    textColor: '{colors.on-primary}'
---
## Overview
Focused.
## Colors
Primary marks main action.
## Typography
Body carries content.
## Layout
Use spacing.
## Shapes
Use radius.
## Components
Button for action.
## Do's and Don'ts
Do preserve hierarchy.
'''
class GraderTests(unittest.TestCase):
 def grade(self,text,mutate_input=False):
  with tempfile.TemporaryDirectory(prefix='aw-design-md-07-grader-') as d:
   p=Path(d);shutil.copy(ROOT/'fixtures/authoring-brief.md',p/'authoring-brief.md')
   if mutate_input:(p/'authoring-brief.md').write_text('tampered')
   if text is not None:(p/'DESIGN.md').write_text(text)
   return m.grade(json.loads((ROOT/'fixtures/authoring-grader.json').read_text()),p)
 def test_equivalent_yaml_quotes(self):self.assertEqual(self.grade(GOOD)['hard'],1)
 def test_legitimate_other_foreground(self):self.assertEqual(self.grade(GOOD.replace('#FFFFFF','#FFFFFE'))['hard'],1)
 def test_keyword_stuffing_is_not_contract(self):
  legacy=['name: Quiet Tools','primary: "#224466"','## Overview','## Colors','## Typography','## Layout','## Shapes','## Components',"## Do's and Don'ts",'{colors.primary}']
  self.assertEqual(self.grade('<!--\n'+'\n'.join(legacy)+'\n-->')['hard'],0)
 def test_wrong_protected_value(self):self.assertEqual(self.grade(GOOD.replace('md: 16px','md: 20px'))['hard'],0)
 def test_input_tampering(self):self.assertEqual(self.grade(GOOD,True)['hard'],0)
 def test_missing_file(self):self.assertEqual(self.grade(None)['hard'],0)
 def test_broken_ref(self):self.assertEqual(self.grade(GOOD.replace('{colors.primary}','{colors.absent}'))['hard'],0)
 def test_reordered_sections(self):self.assertEqual(self.grade(GOOD.replace('## Colors','## Swap').replace('## Typography','## Colors').replace('## Swap','## Typography'))['hard'],0)
 def test_empty_report_rejected(self):
  with tempfile.TemporaryDirectory(prefix='aw-design-md-07-report-') as d:
   p=Path(d);(p/'review.md').write_text('  \n')
   result=m.grade({'file':'review.md','kind':'report'},p)
   self.assertEqual(result['hard'],0)
if __name__=='__main__':unittest.main()
