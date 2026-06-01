from nicegui import ui
with ui.column().classes('w-full h-full bg-pink-400'):
    ui.query('body').style('background-color: #ffb7ce')
ui.query("this is my border").classes('border-2 border-pink-500 p-4 rounded-lg')





ui.run()