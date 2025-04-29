from customtkinter import *
from PIL import Image
from tkinter import filedialog
import io
import base64


import socket, threading




class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.title("LogiTalk")
        self.geometry("800x600")
        self.label = None


        self.user_name = "Dmytro"


        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.animation_speed = -5
        self.btn = CTkButton(self, text="▶️", command=self.toggle_menu, width=30)  # ◀️
        self.btn.place(x=0, y=0)


        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)
        self.message_entry = CTkEntry(
            self, placeholder_text="Введіть повідомлення:", height=40
        )
        self.message_entry.place(x=0, y=0)
        self.send_button = CTkButton(
            self, text=">", width=50, height=40, command=self.send_message
        )
        self.send_button.place(x=0, y=0)


        self.open_img_btn = CTkButton(
            self, text="📁", width=50, height=40, command=self.open_img
        )
        self.open_img_btn.place(x=0, y=0)


        self.raw = None
        self.img_to_send = CTkLabel(self, text='', )
        self.img_to_send.bind("<Button-1>", lambda e: self.remove_img(e) )
        self.adaptive_ui()


        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(("6.tcp.eu.ngrok.io", 10763))  # замінимо на справжню адресу
            hello = f"TEXT@{self.user_name}@[SYSTEM] {self.user_name} підключився(лась) до чату!\n"


            self.socket.send(hello.encode("utf-8"))
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")


    def remove_img(self, event):
        self.img_to_send.place_forget()
        self.raw = None
        self.file_name = None
   
    def toggle_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.animation_speed *= -1
            self.btn.configure(text="▶️")
            self.show_menu()
        else:
            self.is_show_menu = True
            self.animation_speed *= -1
            self.btn.configure(text="◀️")
            self.show_menu()


            self.label = CTkLabel(self.menu_frame, text="Ім'я")
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack()


    def show_menu(self):
        self.menu_frame.configure(
            width=self.menu_frame.winfo_width() + self.animation_speed
        )
        self.btn.configure(width=self.menu_frame.winfo_width())
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)


            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()


    def adaptive_ui(self):
        window_width = self.winfo_width()
        window_height = self.winfo_height()


        self.menu_frame.configure(height=window_height)
        self.chat_field.place(x=self.menu_frame.winfo_width())
        if not self.raw:
            self.chat_field.configure(
            width=window_width - self.menu_frame.winfo_width() - 20,
            height=window_height - 40,
        )
        if self.raw:
            self.chat_field.configure(
                width=window_width - self.menu_frame.winfo_width() - 20,
                height=window_height - 40 -100,
            )
            self.img_to_send.configure(image=CTkImage(Image.open(self.file_name), size=(100, 100)))
            self.img_to_send.place(x=self.chat_field.winfo_x()+20, y=self.message_entry.winfo_y()-100)
        self.send_button.place(x=window_width - 50, y=window_height - 40)
        self.message_entry.place(
            x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y()
        )
        self.message_entry.configure(
            width=window_width
            - self.menu_frame.winfo_width()
            - self.send_button.winfo_width()
            - self.open_img_btn.winfo_width()
        )


        self.open_img_btn.place(x=window_width - 105, y=self.send_button.winfo_y())


        self.after(10, self.adaptive_ui)


    def add_message(self, message, img=None):
        message_frame = CTkFrame(self.chat_field, fg_color="darkcyan")
        message_frame.pack(pady=5, anchor="w")


        w_size = self.winfo_width() - self.menu_frame.winfo_width() - 40


        if not img:
            CTkLabel(
                message_frame,
                text=message,
                wraplength=w_size,
                text_color="white",
                justify="left",
            ).pack(pady=5, padx=10)
        else:
            CTkLabel(
                message_frame,
                text=message,
                wraplength=w_size,
                text_color="white",
                justify="left",
                image=img,
                compound="top",
            ).pack(pady=5, padx=10)


    def send_message(self):
        message = self.message_entry.get()
        if message and not self.raw:
            self.add_message(f"{self.user_name}: {message}")
            data = f"TEXT@{self.user_name}@{message}\n"
            try:
                self.socket.sendall(data.encode())
            except:
                pass
        elif self.raw:
            b64_data = base64.b64encode(self.raw).decode()
            data = f"IMAGE@{self.user_name}@{message}@{b64_data}\n"
            self.socket.sendall(data.encode())
            self.add_message(f"{message}", self.resize_image(Image.open(self.file_name)))
            self.img_to_send.place_forget()
            self.raw = None
            self.file_name = None
        self.message_entry.delete(0, "end")


    def open_img(self):
        self.file_name = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]
        )
        if not self.file_name:
            return
        try:
            with open(self.file_name, "rb") as f:
                self.raw = f.read()
            return self.raw
           
        except Exception as e:
            self.add_message(f"Не вдалося надіслати зображення: {e}")


    def receive_messages(self):
        buffer = ""
        while True:
            try:
                chunk = self.socket.recv(16384)
                buffer += chunk.decode("utf-8", errors="ignore")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.socket.close()


    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        message_type = parts[0]
        if message_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif message_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                message = parts[2]
                b64_data = parts[3]
                try:
                    img_data = base64.b64decode(b64_data)
                    img = Image.open(io.BytesIO(img_data))
                    img = self.resize_image(img)
                    self.add_message(f'{author}: {message}', img=img)
                except Exception as e:
                    self.add_message(f"Помилка відображення зображення: {e}")
            else:
                self.add_message(line)


    def resize_image(self, image):
        width, height = image.size
        max_width = 400
       
        if width <= max_width:
            return CTkImage(image, size=(width, height))
       
        new_height = int(height * max_width / width)
       
        return CTkImage(image, size=(max_width, new_height))
   
window = MainWindow()
window.mainloop()