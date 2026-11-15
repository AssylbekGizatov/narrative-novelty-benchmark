"""Build editable OMML equations and DiGRA-format Word manuscripts."""
from pathlib import Path
import subprocess,re
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'paper'
subprocess.run(['pandoc','manuscript.md','--from=markdown-implicit_figures','--to=docx','-o','base.docx'],cwd=P,check=True)
for anonymous in [False,True]:
 d=Document(P/'base.docx');styles={x.name:x for x in d.styles};s=d.sections[0]
 s.page_width=Cm(21);s.page_height=Cm(29.7);s.left_margin=s.right_margin=Cm(3.5);s.top_margin=s.bottom_margin=Cm(1.7)
 for name in ['Normal','Body Text','First Paragraph','Compact']:
  if name in styles:
   st=styles[name];st.font.name='Open Sans';st.font.size=Pt(10);st.font.color.rgb=RGBColor(0,0,0)
   st.paragraph_format.line_spacing=1.0;st.paragraph_format.space_after=Pt(3);st.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
 for name in ['Heading 1','Heading 2','Heading 3']:
  st=styles[name];st.font.name='Arial';st.font.size=Pt(12);st.font.bold=name!='Heading 3';st.font.italic=name=='Heading 3';st.font.color.rgb=RGBColor(0,0,0)
  st.paragraph_format.space_before=Pt(10);st.paragraph_format.space_after=Pt(5);st.paragraph_format.keep_with_next=True
 st=styles['Title'];st.font.name='Arial';st.font.size=Pt(18);st.font.bold=True;st.font.color.rgb=RGBColor(0,0,0);st.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER;st.paragraph_format.space_after=Pt(9)
 title=d.paragraphs[0]
 from docx.text.paragraph import Paragraph
 el=OxmlElement('w:p');title._p.addnext(el);author=Paragraph(el,title._parent)
 author.alignment=WD_ALIGN_PARAGRAPH.CENTER
 if anonymous:txt='Anonymous author'
 else:txt='Gizatov Assylbek\nResearch Institute of Physics, Mathematics and Applied Technologies\nKh. Dosmukhamedov Atyrau University, Atyrau, Kazakhstan\na.gizatov@asu.edu.kz  |  ORCID 0009-0009-2557-0767'
 run=author.add_run(txt);run.font.name='Open Sans';run.font.size=Pt(10);author.paragraph_format.space_after=Pt(10)
 for p in d.paragraphs:
  if p._p.xpath('.//w:drawing'):
   p.paragraph_format.keep_with_next=True
  if p.text.startswith(('Table ','Figure ')):
   p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(8)
   for r in p.runs:r.font.size=Pt(11);r.bold=True
  if p.style.name=='Heading 1':
   for r in p.runs:r.text=r.text.upper()
 # Avoid long raw URLs expanding a line beyond the text width.
 for h in d.element.xpath('//w:hyperlink'):
  for t in h.xpath('.//w:t'):
   if t.text and len(t.text)>75:
    for token in ['/', '-','_']:t.text=t.text.replace(token,token+'\u200b')
 for table in d.tables:
  table.autofit=False
  cols=len(table.columns);widths=[7.7]+[(14-7.7)/(cols-1)]*(cols-1)
  for rowi,row in enumerate(table.rows):
   for j,cell in enumerate(row.cells):
    cell.width=Cm(widths[j]);pr=cell._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E9EDF0' if rowi==0 else 'FFFFFF');pr.append(shade)
    borders=OxmlElement('w:tcBorders')
    for side in ['top','left','bottom','right']:
     x=OxmlElement('w:'+side);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'D9D9D9');borders.append(x)
    pr.append(borders)
    for p in cell.paragraphs:
     p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(3);p.alignment=WD_ALIGN_PARAGRAPH.LEFT if j==0 else WD_ALIGN_PARAGRAPH.CENTER
     for r in p.runs:r.font.name='Open Sans';r.font.size=Pt(9);r.bold=rowi==0
  # Repeating heading row; permit row expansion but avoid splits inside a row.
  rep=OxmlElement('w:tblHeader');table.rows[0]._tr.get_or_add_trPr().append(rep)
  for row in table.rows:
   prop=row._tr.get_or_add_trPr();prop.append(OxmlElement('w:cantSplit'))
   for cell in row.cells:
    for p in cell.paragraphs:p.paragraph_format.keep_with_next=True
 footer=s.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
 fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
 d.core_properties.author='' if anonymous else 'Gizatov Assylbek';d.core_properties.title='Benchmarking Structural Novelty Loss in Human–AI Game Narrative Authoring';d.core_properties.comments='Research manuscript draft; no publication or acceptance claimed.'
 out=P/('Novelty_Benchmark_DiGRA_Anonymous.docx' if anonymous else 'Novelty_Benchmark_DiGRA.docx');d.save(out)
 print(out.name,'native equations:',len(d.element.xpath('//m:oMath')))
(P/'base.docx').unlink()
text=(P/'manuscript.md').read_text();body=text.split('# REFERENCES')[0]
print('Approximate body words including abstract/captions:',len(body.split()))
