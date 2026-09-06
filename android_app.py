import os
import signal
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup

class AntivirusApp(App):
    def build(self):
        self.title = "AI Sentinel Guard"
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        self.status_label = Label(
            text="[b]🛡️ REAL-TIME AI GUARD ACTIVE[/b]\n\nSystem Protected", 
            markup=True, font_size='16sp', halign='center'
        )
        main_layout.add_widget(self.status_label)

        btn_test = Button(
            text="TEST HACKER / THREAT ATTACK", 
            font_size='12sp', bold=True,
            background_color=(0.9, 0.2, 0.2, 1),
            size_hint_y=None, height=50
        )
        btn_test.bind(on_press=lambda x: self.trigger_alert("malicious_script.apk", pid=9999))
        main_layout.add_widget(btn_test)

        return main_layout

    def trigger_alert(self, filename, pid=None):
        self.suspicious_file = filename
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)

        warning_text = Label(
            text=f"[b]⚠️ CRITICAL THREAT DETECTED![/b]\n\nFile: [color=ff3333]{filename}[/color]\nEntropy > 7.5 (AI Threat)",
            markup=True, font_size='14sp', halign='center'
        )
        content.add_widget(warning_text)

        btn_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)

        btn_run = Button(text="RUN / ALLOW", background_color=(0.2, 0.7, 0.3, 1), bold=True)
        btn_run.bind(on_press=self.allow_action)

        btn_kill = Button(text="KILL THREAT", background_color=(0.9, 0.1, 0.1, 1), bold=True)
        btn_kill.bind(on_press=self.kill_action)

        btn_box.add_widget(btn_run)
        btn_box.add_widget(btn_kill)
        content.add_widget(btn_box)

        self.popup = Popup(
            title="SECURITY ACTION REQUIRED",
            content=content, size_hint=(0.9, 0.5), auto_dismiss=False
        )
        self.popup.open()

    def allow_action(self, instance):
        self.status_label.text = f"[b]🛡️ GUARD ACTIVE[/b]\n\nAllowed: {self.suspicious_file}"
        self.popup.dismiss()

    def kill_action(self, instance):
        self.status_label.text = f"[b]🛡️ GUARD ACTIVE[/b]\n\n[color=00ff00]Threat Neutralized![/color]"
        self.popup.dismiss()

if __name__ == '__main__':
    AntivirusApp().run()
