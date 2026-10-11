import docx
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = Document()
sec = doc.sections[0]
xml_str = f'<w:pgBorders {nsdecls("w")} w:offsetFrom="page"><w:top w:val="single" w:sz="16" w:space="24" w:color="000000"/><w:left w:val="single" w:sz="16" w:space="24" w:color="000000"/><w:bottom w:val="single" w:sz="16" w:space="24" w:color="000000"/><w:right w:val="single" w:sz="16" w:space="24" w:color="000000"/></w:pgBorders>'
pgBorders = parse_xml(xml_str)
sec._sectPr.append(pgBorders)
doc.add_paragraph("Test page with border")
doc.save("test_border.docx")
print("Border created successfully!")
