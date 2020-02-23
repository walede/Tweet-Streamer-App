import tkinter
from tkinter import *
from tkinter import messagebox
import tkinter.font as tkFont
from tkinter import ttk
from db import Database
import streamer
import tweepy
import re
import time
import textwrap

db = Database('tweets.db')

class Application(Frame):

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        app.title('Twitter Streamer')
        # Width & height
        app.geometry("875x390")
        # Create widgets/grid
        self.create_widgets()
        #initialize for filtering result updates
        self.last_result = 0
        
    def create_widgets(self):
        '''Creates the widgets for the Tkinter app'''
        #keyword entry
        self.keyword_txt = StringVar()
        self.kw_label = Label(self.app, text='Keywords', font=('bold', 14))
        self.kw_label.grid(row=0, column=4, sticky=W)
        self.kw_entry = Entry(self.app, textvariable=self.keyword_txt, width=40)
        self.kw_entry.grid(row=0, column=5, columnspan=3, sticky='we')

        #clear keywords button
        self.clearkw_btn = Button(self.app, text='X', width=2, command=self.clear_kw)
        self.clearkw_btn.grid(row=0, column=8)

        #Start stream button
        self.start_btn = Button(self.app, text='Start Streaming', width=15,
                                command=self.start_stream)
        self.start_btn.grid(row=1, column=0, padx=10, sticky='w')

        #Stop stream button
        self.stop_btn = Button(self.app, text='Stop Streaming', width=15,
                               command=self.stop_stream)
        self.stop_btn.grid(row=1, column=3, sticky='w')

        #Streaming label
        self.stream_label = Label(self.app, text='Streaming...', font=(12), fg="green")

        #refresh list button
        self.refresh_btn = Button(self.app, text='Refresh', width=7, 
                                  command=self.refresh_list)
        self.refresh_btn.grid(row=1, column=9, sticky='es')

        #clear list button
        self.clear_btn = Button(self.app, text='Clear List', width=7, 
                                command=self.clear_list)
        self.clear_btn.grid(row=1, column=10, sticky='es')

        #nav buttons
        self.prev_btn = Button(self.app, text='<<', width=2, command=self.nav_prev)
        self.prev_btn.grid(row=12, column=5)

        self.next_btn = Button(self.app, text='>>', width=2, command=self.nav_next)
        self.next_btn.grid(row=12, column=7, sticky='w')

        # pages label
        self.page_num = IntVar(self.app, value=1)
        self.page_entry = Entry(self.app, textvariable=self.page_num, width=5, 
                                justify='center')
        self.page_label = Label(self.app, text=f'/{db.buckets}', font=(14))
        
        # page go button
        self.go_btn = Button(self.app, text='Go', width=2, command=self.nav_go)
  
        #clear filter button
        self.clearf_btn = Button(self.app, text='clear', width=4, height=0,
                                 command=self.clearf, state='disabled')
        self.clearf_btn.grid(row=4, column=0, sticky='nw', padx=(10,0))

        #filter button
        self.filter_btn = Button(self.app, text='Filter', width=4, height=0,
                                 command=self.filter_list)
        self.filter_btn.grid(row=6, column=0)
        self.filter_btn.grid_remove()

        #filter keywords 
        self.locVar = StringVar()
        self.loc_type = ttk.Combobox(self.app, textvariable=self.locVar, width=14)
        #filter keyword entry box
        self.f_txt = StringVar()
        self.f_entry = Entry(self.app, textvariable=self.f_txt, width=17)

        #verified radio buttons
        self.v = StringVar()
        self.v.set("True")
        self.b1 = Radiobutton(self.app, text="True", variable=self.v, value='True')
        self.b2 = Radiobutton(self.app, text="False", variable=self.v, value='False')
        
        #sentiment radio buttons
        self.v = StringVar()
        self.v.set(" ")
        self.b1 = Radiobutton(self.app, text="Positive", variable=self.v, 
                              value='Positive')
        self.b2 = Radiobutton(self.app, text="Negative", variable=self.v, 
                              value='Negative')
        self.b3 = Radiobutton(self.app, text="Neutral", variable=self.v, 
                              value='Neutral')
        self.b4 = Radiobutton(self.app, text=" ", variable=self.v, value=' ')
        
        #time filters
        self.from_hours = IntVar()
        self.from_mins = DoubleVar()
        self.to_hours = IntVar()
        self.to_mins = DoubleVar()
        self.from_h_entry = Spinbox(self.app, from_=00, to=23, width=2, wrap=True, 
                                    format="%02.0f")
        self.from_m_entry = Spinbox(self.app, from_=00, to=59, width=2, wrap=True, 
                                    format="%02.0f")
        self.to_h_entry = Spinbox(self.app, from_=00, to=23, width=2, wrap=True, 
                                    format="%02.0f")
        self.to_m_entry = Spinbox(self.app, from_=00, to=59, width=2, wrap=True, 
                                    format="%02.0f")
        self.colon1 = Label(self.app, text=':', font=6)
        self.colon2 = Label(self.app, text=':', font=6)
        self.from_label = Label(self.app, text='From:', font=('bold', 9))
        self.to_label = Label(self.app, text='To:', font=('bold', 9))
        
        #filter label
        self.f_label = Label(self.app, text='ID:', font=('bold', 9))

        self.column_h = ['Username', 'Time', 'Tweet', 'Sentiment', 'Verified',
                         'Location', 'Media Type']

        #Tweet List 
        self.container = Frame(self.app)
        self.container.grid(row=3, column=3, columnspan=9, rowspan=8, sticky='nsew',
                            pady=(10,0))
        self.tweet_list = ttk.Treeview(columns=self.column_h, show='headings', height=5)
        self.tweet_list.grid(column=0, row=0, sticky='nsew', in_=self.container)
        self.style = ttk.Style()
        self.style.configure('Treeview', rowheight=45)

        #scrollbars
        self.scrolly = Scrollbar(orient="vertical", command=self.tweet_list.yview) 
        self.scrollx = Scrollbar(orient="horizontal", command=self.tweet_list.xview)
        self.scrolly.configure(command=self.tweet_list.yview)
        self.scrollx.configure(command=self.tweet_list.xview)
        self.tweet_list.configure(yscrollcommand=self.scrolly.set, 
                                  xscrollcommand=self.scrollx.set)
        self.scrolly.grid(row=0,column=1, sticky='ns', in_=self.container)
        self.scrollx.grid(row=1, column=0, sticky='ew', in_=self.container)
        #set column
        for col in self.column_h:
                    self.tweet_list.heading(col, text=col, command=lambda c=col: 
                                            self.sortby(self.tweet_list, c, 0))
                    self.tweet_list.column(col, width=tkFont.Font().measure(col + '       '))
        #Bind select to the treeview
        self.tweet_list.bind('<<TreeviewSelect>>', self.select_tweet)
        #Results label
        self.res_label = Label(self.app, text='Results:', font=('bold', 9))
        #tickboxes
        self.verified = IntVar()
        self.verified.set(True)
        self.nt_ca = IntVar()
        self.nt_ca.set(True)
        self.tweet = IntVar()
        self.tweet.set(True)
        self.sentiment = IntVar()
        self.sentiment.set(True)
        self.media_type = IntVar()
        self.media_type.set(True)
        self.user_name = IntVar()
        self.user_name.set(True)
        self.loc = IntVar()
        self.loc.set(True)
        self.ui = Checkbutton(self.app, text="Username", variable=self.user_name,
                              command=self.populate_list)
        self.ui.grid(row=2, column=3, sticky='ew')
        self.nc = Checkbutton(self.app, text="Date Created", variable=self.nt_ca,
                              command=self.populate_list)
        self.nc.grid(row=2, column=4, sticky='ew')
        self.t = Checkbutton(self.app, text="Tweet", variable=self.tweet,
                              command=self.populate_list)
        self.t.grid(row=2, column=5, sticky='ew')
        self.s = Checkbutton(self.app, text="Sentiment", variable=self.sentiment,
                              command=self.populate_list)
        self.s.grid(row=2, column=6, sticky='ew')
        self.ti = Checkbutton(self.app, text="Verified", variable=self.verified,
                              command=self.populate_list)
        self.ti.grid(row=2, column=7, sticky='ew')
        self.li = Checkbutton(self.app, text="Location", variable=self.loc,
                              command=self.populate_list)
        self.li.grid(row=2, column=8, sticky='ew')
        self.mt = Checkbutton(self.app, text="Media Type", variable=self.media_type,
                              command=self.populate_list)
        self.mt.grid(row=2, column=9, sticky='ew')

        #filter combobox
        self.filter_label = Label(self.app, text='Filter by:', font=('bold', 10))
        self.filter_label.grid(row=3, column=0, sticky='s')
        self.filterVar = StringVar()
        self.filter_type = ttk.Combobox(self.app, textvariable=self.filterVar, width=13)
        self.filter_type['values'] = ['Verified','Tweet','Location', 'Media Type', 
                                      'Sentiment', 'Date Created', 'Username']
        self.filter_type.grid(row=4, column=0, sticky=(W,N), padx=(50,0))
        self.filter_type.bind('<<ComboboxSelected>>', self.filter_query)
    
    def wrap(self, string, length=105):
        '''Wrap a text into a new line around a certain length'''
        return '\n'.join(textwrap.wrap(string, length))

    def nav_go(self):
        '''Allows the user to input the navigation page'''
        if self.page_num.get() > db.buckets or self.page_num.get()<=0:
            messagebox.showerror('Out of Bounds', 'Pick a page within bounds.')
        else:
            db.page = self.page_num.get()
            if db.filtered:
                self.filter_list(option=True)
            else:            
                self.populate_list()

    def nav_prev(self):
        '''Navigate to the previous page'''
        db.page -= 1
        self.page_entry.delete(0, END)
        self.page_entry.insert(END, db.page)
        if db.filtered:
            self.filter_list(option=True)
        else:
            self.populate_list()  

    def nav_next(self):
        '''Navigate to the next page'''
        db.page += 1
        self.page_entry.delete(0, END)
        self.page_entry.insert(END, db.page)
        if db.filtered:
            self.filter_list(option=True)
        else:
            self.populate_list()  

    def select_tweet(self, event):
        '''Print the selected tweet in the result list'''
        self.index = self.tweet_list.selection()[0]
        self.select_tweet = self.tweet_list.item(self.index)
        print(self.select_tweet['values'][2])

    def start_stream(self):
        '''Start streaming tweets based on keywords'''
        self.keywords = re.split(',\s*', self.keyword_txt.get())
        if self.keywords[0]!='':
            self.stream_label.grid(row=1, column=4, sticky='w')
            myStream.filter(track=self.keywords, languages=['en'], is_async=True)
        else:
            messagebox.showerror('Keywords required', 'Please add some keywords')
            return

    def stop_stream(self):
        '''Stop Streaming'''
        self.stream_label.grid_remove()
        myStream.disconnect()
        self.populate_list()

    def refresh_list(self):
        '''Refresh List'''
        self.last_result = 0
        self.populate_list()

    def clear_list(self):
        '''Clear the list, reset counters'''
        self.last_result = 0
        self.del_list()
        self.res_label.grid_remove()
        db.delete_entry()
        db.page = 1
        self.page_label.grid_remove()
        self.page_entry.grid_remove()
        mySL.index = 1

    def del_list(self):
        '''Delete all items in the list'''
        x = self.tweet_list.get_children()
        for item in x:
            self.tweet_list.delete(item)

    def clear_kw(self):
        '''Clear keyword entry box'''
        self.kw_entry.delete(0, END)

    def populate_list(self):
        '''Populate the list with the results up to 50 per page, 
           or call the filter function if filtering'''
        if not db.filtered:
            self.del_list()
            checker = [self.verified.get(),self.nt_ca.get(),
                        self.tweet.get(),self.sentiment.get(),
                        self.media_type.get(),self.user_name.get(),
                        self.loc.get()]
            show_col=[]
            if self.user_name.get(): show_col.append('Username') 
            if self.nt_ca.get(): show_col.append('Time')
            if self.tweet.get(): show_col.append('Tweet')
            if self.sentiment.get(): show_col.append('Sentiment')
            if self.verified.get(): show_col.append('Verified') 
            if self.loc.get(): show_col.append('Location')
            if self.media_type.get(): show_col.append('Media Type')
            num_columns = len(show_col)
            for col in show_col:
                self.tweet_list.heading(col, text=col, command=lambda c=col: 
                                        self.sortby(self.tweet_list, c, 0))
                self.tweet_list.column(col, width=int(615/num_columns))
            if any(checker):
                self.tweet_list["displaycolumns"] = show_col
                for row in db.fetch_all():
                    test_row = list(row)
                    test_row[2] = self.wrap(test_row[2])
                    row = tuple(test_row)
                    self.tweet_list.insert('', 0, values=row)                    
                    for ix, val in enumerate(row):
                        col_w = tkFont.Font().measure(val)                       
                        if self.column_h[ix] == 'Tweet':
                            self.tweet_list.column(self.column_h[ix], width=600)
                        elif self.tweet_list.column(self.column_h[ix], width=None) < col_w:
                            self.tweet_list.column(self.column_h[ix], width=col_w)             
                total = db.count_results()
                result = len(self.tweet_list.get_children())
                if result == 1:
                    self.res_label.configure(text=f'{result} Result')
                else:
                    self.res_label.configure(text=f'{result}/{total} Results')
                self.res_label.grid(row=12, column=3, sticky='w')
                if db.page == 1:
                    self.prev_btn.configure(state='disabled')
                else:
                    self.prev_btn.configure(state='normal')
                if db.page == db.buckets:
                    self.next_btn.configure(state='disabled')
                else:
                    self.next_btn.configure(state='normal')
                if result == 0:
                    self.page_label.configure(text=f'0/0')
                else:
                    self.page_label.configure(text=f'/{db.buckets}')
                self.page_entry.delete(0, END)
                self.page_entry.insert(END, db.page)
                if not result:
                    self.go_btn.grid_remove()
                    self.page_entry.grid_remove()
                    self.page_label.grid(row=12, column=6, padx=(0,20))
                else:
                    self.page_entry.grid(row=12, column=6, sticky='w')
                    self.page_label.grid(row=12, column=6, padx=(5,0))
                    self.go_btn.grid(row=12, column=7, sticky='e')
        else:
            self.filter_list(ref_res=True)

    def live_update(self):
        '''When 50 results are already on a page, continues to update 
           result count in the background'''
        if db.filtered:
            total = db.count_f_results()            
        else:
            total = db.count_results()
        result = len(self.tweet_list.get_children())
        self.res_label.configure(text=f'{result}/{total} Results')
        self.res_label.grid(row=12, column=3, sticky='w')
        if db.page == 1:
            self.prev_btn.configure(state='disabled')
        else:
            self.prev_btn.configure(state='normal')
        if db.page == db.buckets:
            self.next_btn.configure(state='disabled')
        else:
            self.next_btn.configure(state='normal')
        self.page_label.configure(text=f'/{db.buckets}')
        self.page_label.grid(row=12, column=6, padx=(5,0))
        self.go_btn.grid(row=12, column=7, sticky='e')


    #create a window object 
    def filter_list(self, option=False, ref_res=False): 
        '''Generate results based on filter criteria'''
        db.filtered = True
        if not option:
            db.page = 1
        if not ref_res: #checks whether it is being called on one occasion
            self.last_result = 0
        if self.selected_filter == 'Verified':
            self.field = 'verified'
            self.filter_kw = self.v.get()
        elif self.selected_filter == 'Date Created':
            self.field = 'time'
            self.filter_kw = ''
            self.filter_kw += str(self.from_h_entry.get())
            self.filter_kw += ':'
            self.filter_kw += str(self.from_m_entry.get())
            self.filter_kw += ' '
            self.filter_kw += str(self.to_h_entry.get())
            self.filter_kw += ':'
            self.filter_kw += str(self.to_m_entry.get())
        elif self.selected_filter == 'Tweet':
            self.field = 'tweet'
            self.filter_kw = self.f_txt.get()
        elif self.selected_filter == 'Sentiment':
            self.field = 'sentiment'
            self.filter_kw = self.v.get()
        elif self.selected_filter == 'Media Type':
            self.field = 'media_type'
            self.filter_kw = self.f_txt.get()
        elif self.selected_filter == 'Location':
            self.field = 'location'
            self.filter_kw = self.locVar.get()
        elif self.selected_filter == 'Username':
            self.field = 'user_name'
            self.filter_kw = self.f_txt.get()
        if self.filter_kw:
            db.filter_fetch(self.filter_kw, self.field)
            total = db.count_f_results()            
            if total > self.last_result:
                self.last_result = total
                self.del_list()
                checker = [self.verified.get(),self.nt_ca.get(),
                            self.tweet.get(),self.sentiment.get(),
                            self.media_type.get(),self.user_name.get(),
                            self.loc.get()]
                show_col=[]
                if self.user_name.get(): show_col.append('Username') 
                if self.nt_ca.get(): show_col.append('Time')
                if self.tweet.get(): show_col.append('Tweet')
                if self.sentiment.get(): show_col.append('Sentiment')
                if self.verified.get(): show_col.append('Verified') 
                if self.loc.get(): show_col.append('Location')
                if self.media_type.get(): show_col.append('Media Type')
                num_columns = len(show_col)
                for col in self.column_h:
                    self.tweet_list.heading(col, text=col, command=lambda c=col: 
                                            self.sortby(self.tweet_list, c, 0))
                    self.tweet_list.column(col, width=int(615/num_columns))
                if any(checker):
                    self.tweet_list["displaycolumns"] = show_col
                    for row in db.filter_fetch(self.filter_kw, self.field):
                        test_row = list(row)
                        test_row[2] = self.wrap(test_row[2])
                        row = tuple(test_row)
                        self.tweet_list.insert('', 0, values=row) 
                        for ix, val in enumerate(row):
                            col_w = tkFont.Font().measure(val)
                            if self.column_h[ix] == 'Tweet':
                                self.tweet_list.column(self.column_h[ix], width=600)
                            elif self.tweet_list.column(self.column_h[ix],width=None)<col_w:
                                self.tweet_list.column(self.column_h[ix], width=col_w)
                    result = len(self.tweet_list.get_children())
                if result == 1:
                    self.res_label.configure(text=f'{result} Result')
                else:
                    self.res_label.configure(text=f'{result}/{total} Results')
                self.res_label.grid(row=12, column=3, sticky='w')
                if db.page == 1:
                    self.prev_btn.configure(state='disabled')
                else:
                    self.prev_btn.configure(state='normal')
                if db.page == db.buckets:
                    self.next_btn.configure(state='disabled')
                else:
                    self.next_btn.configure(state='normal')
                if result == 0:
                    self.page_label.configure(text=f'0/0')
                else:
                    self.page_label.configure(text=f'/{db.buckets}')
                self.page_entry.delete(0, END)
                self.page_entry.insert(END, db.page)
                if not result:
                    self.go_btn.grid_remove()
                    self.page_entry.grid_remove()
                    self.page_label.grid(row=12, column=6, padx=(0,20))
                else:
                    self.page_entry.grid(row=12, column=6, sticky='w')
                    self.page_label.grid(row=12, column=6, padx=(5,0))
                    self.go_btn.grid(row=12, column=7, sticky='e')
        else:
            messagebox.showerror('Keyword required', 'Please add a filter keyword')

    def clearf(self):
        '''Clear the filter toolkit'''
        self.last_result = 0
        self.clearf_btn.config(state='disabled')
        self.filter_type.delete([0], END)
        self.f_entry.delete([0], END)
        self.filter_btn.grid_remove()
        self.f_label.grid_remove()
        self.f_entry.grid_remove()
        self.b1.grid_remove()
        self.b2.grid_remove()
        self.b3.grid_remove()
        self.from_h_entry.grid_remove()
        self.colon1.grid_remove()
        self.colon2.grid_remove()
        self.from_label.grid_remove()
        self.to_label.grid_remove()
        self.from_m_entry.grid_remove()
        self.to_h_entry.grid_remove()
        self.to_m_entry.grid_remove()
        self.v.set(" ")
        self.loc_type.grid_remove()
        db.filtered = False
        db.page = 1
        self.page_entry.delete(0, END)
        self.page_entry.insert(END, db.page)
        self.refresh_list()
        
    def filter_query(self, event):
        '''Discerns what the filtering criteria is and grids the appropriate options'''
        self.last_result = 0
        self.clearf_btn.config(state='normal')
        self.selected_filter = self.filter_type.get()
        self.filter_btn.grid(row=6, column=0, sticky='s')
        self.loc_type.grid_remove()
        self.b1.grid_remove()
        self.b2.grid_remove()
        self.b3.grid_remove()
        self.from_h_entry.grid_remove()
        self.colon1.grid_remove()
        self.colon2.grid_remove()
        self.from_label.grid_remove()
        self.to_label.grid_remove()
        self.from_m_entry.grid_remove()
        self.to_h_entry.grid_remove()
        self.to_m_entry.grid_remove()
        self.v.set(" ")
        self.f_label.grid_remove()
        self.f_entry.grid_remove()
        if self.selected_filter == 'Verified':
            self.b1.configure(text='True', value='True')
            self.b2.configure(text='False', value='False')
            self.b1.grid(row=5, column=0, sticky='n')
            self.b2.grid(row=5, column=0, sticky='s', padx=(5.5,0))
        elif self.selected_filter == 'Date Created':
            self.from_h_entry.grid(row=5, column=0, sticky='n')
            self.colon1.grid(row=5, column=0, padx=(35,0), sticky='n')
            self.from_m_entry.grid(row=5, column=0, padx=(70,0), sticky='n')
            self.from_label.grid(row=5, column=0, sticky='nw', padx=(10,0))
            self.to_h_entry.grid(row=5, column=0, sticky='s')
            self.colon2.grid(row=5, column=0, padx=(35,0), sticky='s')
            self.to_m_entry.grid(row=5, column=0, padx=(70,0), sticky='s')
            self.to_label.grid(row=5, column=0, sticky='sw', padx=(10,0))
        elif self.selected_filter == 'Tweet':
            self.f_label.configure(text='Text:', font=('bold', 9))
            self.f_label.grid(row=5, column=0, sticky=W, padx=(8,0))
            self.f_entry.grid(row=5, column=0, sticky=W, padx=(44,0)) 
        elif self.selected_filter == 'Location':
            self.f_label.configure(text='Country:', font=('bold', 6))
            self.f_label.grid(row=5, column=0, sticky=W, padx=(4,0))
            self.loc_type.grid(row=5, column=0, sticky=W, padx=(44,0))
            self.locs = db.get_locs()
            self.loc_list = []
            for value in self.locs:
                self.loc_list.append(value[0])
            self.loc_type['values'] = self.loc_list
        elif self.selected_filter == 'Sentiment':
            self.b1.configure(text='Positive', value='Positive')
            self.b2.configure(text='Negative', value='Negative')
            self.b1.grid(row=5, column=0, sticky='n', padx=(8,0))
            self.b2.grid(row=5, column=0, sticky='s', padx=(12,0))
            self.b3.grid(row=6, column=0, sticky='n', padx=(4,0))
        elif self.selected_filter == 'Media Type':
            self.f_label.configure(text='Media:', font=('bold', 9))
            self.f_label.grid(row=5, column=0, sticky=W, padx=(5,0))
            self.f_entry.grid(row=5, column=0, sticky=W, padx=(44,0)) 
        elif self.selected_filter == 'Username':
            self.f_label.configure(text='User:', font=('bold', 9))
            self.f_label.grid(row=5, column=0, sticky=W, padx=(8,0))
            self.f_entry.grid(row=5, column=0, sticky=W, padx=(44,0)) 
            
    def sortby(self, tree, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        # now sort the data in place
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so that it will sort in the opposite direction
        tree.heading(col,
            command=lambda col=col: self.sortby(tree, col, int(not descending)))

root = Tk()
app = Application(root)
consumer_key = #tweepy consumer key
consumer_secret = #tweepy consumer_secret
access_token = #tweepy access token
access_secret = #tweepy access_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

mySL = streamer.MyStreamListener(db.cnx, db.cur1, app)
myStream = tweepy.Stream(auth=api.auth, listener=mySL)
app.mainloop()
