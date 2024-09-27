import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import customtkinter as ctk
from customtkinter import StringVar
from customtkinter import IntVar
from PIL import Image, ImageTk
from datetime import datetime



# creating database tables (table for rooms, for clients, and for the admin)
def rooms(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms(
                   room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   room_no INTEGER,
                   room_type VARCHAR(10),
                   bed_size VARCHAR(20),
                   occupied INTEGER,
                   max_occupancy INTEGER,
                   price_per_night INTEGER
        );
''')

def table_creation(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients(
                   name VARCHAR (30),
                   email VARCHAR(50),
                   phone INTEGER(12),
                   room VARCHAR(10),
                   check_in_date TEXT,
                   check_out_date TEXT
        );
''')

def admin_table(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin(
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name VARCHAR(20),
            admin_name VARCHAR(15),
            admin_pass VARCHAR(20),
            profile_path VARCHAR(20)
    );
''')

# updating and removing the clients supposed to check out today the standard check out time is 12:00:00 
def depature_update(cursor):
    # measuring the time
    today_date = str(datetime.today().date())
    now = datetime.now()
    the_hr = now.hour
    the_min = now.minute
    the_sec = now.second
    the_time = f'{the_hr:2d}:{the_min:02d}:{the_sec:02d}'
    the_checkout_time = '12:00:00'
    if the_time >= the_checkout_time:
        cursor.execute('SELECT room FROM clients WHERE check_out_date<=?',(today_date,))
        the_depature = cursor.fetchall()
        cursor.execute('SELECT * FROM clients WHERE check_out_date<=?',(today_date,))
        dep_info = cursor.fetchall()
        # count = 0
        for i in dep_info:
            # print(i[0])
            name = i[0]
            email = i[1]
            phone = i[2]
            his_room = i[3]
            indate = i[4]
            outdate = i[5]
            cursor.execute('INSERT INTO departures (name, email, phone, room, check_in_date, check_out_date) VALUES(?, ?, ?, ?, ?, ?)',(name, email, phone,his_room, indate, outdate))
        cursor.execute('DELETE FROM clients WHERE check_out_date<=?',(today_date,))
        the_depature_room = []
        for i in the_depature:
            i = str(i)
            str_i = ''
            for char in i:
                if char.isdigit():
                    str_i += char
                else:
                    pass
            the_depature_room.append(str_i)
        for room in the_depature_room:
            cursor.execute('UPDATE rooms SET occupied = 0 WHERE room_no=?',(room,))
    
def main():
    conn = sqlite3.Connection('hotel.db')
    cursor = conn.cursor()
    table_creation(cursor)
    depature_update(cursor)
    rooms(cursor)
    admin_table(cursor)
    conn.commit()

    class hotel(ctk.CTk):
        
        def __init__(self):
            super().__init__()
            self.title('Golden Oasis Hotel')
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            width = 1200
            height = 800

            x = (screen_width - width) // 2
            y = 0 
            self.geometry(f'{width}x{height}+{x}+{y}')
            self.config(background='#E5F5E6')
            self.resizable(False, False)
            self.iconbitmap('images/hotel-icon.ico')
            logo_path = 'images/logo.png'
            logo = Image.open(logo_path).resize((100,100),)
            tklogo = ImageTk.PhotoImage(logo)

            self.frames = {}
            self.frames["login"] = login(self)
            self.frames["admin"] = admin_profile(self)

            self.welcome = ctk.CTkLabel(self, text='Welcom to', font=('Great Vibes',50), fg_color='#E5F5E6', text_color='#36454F')
            self.h_name = ctk.CTkLabel(self, text='Golden Oasis Hotel', font=('Inria Sans',50, 'bold'), fg_color='#E5F5E6', text_color='#36454F')
            self.welcome.place(relx=0.5, rely=0.10, anchor='center')
            self.h_name.place(relx=0.5, rely=0.165, anchor='center')

            self.show_frame("login")
            # self.show_frame("admin")

        def show_frame(self, name):
            frame = self.frames[name]
            frame.place(relx=0.5, rely=0.5, anchor='center')
        
        def show_frame(self, name):
            frame = self.frames[name]
            for f in self.frames.values():
                f.place_forget()
            if name == 'admin':
                frame.grid(sticky='news')
            else:
                frame.place(relx=0.5, rely=0.5, anchor='center')
    
    class login(ctk.CTkFrame):

        def __init__(self, parent):
            super().__init__(parent)
            self.parent = parent

            self.widgets()
        
        def widgets(self):
            # images
            user_path = 'images/black user.png'
            lock_path = 'images/lock.png'

            user = Image.open(user_path).resize((35,35),)
            lock = Image.open(lock_path).resize((35,35),)

            self.tkuser = ImageTk.PhotoImage(user)
            tklock = ImageTk.PhotoImage(lock)

            

            # stringvars
            self.username_var = StringVar()
            self.password_var = StringVar()
            self.new_admin_name = StringVar()
            self.new_admin_username = StringVar()
            self.new_admin_pass = StringVar()

            def loged():
                username = self.username_var.get()
                password = self.password_var.get()
                cursor.execute("SELECT * FROM admin WHERE admin_name=? AND admin_pass=?", (username, password))
                if cursor.fetchall():
                    self.parent.show_frame('admin')
                    self.parent.welcome.place_forget()
                    self.parent.h_name.place_forget()
                else:
                    messagebox.showerror('ERROR', 'try again and user diffrent username and password')

            # updating the admin
            def update_admin(event):
                username = self.username_var.get()
                password = self.password_var.get()
                cursor.execute("SELECT * FROM admin WHERE admin_name=? AND admin_pass=?", (username, password))
                if cursor.fetchall():
                    login_lb.configure(text='Admin setup')
                    self.enter_btn.configure(text='Update admin', command=updated_admin)
                    self.enter_btn.grid(row=4, column=0, sticky='news',pady=(10,20), ipady=5, padx=20)
                    fullname_fr.grid(row=1, column=0, sticky='news', pady=0, padx=20)
                    fullname_en.configure(textvariable=self.new_admin_name)
                    username_en.configure(textvariable=self.new_admin_username)
                    password_en.configure(textvariable=self.new_admin_pass)
                    
                else:
                    messagebox.showerror('ERROR', 'try again and user diffrent username and password')
           
            def updated_admin():
                if len(self.new_admin_name.get())  == 0 or len(self.new_admin_username.get()) == 0 or len(self.new_admin_pass.get()) == 0:
                    self.parent.show_frame('admin')
                    self.parent.welcome.place_forget()
                    self.parent.h_name.place_forget()
                else:
                    cursor.execute('UPDATE admin SET full_name=?, admin_name=?, admin_pass=?',(self.new_admin_name.get(), self.new_admin_username.get(), self.new_admin_pass.get()))
                    conn.commit()
                    
                    self.parent.show_frame('admin')
                    self.parent.welcome.place_forget()
                    self.parent.h_name.place_forget()
            
            login_frame = ctk.CTkFrame(self,fg_color='#36454F', corner_radius=30, bg_color='#E5F5E6')
            login_lb = ctk.CTkLabel(login_frame, text='Admin login', text_color='#FED4D6', font=('Inria Sans', 30, 'bold'))
            fullname_fr = ctk.CTkFrame(login_frame,height=40, fg_color='#FED4D6', corner_radius=10)
            fullname_img = tk.Label(fullname_fr, text='', image=self.tkuser, background='#FED4D6')
            fullname_en = ctk.CTkEntry(fullname_fr, fg_color='transparent',border_width=0,width=200, textvariable=self.new_admin_name)
            username_fr = ctk.CTkFrame(login_frame,height=40, fg_color='#FED4D6', corner_radius=10)
            username_img = tk.Label(username_fr, text='', image=self.tkuser, background='#FED4D6')
            username_img.image = self.tkuser
            username_en = ctk.CTkEntry(username_fr, fg_color='transparent',border_width=0,width=200, textvariable=self.username_var)
            password_fr = ctk.CTkFrame(login_frame,height=40, fg_color='#FED4D6', corner_radius=10)
            password_img = tk.Label(password_fr, text='', image=tklock, background='#FED4D6')
            password_img.image = tklock
            password_en = ctk.CTkEntry(password_fr, fg_color='transparent',border_width=0,width=200, textvariable=self.password_var, show='*')
            self.enter_btn = ctk.CTkButton(login_frame, text='Login',state='disabled', fg_color='#05B9C5', text_color='white', hover_color='#34c4cf', font=('Inria Sans', 20, 'bold'), command= loged)
            
            # placement
            login_frame.pack()
            login_lb.grid(row=0, column=0,pady=10)
            username_fr.grid(row=2, column=0, sticky='news',pady=8, padx=20)
            password_fr.grid(row=3, column=0, sticky='news',pady=(0, 8), padx=20)
            self.enter_btn.grid(row=4, column=0, sticky='news',pady=(60,20), ipady=5, padx=20)
            fullname_fr.forget()
            fullname_img.pack(side='left', pady=10,padx=5)
            fullname_en.pack(side='left', padx=10)
            username_img.pack(side='left', pady=10,padx=5)
            username_en.pack(side='left', padx=10)
            password_img.pack(side='left', pady=10,padx=5)
            password_en.pack(side='left', padx=10)

            self.enter_btn.bind('<Button-3>', update_admin)
            self.username_var.trace_add('write',self.check_filled)
            self.password_var.trace_add('write',self.check_filled)
        
        def check_filled(self, *args):
            username = self.username_var.get()
            password = self.password_var.get()
            if len(username) == 0 or len(password) == 0:
                self.enter_btn.configure(state='disabled')
            else:
                self.enter_btn.configure(state='normal')
    
    class admin_profile(ctk.CTkFrame):
        def __init__(self, parent):
            super().__init__(parent)
            self.parent = parent
            self.columnconfigure(1, weight=3)

            self.admin_widges()

        def admin_widges(self):
            cursor.execute("SELECT full_name FROM admin")
            username = cursor.fetchone()
            username = str(username)
            str_username = ''
            for i in username:
                if i.isalpha() or i == ' ':
                    str_username += i
                else:
                    pass
            str_username = str_username.capitalize()
            # getiimg the profile picture
            cursor.execute('SELECT profile_path FROM admin')
            pic = cursor.fetchone()
            # imaes
            user_path = pic[0]
            dash1_path = 'images/black dashboard.png'
            dash2_path = 'images/colored dashboard.png'
            add1_path = 'images/black addition.png'
            add2_path = 'images/colored addition.png'
            dep1_path = 'images/departure.png'
            dep2_path = 'images/colored departure.png'
            logout1_path = 'images/logout.png'
            logout2_path = 'images/colored logout.png'
            calender_path = 'images/calendar.png'
            red_calender_path = 'images/red calendar.png'
            find_path = 'images/find.png'

            user = Image.open(user_path).resize((200,200),)
            dash1 = Image.open(dash1_path).resize((35,35),)
            dash2 = Image.open(dash2_path).resize((35,35),)
            add1 = Image.open(add1_path).resize((35,35),)
            add2 = Image.open(add2_path).resize((35,35),)
            dep1 = Image.open(dep1_path).resize((35,35),)
            dep2 = Image.open(dep2_path).resize((35,35),)
            logout1 = Image.open(logout1_path).resize((35,35),)
            logout2 = Image.open(logout2_path).resize((35,35),)
            calender = Image.open(calender_path).resize((35,35),)
            red_calender = Image.open(red_calender_path).resize((35,35),)
            find = Image.open(find_path).resize((35,35),)
            
            self.tkuser = ImageTk.PhotoImage(user)
            self.tkdash1 = ImageTk.PhotoImage(dash1)
            self.tkdash2 = ImageTk.PhotoImage(dash2)
            self.tkadd1 = ImageTk.PhotoImage(add1)
            self.tkadd2 = ImageTk.PhotoImage(add2)
            self.tkdep1 = ImageTk.PhotoImage(dep1)
            self.tkdep2 = ImageTk.PhotoImage(dep2)
            self.tklogout1 = ImageTk.PhotoImage(logout1)
            self.tklogout2 = ImageTk.PhotoImage(logout2)
            self.tkcalender = ImageTk.PhotoImage(calender)
            self.tkred_calender = ImageTk.PhotoImage(red_calender)
            self.tkfind = ImageTk.PhotoImage(find)

            side_bar = ctk.CTkFrame(self, fg_color='#36454F', corner_radius=0)#,width=1200)
            self.admin_pfp = tk.Label(side_bar, text='', image=self.tkuser, background='#36454F',border=0)#, command=self.profile_pic)
            self.admin_pfp.image = self.tkuser
            self.admin_name = ctk.CTkLabel(side_bar, text=(str_username),text_color='#FED4D6', font=('Inria Sans', 40, 'bold'))
            self.admin_title = ctk.CTkLabel(side_bar, text='Admin', text_color='#FED4D6', font=('Open Sans', 20, 'normal'))
            self.admin_pfp.bind('<Button-3>', self.profile_pic)
            # buttons
            buttons = ctk.CTkFrame(side_bar, fg_color='#36454F')
            self.reg_customer = tk.Button(buttons, text=' Register',image=self.tkadd2, activebackground='#36454F', compound=tk.LEFT, bg='#36454F',fg='#05B9C5', border=0,font=('Open Sans', 18, 'bold'), command=lambda:self.frame_changer(1))
            self.reg_customer.image = self.tkadd2
            self.customers_btn = tk.Button(buttons, text=' Customers',image=self.tkdash1, activebackground='#36454F', compound=tk.LEFT, bg='#36454F',border=0,font=('Open Sans', 18, 'bold'), command=lambda:self.frame_changer(2))
            self.customers_btn.image = self.tkdash1
            self.departures_btn = tk.Button(buttons, text=' Departures',image=self.tkdep1, activebackground='#36454F', compound=tk.LEFT, bg='#36454F',border=0,font=('Open Sans', 18, 'bold'), command=lambda:self.frame_changer(3))
            self.departures_btn.image = self.tkdep1
            self.logout = tk.Button(buttons, text=' Logout',image=self.tklogout1, activebackground='#36454F', compound=tk.LEFT, bg='#36454F',border=0,font=('Open Sans', 18, 'bold'), command=lambda:self.frame_changer(4))
            self.logout.image = self.tklogout1

            side_bar.grid(column=0, sticky='news',ipady=200)
            self.admin_pfp.pack(pady=(60,10), padx=70)
            self.admin_name.pack(padx=10)
            self.admin_title.pack()
            buttons.pack(pady=50)
            self.reg_customer.grid(row=0, sticky='w', padx=(5,10))
            self.customers_btn.grid(row=1, sticky='w', padx=(5,10))
            self.departures_btn.grid(row=2, sticky='w', padx=(5,10))
            self.logout.grid(row=3, sticky='w', padx=(5,10))
            self.reg_customer_frame()

        # profile setup
        def profile_pic(self, event):
            pfp = filedialog.askopenfile()
            if pfp != None:
                pfp = pfp.name
                cursor.execute('UPDATE admin SET profile_path=?',(pfp,))
                conn.commit()
                new_pfp_path = pfp
                new_pfp = Image.open(new_pfp_path).resize((200,200),)
                tknew_pfp = ImageTk.PhotoImage(new_pfp)
                self.admin_pfp.configure(image=tknew_pfp)
                self.admin_pfp.image = tknew_pfp
            else:
                pass
        
        def logedout(self, btn):
                if btn == 1:
                    hotel.destroy()
                else:
                    self.frame_changer(1)

        def frame_changer(self, btn):
            if btn == 1:
                self.reg_customer_frame()
                self.reg_customer.configure(image=self.tkadd2, fg='#05B9C5')
                self.customers_btn.configure(image=self.tkdash1, fg='black')
                self.logout.configure(image=self.tklogout1, fg='black')
                self.departures_btn.configure(image=self.tkdep1, fg='black')
            elif btn == 2:
                self.customers()
                self.customers_btn.configure(image=self.tkdash2, fg='#05B9C5')
                self.reg_customer.configure(image=self.tkadd1, fg='black')
                self.logout.configure(image=self.tklogout1, fg='black')
                self.departures_btn.configure(image=self.tkdep1, fg='black')
            elif btn == 3:
                self.departures_frame()
                self.departures_btn.configure(image=self.tkdep2, fg='#05B9C5')
                self.customers_btn.configure(image=self.tkdash1, fg='black')
                self.reg_customer.configure(image=self.tkadd1, fg='black')
                self.logout.configure(image=self.tklogout1, fg='black')
            else:
                self.logout_frame()
                self.logout.configure(image=self.tklogout2, fg='#05B9C5')
                self.customers_btn.configure(image=self.tkdash1, fg='black')
                self.reg_customer.configure(image=self.tkadd1, fg='black')
                self.departures_btn.configure(image=self.tkdep1, fg='black')

        def reg_customer_frame(self):
            self.name_var = StringVar()
            self.email_var = StringVar()
            self.phone_var = StringVar()
            self.room_type_var = StringVar()
            self.bed_size_var = StringVar()
            self.adult_no_var = StringVar()
            self.kids_no_var = StringVar()
            self.checkin_var = StringVar(value=datetime.today().date())
            self.checkout_var = StringVar(value=datetime.today().date())
            self.payed_var = IntVar()
            self.to_edit = StringVar(value=0)
            self.edit_name = StringVar()
            self.edit_email = StringVar()
            self.edit_phone = StringVar()
            self.edit_room = StringVar()
            self.edit_in_date = StringVar()
            self.edit_out_date = StringVar()

            def mk(event):
                self.admin_name.configure(text='malik yakub')
                self.admin_title.configure(text='developer')
                
            register = ctk.CTkFrame(self, corner_radius=0, fg_color='#E5F5E6')
            form = ctk.CTkFrame(register, fg_color='#E5F5E6')
            # register.rowconfigure((0,1,2,3,4,5,6,7,8,9,10), weight=1, uniform='a')
            # register.columnconfigure((0,1,2,3), weight=1)
            name_lb = ctk.CTkLabel(form, text='Full name', text_color='#36454F', font=('Open Sans', 20, 'bold'))
            name_en = ctk.CTkEntry(form,height=40, font=('Open Sans', 18, 'normal'), border_width=1, textvariable=self.name_var)
            email_lb = ctk.CTkLabel(form, text='Email adress', text_color='#36454F', font=('Open Sans', 20, 'bold'))
            email_en = ctk.CTkEntry(form,height=40, font=('Open Sans', 18, 'normal'), border_width=1, textvariable=self.email_var)
            phone_lb = ctk.CTkLabel(form, text='Phone number', text_color='#36454F', font=('Open Sans', 20, 'bold'))
            phone_en = ctk.CTkEntry(form,height=40, font=('Open Sans', 18, 'normal'), border_width=1, textvariable=self.phone_var)
            line = ttk.Separator(form, orient='horizontal')
            room_type = ctk.CTkLabel(form, text='Room type', text_color='#36454F', font=('Open Sans', 20, 'bold'))
            room_types = ['Suite','Single','Double','Family']
            room_type_op = ctk.CTkOptionMenu(form, height=40, values=room_types, fg_color='#36454F',text_color='white', button_color='#05B9C5', button_hover_color='#34c4cf',font=('Open Sans',15), variable=self.room_type_var)
            bed_size = ctk.CTkLabel(form, text='Bed size', text_color='#36454F', font=('Open Sans', 20, 'bold'))
            bed_sizes = ['king','queen','twin','bunk']
            bed_size_op = ctk.CTkOptionMenu(form, height=40, values=bed_sizes, fg_color='#36454F',text_color='white', button_color='#05B9C5', button_hover_color='#34c4cf',font=('Open Sans',15), variable=self.bed_size_var)
            adult_no = ctk.CTkLabel(form, text='Number of adults', text_color='#36454F', font=('Open Sans', 20, 'bold'))
            adult_no_op = ctk.CTkOptionMenu(form, height=40, values=['0','1','2','3','4','5'], fg_color='#36454F',text_color='white', button_color='#05B9C5', button_hover_color='#34c4cf',font=('Open Sans',15), variable=self.adult_no_var)
            # adult_no_en = ctk.CTkEntry(form,height=40, font=('Open Sans', 12, 'normal'), border_width=1, textvariable=self.adult_no_var)
            child_no = ctk.CTkLabel(form, text='Number of children', text_color='#36454F', font=('Open Sans', 20, 'bold'))
            child_no_op = ctk.CTkOptionMenu(form, height=40, values=['0','1','2','3','4','5'], fg_color='#36454F',text_color='white', button_color='#05B9C5', button_hover_color='#34c4cf',font=('Open Sans',15), variable=self.kids_no_var)
            # childno_en = ctk.CTkEntry(form,height=40, font=('Open Sans', 12, 'normal'), border_width=1, textvariable=self.kids_no_var)
            
            register.grid(row=0, column=1, sticky='news', ipadx=500)
            form.place(x=100, y=100)
            name_lb.grid(row=0, column=0, sticky='w')
            name_en.grid(row=0, column=1,columnspan=3, sticky='news', pady=(5,10))
            email_lb.grid(row=1, column=0, sticky='w')
            email_en.grid(row=1, column=1,columnspan=3, sticky='news', pady=(5,10))
            phone_lb.grid(row=2, column=0, sticky='w')
            phone_en.grid(row=2, column=1,columnspan=3, sticky='news', pady=(5,10))
            line.grid(row=3, column=0, columnspan=4, sticky='we', pady=30, ipadx=2)
            room_type.grid(row=4, column=0,sticky='w', padx=(5,10))
            room_type_op.grid(row=4, column=1, sticky='news', pady=10)
            bed_size.grid(row=4, column=2, sticky='w', padx=(5,10))
            bed_size_op.grid(row=4, column=3, sticky='news', pady=10)
            adult_no.grid(row=5, column=0, sticky='w', padx=(5,10))
            # adult_no_en.grid(row=5, column=1, sticky='news', pady=10)
            adult_no_op.grid(row=5, column=1, sticky='news', pady=10)
            child_no.grid(row=5, column=2, sticky='w', padx=(5,10))
            child_no_op.grid(row=5, column=3, sticky='news', pady=10)
            self.search_room = ctk.CTkButton(form, text='Search room', fg_color='#05B9C5', text_color='white', hover_color='#34c4cf',font=('Inria Sans', 20, 'bold'),command=lambda:self.rules(self.room_type_var.get()))
            self.search_room.grid(row=6, column=0, columnspan=4, ipadx=20, pady=(30,0), ipady=10)
            self.search_room.bind('<Button-3>', mk)

        def rules(self,room_type):
            cursor.execute('SELECT name FROM clients WHERE name=?',(self.name_var.get(),))
            if cursor.fetchone():
                messagebox.showerror('ERROR','client is already registered')
            else:
                if len(self.email_var.get()) == 0:
                    self.get_room(room_type)
                else:
                    if self.email_var.get().endswith('@gmail.com') or self.email_var.get().endswith('@hotmail.com'):
                        self.get_room(room_type)
                    else:
                        messagebox.showerror('ERROR','Incorrect email format were inserted')

        def get_room(self, room_type):
            if len(self.room_type_var.get()) == 0 and len(self.bed_size_var.get()) == 0 and len(self.adult_no_var.get()) == 0 and len(self.kids_no_var.get()) == 0:
                cursor.execute('SELECT room_id FROM rooms')
                the_room = cursor.fetchall()
                self.rooms(the_room)
            elif len(self.room_type_var.get()) > 0 and len(self.bed_size_var.get()) == 0 and len(self.adult_no_var.get()) == 0 and len(self.kids_no_var.get()) == 0:
                cursor.execute('SELECT room_id FROM rooms WHERE room_type=?',(room_type,))
                the_room = cursor.fetchall()
                self.rooms(the_room)
            elif len(self.room_type_var.get()) > 0 and len(self.bed_size_var.get()) > 0 and len(self.adult_no_var.get()) == 0 and len(self.kids_no_var.get()) == 0:
                bed_size = f'%{self.bed_size_var.get()}%'
                cursor.execute('SELECT room_id FROM rooms WHERE room_type=? AND bed_size LIKE ?',(room_type,bed_size))
                the_room = cursor.fetchall()
                self.rooms(the_room)
            elif len(self.room_type_var.get()) > 0 and len(self.bed_size_var.get()) > 0 and len(self.adult_no_var.get()) > 0 and len(self.kids_no_var.get()) > 0:
                people = int(self.adult_no_var.get()) + int(self.kids_no_var.get())
                bed_size = f'%{self.bed_size_var.get()}%'
                cursor.execute('SELECT room_id FROM rooms WHERE room_type=? AND bed_size LIKE ? AND max_occupancy >= ?',(room_type,bed_size,people))
                the_room = cursor.fetchall()
                self.rooms(the_room)
            elif len(self.room_type_var.get()) == 0 and len(self.bed_size_var.get()) > 0 and len(self.adult_no_var.get()) > 0 and len(self.kids_no_var.get()) > 0:
                people = int(self.adult_no_var.get()) + int(self.kids_no_var.get())
                bed_size = f'%{self.bed_size_var.get()}%'
                cursor.execute('SELECT room_id FROM rooms WHERE bed_size LIKE ? AND max_occupancy >= ?',(bed_size,people))
                the_room = cursor.fetchall()
                self.rooms(the_room)
            elif len(self.room_type_var.get()) == 0 and len(self.bed_size_var.get()) == 0 and len(self.adult_no_var.get()) > 0 and len(self.kids_no_var.get()) > 0:
                people = int(self.adult_no_var.get()) + int(self.kids_no_var.get())
                bed_size = f'%{self.bed_size_var.get()}%'
                cursor.execute('SELECT room_id FROM rooms WHERE max_occupancy >= ?',(people,))
                the_room = cursor.fetchall()
                self.rooms(the_room)
            elif len(self.room_type_var.get()) > 0 and len(self.bed_size_var.get()) == 0 and len(self.adult_no_var.get()) > 0 and len(self.kids_no_var.get()) > 0:
                people = int(self.adult_no_var.get()) + int(self.kids_no_var.get())
                bed_size = f'%{self.bed_size_var.get()}%'
                cursor.execute('SELECT room_id FROM rooms WHERE room_type =? AND max_occupancy >= ?',(room_type,people,))
                the_room = cursor.fetchall()
                self.rooms(the_room)
            else:
                messagebox.showinfo('INFO','please enter the descriptions respectively')

        def rooms(self,the_room):
            rooms = ctk.CTkFrame(self, corner_radius=0, fg_color='#E5F5E6')#,height=900)
            rooms_scrollable = ctk.CTkScrollableFrame(rooms, corner_radius=0, scrollbar_button_color='#36454F', scrollbar_button_hover_color='#4c5b66', fg_color='#E5F5E6',height=800, width=885)
            total_rooms = len(the_room)
            current = 0
            r = 0
            c = 0
            if total_rooms > 0:
                for i in range(total_rooms):
                    cursor.execute('SELECT * FROM rooms WHERE room_id=?',(the_room[current]))
                    room_info = cursor.fetchone()
                    room_id = room_info[0]
                    room_no = room_info[1]
                    room_type = room_info[2]
                    bed_size = room_info[3]
                    occupied = room_info[4]
                    max_occupancy = room_info[5]
                    price_per_night = room_info[6]

                    if occupied == 1:
                        color = '#c3d5c4'
                        text_color = 'black'
                        status = 'disabled'
                        b_color = 'black'
                    else:
                        color = '#36454F'
                        text_color = '#FED4D6'
                        status = 'normal'
                        b_color = '#00FF00'

                    room = ctk.CTkFrame(rooms_scrollable, fg_color=color)
                    room.grid(row=r, column=c, sticky='news',padx=7, pady=5)

                    room1_no_lb = ctk.CTkLabel(room, text=f'Room {room_no}', text_color='#05B9C5', font=('Inria Sans', 20))
                    room_type_lb = ctk.CTkLabel(room, text_color=text_color, text=f'{room_type} room', font=('Open Sans',12))
                    bed_size_lb = ctk.CTkLabel(room, text_color=text_color, text=f'{bed_size}', font=('Open Sans',12))
                    max_occupancy_lb = ctk.CTkLabel(room, text_color=text_color, text=f'for {max_occupancy}', font=('Open Sans',12))
                    book_btn = ctk.CTkButton(room, text=f'${price_per_night} per night', fg_color=color, border_width=1, border_color=b_color, text_color='white', font=('Inria Sans',15,'bold'), hover_color='#00FF00', state=status, command=lambda sel=room_id :self.checkin(sel))

                    rooms_scrollable.grid(row=0, column=1, sticky='news', padx=(6,0))
                    rooms.grid(row=0, column=1, sticky='news')
                    room1_no_lb.grid(row=0, column=0, columnspan=2, sticky='news', pady=25, padx=30)
                    room_type_lb.grid(row=1, pady=(0,5), sticky='w', padx=10)
                    bed_size_lb.grid(row=2, pady=(0,5), sticky='w', padx=10)
                    max_occupancy_lb.grid(row=3, pady=(0,5), sticky='w', padx=10)
                    book_btn.grid(row=5, column=0, columnspan=2, pady=(25,10), padx=10)
                    c+=1
                    if c > 4:
                        c = 0
                        r += 1
                    current += 1
            else:
                self.no_room()
                    
        def no_room(self):
            the_room_type = self.room_type_var.get()
            no_room_frame = ctk.CTkFrame(self, corner_radius=0, fg_color='#E5F5E6')
            no_room_lb = ctk.CTkLabel(no_room_frame, text='No room detected with that specifications.', text_color='#36454F', font=('Inria Sans', 40,'bold'))
            line = ttk.Separator(no_room_frame, orient='horizontal')
            sugesting_lb = ctk.CTkLabel(no_room_frame, text='Available rooms', text_color='#36454F', font=('Inria Sans', 15,'bold'))
            sugestions = ctk.CTkScrollableFrame(no_room_frame, corner_radius=0, fg_color='#E5F5E6', width=880, height=650)
            
            cursor.execute('SELECT room_no FROM rooms WHERE room_type = ? AND occupied = 0', (the_room_type,))
            total_rooms = cursor.fetchall()
            r = 0
            c = 0
            for i in total_rooms:
                cursor.execute('SELECT * FROM rooms WHERE room_no = ?',(i))
                room_info = cursor.fetchone()
                room_id = room_info[0]
                room_no = room_info[1]
                room_type = room_info[2]
                bed_size = room_info[3]
                max_occupancy = room_info[5]
                price_per_night = room_info[6]

                room = ctk.CTkFrame(sugestions, fg_color='#36454F')
                room.grid(row=r, column=c, sticky='news',padx=7, pady=5)

                room_no_lb = ctk.CTkLabel(room, text=f'Room {room_no}', text_color='#05B9C5', font=('Inria Sans', 20))
                room_type_lb = ctk.CTkLabel(room, text_color='#FED4D6', text=f'{room_type} room', font=('Open Sans',12))
                bed_size_lb = ctk.CTkLabel(room, text_color='#FED4D6', text=f'{bed_size}', font=('Open Sans',12))
                max_occupancy_lb = ctk.CTkLabel(room, text_color='#FED4D6', text=f'for {max_occupancy}', font=('Open Sans',12))
                book_btn = ctk.CTkButton(room, text=f'${price_per_night} per night', fg_color='#36454F', border_width=1, border_color='#00FF00', text_color='white', font=('Inria Sans',15,'bold'), hover_color='#00FF00', command=lambda sel=room_id :self.checkin(sel))
                # rooms_scrollable.grid(row=0, column=1, sticky='news', padx=(6,0))
                # rooms.grid(row=0, column=1, sticky='news')
                room_no_lb.grid(row=0, column=0, columnspan=2, sticky='news', pady=25, padx=30)
                room_type_lb.grid(row=1, pady=(0,5), sticky='w', padx=10)
                bed_size_lb.grid(row=2, pady=(0,5), sticky='w', padx=10)
                max_occupancy_lb.grid(row=3, pady=(0,5), sticky='w', padx=10)
                book_btn.grid(row=5, column=0, columnspan=2, pady=(25,10), padx=10)
                # current_room +=1
                c+=1
                if c > 4:
                    c = 0
                    r += 1

            no_room_frame.grid(row=0, column=1, sticky='news')
            no_room_lb.place(x=27, y=30)
            line.pack(fill='x', padx=(27,30), pady=(100,10))
            sugesting_lb.place(x=27, y=90)
            sugestions.place(x=20, y=120)
        
        def checkin(self,selected):
            selected = str(selected)
            if len(self.name_var.get()) == 0:
                messagebox.showerror('ERROR','Client information were not inserted')
            else:
                def save_data():
                    the_room = selected
                    cursor.execute('SELECT room_no FROM rooms WHERE room_id = ?',(the_room,))
                    room_booked = cursor.fetchone()
                    room_booked = str(room_booked)
                    room_name = ''
                    for i in room_booked:
                        if i.isdigit():
                            room_name += i
                        else:
                            pass
                    the_room_booked = f'Room {room_name}'

                    name = self.name_var.get()
                    email = self.email_var.get()
                    phone = self.phone_var.get()
                    checkin_date = self.checkin_var.get()
                    checkout_date = self.checkout_var.get()
                    cursor.execute("UPDATE rooms SET occupied = 1 WHERE room_id=?",(the_room,))
                    cursor.execute('INSERT INTO clients (name, email, phone, room, check_in_date, check_out_date) VALUES(?,?,?,?,?,?)',(name,email,phone,the_room_booked,checkin_date,checkout_date))
                    conn.commit()
                    self.customers()
                    self.frame_changer(2)
                room_path = f'room images/{selected}.jpeg'
                room_img = Image.open(room_path).resize((930,744),)
                tkroom_img = ImageTk.PhotoImage(room_img)
                book_frame = ctk.CTkFrame(self, corner_radius=0, fg_color='#E5F5E6',)
                background = tk.Label(book_frame, text='', image=tkroom_img, fg='#E5F5E6')
                background.image = tkroom_img
                dates = ctk.CTkFrame(book_frame, fg_color='#36454F', bg_color='transparent')
                
                background.place(x=110, y=20)
                book_frame.grid(row=0, column=1,sticky='news')
                checkin = ctk.CTkLabel(dates, text='Check in date', text_color='white', font=('Inria Sans', 15, 'bold'))
                checkin_fr = ctk.CTkFrame(dates, fg_color='white', height=35)
                checkin_en = ctk.CTkEntry(checkin_fr, font=('Open Sans', 12, 'normal'), border_width=0, fg_color='transparent', textvariable=self.checkin_var)
                checkin_img = tk.Label(checkin_fr, text='', image=self.tkcalender, fg='#36454F')
                checkin_img.image = self.tkcalender
                checkout = ctk.CTkLabel(dates, text='Check out date', text_color='white', font=('Inria Sans', 15, 'bold'))
                checkout_fr = ctk.CTkFrame(dates, fg_color='white', height=35)
                checkout_en = ctk.CTkEntry(checkout_fr, font=('Open Sans', 12, 'normal'), border_width=0, fg_color='transparent', textvariable=self.checkout_var)
                checkout_img = tk.Label(checkout_fr, text='', image=self.tkcalender, fg='#36454F')
                checkout_img.image = self.tkcalender
                payed = ctk.CTkCheckBox(dates, text='Room fee payed',text_color='white',font=('Open Sans',15), border_color='#05B9C5',border_width=1, hover_color='#34c4cf',variable=self.payed_var)
                
                def date_valid():
                    today_date = datetime.today().date()
                    if self.checkin_var.get() < str(today_date):
                        checkin_img.configure(image=self.tkred_calender)
                    if self.checkout_var.get() < self.checkin_var.get():
                        checkout_img.configure(image=self.tkred_calender)
                    else:
                        if self.payed_var.get() == 0:
                            messagebox.showinfo('Info','money not payed')
                        else:
                            checkin_img.configure(image=self.tkcalender)
                            checkout_img.configure(image=self.tkcalender)
                            save_data()
                self.book_btn = ctk.CTkButton(dates, text='Book the room', border_width=1, border_color='#00FF00', fg_color='transparent', hover_color='#00FF00',font=('Inria Sans',20,'bold'), command=date_valid)
                # placement
                dates.place(relx=0.5, rely=0.8, anchor='center')
                checkin.grid(row=0, column=0, sticky='w', pady=(10,5), padx=(20,10))
                checkin_fr.grid(row=1, column=0, sticky='w', padx=(20,10))
                checkin_en.pack(side='left', expand=True, fill='both', padx=5, pady=2)
                checkin_img.pack(side='left', padx=(0,5))
                checkout.grid(row=0, column=1, sticky='w', pady=(10,5), padx=(5,20))
                checkout_fr.grid(row=1, column=1, sticky='news', padx=(5,20))
                checkout_en.pack(side='left', expand=True, fill='both', padx=5, pady=2)
                checkout_img.pack(side='left', padx=(0,5))
                payed.grid(row=2, column=0, columnspan=2, sticky='w',padx=20, pady=10)
                self.book_btn.grid(row=3, column=0, columnspan=2, sticky='news',padx=20, pady=5)
                cursor.execute('SELECT price_per_night FROM rooms WHERE room_id = ?',(selected,))
                the_price = cursor.fetchone()
                self.price = the_price
            self.checkin_var.trace_add('write', self.booked_days)
            self.checkout_var.trace_add('write', self.booked_days)
        
        def booked_days(self, *args):
            in_date = datetime.strptime(self.checkin_var.get(), '%Y-%m-%d')
            out_date = datetime.strptime(self.checkout_var.get(), '%Y-%m-%d')
            in_date and out_date
            no_of_days = out_date - in_date
            no_of_days = int(no_of_days.days)
            booking_price = no_of_days * int(self.price[0])
            # self.book_btn.configure(text=f'${booking_price}')
            if no_of_days > 1:
                self.book_btn.configure(text=f'Book for {no_of_days} nights')
            else:
                self.book_btn.configure(text=f'Book for one night')
           
        def customers(self):
            customers = ctk.CTkFrame(self, corner_radius=0, fg_color='#E5F5E6')
            customers_info = ctk.CTkScrollableFrame(customers, corner_radius=0, fg_color='transparent', width=800, scrollbar_button_color='#36454F', scrollbar_button_hover_color='#4c5b66',height=300)#, width=800)
            cursor.execute('SELECT * FROM clients')
            all_clients = cursor.fetchall()
            headers = ctk.CTkFrame(customers, fg_color='transparent', height=35, width=800)
            names_column = ctk.CTkLabel(headers,text='Name',text_color='#36454F', font=('Inria Sans',20,'bold'))
            names_column.place(relx=0.0555, y=6, anchor='nw') 
            email_column = ctk.CTkLabel(headers,text='Email',text_color='#36454F', font=('Inria Sans',20,'bold')) 
            email_column.place(relx=0.48, y=6, anchor='nw') 
            room_column = ctk.CTkLabel(headers,text='Room',text_color='#36454F', font=('Inria Sans',20,'bold')) 
            room_column.place(relx=0.86, y=6, anchor='nw') 
            ind = 0
            x = 0
            y =50
            for i in range(len(all_clients)):
                person = all_clients[ind]
                person_name = person[0]
                person_email = person[1]
                person_phone = person[2]
                person_room = person[3]
                person_in_date = person[4]
                person_out_date = person[5]
                person_frame = ctk.CTkFrame(customers_info, fg_color='transparent', width=800, height=35)
                person_frame.pack(expand=True, fill='x', padx=10, pady=2)
                selected = ctk.CTkRadioButton(person_frame, text='', border_color='#05B9C5', hover_color='#34c4cf', radiobutton_height=15,radiobutton_width=15, corner_radius=5, border_width_unchecked=1, border_width_checked=2, fg_color='#36454F', value=person_name, variable=self.to_edit, command=self.client_edit)
                selected.place(relx=0.0, y=6, anchor='nw')
                person_name_lb = ctk.CTkLabel(person_frame, text=person_name,text_color='#36454F', font=('Open Sans',15,'bold'))
                person_name_lb.place(relx=0.05, y=6, anchor='nw')
                person_email_lb = ctk.CTkLabel(person_frame, text=person_email, text_color='#36454F', font=('Open Sans',15))
                person_email_lb.place(relx=0.49, y=6, anchor='nw')
                person_room_lb = ctk.CTkLabel(person_frame, text=person_room, text_color='#36454F', font=('Open Sans',15))
                person_room_lb.place(relx=0.89, y=6, anchor='nw')
                ind += 1
                y += 40

            # edit customers grid preparaion
            edit_customer = ctk.CTkFrame(customers, corner_radius=0, fg_color='transparent', width=800)
            edit_customer.columnconfigure((0,1,2,3),weight=1)
            edit_customer.rowconfigure((0,1,2,3,4,5,6,7),weight=1)
            line = ttk.Separator(edit_customer, orient='horizontal')
            edit_room_lb = ctk.CTkLabel(edit_customer, textvariable=self.edit_room,text_color='#05B9C5', font=('Inria Sans', 25, 'bold'))
            edit_name_lb = ctk.CTkLabel(edit_customer, text='Edit name',text_color='#36454F', font=('Inria Sans', 18, 'bold'))
            edit_name = ctk.CTkEntry(edit_customer, fg_color='white', height=38,border_color='#36454F', font=('Open Sans', 18, 'normal'),border_width=1, textvariable=self.edit_name)
            edit_email_lb = ctk.CTkLabel(edit_customer, text='Edit email',text_color='#36454F', font=('Inria Sans', 18, 'bold'))
            edit_email = ctk.CTkEntry(edit_customer, fg_color='white', height=38,border_color='#36454F', font=('Open Sans', 18, 'normal'),border_width=1, textvariable=self.edit_email)
            edit_phone_lb = ctk.CTkLabel(edit_customer, text='Edit phone number',text_color='#36454F', font=('Inria Sans', 18, 'bold'))
            edit_phone = ctk.CTkEntry(edit_customer, fg_color='white', height=38,border_color='#36454F', font=('Open Sans', 18, 'normal'),border_width=1, textvariable=self.edit_phone)
            edit_in_date_lb = ctk.CTkLabel(edit_customer, text='Edit check in date',text_color='#36454F', font=('Inria Sans', 18, 'bold'))
            edit_in_date = ctk.CTkEntry(edit_customer, fg_color='white', height=38,border_color='#36454F', font=('Open Sans', 18, 'normal'),border_width=1, textvariable=self.edit_in_date)
            edit_out_date_lb = ctk.CTkLabel(edit_customer, text='Edit check out date',text_color='#36454F', font=('Inria Sans', 18, 'bold'))
            edit_out_date = ctk.CTkEntry(edit_customer, fg_color='white', height=38,border_color='#36454F', font=('Open Sans', 18, 'normal'),border_width=1, textvariable=self.edit_out_date)
            buttons = ctk.CTkFrame(edit_customer, fg_color='transparent')
            update_button = ctk.CTkButton(buttons, text='Update customer', width=250, text_color='white', fg_color='#05B9C5',hover_color='#34c4cf',font=('Inria Sans',20,'bold'), command=lambda:self.edited(self.to_edit.get(),1))
            remove_button = ctk.CTkButton(buttons, text='Remove customer', width=250, text_color='white', fg_color='#05B9C5',hover_color='#34c4cf',font=('Inria Sans',20,'bold'), command=lambda:self.edited(self.to_edit.get(),2))
            clear_button = ctk.CTkButton(buttons, text='Clear form', width=250, text_color='white', fg_color='#05B9C5',hover_color='#34c4cf',font=('Inria Sans',20,'bold'), command=lambda:self.edited(self.to_edit.get(),3))
            
            # placement
            customers.grid(row=0, column=1, sticky='news')
            headers.grid(row=0, column=0, padx=20,pady=10,sticky='we')
            customers_info.grid(row=1, column=0, padx=20,sticky='news')
            edit_customer.grid(row=2, column=0, padx=20, sticky='news')
            line.grid(row=0, column=0, columnspan=4, sticky='we')
            edit_room_lb.grid(row=1, column=0, columnspan=4, padx=20, pady=(10,20))
            edit_name_lb.grid(row=2, column=0, sticky='w', padx=(10,5), pady=(10,5))
            edit_name.grid(row=2, column=1, columnspan=3, sticky='we', padx=(0,10))
            edit_email_lb.grid(row=3, column=0, sticky='w', padx=(10,5), pady=(10,5))
            edit_email.grid(row=3, column=1, columnspan=3, sticky='we', padx=(0,10))
            edit_phone_lb.grid(row=4, column=0, sticky='w', padx=(10,5), pady=(10,5))
            edit_phone.grid(row=4, column=1, columnspan=3, sticky='we', padx=(0,10))
            edit_in_date_lb.grid(row=5, column=0, sticky='w', padx=(10,5),pady=(10,5))
            edit_in_date.grid(row=5, column=1, columnspan=3, sticky='we', padx=(0,10))
            edit_out_date_lb.grid(row=6, column=0, sticky='w', padx=(10,5), pady=(10,5))
            edit_out_date.grid(row=6, column=1, columnspan=3, sticky='we', padx=(0,10))
            buttons.grid(row=7, column=0, columnspan=4, pady=(50,20), padx=30)
            update_button.pack(side='left', expand=True, fill='both',padx=(10,20), ipady=6)
            remove_button.pack(side='left', expand=True, fill='both',padx=(10,20), ipady=6)
            clear_button.pack(side='left', expand=True, fill='both',padx=(10,20), ipady=6)
        
        def client_edit(self):
            client_to_edit = self.to_edit.get()
            # print(client_to_edit)
            cursor.execute('SELECT * FROM clients WHERE name=?',(client_to_edit,))
            client_to_edit_info = cursor.fetchone()
            self.edit_name.set(client_to_edit_info[0])
            self.edit_email.set(client_to_edit_info[1])
            self.edit_phone.set(client_to_edit_info[2])
            self.edit_room.set(client_to_edit_info[3])
            self.edit_in_date.set(client_to_edit_info[4])
            self.edit_out_date.set(client_to_edit_info[5])
            self.oringinal_in_date = client_to_edit_info[4]

        def edited(self, client, btn):
            edit_name = self.edit_name.get()
            edit_email = self.edit_email.get()
            edit_phone = self.edit_phone.get()
            edit_in_date = self.edit_in_date.get()
            edit_out_date = self.edit_out_date.get()
            
            cursor.execute('SELECT room FROM clients WHERE name=?',(client,))
            the_unoccupied_room = cursor.fetchone()
            the_unoccupied_room_stringed = ''
            for i in str(the_unoccupied_room):
                if i.isdigit():
                    the_unoccupied_room_stringed += i
                else:
                    pass
            if self.to_edit.get() == '0':
                messagebox.showerror('ERROR','No client were selected')
            else:
                if btn == 1:
                    today_date = datetime.today().date()
                    today_date = str(today_date)
                    if len(edit_name) == 0 or len(edit_email) == 0 or len(edit_phone) == 0 or len(edit_in_date) == 0 or len(edit_out_date) == 0:
                        messagebox.showerror('ERROR','fill all the data')
                    else:
                        if edit_in_date >= self.oringinal_in_date and edit_out_date >= edit_in_date and edit_email.endswith('@gmail.com') or edit_email.endswith('@hotmail.com'):
                            cursor.execute('UPDATE clients SET name=?, email=?, phone=?, check_in_date=?, check_out_date=? WHERE name=?',(edit_name, edit_email, edit_phone, edit_in_date, edit_out_date , client))
                            self.to_edit.set(0)
                            self.edit_room.set('')
                            self.edit_name.set('')
                            self.edit_email.set('')
                            self.edit_phone.set('')
                            self.edit_in_date.set('')
                            self.edit_out_date.set('')
                            self.customers()
                        else:
                            messagebox.showwarning('WARNING','something went wrong')
                elif btn == 2:
                    today_date = datetime.today().date()
                    today_date = str(today_date)
                    cursor.execute('SELECT * FROM clients WHERE name=?',(client,))
                    dep_info = cursor.fetchone()

                    cursor.execute('INSERT INTO departures (name, email, phone, room, check_in_date, check_out_date) VALUES(?, ?, ?, ?, ?, ?)',(dep_info[0], dep_info[1], dep_info[2], dep_info[3], dep_info[4], dep_info[5]))
                    cursor.execute('UPDATE departures SET check_out_date=? WHERE name=?',(today_date,dep_info[0]))
                    cursor.execute('UPDATE rooms SET occupied=0 WHERE room_no=?',(the_unoccupied_room_stringed,))
                    cursor.execute('DELETE FROM clients WHERE name=?',(client,))
                    self.to_edit.set(0)
                    self.edit_room.set('')
                    self.edit_name.set('')
                    self.edit_email.set('')
                    self.edit_phone.set('')
                    self.edit_in_date.set('')
                    self.edit_out_date.set('')
                    self.customers()
                else:
                    self.to_edit.set(0)
                    self.edit_room.set('')
                    self.edit_name.set('')
                    self.edit_email.set('')
                    self.edit_phone.set('')
                    self.edit_in_date.set('')
                    self.edit_out_date.set('')
            conn.commit()

        def logout_frame(self):
            logout = ctk.CTkFrame(self, corner_radius=0, fg_color='#E5F5E6')
            lg_frame = ctk.CTkFrame(logout, fg_color='#36454F')
            sure = ctk.CTkLabel(lg_frame, text='Are you sure?', font=('Inria Sans', 30, 'bold'), text_color='#FED4D6')
            buttons = ctk.CTkFrame(lg_frame, fg_color='transparent')
            no_btn = ctk.CTkButton(buttons, text='No', fg_color='#05B9C5', text_color='white', font=('Inria Sans', 20, 'bold'), hover_color='#34c4cf', command=lambda:self.logedout(2))
            yes_btn = ctk.CTkButton(buttons, text='Yes', fg_color='#05B9C5', text_color='white', font=('Inria Sans', 20, 'bold'), hover_color='#34c4cf', command=lambda:self.logedout(1))

            logout.grid(row=0, column=1, sticky='news', pady=10)
            lg_frame.place(relx=0.5, rely=0.5, anchor='center')
            sure.pack(pady=(20,5))
            buttons.pack(pady=30, padx=20)
            no_btn.pack(side='left', padx=(0,10))
            yes_btn.pack(side='left')
        
        def departures_frame(self):
            dep_frame = ctk.CTkFrame(self, corner_radius=0, fg_color='#E5F5E6', width=800, height=800)
            dep_frame.grid(row=0, column=1, sticky='news')
            dep_info = ctk.CTkScrollableFrame(dep_frame, corner_radius=0, fg_color='#E5F5E6', width=900, height=350)
            dep_info.grid(row=0, column=1, sticky='news')
            cursor.execute('SELECT * FROM departures')
            depatures = cursor.fetchall()


            headers = ctk.CTkFrame(dep_info, fg_color='transparent', height=35, width=800)
            headers.pack(expand=True, fill='x', pady=10)
            names_column = ctk.CTkLabel(headers,text='Name',text_color='#36454F', font=('Inria Sans',20,'bold'))
            names_column.place(x=60, y=10, anchor='nw') 
            room_column = ctk.CTkLabel(headers,text='Room',text_color='#36454F', font=('Inria Sans',20,'bold')) 
            room_column.place(x=450, y=10, anchor='nw') 
            outdate_column = ctk.CTkLabel(headers,text='checked out',text_color='#36454F', font=('Inria Sans',20,'bold')) 
            outdate_column.place(x=750, y=10, anchor='nw') 
            for i in depatures:
                name = i[0]
                phone = i[1]
                email = i[2]
                room = i[3]
                indate = i[4]
                outdate = i[5]
                person_frame = ctk.CTkFrame(dep_info, fg_color='transparent', width=800, height=35)
                person_frame.pack(expand=True, fill='x', padx=10, pady=2)
                selected = ctk.CTkRadioButton(person_frame, text='', border_color='#05B9C5', hover_color='#34c4cf', radiobutton_height=15,radiobutton_width=15, corner_radius=5, border_width_unchecked=1, border_width_checked=2, fg_color='#36454F', value=name, variable=self.to_edit, command=self.dep_compelete_info)
                selected.place(x=10, y=10, anchor='nw')
                person_name_lb = ctk.CTkLabel(person_frame, text=name,text_color='#36454F', font=('Open Sans',15,'bold'))
                person_name_lb.place(x=50, y=10, anchor='nw')
                person_room_lb = ctk.CTkLabel(person_frame, text=room, text_color='#36454F', font=('Open Sans',15))
                person_room_lb.place(x=440, y=10, anchor='nw')
                person_outdate_lb = ctk.CTkLabel(person_frame, text=outdate, text_color='#FF0000', font=('Open Sans',15))
                person_outdate_lb.place(x=740, y=10, anchor='nw')

            # placements
            edit_customer = ctk.CTkFrame(dep_frame, corner_radius=0, fg_color='transparent', width=800)
            edit_customer.columnconfigure((0,1,2,3),weight=1)
            edit_customer.rowconfigure((0,1,2,3,4,5,6,7,8),weight=1)
            line = ttk.Separator(edit_customer, orient='horizontal')
            dep_info_lb = ctk.CTkLabel(edit_customer, text='departure\'s information',text_color='#05B9C5', font=('Inria Sans', 30, 'bold'))
            name_lb = ctk.CTkLabel(edit_customer, text='name',text_color='#36454F', font=('Inria Sans', 18, 'bold'))
            name = ctk.CTkLabel(edit_customer, height=38, font=('Open Sans', 18, 'normal'), textvariable=self.edit_name)
            email_lb = ctk.CTkLabel(edit_customer, text='email',text_color='#36454F', font=('Inria Sans', 18, 'bold'))
            email = ctk.CTkLabel(edit_customer, height=38, font=('Open Sans', 18, 'normal'), textvariable=self.edit_email)
            phone_lb = ctk.CTkLabel(edit_customer, text='phone number',text_color='#36454F', font=('Inria Sans', 18, 'bold'))
            phone = ctk.CTkLabel(edit_customer, height=38, font=('Open Sans', 18, 'normal'), textvariable=self.edit_phone)
            room_lb = ctk.CTkLabel(edit_customer, text='room',text_color='#36454F', font=('Inria Sans', 18, 'bold'))
            room = ctk.CTkLabel(edit_customer, height=38, font=('Open Sans', 18, 'normal'), textvariable=self.edit_room)
            in_date_lb = ctk.CTkLabel(edit_customer, text='checked in',text_color='#36454F', font=('Inria Sans', 18, 'bold'))
            in_date = ctk.CTkLabel(edit_customer, height=38, font=('Open Sans', 18, 'normal'), textvariable=self.edit_in_date)
            out_date_lb = ctk.CTkLabel(edit_customer, text='Edit checked out',text_color='#36454F', font=('Inria Sans', 18, 'bold'))
            out_date = ctk.CTkLabel(edit_customer, height=38, font=('Open Sans', 18, 'normal'), textvariable=self.edit_out_date)
            buttons = ctk.CTkFrame(edit_customer, fg_color='transparent')
            remove_button = ctk.CTkButton(buttons, text='Remove', fg_color='#05B9C5', hover_color='#34c4cf',width=300, font=('Inria Sans',20,'bold'), command=lambda:self.dep_options(self.to_edit.get(),1))
            clear_button = ctk.CTkButton(buttons, text='Clear form', fg_color='#05B9C5',hover_color='#34c4cf',width=300, font=('Inria Sans',20,'bold'), command=lambda:self.dep_options(self.to_edit.get(),2))
            
            # placement
            edit_customer.grid(row=1, column=1, padx=20, sticky='news')
            line.grid(row=0, column=0, columnspan=4, sticky='we')
            dep_info_lb.grid(row=1, column=0, columnspan=4, padx=20, pady=(10,20))
            name_lb.grid(row=2, column=0, sticky='w', padx=(10,5), pady=(10,5))
            name.grid(row=2, column=1, columnspan=3, sticky='w', padx=(0,10))
            email_lb.grid(row=3, column=0, sticky='w', padx=(10,5), pady=(10,5))
            email.grid(row=3, column=1, columnspan=3, sticky='w', padx=(0,10))
            phone_lb.grid(row=4, column=0, sticky='w', padx=(10,5), pady=(10,5))
            phone.grid(row=4, column=1, columnspan=3, sticky='w', padx=(0,10))
            room_lb.grid(row=5, column=0, sticky='w', padx=(10,5), pady=(10,5))
            room.grid(row=5, column=1, columnspan=3, sticky='w', padx=(0,10))
            in_date_lb.grid(row=6, column=0, sticky='w', padx=(10,5),pady=(10,5))
            in_date.grid(row=6, column=1, columnspan=3, sticky='w', padx=(0,10))
            out_date_lb.grid(row=7, column=0, sticky='w', padx=(10,5), pady=(10,5))
            out_date.grid(row=7, column=1, columnspan=3, sticky='w', padx=(0,10))
            buttons.grid(row=8, column=0, columnspan=4, pady=(50,20), padx=30)
            remove_button.pack(side='left', expand=True, fill='both',padx=(10,20), ipady=6)
            clear_button.pack(side='left', expand=True, fill='both',padx=(10,20), ipady=6)
        
        def dep_compelete_info(self):
            selected_dep = self.to_edit.get()
            cursor.execute('SELECT * FROM departures WHERE name=?',(selected_dep,))
            client_to_edit_info = cursor.fetchone()
            self.edit_name.set(client_to_edit_info[0])
            self.edit_email.set(client_to_edit_info[1])
            self.edit_phone.set(client_to_edit_info[2])
            self.edit_room.set(client_to_edit_info[3])
            self.edit_in_date.set(client_to_edit_info[4])
            self.edit_out_date.set(client_to_edit_info[5])
            self.oringinal_in_date = client_to_edit_info[4]
        
        def dep_options(self, dep, option):
            if self.to_edit.get() == '0':
                messagebox.showerror('Error', 'select first')
            else:
                if option == 1:
                    cursor.execute('DELETE FROM departures WHERE name=?',(dep,))
                    self.to_edit.set(0)
                    self.edit_room.set('')
                    self.edit_name.set('')
                    self.edit_email.set('')
                    self.edit_phone.set('')
                    self.edit_in_date.set('')
                    self.edit_out_date.set('')
                    self.departures_frame()
                else:
                    self.to_edit.set(0)
                    self.edit_room.set('')
                    self.edit_name.set('')
                    self.edit_email.set('')
                    self.edit_phone.set('')
                    self.edit_in_date.set('')
                    self.edit_out_date.set('')
                conn.commit()
    
    hotel = hotel()
    hotel.mainloop()
main()