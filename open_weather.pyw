import customtkinter as ctk
from CTkToolTip import *
from PIL import Image
import requests
from io import BytesIO
from ctypes import windll
import webbrowser
from settings import *

base_url = 'https://api.openweathermap.org/data/2.5/weather'
api_key = 'ed84f56e84468359766850e093de2612'

class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color = BG)

        self.title('')
        self.iconbitmap('images/empty.ico')
        ctk.set_appearance_mode('light')

        self.overrideredirect(True)
        self.focus_force()

        self.size = (350,550)
        self.center = self.calculate_center()
        self.geometry(f'{self.size[0]}x{self.size[1]}+{self.center[0]}+{self.center[1]}')

        self.load_images()
        self.create_main_menu()
        self.create_weather_frame()
        self.place_frame(self.main_menu)

        # self.after(10, lambda: self.set_appwindow(self))
        self.mainloop()

    def set_appwindow(self, window):

        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        # Magic
        hwnd = windll.user32.GetParent(window.winfo_id())
        stylew = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        stylew = stylew & ~WS_EX_TOOLWINDOW
        stylew = stylew | WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, stylew)
    
        window.wm_withdraw()
        window.after(10, lambda: window.wm_deiconify())  

    def get_window_pos(self, event):
        start_x = event.x
        start_y = event.y

        def move_window(event):
            self.geometry(f'+{event.x_root - start_x}+{event.y_root - start_y}')\
            
        self.move_frame_1.bind('<B1-Motion>', move_window)
        self.move_frame_2.bind('<B1-Motion>', move_window)

    def calculate_center(self):

        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()

        x = (width-self.size[0])//2
        y = (height-self.size[1]-10)//2

        return (x, y)

    def load_images(self):

        search = Image.open('images/search.png')
        self.search = ctk.CTkImage(search)

        missing_icon = Image.open('images/missing_icon.png')
        self.missing_icon = ctk.CTkImage(missing_icon)

        back_arrow = Image.open('images/back_arrow.png')
        self.back_arrow = ctk.CTkImage(back_arrow)

    def create_main_menu(self):

        self.main_menu = ctk.CTkFrame(self, fg_color = BG)

        self.move_frame_1 = ctk.CTkFrame(self.main_menu, fg_color = BG, corner_radius = 0)
        self.move_frame_1.place(relx = 0, rely = 0, relwidth = 1, relheight = 0.075)
        self.move_frame_1.bind('<Button-1>', self.get_window_pos)

        self.close_button = ctk.CTkButton(self.main_menu,
                                          text = '❌',
                                          font = ('Lato Black', 20),
                                          hover_color = '#BFDE52',
                                          text_color = L_GRAY,
                                          fg_color = BG,
                                          width = 40,
                                          height = 40,
                                          corner_radius = 0,
                                          command = lambda: self.destroy())
        self.close_button.place(relx = 1, rely = 0, anchor = 'ne')
        self.tooltip(self.close_button, 'Close')
        
        self.title1 = ctk.CTkLabel(self.main_menu,
                                  text = 'OPEN',
                                  font = ('Staatliches', 125),
                                  text_color = TITLE_L)
        self.title1.place(relx = 0.5, rely = 0.35, anchor = 'center')
        self.title2 = ctk.CTkLabel(self.main_menu,
                                  text = 'WEATHER',
                                  font = ('Staatliches', 67),
                                  text_color = TITLE_D)
        self.title2.place(relx = 0.5, rely = 0.51, anchor = 'center')

        self.location_entry = ctk.CTkEntry(self.main_menu,
                                           placeholder_text = 'Enter Location',
                                           font = ('Lato Black', 27),
                                           fg_color = FILL,
                                           text_color = WHITE,
                                           border_color = ACCENT,
                                           placeholder_text_color = WHITE)
        self.location_entry.place(relx = 0.5, rely = 0.65, anchor = 'center', relwidth = 0.7)
        self.location_entry.bind('<Return>', lambda e: self.get_weather())

        self.location_submit = ctk.CTkButton(self.main_menu,
                                             text = '',
                                             image = self.search,
                                             fg_color = ACCENT,
                                             hover_color = HOVER,
                                             width = 40,
                                             height = 40,
                                             corner_radius = 10,
                                             background_corner_colors = [ACCENT, BG, BG, ACCENT],
                                             command = lambda: self.get_weather())
        self.location_submit.place(relx = 0.85, rely = 0.65, anchor = 'e')
        self.tooltip(self.location_submit, 'Search')
        self.hover_bind(self.location_submit)

        self.website_info = ctk.CTkButton(self.main_menu,
                                         text = 'https://openweathermap.org',
                                         font = ('Staatliches', 25),
                                         text_color = '#AFCE42',
                                         hover = False,
                                         fg_color = BG,
                                         command = lambda: webbrowser.open('https://openweathermap.org'))
        self.website_info.place(relx = 0.5, rely = 0.95, anchor = 'center')
        self.tooltip(self.website_info, 'Website')

        self.info_label = ctk.CTkLabel(self.main_menu,
                                       text = '',
                                       font = ('Lato Black', 20),
                                       text_color = ACCENT)
        self.info_label.place(relx = 0.5, rely = 0.73, anchor = 'center')

    def create_weather_frame(self):

        self.weather_frame = ctk.CTkFrame(self, fg_color = BG)
        self.bind('<Escape>', lambda e: self.weather_frame.place_forget())

        self.move_frame_2 = ctk.CTkFrame(self.weather_frame, fg_color = BG, corner_radius = 0)
        self.move_frame_2.place(relx = 0, rely = 0, relwidth = 1, relheight = 0.075)
        self.move_frame_2.bind('<Button-1>', self.get_window_pos)

        self.close_button = ctk.CTkButton(self.weather_frame,
                                          text = '❌',
                                          font = ('Lato Black', 20),
                                          hover_color = '#BFDE52',
                                          text_color = L_GRAY,
                                          fg_color = BG,
                                          width = 40,
                                          height = 40,
                                          corner_radius = 0,
                                          command = lambda: self.destroy())
        self.close_button.place(relx = 1, rely = 0, anchor = 'ne')
        self.tooltip(self.close_button, 'Close')

        self.back_arrow = ctk.CTkButton(self.weather_frame,
                                          text = '',
                                          image = self.back_arrow,
                                          font = ('Lato Black', 20),
                                          hover_color = '#BFDE52',
                                          text_color = L_GRAY,
                                          fg_color = BG,
                                          width = 40,
                                          height = 40,
                                          corner_radius = 0,
                                          command = lambda: self.weather_frame.place_forget())
        self.back_arrow.place(relx = 0, rely = 0, anchor = 'nw')
        self.tooltip(self.back_arrow, 'Back')

        self.weather_frame.columnconfigure(0, weight = 1, uniform = 'A')
        self.weather_frame.rowconfigure(0, weight = 2, uniform = 'A')
        self.weather_frame.rowconfigure(1, weight = 10, uniform = 'A')
        self.weather_frame.rowconfigure(2, weight = 3, uniform = 'A')
        self.weather_frame.rowconfigure((3,4,5), weight = 2, uniform = 'A')
        self.weather_frame.rowconfigure(6, weight = 1, uniform = 'A')

        self.icon = self.missing_icon
        self.weather_icon = ctk.CTkLabel(self.weather_frame,
                                         text = '',
                                         image = self.icon,
                                         corner_radius = 15,
                                         fg_color = '#BFDE52')
        self.weather_icon.grid(row = 1, column = 0)

        self.weather_main_var = ctk.StringVar(value = 'ERROR')
        self.weather_main_label = ctk.CTkLabel(self.weather_frame,
                                               text = '',
                                               textvariable = self.weather_main_var,
                                               font = ('Lato Black', 55),
                                               text_color = TITLE_D)
        self.weather_main_label.grid(row = 2, column = 0)
        
        self.weather_description_var = ctk.StringVar(value = 'ERROR')
        self.weather_description_label = ctk.CTkLabel(self.weather_frame,
                                               text = '',
                                               textvariable = self.weather_description_var,
                                               font = ('Lato Black', 25),
                                               text_color = TITLE_L)
        self.weather_description_label.grid(row = 3, column = 0, sticky = 'n')
        
        self.weather_subframe = ctk.CTkFrame(self.weather_frame, fg_color = '#BFDE52')
        self.weather_subframe.grid(row = 4, column = 0, sticky = 'news', padx = 60)
        self.weather_subframe.columnconfigure((0,1), weight = 1, uniform = 'B')
        self.weather_subframe.rowconfigure(0, weight = 1, uniform = 'B')

        self.temp_var = ctk.StringVar(value = 'ERROR')
        self.temp_label = ctk.CTkLabel(self.weather_subframe,
                                               text = '',
                                               textvariable = self.temp_var,
                                               font = ('Lato Black', 35),
                                               text_color = NUMS)
        self.temp_label.grid(row = 0, column = 0)
        self.tooltip(self.temp_label, 'Temperature')

        self.humidity_var = ctk.StringVar(value = 'ERROR')
        self.humidity_label = ctk.CTkLabel(self.weather_subframe,
                                               text = '',
                                               textvariable = self.humidity_var,
                                               font = ('Lato Black', 35),
                                               text_color = NUMS)
        self.humidity_label.grid(row = 0, column = 1)
        self.tooltip(self.humidity_label, 'Humidity')
        
        self.location_var = ctk.StringVar(value = 'ERROR')
        self.location_label = ctk.CTkLabel(self.weather_frame,
                                           text = '',
                                           textvariable = self.location_var,
                                           font = ('Lato Black', 30),
                                           text_color = L_GRAY)
        self.location_label.grid(row = 5, column = 0, sticky = 's')

    def place_frame(self, frame):
        
        frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

    def get_weather(self):
        self.location = self.location_entry.get()
        if self.location:
            self.url = f'{base_url}?appid={api_key}&q={self.location}'

            self.info_label.configure(text = '')

            try:
                response = requests.get(self.url)
                
                if response.status_code == 200:
                    data = response.json()
                    self.location_entry.delete(0,100)
                    self.location = data['name']
                    self.weather_main = data['weather'][0]['main']
                    self.weather_description = data['weather'][0]['description'].title()
                    self.temp = str(int(data['main']['temp']-273))+'°C'
                    self.humidity = str(data['main']['humidity'])+'%'
                    self.icon_url = f'https://openweathermap.org/img/wn/{data["weather"][0]["icon"]}@4x.png'
                    
                    try:
                        response = requests.get(self.icon_url)
                        image = Image.open(BytesIO(response.content))
                        self.icon = ctk.CTkImage(image, size = (250, 250))
                    except:
                        self.icon = self.missing_icon

                    self.update_weather()
                    self.place_frame(self.weather_frame)
                elif response.status_code in (400, 404):
                    self.info_label.configure(text = 'Location Not Found!')
                else:
                    print(response.status_code)
            except:
                self.info_label.configure(text = 'Network Error!')
        else:
            self.info_label.configure(text = 'Enter A Location!')

    def update_weather(self):

        self.location_var.set(self.location)
        self.weather_main_var.set(self.weather_main)
        self.weather_description_var.set(self.weather_description)
        self.temp_var.set(self.temp)
        self.humidity_var.set(self.humidity)
        self.weather_icon.configure(image = self.icon)

    def hover_bind(self, widget):
        widget.bind('<Enter>', lambda e: widget.configure(fg_color = HOVER))
        widget.bind('<Leave>', lambda e: widget.configure(fg_color = ACCENT))
        widget.bind('<Enter>', lambda e: widget.configure(background_corner_colors = [HOVER, BG, BG, HOVER]))
        widget.bind('<Leave>', lambda e: widget.configure(background_corner_colors = [ACCENT, BG, BG, ACCENT]))

    def tooltip(self, widget, message):
        CTkToolTip(widget,
                   message = message,
                   delay = 0,
                   corner_radius = 5,
                   bg_color = WHITE,
                   text_color = BLACK,
                   border_width = 1,
                   border_color = BLACK,
                   x_offset = 15,
                   alpha = 0.9,
                   font = ('Lato', 12))

WeatherApp()