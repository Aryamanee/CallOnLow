"""
An app that constantly polls dexcom's share servers and makes a call using ifttt if a certain threshold is met
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import pydexcom
import json
import requests

class CallOnLow(toga.App):
    def startup(self):
        try:
            prefsfile = open("prefs.json", "r")
        except FileNotFoundError:
            prefsfile = open("prefs.json", "w+")
            prefsfile.write("{}")
            prefsfile.close()
            prefsfile = open("prefs.json", "r")
        self.prefs = json.loads(prefsfile.read())
        prefsfile.close()

        try:
            self.username = str(self.prefs["username"])
            self.passsword = str(self.prefs["password"])
            self.ous = bool(self.prefs["ous"])
            pydexcom.Dexcom(self.username, self.passsword, self.ous)
            self.window = "MainUI"
        except:
            self.window = "Login"


        login_box = toga.Box(style=Pack(direction=COLUMN))

        self.user_enter = toga.TextInput(style=Pack(flex=1), placeholder="Username")

        user_box = toga.Box(style=Pack(direction=ROW, padding=5))
        user_box.add(self.user_enter)

        self.password_enter = toga.PasswordInput(style=Pack(flex=1), placeholder="Password")

        password_box = toga.Box(style=Pack(direction=ROW, padding=5))
        password_box.add(self.password_enter)

        self.us_enter = toga.Switch(style=Pack(flex=1), text="US Account")
        login_button = toga.Button(
            "Login",
            on_press=self.login,
            style=Pack(padding=5)
        )

        us_box = toga.Box(style=Pack(direction=ROW, padding=5))
        us_box.add(self.us_enter)

        login_box.add(user_box)
        login_box.add(password_box)
        login_box.add(us_box)
        login_box.add(login_button)

        main_box = toga.Box(style=Pack(direction=COLUMN))

        try:
            self. url = self.prefs["url"]
        except KeyError:
            self.url = "Url"

        self.url_enter = toga.TextInput(style=Pack(flex=1), placeholder=self.url)



        url_box = toga.Box(style=Pack(direction=ROW, padding=5))
        url_box.add(self.url_enter)

        url_button = toga.Button(
            "Set Url",
            on_press=self.set_url,
            style=Pack(padding=5)
        )

        test_call_button = toga.Button(
            "Test Call",
            on_press=self.test_call,
            style=Pack(padding=5)
        )
        main_box.add(url_box)
        main_box.add(url_button)
        main_box.add(test_call_button)

        self.main_window = toga.MainWindow(title=self.formal_name)
        if self.window == "MainUI":
            self.main_window.content = main_box
        else:
            self.main_window.content = login_box
        self.main_window.show()

    def login(self, widget):
        try:
            self.username = self.user_enter.value
            self.password = self.password_enter.value
            self.ous = not self.us_enter.value
            pydexcom.Dexcom(self.username, self.password, ous=self.ous)
            self.prefs["username"] = self.username
            self.prefs["password"] = self.password
            self.prefs["ous"] = self.ous
            prefsfile = open("prefs.json", "w+")
            prefsfile.write(json.dumps(self.prefs))
            prefsfile.close()
        except pydexcom.errors.AccountError:
            self.main_window.error_dialog(title = "Login Failed", message = "The Login Has Failed! Check Your Password!")
            self.user_enter.clear()
            self.password_enter.clear()
    def set_url(self, widget):
        self.url = self.url_enter.value
        self.prefs["url"] = self.url
        prefsfile = open("prefs.json", "w+")
        prefsfile.write(json.dumps(self.prefs))
        prefsfile.close()
    def call(self, body):
        try:
            requests.request(method="POST", json=body, url=self.url)
        except requests.HTTPError:
            print("Error while calling")
    def test_call(self, widget):
        dexcom = pydexcom.Dexcom(self.prefs["username"], self.prefs["password"], self.prefs["ous"])
        self.call({"This ":"is a test call by callonlow, the current reading is " + str(dexcom.get_latest_glucose_reading().mmol_l) + " milimols per litre."})
def main():
    return CallOnLow()
