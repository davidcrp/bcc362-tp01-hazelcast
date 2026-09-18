"""Gera os PDFs de leitura; os slides são compilados diretamente do LaTeX."""
from pathlib import Path
import re,html,textwrap
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Preformatted,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
DOC=Path(__file__).resolve().parents[1]/'docs'
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyPT',parent=styles['BodyText'],fontSize=10,leading=14,spaceAfter=7))
styles.add(ParagraphStyle(name='CodePT',fontName='Courier',fontSize=7,leading=10,spaceAfter=7))
styles.add(ParagraphStyle(name='CellPT',fontName='Helvetica',fontSize=7,leading=9))
def inline(s):return re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',html.escape(s)).replace('`','')
def footer(canvas,doc):
 canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#536579'))
 canvas.drawString(44,25,'UFOP | BCC362 | Hazelcast: soma distribuída')
 canvas.drawRightString(A4[0]-44,25,str(doc.page))
def build(files,name):
 story=[]
 for file in files:
  if story:story.append(PageBreak())
  lines=(DOC/file).read_text(encoding='utf-8').splitlines();i=0
  while i<len(lines):
   line=lines[i];i+=1
   if not line.strip():continue
   if line.startswith('```'):
    code=[]
    while i<len(lines) and not lines[i].startswith('```'):
     code.extend(textwrap.wrap(lines[i],width=100,replace_whitespace=False,drop_whitespace=False) or ['']);i+=1
    i+=1;story.append(Preformatted('\n'.join(code),styles['CodePT']));continue
   if line.startswith('|'):
    table=[line]
    while i<len(lines) and lines[i].startswith('|'):table.append(lines[i]);i+=1
    data=[]
    for row in table:
     if re.fullmatch(r'[|:\-\s]+',row):continue
     data.append([Paragraph(inline(c.strip()),styles['CellPT']) for c in row.strip('|').split('|')])
    cols=len(data[0]);widths=[(A4[0]-88)/cols]*cols
    if cols==2:widths=[155,A4[0]-88-155]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EDF5F5')),('GRID',(0,0),(-1,-1),.3,colors.lightgrey),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]))
    story.extend([t,Spacer(1,10)]);continue
   if line.startswith('#'):
    level=len(line)-len(line.lstrip('#'));sty=styles['Title'] if level==1 else styles['Heading'+str(min(level-1,3))]
    story.append(Paragraph(inline(line.lstrip('# ')),sty));continue
   story.append(Paragraph(inline(line),styles['BodyPT']))
 SimpleDocTemplate(str(DOC/name),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=40,bottomMargin=42,title='BCC362 — Hazelcast: soma distribuída').build(story,onFirstPage=footer,onLaterPages=footer)
 print('Gerado:',name)
build(['RELATORIO.md','RESULTADOS.md','REQUISITOS.md','REFERENCIAS.md'],'RELATORIO.pdf')
build(['GUIA_PASSO_A_PASSO.md'],'GUIA_PASSO_A_PASSO.pdf')
build(['EXPLICACAO_DO_CODIGO.md'],'EXPLICACAO_DO_CODIGO.pdf')
