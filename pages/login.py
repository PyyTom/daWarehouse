import sqlite3
from flet import *
from flet_route import Params,Basket
def Login(page:Page,params:Params,basket:Basket):
    def login(e):
        if dd_user.value=='' or t_pw.value=='':dialog.title=Text('FIELDS MISSING')
        else:
            db=sqlite3.connect('db.db')
            if db.execute('select PASSWORD from USERS where USER=?',(dd_user.value,)).fetchone()[0]!=t_pw.value:dialog.title=Text('PASSWORD WRONG')
            else:
                db.execute('update USERS set ON_AIR="v" where USER=?',(dd_user.value,))
                db.commit()
                dialog.title=Text('WELCOME BACK, '+dd_user.value)
                dialog.on_dismiss=lambda e:page.go('/home')
            db.close()
        dialog.open=True
        page.update()
    def register(e):
        if t_user.value=='' or t_pw.value=='' or t_re_pw.value=='':dialog.title=Text('FIELDS MISSING')
        elif t_pw.value!=t_re_pw.value:dialog.title=Text("PASSWORDS DON'T MATCH")
        else:
            db=sqlite3.connect('db.db')
            db.execute('insert into USERS values(?,?,?)',((t_user.value).upper(),t_re_pw.value,'',))
            db.commit()
            db.close()
            dialog.title=Text('WELCOME, '+t_user.value)
        dialog.open=True
        page.update()
    def action(e):
        dd_user.disabled,t_user.disabled,t_pw.disabled,t_re_pw.disabled,b_login.disabled,b_register.disabled =True,True,True,True,True,True
        dd_user.value,t_user.value,t_pw.value,t_re_pw.value='','','',''
        if radio.value == 'login':
            dd_user.disabled = False
            t_pw.disabled=False
            b_login.disabled=False
            db=sqlite3.connect('db.db')
            dd_user.options=[dropdown.Option(user[0]) for user in db.execute('select USER from USERS').fetchall()]
            db.close()
        if radio.value == 'register':
            t_user.disabled = False
            t_pw.disabled=False
            t_re_pw.disabled = False
            b_register.disabled=False
        page.update()
    db = sqlite3.connect('db.db')
    db.execute('update USERS set ON_AIR="" where ON_AIR="v"')
    db.commit()
    db.close()
    dialog=AlertDialog()
    page.dialog=dialog
    radio=RadioGroup(content=Row([Radio(value='login',label='LOGIN'),Radio(value='register',label='REGISTER')]),on_change=action)
    dd_user = Dropdown(label='USERNAME')
    t_user = TextField(label='USERNAME')
    t_pw = TextField(label='PASSWORD',password=True,can_reveal_password=True)
    t_re_pw = TextField(label='CONFIRM PASSWORD',password=True,can_reveal_password=True)
    b_login = ElevatedButton('LOGIN', on_click=login)
    b_register = ElevatedButton('REGISTER', on_click=register)
    return View('/',controls=[Row([IconButton(on_click=lambda _:page.window_destroy(),icon=icons.EXIT_TO_APP_OUTLINED,icon_size=50,icon_color='red')],alignment=MainAxisAlignment.END),
                              Row(controls=[Column(controls=[Row([radio],alignment=MainAxisAlignment.CENTER),
                                                             dd_user,t_user,t_pw,t_re_pw,
                                                             Row([b_login,b_register],alignment=MainAxisAlignment.CENTER)])],
                              alignment=MainAxisAlignment.CENTER)])