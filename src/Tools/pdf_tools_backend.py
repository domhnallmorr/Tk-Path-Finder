from PyPDF2 import PdfReader, PdfFileReader, PdfFileWriter, PdfFileMerger

def read_pdf(pdf):
	pdf_file = PdfReader(pdf)
	
	return pdf_file
	
def get_number_of_pages(pdf_file):
	
	return len(pdf_file.pages)
	
	
def extract_pages(file, start, end):
	
	# Note: index starts at 1 and is inclusive of the end. 
	# The following will extract page 3 of the pdf file.
	pdfs = {file: ({'start': start, 'end': end},)}  

	for pdf, segments in pdfs.items():
		pdf_reader = PdfFileReader(open(pdf, 'rb'))
		#pdf_reader.decrypt('') #sometimes need to use this, sometimes not, don't know why
		for segment in segments:
			pdf_writer = PdfFileWriter()
			start_page = segment['start']
			end_page = segment['end']
			for page_num in range(start_page - 1, end_page):
				pdf_writer.addPage(pdf_reader.getPage(page_num))
			output_filename = f'{pdf}_{start_page}_page_{end_page}.pdf'
			with open(output_filename,'wb') as out:
				pdf_writer.write(out)
				
	return output_filename

def merge_pdfs(input_files, output_file):
	merger = PdfFileMerger()
	for pdf in input_files:
		merger.append(open(pdf,'rb'))
		
	with open(output_file, "wb") as fout:
		merger.write(fout)
