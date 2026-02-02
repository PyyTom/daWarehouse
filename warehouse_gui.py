import sqlite3,datetime
db=sqlite3.connect('db.db')
db.execute('create table if not exists PRODUCTS(SUPPLIER,NAME,PRICE float,STOCK integer,POSITION)')
db.execute('create table if not exists SUPPLIERS(NAME,DOC,ADDRESS,PHONE,MAIL)')
db.execute('create table if not exists CLIENTS(NAME,DOC,ADDRESS,PHONE,MAIL)')
db.execute('create table if not exists SALES(DATE,CLIENT,PRODUCT,PRICE float,QUANTITY integer)')
db.execute('create table if not exists PURCHASES(DATE,SUPPLIER,PRODUCT,PRICE float,QUANTITY integer)')
db.close()
tables=['PRODUCTS','SUPPLIERS','CLIENTS','SALES','PURCHASES']
from flet import app,Page,Row,Switch,Text,IconButton,Divider,Tabs,Tab,Column,VerticalDivider,TextButton,TextField,ElevatedButton,AlertDialog,Dropdown,dropdown,Slider,KeyboardType
def main(page:Page):
    def theme_manager(e):
        page.theme_mode='dark' if page.theme_mode=='light' else 'light'
        page.update()
    def refresh_tabs():
        db=sqlite3.connect('db.db')
        tabs.tabs=[Tab(text='PRODUCTS',content=Column([TextButton(i,on_click=lambda e:populate_editor(e,'editing')) for i in db.execute(f'select * from PRODUCTS order by SUPPLIER,NAME').fetchall()])),
                   Tab(text='SUPPLIERS',content=Column([TextButton(i,on_click=lambda e:populate_editor(e,'editing')) for i in db.execute(f'select * from SUPPLIERS order by NAME').fetchall()])),
                   Tab(text='CLIENTS',content=Column([TextButton(i,on_click=lambda e:populate_editor(e,'editing')) for i in db.execute(f'select * from CLIENTS order by NAME').fetchall()])),
                   Tab(text='SALES',content=Column([Text(str(i)) for i in db.execute(f'select * from SALES order by DATE,CLIENT').fetchall()])),
                   Tab(text='PURCHASES',content=Column([Text(str(i)) for i in db.execute(f'select * from PURCHASES order by DATE,SUPPLIER').fetchall()]))]
        db.close()
        page.update()
    def save(e,how,subject):
        db=sqlite3.connect('db.db')
        values=[((textfield.value).upper() if isinstance(textfield.value, str) else textfield.value) for textfield in r_editor.controls if isinstance(textfield,TextField) or isinstance(textfield,Dropdown)]
        if how=='inserting':
            db.execute(f'insert into {tables[tabs.selected_index]} values(?,?,?,?,?)',values)
            alert.title=Text(f'RECORD {subject} INSERTED SUCCESSFULLY',color='green')
        elif how=='updating':
            if tables[tabs.selected_index]=='PRODUCTS':db.execute(f'update {tables[tabs.selected_index]} set SUPPLIER=?,NAME=?,PRICE=?,STOCK=?,POSITION=? where SUPPLIER=? and NAME=?',values+list(subject))
            else:db.execute(f'update {tables[tabs.selected_index]} set NAME=?,DOC=?,ADDRESS=?,PHONE=?,MAIL=? where NAME=? and DOC=?',values+list(subject))
            alert.title=Text(f'RECORD {subject} UPDATED SUCCESSFULLY',color='green')
        elif how=='deleting':
            db.execute(f'delete from {tables[tabs.selected_index]} where NAME=? and DOC=?',subject)
            alert.title=Text(f'RECORD {subject} DELETED SUCCESSFULLY',color='red')
        db.commit()
        db.close()
        r_editor.controls.clear()
        alert.open=True
        refresh_tabs()
    def order(e,subject):
        def add_row():
            rows=c_order.controls[2]
            def set_max(e):
                db=sqlite3.connect('db.db')
                stock=db.execute('select STOCK from PRODUCTS where NAME=?', (d_product.value,)).fetchone()[0]
                db.close()
                t_quantity.max=stock
                t_quantity.divisions=stock-1 if stock>1 else 1
                if t_quantity.value>t_quantity.max:t_quantity.value=t_quantity.max
                page.update()
            def slider_change(e):
                page.update()
            db=sqlite3.connect('db.db')
            if tables[tabs.selected_index]=='CLIENTS':
                t_quantity=Slider(label='QUANTITY {value}',min=1,max=1,value=1,divisions=1,width=200,on_change=slider_change)
                d_product=Dropdown(label='PRODUCT',options=[dropdown.Option(p[0]) for p in db.execute('select NAME from PRODUCTS where STOCK>0').fetchall()],on_change=set_max,width=200)
            elif tables[tabs.selected_index]=='SUPPLIERS':
                t_quantity=TextField(label='QUANTITY',width=200,keyboard_type=KeyboardType.NUMBER,value='1')
                d_product=Dropdown(label='PRODUCT',options=[dropdown.Option(p[0]) for p in db.execute('select NAME from PRODUCTS').fetchall()],width=200)
            db.close()
            row=(Row([IconButton(icon='remove_circle',icon_color='red',on_click=lambda e:c_order.controls.remove(e.control.parent) or page.update()),
                                        d_product,
                                        t_quantity,
                                        IconButton(icon='add_circle',icon_color='green',on_click=lambda e:add_row())]))
            rows.controls.append(row)
            page.update()
        def order_confirm(e):
            if tables[tabs.selected_index]=='CLIENTS':
                db=sqlite3.connect('db.db')
                rows= c_order.controls[2].controls
                for row in rows:
                    product=row.controls[1].value
                    quantity=int(row.controls[2].value)
                    price=db.execute('select PRICE from PRODUCTS where NAME=?', (product,)).fetchone()[0]
                    partial=quantity*price
                    db.execute('insert into SALES values(?,?,?,?,?)',(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),subject[0],product,partial,quantity))
                    db.commit()
                    db.execute('update PRODUCTS set STOCK=STOCK-? where NAME=?',(quantity,product))
                    db.commit()
                db.close()
                alert.title=Text(f'ORDER FOR CLIENT: {subject[0]} PLACED SUCCESSFULLY',color='green')
            elif tables[tabs.selected_index]=='SUPPLIERS':
                db=sqlite3.connect('db.db')
                rows= c_order.controls[2].controls
                for row in rows:
                    product=row.controls[1].value
                    quantity=int(row.controls[2].value)
                    price=db.execute('select PRICE from PRODUCTS where NAME=?', (product,)).fetchone()[0]
                    db.execute('insert into PURCHASES values(?,?,?,?,?)',(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),subject[0],product,price,quantity))
                    db.commit()
                    db.execute('update PRODUCTS set STOCK=STOCK+? where NAME=?',(quantity,product))
                    db.commit()
                db.close()
                alert.title=Text(f'ORDER FROM SUPPLIER: {subject[0]} PLACED SUCCESSFULLY',color='green')
            alert.open=True
            c_order.controls.clear()
            refresh_tabs()
        if tables[tabs.selected_index]=='CLIENTS':c_order.controls=[Text(f'ORDER FOR CLIENT: {subject[0]}',color='blue',size=20),
                                                                    ElevatedButton('ORDER',on_click=order_confirm,color='green'),
                                                                    Column()] 
        elif tables[tabs.selected_index]=='SUPPLIERS':c_order.controls=[Text(f'ORDER FROM SUPPLIER: {subject[0]}',color='blue',size=20),
                                                                        ElevatedButton('ORDER',on_click=order_confirm,color='green'),
                                                                        Column()]
        add_row()
        page.update()
    def populate_editor(e,how):
        t_editor_title.value,r_editor.controls,c_order.controls='',[],[]
        if tables[tabs.selected_index] not in ['SALES','PURCHASES']:
            t_editor_title.value=f'EDITOR - {tables[tabs.selected_index][:-1]} - {how.upper()}'
            db=sqlite3.connect('db.db')
            if tables[tabs.selected_index] in ['CLIENTS','SUPPLIERS']:
                if how=='inserting':
                    r_editor.controls=[TextField(label=label[1],width=200) for label in db.execute(f'pragma table_info("{tables[tabs.selected_index]}")').fetchall()]
                    r_editor.controls.append(Column([ElevatedButton('INSERT',on_click=lambda e:save(e,'inserting',None),color='green'),
                                                    ElevatedButton('CANCEL',on_click=lambda e:r_editor.controls.clear() or page.update(),color='orange')]))
                elif how=='editing':
                    subject=e.control.text
                    r_editor.controls=[TextField(label=label[1],width=200,value=subject[i]) for i,label in enumerate(db.execute(f'pragma table_info("{tables[tabs.selected_index]}")').fetchall())]
                    r_editor.controls.append(Column([ElevatedButton('UPDATE',on_click=lambda e:save(e,'updating',subject[:2]),color='green'),
                                                    ElevatedButton('CANCEL',on_click=lambda e:r_editor.controls.clear() or page.update(),color='orange')]))
                    r_editor.controls.append(Column([ElevatedButton('DELETE',on_click=lambda e:save(e,'deleting',subject[:2]),color='red'),
                                                    ElevatedButton('ORDER',on_click=lambda e:order(e,subject),color='blue')]))
            elif tables[tabs.selected_index]=='PRODUCTS':
                r_editor.controls=[d_supplier]
                if how=='inserting':
                    d_supplier.options=[dropdown.Option(supplier[0]) for supplier in db.execute('select NAME from SUPPLIERS').fetchall()]
                    r_editor.controls+=[TextField(label=label[1],width=200) for label in db.execute(f'pragma table_info("PRODUCTS")').fetchall()[1:]]
                    r_editor.controls[3].value='0'
                    r_editor.controls[3].read_only=True
                    r_editor.controls.append(Column([ElevatedButton('INSERT',on_click=lambda e:save(e,'inserting',None),color='green'),
                                                    ElevatedButton('CANCEL',on_click=lambda e:r_editor.controls.clear() or page.update(),color='orange')]))
                elif how=='editing':
                    subject=e.control.text
                    d_supplier.value=subject[0]
                    r_editor.controls[0].value=subject[0]
                    r_editor.controls+=[TextField(label=label[1],width=200,value=subject[i+1]) for i,label in enumerate(db.execute(f'pragma table_info("PRODUCTS")').fetchall()[1:])]
                    r_editor.controls.append(Column([ElevatedButton('UPDATE',on_click=lambda e:save(e,'updating',subject[:2]),color='green'),
                                                    ElevatedButton('CANCEL',on_click=lambda e:r_editor.controls.clear() or page.update(),color='orange')]))
                    r_editor.controls.append(Column([ElevatedButton('DELETE',on_click=lambda e:save(e,'deleting',subject[:2]),color='red')]))
            db.close()
        page.update()
    page.window.full_screen=True
    tabs=Tabs(on_change=lambda e:populate_editor(e,'inserting'),width=600,scrollable=True)
    refresh_tabs()
    c_order=Column(width=600)
    t_editor_title=Text('EDITOR',color='green',size=20)
    r_editor=Row(alignment='center')
    d_supplier=Dropdown(label='SUPPLIER',width=200)
    alert=AlertDialog(title=Text(''))
    page.dialog=alert
    page.add(Row([Switch(on_change=theme_manager),
                  Text('© 2026 daWAREHOUSE - All rights reserved',color='orange',size=40),
                  IconButton(icon='exit_to_app',icon_color='red',icon_size=50,on_click=lambda e:page.window.destroy())],alignment='center'),
             Divider(),
             Row([tabs,VerticalDivider(),c_order],alignment='center',height=500),
             Divider(),
             Row([t_editor_title],alignment='center'),
             r_editor,
             alert)
app(main)