# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 10:07:01 2023

@author: Robert
"""

# Create output report
from fpdf import FPDF
import datetime


#%% Place holder data
name = 'PLACE HOLDER NAME'
purpose = 'PLACE HOLDER PURPOSE'
album_list = ['Atom Heart Mother --- Pink Floyd', 'Meddle --- Pink Floyd']
note = 'Make this a little too long...  Im am trying to capture the XYZ of these albums to better guide the structure of my next album.'
border_bool = 0
section_title = ['Heatmap', 'Feature Comparison', 'Stats Tables']
o = 0
i = 0
filepath = '' #/Users/Robert/Desktop/00_PythonWIP_New/AnimeScraper'


#%% Create function to make header

# Header text for the Image Chapters
explanation1_a = 'Displayed below are the individual album heatmaps depicting the intensity of each Spotify acoustic features.  This section is here to allow you to easily read each albums features.  The stats info is not in this section.'
explanation1_b = 'Blue is low intensity, and Red is high intensity.'
explanation2_a = 'Displayed below are the graphs containing the selected albums features where one of the first three degrees of regression was found to have significant fit, aswell as the interpolated representation of that album.  After each feature is also the descriptive statistics for any album that was not found to have significant fit for the regression fit.'
explanation2_b = 'The descriptive statistics are not as easy to understand as a regression line with good fit.  The Mean is the average value of the time normalized feature.  When on a 0 to 1 scale, it is a general intensity or "probability of being". 0 - Not prevalent or likely, 1 - Most prevalent or likely.  The Variance is the total accumulation of differences of all points from the mean (multiplied by 2000 for the sake of interpolation). The Skew is a coefficient value judging whether the majority of the data points are higher or lower than the mean and median values of the album. Positive - Large quantity of data points towards the upper end of the extreme (Left Leaning), Negative - Large Quantity of data points towards the lower end of the extremes (Right Leaning).  Finally, the Kurtosis is a coefficient value expressing the existence of data points in the "tails" of the distribution. Positive - More centralized Data points, Negative - Large number of data points far from the mean (wider than normally distributed).'

class PDF(FPDF):
    # Overwrites/Sets a header for each page
    def header(self):
        self.set_font("helvetica", "BUI", 12)
        # Moving cursor to the right:
        #self.cell(80)
        # Printing title:
        self.cell(0, 5, "Album Comparison Report", border=border_bool, align="C")
        #self.cell(0, 5, f"{album_list}", border=border_bool, align="C")
        self.ln(8)
        
    
    # Overwrites/Sets a footer for each page    
    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-10)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        # Printing page number:
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}", align="C")
        self.ln(0)
        self.cell(0, 8, datetime.datetime.now().strftime("%m/%d/%Y, %H:%M"), align="R")
    
    
    # Creates the front page of the PDF report
    def front_page_info(self, name, purpose, album_list):
        # Setting font: helvetica bold 15
        self.set_font("helvetica", "BUI", 12)
        # Moving cursor to the right:
        #self.cell(80)
        albums_string = []
        al_str = ''
        for album in album_list:
            display_album = album.replace('---','by')
            albums_string.append(display_album)
        album_string = ", ".join(albums_string)
        #something = al_str.join(albums_string)  
        # Printing title:
        self.multi_cell(0, 5, f"{name}'s report for: {purpose}", border=border_bool, align="C", ln=1)
        self.multi_cell(0, 5, f"Albums Include: {album_string}", border=border_bool, align="C")
        #self.cell(0, 5, f"{album_list}", border=border_bool, align="C")
        self.ln(8)
        
    
    # Creates the section header box
    def section_headers(self, num, label):
        # Setting font: helvetica 12
        self.set_font("helvetica", "", 16)
        # Setting background color
        self.set_fill_color(211, 211, 211)
        # Printing chapter name:
        self.cell(
            0,
            6,
            f"Section {num} : {label}",
            new_x="LMARGIN",
            new_y="NEXT",
            align="L",
            fill=True,
        )
        # Performing a line break:
        self.ln(4)
    def front_page(self, user_name, analysis_purpos, album_select, notes):
        self.add_page()
        self.front_page_info(user_name, analysis_purpos, album_select)
        
        self.cell(0, 10, 'Input Notes:', ln=1)
        self.set_font("helvetica", "I", size=12)
        self.multi_cell(0, 5, notes, 0)
        self.ln(15)
        self.set_font("helvetica", "BUI", size=22)
        
        #self.heatmap_link = self.add_link()
        #self.cell(0,20,"Section 1: Heatmaps", ln = 1, align = 'l', link = self.heatmap_link)
        #self.feature_link = self.add_link()
        #self.cell(0,20,"Section 2: Feature Comparison", ln = 1, align = 'l', link = self.feature_link)
        
        heatmap_page = self.add_link(page = 2)
        self.cell(0,20,"Section 1: Heatmaps", ln = 1, align = 'l', link = heatmap_page)
        feature_page = self.add_link(page = (3+len(album_select)))
        self.cell(0,20,"Section 2: Feature Comparison", ln = 1, align = 'l', link = feature_page)
        self.set_font("helvetica", "I", size=18)
        self.cell(0,10, "     Acousticness", ln = 1, align = 'l', link = self.add_link(page = (4+len(album_select))))   
        self.cell(0,10, "     Danceability", ln = 1, align = 'l', link = self.add_link(page = (5+len(album_select))))   
        self.cell(0,10, "     Duration", ln = 1, align = 'l', link = self.add_link(page = (6+len(album_select))))  
        self.cell(0,10, "     Energy", ln = 1, align = 'l', link = self.add_link(page = (7+len(album_select))))   
        self.cell(0,10, "     Instrumentalness", ln = 1, align = 'l', link = self.add_link(page = (8+len(album_select))))   
        self.cell(0,10, "     Liveness", ln = 1, align = 'l', link = self.add_link(page = (9+len(album_select))))   
        self.cell(0,10, "     Loudness", ln = 1, align = 'l', link = self.add_link(page = (10+len(album_select))))   
        self.cell(0,10, "     Speechiness", ln = 1, align = 'l', link = self.add_link(page = (11+len(album_select))))   
        self.cell(0,10, "     Valence", ln = 1, align = 'l', link = self.add_link(page = (12+len(album_select)))) 
        self.cell(0,10, "     Tempo", ln = 1, align = 'l', link = self.add_link(page = (13+len(album_select))))   
        self.cell(0,10,'', ln = 1)
        self.set_font("helvetica", "BUI", size=22)
        self.cell(0,20, "Appendix: R-Squared Table", ln = 1, align = 'l', link = self.add_link(page = (14+len(album_select))))   
        
                
        
    # Populates an image on a page
    def report_image_insert(self, file_name_list, i):
        #self.image(f'{file_name_list[i]}',10, None, 190.5)
        self.image(f'{file_name_list[i]}',None, None, 190.5, 165)
        self.ln(8)
    
    
    # Inserts a 'end of section' text marker   
    def end_of_section_footer(self, num, label):
        # Setting font: Times 12
        self.set_font("helvetica", size=12)
        # Printing justified text:
        #self.multi_cell(0, 5, 'SOME TEXT GOES HERE MAYBE?')
        # Performing a line break:
        self.ln()
        # Final mention in italics:
        self.set_font(style="I")
        self.cell(0, 5, f"(end of section {num}: {label})", ln = 1)
        
    
    # Populates a Table from a dataframe
    def create_table_from_df(self, data_frame, table_header, page_or = 'L', index_count = 1, cof_fill = True):
        
        if page_or == 'P':
            df = data_frame.round(decimals = 6).applymap(str)
        else:
            df = data_frame.round(decimals = 3).applymap(str)  # Convert all data inside dataframe into string type
        columns = [list(df)]  # Get list of dataframe columns
        rows = df.values.tolist()  # Get list of dataframe rows
        data = columns + rows
        indexes = df.index.tolist()
        if index_count == 2:
            index_skip = ['', '']
            indexes.insert(0, index_skip)
            for i, row in enumerate(data):
                row.insert(0, indexes[i][1])
                row.insert(0, indexes[i][0])
        elif index_count == 1:
            index_skip = ['']
            indexes.insert(0, index_skip)
            for i, row in enumerate(data):
                if len(str(indexes[i])) == 0:
                    row.insert(0, indexes[i])
                else:
                    row.insert(0, str(indexes[i]))
        if page_or == 'P':
            pass
        else:
            self.add_page('L')
        self.cell(0,15, table_header,  align = 'C', ln = 1)
        self.set_font("helvetica", size=10)
        line_height = self.font_size * 2
        col_width = self.epw / len(data[0])  # distribute content evenly
        for row in data:
            for datum in row:
                if cof_fill == True:
                    try:
                        r_squared_value = float(datum)
                        if r_squared_value >= 0.9:
                            self.set_fill_color(0, 255, 34)
                        elif r_squared_value >= 0.7:
                            self.set_fill_color(97, 242, 7)
                        elif r_squared_value >= 0.6:
                            self.set_fill_color(255, 251, 0)
                        elif r_squared_value >= 0.5:
                            self.set_fill_color(255, 204, 0)
                        else:
                            self.set_fill_color(136, 8, 8)
                            #self.set_fill_color(0, 255, 34)
                        
                        self.multi_cell(
                            col_width,
                            line_height,
                            datum,
                            border=1,
                            align = 'C',
                            new_y="TOP",
                            max_line_height=self.font_size,
                            fill=True,
                        )
                    except:
                        self.set_fill_color(211, 211, 211)
                        self.multi_cell(
                            col_width,
                            line_height,
                            datum,
                            border=1,
                            align = 'C',
                            new_y="TOP",
                            max_line_height=self.font_size,
                            fill=True,
                        )
                else:
                    self.multi_cell(
                        col_width,
                        line_height,
                        datum,
                        border=1,
                        align = 'C',
                        new_y="TOP",
                        max_line_height=self.font_size,
                        fill=False,
                    )
            self.ln(line_height)
    
   
    # Inserts information about the image sections.   
    def section_explanation(self, text, text2):
        self.multi_cell(0, h=None, txt = text, align = 'l')
        self.ln(8)
        self.multi_cell(0, h=None, txt = text2, align = 'l')
    
    
    # Creates the image based report sections
    def print_image_chapter(self, num, title, file_name_list, table_bool = False, data_frame = '', table_header = ''):
        self.add_page()
        self.section_headers(num, title)
        self.ln(10)
        if num == 1:
            self.section_explanation(explanation1_a, explanation1_b)
            # FPDF does not allow you go to go back and add the index hyperlinks, so you have to do math for the linking...
            #self.set_link(link=self.heatmap_link, page = self.page_no())
            
        elif num == 2:
            self.section_explanation(explanation2_a, explanation2_b) 
            #self.set_link(self.feature_link, page = self.page_no())
            
        table_header = ['Acousticness', 'Danceability', 'Duration_ms', 'Energy', 'Instrumentalness', 'Liveness', 'Loudness',
                       'Speechiness', 'Valence', 'Tempo']
        for i in range(len(file_name_list)): 
            self.add_page()
            self.report_image_insert(file_name_list, i)
            if table_bool == True:
                self.create_table_from_df(data_frame[i][0], table_header[i], index_count = 1, cof_fill = False, page_or = 'P')    
        self.end_of_section_footer(num,title)
        
        
#%%

