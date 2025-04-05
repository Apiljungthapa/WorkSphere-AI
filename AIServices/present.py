
from imports import *

from AIServices.slideAI import process_pdf
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def new_presentation(pdf_path, api_key, template_path, output_path):
    """
    Generate a PowerPoint presentation from a PDF document
    
    Args:
        pdf_path (str): Path to the PDF file to process
        api_key (str): Google API key for accessing Gemini model
        template_path (str): Path to the template presentation
        output_path (str): Path where the output presentation will be saved
    """
    # Process the PDF and get the sections
    introsection, bodysection, concsection = process_pdf(pdf_path, api_key)
    
    prs = Presentation(template_path)

    def add_paginated_text(slide_title, heading_desc, bullet_points):
        """
        Adds text content dynamically, splitting into new slides if necessary.
        - If heading paragraph > 100 words → New slide.
        - If bullet points > 3 → New slide.
        """
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        title.text = slide_title
        
        content = slide.shapes.placeholders[1]
        text_frame = content.text_frame
        text_frame.word_wrap = True

        # Handling heading description as a paragraph (not a bullet point)
        if heading_desc:
            word_count = len(heading_desc.split())

            if word_count > 100:

                words = heading_desc.split()
                chunks = []
                current_chunk = []
                current_count = 0

                for word in words:
                    current_chunk.append(word)
                    current_count += 1
                    if current_count >= 100:
                        chunks.append(' '.join(current_chunk))
                        current_chunk = []
                        current_count = 0

                if current_chunk:
                    chunks.append(' '.join(current_chunk))

                p = text_frame.add_paragraph()
                p.text = chunks[0]
                p.font.size = Pt(16)
                p.alignment = PP_ALIGN.JUSTIFY
                p.level = 0  
                p.space_after = Pt(15)

                for i in range(1, len(chunks)):
                    slide = prs.slides.add_slide(slide_layout)
                    title = slide.shapes.title
                    title.text = slide_title + " (Continued)"
                    content = slide.shapes.placeholders[1]
                    text_frame = content.text_frame
                    text_frame.word_wrap = True

                    p = text_frame.add_paragraph()
                    p.text = chunks[i]
                    p.font.size = Pt(16)
                    p.alignment = PP_ALIGN.JUSTIFY
                    p.level = 0
                    p.space_after = Pt(15)
            else:
                p = text_frame.add_paragraph()
                p.text = heading_desc
                p.font.size = Pt(16)
                p.alignment = PP_ALIGN.JUSTIFY
                p.level = 0 
                p.space_after = Pt(15)


        bullet_count = 0  # Track number of bullets
        for bullet in bullet_points:
            if bullet_count >= 4:
                slide = prs.slides.add_slide(slide_layout)
                title = slide.shapes.title
                title.text = slide_title + " (Continued)"
                content = slide.shapes.placeholders[1]
                text_frame = content.text_frame
                text_frame.word_wrap = True
                bullet_count = 0  # Reset bullet count

            # Add bullet point
            p = text_frame.add_paragraph()
            p.text = bullet
            p.font.size = Pt(16)
            p.alignment = PP_ALIGN.JUSTIFY
            p.level = 1  # This makes it a bullet point
            p.space_after = Pt(10)

            bullet_count += 1  # Increment bullet count

    # Add a title slide
    slide_layout = prs.slide_layouts[0]  # Title slide layout
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    title.text_frame.text = introsection["MainTitle"]
    title.text_frame.paragraphs[0].font.size = Pt(32)
    title.text_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
    title.text_frame.paragraphs[0].alignment = PP_ALIGN.JUSTIFY

    subtitle.text_frame.text = introsection["SubTitle"]
    subtitle.text_frame.paragraphs[0].font.size = Pt(18)
    subtitle.text_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
    subtitle.text_frame.paragraphs[0].alignment = PP_ALIGN.JUSTIFY

    # Add Introduction Slide
    add_paginated_text("Introduction", introsection["Introduction"], [])

    # For Aims
    add_paginated_text("Aims", "", [introsection['Aims_Objectives'][0]['Aims']])

    # For Objectives
    add_paginated_text("Objectives", "", introsection['Aims_Objectives'][0]['Objectives'])

    # Add body content dynamically from bodysection['Pages']
    for page in bodysection['Pages']:
        add_paginated_text(page['Headings'], page.get('Description', ''), page['Bulletpoints'])

    # Add Conclusion
    add_paginated_text("Conclusion", concsection['FinalSummary']['Summary'], [])

    # Save the presentation
    prs.save(output_path)
    
    return output_path
